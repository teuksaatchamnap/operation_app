<?php

namespace App\Services;

use Carbon\Carbon;
use Illuminate\Support\Facades\DB;

/**
 * Shared tier-classification service.
 *
 * Replicates the Python `NewCalculTier()` logic so that every report
 * (F2F, OFD, Activity Indicators, Advisor Bonus, …) uses the **same**
 * classification without duplicating code.
 *
 * Return format of calculateTiers():
 *   [
 *     'allSiteTier' => [ ['site_id' => 'A1', 'tier' => 'ST1'], … ],
 *     'tierLists'   => [
 *         0 => [site_ids…],  // Super Tier 1
 *         1 => [site_ids…],  // Tier 1
 *         2 => [site_ids…],  // Tier 2
 *         3 => [site_ids…],  // Tier 3
 *         4 => [site_ids…],  // New
 *         5 => [site_ids…],  // Reopen
 *         6 => [site_ids…],  // Inactive
 *         7 => [site_ids…],  // Closed
 *         8 => [site_ids…],  // Dead
 *     ],
 *   ]
 */
class TierService
{
    /** Tier-label constants (index = position in tierLists). */
    public const TIER_LABELS = ['ST1', '1', '2', '3', 'New', 'Reopen', 'Inactive', 'Closed', 'Dead'];

    // Bot/day thresholds
    private const THRESHOLD_ST1 = 110;
    private const THRESHOLD_T1  = 70;
    private const THRESHOLD_T2  = 45;

    /**
     * Classify every site into tiers for a given reference month.
     *
     * @param  Carbon  $referenceMonth  First day of the target month.
     * @return array{allSiteTier: array, tierLists: array, tierMaps: array}
     */
    public function calculateTiers(Carbon $referenceMonth): array
    {
        $currentDate = $referenceMonth->copy()->startOfMonth();
        $dateN1      = $currentDate->copy()->subMonths(12);

        // All sites ordered the same way as Python
        $allSites = DB::table('Sites')
            ->select('Id_Site', 'Platform')
            ->orderByRaw("LEFT(Id_Site, 1), LENGTH(Id_Site), Id_Site")
            ->get();

        // Sales per site in the last 12 months (only rows with open days > 0)
        $salesPerSite = DB::table('Sales')
            ->join('Sites', 'Sales.Id_Site', '=', 'Sites.Id_Site')
            ->where('Sales.Month', '<=', $currentDate)
            ->where('Sales.Month', '>', $dateN1)
            ->where('Sales.Number_Open_Days', '>', 0)
            ->selectRaw('(Total_Sales - WiS_Sales - Bottle_Sales) / Number_Open_Days as bot_day')
            ->addSelect('Sales.Id_Site', 'Number_Open_Days', 'Sales.Month')
            ->get()
            ->groupBy('Id_Site');

        // Batch-fetch sites that have ever had any sales (eliminates N+1 queries)
        $sitesWithAnySales = DB::table('Sales')->distinct()->pluck('Id_Site')->flip()->all();

        // Batch-fetch sites that had sales > 3 months ago (eliminates N+1 for New detection)
        $sitesWithSalesBefore3 = DB::table('Sales')
            ->where('Month', '<=', $currentDate->copy()->subMonths(3))
            ->distinct()
            ->pluck('Id_Site')
            ->flip()
            ->all();

        $lists = array_fill(0, 9, []);   // 9 tiers
        $allSiteTier = [];

        foreach ($allSites as $site) {
            $siteId   = $site->Id_Site;
            $platform = $site->Platform;

            $siteSales = $salesPerSite->get($siteId, collect());

            // ── Dead ──
            if ($platform === 'Dead') {
                $lists[8][] = $siteId;
                $allSiteTier[] = ['site_id' => $siteId, 'tier' => 'Dead'];
                continue;
            }

            // ── Closed ── no sales in last 12 months but had sales before
            if ($siteSales->isEmpty()) {
                $hadSalesBefore = isset($sitesWithAnySales[$siteId]);

                if ($hadSalesBefore) {
                    $lists[7][] = $siteId;
                    $allSiteTier[] = ['site_id' => $siteId, 'tier' => 'Closed'];
                } else {
                    $lists[8][] = $siteId;
                    $allSiteTier[] = ['site_id' => $siteId, 'tier' => 'Dead'];
                }
                continue;
            }

            // ── Inactive ── no sales in the current month
            $hasCurrentMonth = $siteSales->contains(function ($row) use ($currentDate) {
                return Carbon::parse($row->Month)->startOfMonth()->eq($currentDate);
            });

            if (! $hasCurrentMonth) {
                $lists[6][] = $siteId;
                $allSiteTier[] = ['site_id' => $siteId, 'tier' => 'Inactive'];
                continue;
            }

            // ── New ── ≤ 3 months of sales history ever
            if ($siteSales->count() <= 3) {
                $hadSalesBefore3 = isset($sitesWithSalesBefore3[$siteId]);

                if (! $hadSalesBefore3) {
                    $lists[4][] = $siteId;
                    $allSiteTier[] = ['site_id' => $siteId, 'tier' => 'New'];
                } else {
                    $lists[5][] = $siteId;
                    $allSiteTier[] = ['site_id' => $siteId, 'tier' => 'Reopen'];
                }
                continue;
            }

            // ── Reopen ── < 4 months with sales in the last 3 months
            $recentSalesCount = $siteSales->filter(function ($row) use ($currentDate) {
                return Carbon::parse($row->Month)->gte($currentDate->copy()->subMonths(3));
            })->count();

            if ($recentSalesCount < 4) {
                $lists[5][] = $siteId;
                $allSiteTier[] = ['site_id' => $siteId, 'tier' => 'Reopen'];
                continue;
            }

            // ── Active tiers based on avg bot/day ──
            $avg = $siteSales->avg('bot_day');

            if ($avg > self::THRESHOLD_ST1) {
                $lists[0][] = $siteId;
                $allSiteTier[] = ['site_id' => $siteId, 'tier' => 'ST1'];
            } elseif ($avg > self::THRESHOLD_T1) {
                $lists[1][] = $siteId;
                $allSiteTier[] = ['site_id' => $siteId, 'tier' => '1'];
            } elseif ($avg >= self::THRESHOLD_T2) {
                $lists[2][] = $siteId;
                $allSiteTier[] = ['site_id' => $siteId, 'tier' => '2'];
            } elseif ($avg > 0) {
                $lists[3][] = $siteId;
                $allSiteTier[] = ['site_id' => $siteId, 'tier' => '3'];
            }
        }

        return [
            'allSiteTier' => $allSiteTier,
            'tierLists'   => $lists,
            'tierMaps'    => array_map('array_flip', $lists),
        ];
    }

    /**
     * Calculate tiers for multiple years (current year, N-1, N-2, …).
     *
     * @param  Carbon  $currentDate  Reference month.
     * @param  int     $yearStart    Earliest year to include.
     * @return array   Indexed by year offset (0 = current, 1 = N-1, …).
     */
    public function calculateTiersMultiYear(Carbon $currentDate, int $yearStart = 2018): array
    {
        $nbYears = $currentDate->year - $yearStart + 1;
        $tiers   = [];

        for ($i = 0; $i < $nbYears; $i++) {
            $date = Carbon::create($currentDate->year - $i, $currentDate->month, 1);
            $tiers[] = $this->calculateTiers($date);
        }

        return $tiers;
    }

    /**
     * Hardcoded exchange rates (KHR/USD) matching Python's exchange_rate_year().
     */
    public static function exchangeRate(Carbon $date): int
    {
        return match ($date->year) {
            2017 => 4050,
            2018 => 4050,
            2019 => 4050,
            2020 => 4100,
            2021 => 4100,
            2022 => 4100,
            2023 => 4100,
            2024 => 4100,
            2025 => 4100,
            2026 => 4100,
            default => 4100,
        };
    }

    /**
     * Returns expense categories matching Python's CategoryExpenses().
     */
    public static function categoryExpenses(): array
    {
        return ['production', 'salary', 'delivery', 'contribution', 'investment', 'technical'];
    }

    /**
     * Returns platform list from DB.
     */
    public static function platformList(): array
    {
        return DB::table('Platform')
            ->distinct()
            ->orderBy('Code_Platform')
            ->pluck('Code_Platform')
            ->toArray();
    }
}
