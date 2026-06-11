<?php

namespace App\Services;

use Carbon\Carbon;
use Illuminate\Support\Facades\DB;
use PhpOffice\PhpSpreadsheet\Cell\Coordinate;
use PhpOffice\PhpSpreadsheet\Style\Alignment;
use PhpOffice\PhpSpreadsheet\Style\Border;
use PhpOffice\PhpSpreadsheet\Style\Fill;
use PhpOffice\PhpSpreadsheet\Style\NumberFormat;
use PhpOffice\PhpSpreadsheet\Worksheet\Worksheet;

/**
 * Shared KPI sheet‑block service.
 *
 * Every method writes a *tier × platform* grid into an existing worksheet.
 * The SAME instance can be reused by F2F, OFD, Activity Indicators, or any
 * future report that needs KPI blocks — change it here, change it everywhere.
 *
 * All row / column parameters are **0‑based** (matching the original Python
 * code) and converted internally to PhpSpreadsheet's 1‑based references.
 */
class KpiSheetService
{
    private TierService $tierService;

    // ── Query caches ──
    /** @var array<string, \Illuminate\Support\Collection> Cached master Sales data keyed by date range */
    private array $salesCache = [];
    /** @var array<string, \Illuminate\Support\Collection> Cached master Expenses data keyed by date range */
    private array $expensesCache = [];


    // ── Tier labels (index matches TierService::tierLists) ──
    private const LABELS_7 = ['Super Tier 1', 'Tier 1', 'Tier 2', 'Tier 3', 'New', 'Reopen', 'Inactive']; // excludes Closed + Dead
    private const LABELS_8 = ['Super Tier 1', 'Tier 1', 'Tier 2', 'Tier 3', 'New', 'Reopen', 'Inactive', 'Closed']; // excludes Dead only
    private const LABELS_9 = ['Super Tier 1', 'Tier 1', 'Tier 2', 'Tier 3', 'New', 'Reopen', 'Total', 'Inactive', 'Closed']; // NbSite layout

    // ── Common number‑format codes ──
    public const FMT_NUM     = '#,##0';
    public const FMT_PCT     = '0%';
    public const FMT_GROWTH  = '+0%;-0%';
    public const FMT_DOLLAR  = '#,##0" $"';

    /**
     * Number of historical year columns shown in every KPI sheet (most recent first).
     * Change this value to display 4, 5, 6 … years across all KPI blocks at once.
     */
    public const KPI_YEARS_SHOWN = 4;

    public function __construct(?TierService $tierService = null)
    {
        $this->tierService = $tierService ?? new TierService();
    }

    // ═══════════════════════════════════════════════════════════════
    //  KPI FORMAT — header row + column layout + tier calculation
    // ═══════════════════════════════════════════════════════════════

    /**
     * Set up the KPI worksheet header (year labels, platform columns, freeze panes)
     * AND compute multi‑year tiers.
     *
     * @return array  Multi‑year tiers (index 0 = current year, 1 = N‑1, …)
     */
    public function kpiFormat(
        Worksheet $ws,
        Carbon $currentDate,
        Carbon $date1,
        int $yearStart,
        array $platforms,
        ?array $precomputedTiers = null,
    ): array {
        $nbYear = min($currentDate->year - $yearStart + 1, self::KPI_YEARS_SHOWN);
        $col    = 0;

        // Column widths
        $ws->getColumnDimension('A')->setWidth(15);
        $ws->getColumnDimension('B')->setWidth(11);
        for ($c = 3; $c <= 53; $c++) {
            $ws->getColumnDimensionByColumn($c)->setWidth(13);
        }
        $ws->freezePane('C3');
        $ws->getSheetView()->setZoomScale(70);

        $tiers = [];
        $nPlat = count($platforms);

        for ($i = 0; $i < $nbYear; $i++) {
            // Year header + "Total"
            $totalCol = 2 + $col + $nPlat; // 0‑based
            $this->writeCell($ws, 0, $totalCol, $currentDate->year - $i, $this->boldStyle());
            $this->writeCell($ws, 1, $totalCol, 'Total', $this->boldStyle());

            // Platform names
            for ($k = 0; $k < $nPlat; $k++) {
                $this->writeCell($ws, 1, 2 + $col, $platforms[$k], $this->boldStyle());
                $col++;
            }

            // Separator column (+2 skip: Total + blank)
            $col += 2;

            // Use precomputed tiers if available, otherwise compute
            if ($precomputedTiers !== null) {
                $tiers[] = $precomputedTiers[$i];
            } else {
                $date = Carbon::create($currentDate->year - $i, $currentDate->month, 1);
                $tiers[] = $this->tierService->calculateTiers($date);
            }
        }

        return $tiers;
    }

    // ═══════════════════════════════════════════════════════════════
    //  QUERY CACHING — fetch once per date range, reuse across methods
    // ═══════════════════════════════════════════════════════════════

    /**
     * Get cached Sales master data for a given date range.
     * All Sales-based KPI methods share this single query instead of each
     * running their own.
     */
    private function getCachedSales(Carbon $dateEnd, Carbon $date1, int $yearOffset): \Illuminate\Support\Collection
    {
        $key = $dateEnd->format('Y-m') . '|' . $date1->format('Y-m') . '|' . $yearOffset;
        if (!isset($this->salesCache[$key])) {
            $this->salesCache[$key] = DB::table('Sales')
                ->join('Sites', 'Sales.Id_Site', '=', 'Sites.Id_Site')
                ->where('Month', '<=', $dateEnd->copy()->subMonths(12 * $yearOffset))
                ->where('Month', '>', $date1->copy()->subMonths(12 * $yearOffset))
                ->groupBy('Sales.Id_Site', 'Sites.Old_Platform')
                ->selectRaw("Sales.Id_Site, Sites.Old_Platform,
                    SUM(Total_Sales) as total_sales,
                    SUM(Bottle_Sales) as bottle_sales,
                    SUM(WiS_Sales) as wis_sales,
                    SUM(Bottle_Income) as bottle_income,
                    SUM(Total_Sales - Bottle_Sales) as bot_inc,
                    SUM(Total_Sales - WiS_Sales - Bottle_Sales) as bot_exc,
                    SUM(Number_Open_Days) as total_days,
                    SUM(Total_Income) as total_income,
                    SUM(WiS_Income) as wis_income,
                    SUM(Total_Income - WiS_Income) as income_exc,
                    COUNT(*) as active_months")
                ->get();
        }
        return $this->salesCache[$key];
    }

    /**
     * Get cached Expenses master data for a given date range.
     */
    private function getCachedExpenses(Carbon $dateEnd, Carbon $date1, int $yearOffset): \Illuminate\Support\Collection
    {
        $key = 'exp|' . $dateEnd->format('Y-m') . '|' . $date1->format('Y-m') . '|' . $yearOffset;
        if (!isset($this->expensesCache[$key])) {
            $this->expensesCache[$key] = DB::table('Expenses')
                ->join('Sites', 'Expenses.Id_Site', '=', 'Sites.Id_Site')
                ->where('Month', '<=', $dateEnd->copy()->subMonths(12 * $yearOffset))
                ->where('Month', '>', $date1->copy()->subMonths(12 * $yearOffset))
                ->groupBy('Expenses.Id_Site', 'Sites.Old_Platform', 'Ref_expenses', 'Category_expenses')
                ->selectRaw("Expenses.Id_Site, Sites.Old_Platform, Ref_expenses, Category_expenses,
                    SUM(Amount_Expenses) as total_amount,
                    SUM(Paid) as total_paid")
                ->get();
        }
        return $this->expensesCache[$key];
    }

    /**
     * Pre-warm the expenses cache for all year offsets at once.
     * ONE DB query replaces up to N individual getCachedExpenses() calls.
     */
    private function preWarmExpensesCache(Carbon $dateEnd, Carbon $date1, int $numYears): void
    {
        $missing = [];
        for ($m = 0; $m < $numYears; $m++) {
            $key = 'exp|' . $dateEnd->format('Y-m') . '|' . $date1->format('Y-m') . '|' . $m;
            if (!isset($this->expensesCache[$key])) $missing[] = $m;
        }
        if (empty($missing)) return;

        $maxOffset = max($missing);
        $minDate = $date1->copy()->subMonths(12 * $maxOffset);

        $allRows = DB::table('Expenses')
            ->join('Sites', 'Expenses.Id_Site', '=', 'Sites.Id_Site')
            ->where('Month', '<=', $dateEnd)
            ->where('Month', '>', $minDate)
            ->groupBy('Expenses.Id_Site', 'Sites.Old_Platform', 'Ref_expenses', 'Category_expenses', 'Month')
            ->selectRaw("Expenses.Id_Site, Sites.Old_Platform, Ref_expenses, Category_expenses, Month,
                SUM(Amount_Expenses) as total_amount, SUM(Paid) as total_paid")
            ->get();

        $rowsByMonth = [];
        foreach ($allRows as $row) {
            $rowsByMonth[$row->Month][] = $row;
        }
        ksort($rowsByMonth);

        foreach ($missing as $m) {
            $key = 'exp|' . $dateEnd->format('Y-m') . '|' . $date1->format('Y-m') . '|' . $m;
            $rangeEnd   = $dateEnd->copy()->subMonths(12 * $m)->toDateString();
            $rangeStart = $date1->copy()->subMonths(12 * $m)->toDateString();

            $grouped = [];
            foreach ($rowsByMonth as $month => $rows) {
                if ($month > $rangeEnd || $month <= $rangeStart) continue;
                foreach ($rows as $row) {
                    $gk = $row->Id_Site . '|' . $row->Ref_expenses . '|' . $row->Category_expenses;
                    if (!isset($grouped[$gk])) {
                        $grouped[$gk] = (object) [
                            'Id_Site' => $row->Id_Site,
                            'Old_Platform' => $row->Old_Platform,
                            'Ref_expenses' => $row->Ref_expenses,
                            'Category_expenses' => $row->Category_expenses,
                            'total_amount' => 0.0,
                            'total_paid' => 0.0,
                        ];
                    }
                    $grouped[$gk]->total_amount += (float) $row->total_amount;
                    $grouped[$gk]->total_paid += (float) $row->total_paid;
                }
            }

            $this->expensesCache[$key] = collect(array_values($grouped));
        }
    }

    /**
     * Pre-warm the sales cache for all year offsets at once.
     */
    private function preWarmSalesCache(Carbon $dateEnd, Carbon $date1, int $numYears): void
    {
        $missing = [];
        for ($m = 0; $m < $numYears; $m++) {
            $key = $dateEnd->format('Y-m') . '|' . $date1->format('Y-m') . '|' . $m;
            if (!isset($this->salesCache[$key])) $missing[] = $m;
        }
        if (empty($missing)) return;

        $maxOffset = max($missing);
        $minDate = $date1->copy()->subMonths(12 * $maxOffset);

        $allRows = DB::table('Sales')
            ->join('Sites', 'Sales.Id_Site', '=', 'Sites.Id_Site')
            ->where('Month', '<=', $dateEnd)
            ->where('Month', '>', $minDate)
            ->groupBy('Sales.Id_Site', 'Sites.Old_Platform', 'Month')
            ->selectRaw("Sales.Id_Site, Sites.Old_Platform, Month,
                SUM(Total_Sales) as total_sales, SUM(Bottle_Sales) as bottle_sales,
                SUM(WiS_Sales) as wis_sales, SUM(Bottle_Income) as bottle_income,
                SUM(Total_Sales - Bottle_Sales) as bot_inc,
                SUM(Total_Sales - Bottle_Sales - WiS_Sales) as bot_exc,
                SUM(Number_Open_Days) as total_days, SUM(Total_Income) as total_income,
                SUM(WiS_Income) as wis_income, SUM(Total_Income - WiS_Income) as income_exc,
                COUNT(*) as active_months")
            ->get();

        $rowsByMonth = [];
        foreach ($allRows as $row) {
            $rowsByMonth[$row->Month][] = $row;
        }
        ksort($rowsByMonth);

        foreach ($missing as $m) {
            $key = $dateEnd->format('Y-m') . '|' . $date1->format('Y-m') . '|' . $m;
            $rangeEnd   = $dateEnd->copy()->subMonths(12 * $m)->toDateString();
            $rangeStart = $date1->copy()->subMonths(12 * $m)->toDateString();

            $grouped = [];
            foreach ($rowsByMonth as $month => $rows) {
                if ($month > $rangeEnd || $month <= $rangeStart) continue;
                foreach ($rows as $row) {
                    $id = $row->Id_Site;
                    if (!isset($grouped[$id])) {
                        $grouped[$id] = (object) [
                            'Id_Site' => $id, 'Old_Platform' => $row->Old_Platform,
                            'total_sales' => 0.0, 'bottle_sales' => 0.0, 'wis_sales' => 0.0,
                            'bottle_income' => 0.0, 'bot_inc' => 0.0, 'bot_exc' => 0.0,
                            'total_days' => 0, 'total_income' => 0.0, 'wis_income' => 0.0,
                            'income_exc' => 0.0, 'active_months' => 0,
                        ];
                    }
                    $g = $grouped[$id];
                    $g->total_sales += (float) $row->total_sales;
                    $g->bottle_sales += (float) $row->bottle_sales;
                    $g->wis_sales += (float) $row->wis_sales;
                    $g->bottle_income += (float) $row->bottle_income;
                    $g->bot_inc += (float) $row->bot_inc;
                    $g->bot_exc += (float) $row->bot_exc;
                    $g->total_days += (int) $row->total_days;
                    $g->total_income += (float) $row->total_income;
                    $g->wis_income += (float) $row->wis_income;
                    $g->income_exc += (float) $row->income_exc;
                    $g->active_months += (int) $row->active_months;
                }
            }

            $this->salesCache[$key] = collect(array_values($grouped));
        }
    }

    /**
     * Pre-warm both Expenses and Sales caches for multiple date1 periods simultaneously.
     *
     * Uses one DB query per year-offset with conditional SUM (CASE WHEN per period)
     * so a single MySQL scan covers Monthly + YTD + LTM in one pass, populating the
     * same cache entries that getCachedExpenses() / getCachedSales() would have filled
     * through separate queries.
     *
     * Call this before generating exports with multiple KPI periods (e.g., ActivityIndicators
     * with Monthly + YTD + LTM).  For single-period exports (F2F, OFD, etc.) skip it —
     * the caches warm lazily as before.
     *
     * @param Carbon   $currentDate  The reference date (= dateEnd for all periods)
     * @param Carbon[] $date1Values  One Carbon per period, in any order
     * @param int      $numYears     Number of year offsets to pre-warm
     */
    public function prewarmMultiPeriod(Carbon $currentDate, array $date1Values, int $numYears = 9): void
    {
        if (count($date1Values) < 2) return;

        for ($m = 0; $m < $numYears; $m++) {
            $dateEndOffset = $currentDate->copy()->subMonths(12 * $m);
            $d1Offsets     = array_map(fn($d1) => $d1->copy()->subMonths(12 * $m), $date1Values);

            // Widest range = earliest date1 offset → used as the WHERE lower bound
            $minD1 = $d1Offsets[0];
            foreach ($d1Offsets as $d) {
                if ($d->lt($minD1)) $minD1 = $d;
            }

            // ── Expenses ──────────────────────────────────────────────────────
            $expSel = ['Expenses.Id_Site', 'Sites.Old_Platform', 'Ref_expenses', 'Category_expenses'];
            foreach ($d1Offsets as $idx => $d1) {
                $d = $d1->format('Y-m-d');
                $expSel[] = DB::raw("SUM(CASE WHEN Month > '{$d}' THEN Amount_Expenses ELSE 0 END) as ea{$idx}");
                $expSel[] = DB::raw("SUM(CASE WHEN Month > '{$d}' THEN Paid             ELSE 0 END) as ep{$idx}");
            }

            $expRows = DB::table('Expenses')
                ->join('Sites', 'Expenses.Id_Site', '=', 'Sites.Id_Site')
                ->where('Month', '<=', $dateEndOffset)
                ->where('Month', '>',  $minD1)
                ->groupBy('Expenses.Id_Site', 'Sites.Old_Platform', 'Ref_expenses', 'Category_expenses')
                ->select($expSel)
                ->get();

            foreach ($date1Values as $idx => $date1) {
                $key = 'exp|' . $currentDate->format('Y-m') . '|' . $date1->format('Y-m') . '|' . $m;
                if (isset($this->expensesCache[$key])) continue;
                $this->expensesCache[$key] = $expRows->map(fn($r) => (object)[
                    'Id_Site'           => $r->Id_Site,
                    'Old_Platform'      => $r->Old_Platform,
                    'Ref_expenses'      => $r->Ref_expenses,
                    'Category_expenses' => $r->Category_expenses,
                    'total_amount'      => $r->{"ea{$idx}"},
                    'total_paid'        => $r->{"ep{$idx}"},
                ]);
            }

            // ── Sales ─────────────────────────────────────────────────────────
            $salSel = ['Sales.Id_Site', 'Sites.Old_Platform'];
            foreach ($d1Offsets as $idx => $d1) {
                $d = $d1->format('Y-m-d');
                $salSel[] = DB::raw("SUM(CASE WHEN Month > '{$d}' THEN Total_Sales                             ELSE 0 END) as s_ts{$idx}");
                $salSel[] = DB::raw("SUM(CASE WHEN Month > '{$d}' THEN Bottle_Sales                            ELSE 0 END) as s_bs{$idx}");
                $salSel[] = DB::raw("SUM(CASE WHEN Month > '{$d}' THEN WiS_Sales                              ELSE 0 END) as s_ws{$idx}");
                $salSel[] = DB::raw("SUM(CASE WHEN Month > '{$d}' THEN Bottle_Income                          ELSE 0 END) as s_bi{$idx}");
                $salSel[] = DB::raw("SUM(CASE WHEN Month > '{$d}' THEN Total_Sales - Bottle_Sales             ELSE 0 END) as s_ni{$idx}");
                $salSel[] = DB::raw("SUM(CASE WHEN Month > '{$d}' THEN Total_Sales - WiS_Sales - Bottle_Sales ELSE 0 END) as s_xe{$idx}");
                $salSel[] = DB::raw("SUM(CASE WHEN Month > '{$d}' THEN Number_Open_Days                       ELSE 0 END) as s_od{$idx}");
                $salSel[] = DB::raw("SUM(CASE WHEN Month > '{$d}' THEN Total_Income                           ELSE 0 END) as s_ti{$idx}");
                $salSel[] = DB::raw("SUM(CASE WHEN Month > '{$d}' THEN WiS_Income                             ELSE 0 END) as s_wi{$idx}");
                $salSel[] = DB::raw("SUM(CASE WHEN Month > '{$d}' THEN Total_Income - WiS_Income              ELSE 0 END) as s_ie{$idx}");
                $salSel[] = DB::raw("SUM(CASE WHEN Month > '{$d}' THEN 1                                      ELSE 0 END) as s_am{$idx}");
            }

            $salRows = DB::table('Sales')
                ->join('Sites', 'Sales.Id_Site', '=', 'Sites.Id_Site')
                ->where('Month', '<=', $dateEndOffset)
                ->where('Month', '>',  $minD1)
                ->groupBy('Sales.Id_Site', 'Sites.Old_Platform')
                ->select($salSel)
                ->get();

            foreach ($date1Values as $idx => $date1) {
                $key = $currentDate->format('Y-m') . '|' . $date1->format('Y-m') . '|' . $m;
                if (isset($this->salesCache[$key])) continue;
                $this->salesCache[$key] = $salRows->map(fn($r) => (object)[
                    'Id_Site'       => $r->Id_Site,
                    'Old_Platform'  => $r->Old_Platform,
                    'total_sales'   => $r->{"s_ts{$idx}"},
                    'bottle_sales'  => $r->{"s_bs{$idx}"},
                    'wis_sales'     => $r->{"s_ws{$idx}"},
                    'bottle_income' => $r->{"s_bi{$idx}"},
                    'bot_inc'       => $r->{"s_ni{$idx}"},
                    'bot_exc'       => $r->{"s_xe{$idx}"},
                    'total_days'    => $r->{"s_od{$idx}"},
                    'total_income'  => $r->{"s_ti{$idx}"},
                    'wis_income'    => $r->{"s_wi{$idx}"},
                    'income_exc'    => $r->{"s_ie{$idx}"},
                    'active_months' => $r->{"s_am{$idx}"},
                ]);
            }
        }
    }

    /**
     * Get count of active months per site from cached Sales data.
     */
    private function getCachedActiveMonths(Carbon $dateEnd, Carbon $date1, int $yearOffset): \Illuminate\Support\Collection
    {
        // active_months is already included in getCachedSales
        return $this->getCachedSales($dateEnd, $date1, $yearOffset);
    }

    /**
     * Get Expenses data filtered by Ref_expenses and/or Category_expenses,
     * re-aggregated per Id_Site (collapses the Ref/Category dimensions).
     */
    private function getFilteredExpensesBySite(
        Carbon $dateEnd, Carbon $date1, int $yearOffset,
        array $refFilter = [], array $catFilter = []
    ): \Illuminate\Support\Collection {
        $data = $this->getCachedExpenses($dateEnd, $date1, $yearOffset);
        if ($refFilter) {
            $data = $data->whereIn('Ref_expenses', $refFilter);
        }
        if ($catFilter) {
            $data = $data->whereIn('Category_expenses', $catFilter);
        }
        $grouped = [];
        foreach ($data as $row) {
            $id = $row->Id_Site;
            if (!isset($grouped[$id])) {
                $grouped[$id] = (object) [
                    'Id_Site' => $id,
                    'Old_Platform' => $row->Old_Platform,
                    'total_amount' => 0.0,
                    'total_paid' => 0.0,
                ];
            }
            $grouped[$id]->total_amount += (float) $row->total_amount;
            $grouped[$id]->total_paid += (float) $row->total_paid;
        }
        return collect(array_values($grouped));
    }

    // ═══════════════════════════════════════════════════════════════
    //  INDIVIDUAL KPI BLOCKS
    // ═══════════════════════════════════════════════════════════════

    /** Number of sites per tier. */
    public function kpiNbSite(Worksheet $ws, int $line, Carbon $currentDate, Carbon $date1, array $tiers, array $platforms): void
    {
        $nPlat = count($platforms);
        $labels = ['Super Tier 1', 'Tier 1', 'Tier 2', 'Tier 3', 'New', 'Reopen', 'Total', 'Inactive', 'Closed'];
        $this->writeTierLabels($ws, $line, $labels, $this->boldBorderStyle(), self::FMT_NUM);
        $dateRange = $this->dateRangeLabel($date1, $currentDate);
        $this->mergeWrite($ws, $line, 0, $line + 8, 0, "Nb of Sites \n{$dateRange}", $this->titleStyle());

        $nbTier = 8; // excludes Dead only

        // Fetch once, outside the tiers loop — results don't depend on year
        $allSiteIds = DB::table('Sales')
            ->join('Sites', 'Sales.Id_Site', '=', 'Sites.Id_Site')
            ->where('Sales.Id_Site', '<>', 'EBM')
            ->select('Sales.Id_Site', 'Sites.Old_Platform')
            ->distinct()
            ->get();
        // Pre-group by platform for O(1) per-platform access
        $sitesByPlatform = [];
        foreach ($allSiteIds as $s) {
            $sitesByPlatform[$s->Old_Platform][] = $s->Id_Site;
        }

        foreach ($tiers as $m => $tierData) {
            $tierMaps = $tierData['tierMaps'];
            $totalPerTier = array_fill(0, $nbTier, 0);

            for ($i = 0; $i < $nPlat; $i++) {
                $platIds = $sitesByPlatform[$platforms[$i]] ?? [];
                $siteTot = 0;

                for ($j = 0; $j < $nbTier; $j++) {
                    $cnt = 0;
                    foreach ($platIds as $sid) {
                        if (isset($tierMaps[$j][$sid])) $cnt++;
                    }
                    $totalPerTier[$j] += $cnt;

                    // NbSite has a special layout: Total row at index 6, Inactive at 7, Closed at 8
                    $rowOffset = ($j <= $nbTier - 3) ? $j : $j + 1;
                    if ($j <= $nbTier - 3) {
                        $siteTot += $cnt;
                    }

                    $this->writeCell($ws, $line + $rowOffset, $this->kpiCol($m, $i, $nPlat), $cnt, $this->borderStyle(), self::FMT_NUM);
                    $this->writeCell($ws, $line + $rowOffset, $this->kpiTotalCol($m, $nPlat), $totalPerTier[$j], $this->boldBorderStyle(), self::FMT_NUM);
                }

                // Total row (index 6 = $nbTier - 2)
                $this->writeCell($ws, $line + $nbTier - 2, $this->kpiCol($m, $i, $nPlat), $siteTot, $this->boldBorderStyle(), self::FMT_NUM);
            }

            // Grand total for "Total" row
            $grandTotal = array_sum($totalPerTier) - ($totalPerTier[$nbTier - 1] ?? 0) - ($totalPerTier[$nbTier - 2] ?? 0);
            $this->writeCell($ws, $line + $nbTier - 2, $this->kpiTotalCol($m, $nPlat), $grandTotal, $this->boldBorderStyle(), self::FMT_NUM);
        }
    }

    /** Number of sites as percentage of total. */
    public function kpiNbSitePercentage(Worksheet $ws, int $line, Carbon $currentDate, Carbon $date1, array $tiers, array $platforms): void
    {
        $nPlat  = count($platforms);
        $nbTier = 7; // excludes Closed + Dead
        $this->writeTierLabels($ws, $line, array_merge(self::LABELS_7, ['Total']), $this->boldBorderStyle(), self::FMT_PCT);
        $dateRange = $this->dateRangeLabel($date1, $currentDate);
        $this->mergeWrite($ws, $line, 0, $line + 7, 0, "Nb of Sites % \n{$dateRange}", $this->titleStyle());

        // Fetch once, outside the tiers loop
        $allSites = DB::table('Sites')
            ->where('Id_Site', '<>', 'EBM')
            ->select('Id_Site', 'Old_Platform')
            ->distinct()
            ->get();
        $sitesByPlatform = [];
        foreach ($allSites as $s) {
            $sitesByPlatform[$s->Old_Platform][] = $s->Id_Site;
        }

        foreach ($tiers as $m => $tierData) {
            $tierMaps = $tierData['tierMaps'];
            $totalPerTier = array_fill(0, $nbTier, 0);

            for ($i = 0; $i < $nPlat; $i++) {
                $platIds = $sitesByPlatform[$platforms[$i]] ?? [];
                $siteTot = 0;

                for ($j = 0; $j < $nbTier; $j++) {
                    $cnt = 0;
                    foreach ($platIds as $sid) {
                        if (isset($tierMaps[$j][$sid])) $cnt++;
                    }
                    $totalPerTier[$j] += $cnt;
                    $siteTot += $cnt;

                    $totalCell = $this->cell($line + $nbTier, $this->kpiCol($m, $i, $nPlat));
                    $this->writeCell($ws, $line + $j, $this->kpiCol($m, $i, $nPlat),
                        "=IFERROR({$cnt}/{$totalCell},0)", $this->borderStyle(), self::FMT_PCT);

                    $totalCellGlobal = $this->cell($line + $nbTier, $this->kpiTotalCol($m, $nPlat));
                    $this->writeCell($ws, $line + $j, $this->kpiTotalCol($m, $nPlat),
                        "=IFERROR({$totalPerTier[$j]}/{$totalCellGlobal},0)", $this->boldBorderStyle(), self::FMT_PCT);
                }

                $this->writeCell($ws, $line + $nbTier, $this->kpiCol($m, $i, $nPlat), $siteTot, $this->boldBorderStyle(), self::FMT_NUM);
            }

            $this->writeCell($ws, $line + $nbTier, $this->kpiTotalCol($m, $nPlat), array_sum($totalPerTier), $this->boldBorderStyle(), self::FMT_NUM);
        }
    }

    /** Beneficiaries (consumers) per tier — always last 12 months. */
    public function kpiBeneficiaries(Worksheet $ws, int $line, Carbon $currentDate, Carbon $date1, array $tiers, array $platforms): void
    {
        $nPlat  = count($platforms);
        $nbTier = 7;
        $this->writeTierLabels($ws, $line, array_merge(self::LABELS_7, ['Total']), $this->boldBorderStyle(), self::FMT_NUM);
        $date1Benef = $currentDate->copy()->subMonths(12); // always last 12 months for beneficiaries
        $dateRange  = $this->dateRangeLabel($date1Benef, $currentDate);
        $this->mergeWrite($ws, $line, 0, $line + 7, 0, "Consumers \n{$dateRange}", $this->titleStyle());

        // Batch-fetch all reference months in a single query
        $refDates = [];
        foreach (array_keys($tiers) as $m) {
            $refDates[] = $currentDate->copy()->subMonths(12 * $m)->toDateString();
        }
        $allBenefRaw = DB::table('Beneficiaries')
            ->join('Sites', 'Beneficiaries.Id_Site', '=', 'Sites.Id_Site')
            ->whereIn('Month', $refDates)
            ->select('Beneficiaries.Beneficiaries', 'Sites.Old_Platform', 'Beneficiaries.Id_Site', 'Beneficiaries.Month')
            ->get();
        // Index by [monthKey][Old_Platform] for O(1) access
        $benefByMonth = [];
        foreach ($allBenefRaw as $row) {
            $mk = Carbon::parse($row->Month)->format('Y-m');
            $benefByMonth[$mk][$row->Old_Platform][$row->Id_Site] = (int) $row->Beneficiaries;
        }

        foreach ($tiers as $m => $tierData) {
            $tierMaps = $tierData['tierMaps'];
            $mk = $currentDate->copy()->subMonths(12 * $m)->format('Y-m');
            $benefForMonth = $benefByMonth[$mk] ?? [];

            $totalPerTier = array_fill(0, $nbTier, 0);

            for ($i = 0; $i < $nPlat; $i++) {
                $platBenef = $benefForMonth[$platforms[$i]] ?? [];
                $tot = 0;

                for ($j = 0; $j < $nbTier; $j++) {
                    $val = 0;
                    foreach ($platBenef as $siteId => $benef) {
                        if (isset($tierMaps[$j][$siteId])) $val += $benef;
                    }
                    $totalPerTier[$j] += $val;
                    $tot += $val;

                    $this->writeCell($ws, $line + $j, $this->kpiCol($m, $i, $nPlat), $val, $this->borderStyle(), self::FMT_NUM);
                    $this->writeCell($ws, $line + $j, $this->kpiTotalCol($m, $nPlat), $totalPerTier[$j], $this->boldBorderStyle(), self::FMT_NUM);
                }

                $this->writeCell($ws, $line + $nbTier, $this->kpiCol($m, $i, $nPlat), $tot, $this->boldBorderStyle(), self::FMT_NUM);
            }

            $this->writeCell($ws, $line + $nbTier, $this->kpiTotalCol($m, $nPlat), array_sum($totalPerTier), $this->boldBorderStyle(), self::FMT_NUM);
        }
    }

    /** Average bot/day (ratio pattern). */
    public function kpiBotDay(Worksheet $ws, int $line, Carbon $currentDate, Carbon $date1, array $tiers, array $platforms, bool $withSchool, bool $hide = false): void
    {
        $nPlat  = count($platforms);
        $nbTier = 8; // includes Closed, excludes Dead
        $labels = array_merge(self::LABELS_8, ['Total']);
        $this->writeTierLabels($ws, $line, $labels, $this->boldBorderStyle(), self::FMT_NUM);
        $winLabel   = $withSchool ? 'inc.' : 'exc.';
        $dateRange  = $this->dateRangeLabel($date1, $currentDate);
        $this->mergeWrite($ws, $line, 0, $line + 8, 0, "Bot/day {$winLabel} WinS \n{$dateRange}", $this->titleStyle());

        foreach ($tiers as $m => $tierData) {
            $tierLists = $tierData['tierLists'];
            $tierMaps = $tierData['tierMaps'];
            $data = $this->getCachedSales($currentDate, $date1, $m);
            $botField = $withSchool ? 'bot_inc' : 'bot_exc';

            // Pre-group by platform for O(1) per-platform access (avoid repeated O(n) ->where())
            $dataByPlatform = [];
            foreach ($data as $row) {
                $dataByPlatform[$row->Old_Platform][] = $row;
            }

            $totalBot  = array_fill(0, $nbTier, 0.0);
            $totalSite = array_fill(0, $nbTier, 0);

            for ($i = 0; $i < $nPlat; $i++) {
                $platData = $dataByPlatform[$platforms[$i]] ?? [];
                $botTot  = 0.0;
                $siteTot = 0;

                for ($j = 0; $j < $nbTier; $j++) {
                    $botPlat  = 0.0;
                    $sitePlat = 0;
                    foreach ($platData as $row) {
                        if (isset($tierMaps[$j][$row->Id_Site])) {
                            $botPlat  += ($row->total_days > 0) ? (float) $row->$botField / (float) $row->total_days : 0;
                            $sitePlat++;
                        }
                    }

                    $this->writeCell($ws, $line + $j, $this->kpiCol($m, $i, $nPlat),
                        "=IFERROR({$botPlat}/{$sitePlat},0)", $this->borderStyle(), self::FMT_NUM);
                    $botTot  += $botPlat;
                    $siteTot += $sitePlat;
                    $totalBot[$j]  += $botPlat;
                    $totalSite[$j] += $sitePlat;
                    $this->writeCell($ws, $line + $j, $this->kpiTotalCol($m, $nPlat),
                        "=IFERROR({$totalBot[$j]}/{$totalSite[$j]},0)", $this->boldBorderStyle(), self::FMT_NUM);
                }

                $this->writeCell($ws, $line + $nbTier, $this->kpiCol($m, $i, $nPlat),
                    "=IFERROR({$botTot}/{$siteTot},0)", $this->boldBorderStyle(), self::FMT_NUM);
            }

            $this->writeCell($ws, $line + $nbTier, $this->kpiTotalCol($m, $nPlat),
                "=IFERROR(" . array_sum($totalBot) . "/" . array_sum($totalSite) . ",0)", $this->boldBorderStyle(), self::FMT_NUM);
        }

        if ($hide) {
            $this->groupRowBlock($ws, $line, $nbTier + 1);
        }
    }
    public function kpiTotBot(Worksheet $ws, int $line, Carbon $currentDate, Carbon $date1, array $tiers, array $platforms, bool $withSchool, bool $hide = false): void
    {
        $this->writeSimpleSumBlock($ws, $line, $currentDate, $date1, $tiers, $platforms,
            $withSchool ? 'Total Sales (Bot) inc. WinS' : 'Total Sales (Bot) exc. WinS',
            $withSchool ? 'bot_inc' : 'bot_exc',
            1.0, self::FMT_NUM, 7
        );
        if ($hide) {
            $this->groupRowBlock($ws, $line, 8);
        }
    }

    /** Total litres sold (bottles × 20). */
    public function kpiTotLit(Worksheet $ws, int $line, Carbon $currentDate, Carbon $date1, array $tiers, array $platforms, bool $withSchool, bool $hide = false): void
    {
        $this->writeSimpleSumBlock($ws, $line, $currentDate, $date1, $tiers, $platforms,
            $withSchool ? 'Total Sales (Litres) inc. WinS' : 'Total Sales (Litres) exc. WinS',
            $withSchool ? 'bot_inc' : 'bot_exc',
            20.0, self::FMT_NUM, 7
        );
        if ($hide) {
            $this->groupRowBlock($ws, $line, 8);
        }
    }

    /** Total income ($). */
    public function kpiTotInc(Worksheet $ws, int $line, Carbon $currentDate, Carbon $date1, array $tiers, array $platforms, int $exchangeRate, bool $withSchool, bool $hide = false): void
    {
        $this->writeSimpleSumBlock($ws, $line, $currentDate, $date1, $tiers, $platforms,
            $withSchool ? 'Total Sales ($) inc. WinS' : 'Total Sales ($) exc. WinS',
            $withSchool ? 'total_income' : 'income_exc',
            1.0 / $exchangeRate, self::FMT_NUM, 7
        );
        if ($hide) {
            $this->groupRowBlock($ws, $line, 8);
        }
    }

    /** Average price (Riels) — ratio pattern. */
    public function kpiPrice(Worksheet $ws, int $line, Carbon $currentDate, Carbon $date1, array $tiers, array $platforms, int $exchangeRate, bool $withSchool, bool $hide = false): void
    {
        $nPlat  = count($platforms);
        $nbTier = 7;
        $this->writeTierLabels($ws, $line, array_merge(self::LABELS_7, ['Total']), $this->boldBorderStyle(), self::FMT_NUM);
        $winLabel  = $withSchool ? 'inc.' : 'exc.';
        $dateRange = $this->dateRangeLabel($date1, $currentDate);
        $this->mergeWrite($ws, $line, 0, $line + 7, 0, "Price (Riels) {$winLabel} WinS \n{$dateRange}", $this->titleStyle());

        foreach ($tiers as $m => $tierData) {
            $tierLists = $tierData['tierLists'];
            $tierMaps = $tierData['tierMaps'];
            $data = $this->getCachedSales($currentDate, $date1, $m);

            // Pre-group by platform
            $dataByPlatform = [];
            foreach ($data as $row) {
                $dataByPlatform[$row->Old_Platform][] = $row;
            }

            $totalInc  = array_fill(0, $nbTier, 0.0);
            $totalSite = array_fill(0, $nbTier, 0);

            for ($i = 0; $i < $nPlat; $i++) {
                $platData = $dataByPlatform[$platforms[$i]] ?? [];
                $incTot  = 0.0;
                $siteTot = 0;

                for ($j = 0; $j < $nbTier; $j++) {
                    $incPlat  = 0.0;
                    $sitePlat = 0;
                    foreach ($platData as $row) {
                        $incVal = $withSchool
                            ? (float) $row->total_income - (float) $row->bottle_income
                            : (float) $row->total_income - (float) $row->bottle_income - (float) $row->wis_income;
                        $salesVal = $withSchool ? (float) $row->bot_inc : (float) $row->bot_exc;
                        if (isset($tierMaps[$j][$row->Id_Site]) && $salesVal > 0) {
                            $incPlat  += $incVal / $salesVal;
                            $sitePlat++;
                        }
                    }

                    $this->writeCell($ws, $line + $j, $this->kpiCol($m, $i, $nPlat),
                        "=IFERROR({$incPlat}/{$sitePlat},0)", $this->borderStyle(), self::FMT_NUM);
                    $incTot  += $incPlat;
                    $siteTot += $sitePlat;
                    $totalInc[$j]  += $incPlat;
                    $totalSite[$j] += $sitePlat;
                    $this->writeCell($ws, $line + $j, $this->kpiTotalCol($m, $nPlat),
                        "=IFERROR({$totalInc[$j]}/{$totalSite[$j]},0)", $this->boldBorderStyle(), self::FMT_NUM);
                }

                $this->writeCell($ws, $line + $nbTier, $this->kpiCol($m, $i, $nPlat),
                    "=IFERROR({$incTot}/{$siteTot},0)", $this->boldBorderStyle(), self::FMT_NUM);
            }

            $this->writeCell($ws, $line + $nbTier, $this->kpiTotalCol($m, $nPlat),
                "=IFERROR(" . array_sum($totalInc) . "/" . array_sum($totalSite) . ",0)", $this->boldBorderStyle(), self::FMT_NUM);
        }

        if ($hide) {
            $this->groupRowBlock($ws, $line, $nbTier + 1);
        }
    }

    /** Average entrepreneur salary ($). */
    public function kpiSalaryEnt(Worksheet $ws, int $line, Carbon $currentDate, Carbon $date1, array $tiers, array $platforms, int $exchangeRate, bool $hide = false): void
    {
        $nPlat  = count($platforms);
        $nbTier = 7;
        $salaryRefs = ['variable_salary_entrepreneurs', 'fix_salary_entrepreneurs'];
        $this->writeTierLabels($ws, $line, array_merge(self::LABELS_7, ['Total']), $this->boldBorderStyle(), self::FMT_DOLLAR);
        $dateRange = $this->dateRangeLabel($date1, $currentDate);
        $this->mergeWrite($ws, $line, 0, $line + 7, 0, "Avg Salary Ent \n{$dateRange}", $this->titleStyle());

        foreach ($tiers as $m => $tierData) {
            $tierLists = $tierData['tierLists'];
            $tierMaps = $tierData['tierMaps'];
            $salaryData  = $this->getFilteredExpensesBySite($currentDate, $date1, $m, $salaryRefs);
            $salesData   = $this->getCachedSales($currentDate, $date1, $m);

            // Pre-group and pre-key for O(1) lookups
            $salesByPlatform = [];
            foreach ($salesData as $row) {
                $salesByPlatform[$row->Old_Platform][] = $row;
            }
            $salaryBySite = $salaryData->keyBy('Id_Site');

            $totalSal   = array_fill(0, $nbTier, 0.0);
            $totalMonth = array_fill(0, $nbTier, 0);

            for ($i = 0; $i < $nPlat; $i++) {
                $platActive = $salesByPlatform[$platforms[$i]] ?? [];
                $salTot   = 0.0;
                $monthTot = 0;

                for ($j = 0; $j < $nbTier; $j++) {
                    $salPlat   = 0.0;
                    $monthPlat = 0;
                    foreach ($platActive as $row) {
                        if (isset($tierMaps[$j][$row->Id_Site])) {
                            $salary = $salaryBySite->get($row->Id_Site);
                            $salPlat   += $salary ? (float) $salary->total_amount / $exchangeRate : 0;
                            $monthPlat += (int) $row->active_months;
                        }
                    }

                    $this->writeCell($ws, $line + $j, $this->kpiCol($m, $i, $nPlat),
                        "=IFERROR({$salPlat}/{$monthPlat},0)", $this->borderStyle(), self::FMT_NUM);
                    $salTot   += $salPlat;
                    $monthTot += $monthPlat;
                    $totalSal[$j]   += $salPlat;
                    $totalMonth[$j] += $monthPlat;
                    $this->writeCell($ws, $line + $j, $this->kpiTotalCol($m, $nPlat),
                        "=IFERROR({$totalSal[$j]}/{$totalMonth[$j]},0)", $this->boldBorderStyle(), self::FMT_DOLLAR);
                }

                $this->writeCell($ws, $line + $nbTier, $this->kpiCol($m, $i, $nPlat),
                    "=IFERROR({$salTot}/{$monthTot},0)", $this->boldBorderStyle(), self::FMT_DOLLAR);
            }

            $this->writeCell($ws, $line + $nbTier, $this->kpiTotalCol($m, $nPlat),
                "=IFERROR(" . array_sum($totalSal) . "/" . array_sum($totalMonth) . ",0)", $this->boldBorderStyle(), self::FMT_DOLLAR);
        }

        if ($hide) {
            $this->groupRowBlock($ws, $line, $nbTier + 1);
        }
    }

    /** Average entrepreneur income (salary + revenue − costs). */
    public function kpiIncomeEnt(Worksheet $ws, int $line, Carbon $currentDate, Carbon $date1, array $tiers, array $platforms, int $exchangeRate, bool $hide = false): void
    {
        $nPlat  = count($platforms);
        $nbTier = 7;
        $catExp = TierService::categoryExpenses();
        $salaryRefs = ['variable_salary_entrepreneurs', 'fix_salary_entrepreneurs'];
        $this->writeTierLabels($ws, $line, array_merge(self::LABELS_7, ['Total']), $this->boldBorderStyle(), self::FMT_DOLLAR);
        $dateRange = $this->dateRangeLabel($date1, $currentDate);
        $this->mergeWrite($ws, $line, 0, $line + 7, 0, "Avg Income Ent \n{$dateRange}", $this->titleStyle());

        foreach ($tiers as $m => $tierData) {
            $tierLists = $tierData['tierLists'];
            $tierMaps = $tierData['tierMaps'];

            $salaryData  = $this->getFilteredExpensesBySite($currentDate, $date1, $m, $salaryRefs);
            $salesData   = $this->getCachedSales($currentDate, $date1, $m);
            $costData    = $this->getFilteredExpensesBySite($currentDate, $date1, $m, [], $catExp);

            // Pre-group and pre-key for O(1) lookups
            $salesByPlatform = [];
            foreach ($salesData as $row) {
                $salesByPlatform[$row->Old_Platform][] = $row;
            }
            $salaryBySite = $salaryData->keyBy('Id_Site');
            $costBySite   = $costData->keyBy('Id_Site');

            $totalInc   = array_fill(0, $nbTier, 0.0);
            $totalMonth = array_fill(0, $nbTier, 0);

            for ($i = 0; $i < $nPlat; $i++) {
                $platActive = $salesByPlatform[$platforms[$i]] ?? [];
                $incTot   = 0.0;
                $monthTot = 0;

                for ($j = 0; $j < $nbTier; $j++) {
                    $incPlat   = 0.0;
                    $monthPlat = 0;
                    foreach ($platActive as $row) {
                        if (isset($tierMaps[$j][$row->Id_Site])) {
                            $sal = (float) ($salaryBySite->get($row->Id_Site)?->total_amount ?? 0) / $exchangeRate;
                            $rev = (float) $row->total_income / $exchangeRate;
                            $cst = (float) ($costBySite->get($row->Id_Site)?->total_amount ?? 0) / $exchangeRate;
                            $incPlat   += $sal + $rev - $cst;
                            $monthPlat += (int) $row->active_months;
                        }
                    }

                    $this->writeCell($ws, $line + $j, $this->kpiCol($m, $i, $nPlat),
                        "=IFERROR({$incPlat}/{$monthPlat},0)", $this->borderStyle(), self::FMT_NUM);
                    $incTot   += $incPlat;
                    $monthTot += $monthPlat;
                    $totalInc[$j]   += $incPlat;
                    $totalMonth[$j] += $monthPlat;
                    $this->writeCell($ws, $line + $j, $this->kpiTotalCol($m, $nPlat),
                        "=IFERROR({$totalInc[$j]}/{$totalMonth[$j]},0)", $this->boldBorderStyle(), self::FMT_DOLLAR);
                }

                $this->writeCell($ws, $line + $nbTier, $this->kpiCol($m, $i, $nPlat),
                    "=IFERROR({$incTot}/{$monthTot},0)", $this->boldBorderStyle(), self::FMT_DOLLAR);
            }

            $this->writeCell($ws, $line + $nbTier, $this->kpiTotalCol($m, $nPlat),
                "=IFERROR(" . array_sum($totalInc) . "/" . array_sum($totalMonth) . ",0)", $this->boldBorderStyle(), self::FMT_DOLLAR);
        }

        if ($hide) {
            $this->groupRowBlock($ws, $line, $nbTier + 1);
        }
    }

    /** P&L total ($). */
    public function kpiPL(Worksheet $ws, int $line, Carbon $currentDate, Carbon $date1, array $tiers, array $platforms, int $exchangeRate): void
    {
        $nPlat  = count($platforms);
        $nbTier = 7;
        $catExp = TierService::categoryExpenses();
        $this->writeTierLabels($ws, $line, array_merge(self::LABELS_7, ['Total']), $this->boldBorderStyle(), self::FMT_DOLLAR);
        $dateRange = $this->dateRangeLabel($date1, $currentDate);
        $this->mergeWrite($ws, $line, 0, $line + 7, 0, "P&L Tot ($) \n{$dateRange}", $this->titleStyle());

        foreach ($tiers as $m => $tierData) {
            $tierLists = $tierData['tierLists'];
            $tierMaps = $tierData['tierMaps'];

            $salesData = $this->getCachedSales($currentDate, $date1, $m);
            $costData  = $this->getFilteredExpensesBySite($currentDate, $date1, $m, [], $catExp);

            // Pre-group and pre-key for O(1)
            $salesByPlatform = [];
            foreach ($salesData as $row) {
                $salesByPlatform[$row->Old_Platform][] = $row;
            }
            $costByPlatform = [];
            foreach ($costData as $row) {
                $costByPlatform[$row->Old_Platform][] = $row;
            }

            $totalPerTier = array_fill(0, $nbTier, 0.0);

            for ($i = 0; $i < $nPlat; $i++) {
                $plTot = 0.0;

                for ($j = 0; $j < $nbTier; $j++) {
                    $revPlat = 0.0;
                    $cstPlat = 0.0;
                    foreach ($salesByPlatform[$platforms[$i]] ?? [] as $r) {
                        if (isset($tierMaps[$j][$r->Id_Site])) {
                            $revPlat += (float) $r->total_income / $exchangeRate;
                        }
                    }
                    foreach ($costByPlatform[$platforms[$i]] ?? [] as $c) {
                        if (isset($tierMaps[$j][$c->Id_Site])) {
                            $cstPlat += (float) $c->total_amount / $exchangeRate;
                        }
                    }

                    $pl = $revPlat - $cstPlat;
                    $totalPerTier[$j] += $pl;
                    $plTot += $pl;

                    $this->writeCell($ws, $line + $j, $this->kpiCol($m, $i, $nPlat), $pl, $this->borderStyle(), self::FMT_NUM);
                    $this->writeCell($ws, $line + $j, $this->kpiTotalCol($m, $nPlat), $totalPerTier[$j], $this->boldBorderStyle(), self::FMT_DOLLAR);
                }

                $this->writeCell($ws, $line + $nbTier, $this->kpiCol($m, $i, $nPlat), $plTot, $this->boldBorderStyle(), self::FMT_DOLLAR);
            }

            $this->writeCell($ws, $line + $nbTier, $this->kpiTotalCol($m, $nPlat), array_sum($totalPerTier), $this->boldBorderStyle(), self::FMT_DOLLAR);
        }
    }

    /** Total debts. */
    public function kpiDebt(Worksheet $ws, int $line, Carbon $currentDate, Carbon $date1, array $tiers, array $platforms, int $exchangeRate, bool $hide = false): void
    {
        $nPlat  = count($platforms);
        $nbTier = 8;
        $this->writeTierLabels($ws, $line, array_merge(self::LABELS_7, ['Total']), $this->boldBorderStyle(), self::FMT_NUM);
        $this->mergeWrite($ws, $line, 0, $line + 8, 0, "Total Debts \n" . $currentDate->format('M Y'), $this->titleStyle());

        // Batch query for all reference months at once
        $refMonths = [];
        foreach (array_keys($tiers) as $m) {
            $refMonths[] = $currentDate->copy()->subMonths(12 * $m)->toDateString();
        }
        $allDebtRaw = DB::table('Expenses')->join('Sites', 'Expenses.Id_Site', '=', 'Sites.Id_Site')
            ->whereIn('Month', $refMonths)
            ->where('Ref_expenses', 'debt')
            ->where('Amount_Expenses', '>', 0)
            ->groupBy('Expenses.Id_Site', 'Sites.Old_Platform', 'Month')
            ->selectRaw("SUM(Amount_Expenses) / {$exchangeRate} as val, Old_Platform, Expenses.Id_Site, Month")
            ->get();
        $debtByMonth = [];
        foreach ($allDebtRaw as $r) {
            $debtByMonth[$r->Month][$r->Old_Platform][$r->Id_Site] = (float) $r->val;
        }

        foreach ($tiers as $m => $tierData) {
            $tierMaps = $tierData['tierMaps'];
            $mk = $currentDate->copy()->subMonths(12 * $m)->toDateString();
            $debtForMonth = $debtByMonth[$mk] ?? [];

            $totalPerTier = array_fill(0, $nbTier, 0.0);

            for ($i = 0; $i < $nPlat; $i++) {
                $platDebt = $debtForMonth[$platforms[$i]] ?? [];
                $tot = 0.0;
                for ($j = 0; $j < $nbTier; $j++) {
                    $val = 0.0;
                    foreach ($platDebt as $siteId => $dv) {
                        if (isset($tierMaps[$j][$siteId])) $val += $dv;
                    }
                    $totalPerTier[$j] += $val;
                    $tot += $val;
                    $this->writeCell($ws, $line + $j, $this->kpiCol($m, $i, $nPlat), $val, $this->borderStyle(), self::FMT_NUM);
                    $this->writeCell($ws, $line + $j, $this->kpiTotalCol($m, $nPlat), $totalPerTier[$j], $this->boldBorderStyle(), self::FMT_NUM);
                }
                $this->writeCell($ws, $line + $nbTier, $this->kpiCol($m, $i, $nPlat), $tot, $this->boldBorderStyle(), self::FMT_NUM);
            }

            $this->writeCell($ws, $line + $nbTier, $this->kpiTotalCol($m, $nPlat), array_sum($totalPerTier), $this->boldBorderStyle(), self::FMT_NUM);
        }

        if ($hide) {
            $this->groupRowBlock($ws, $line, $nbTier + 1);
        }
    }

    /** Total savings. */
    public function kpiSaving(Worksheet $ws, int $line, Carbon $currentDate, Carbon $date1, array $tiers, array $platforms, int $exchangeRate, bool $hide = false): void
    {
        $nPlat  = count($platforms);
        $nbTier = 8;
        $this->writeTierLabels($ws, $line, array_merge(self::LABELS_7, ['Total']), $this->boldBorderStyle(), self::FMT_NUM);
        $this->mergeWrite($ws, $line, 0, $line + 8, 0, "Total Savings \n" . $currentDate->format('M Y'), $this->titleStyle());

        // Batch query for all reference months at once
        $refMonths = [];
        foreach (array_keys($tiers) as $m) {
            $refMonths[] = $currentDate->copy()->subMonths(12 * $m)->toDateString();
        }
        $allSavingRaw = DB::table('Expenses')->join('Sites', 'Expenses.Id_Site', '=', 'Sites.Id_Site')
            ->whereIn('Month', $refMonths)
            ->where('Ref_expenses', 'debt')
            ->where('Amount_Expenses', '<', 0)
            ->groupBy('Expenses.Id_Site', 'Sites.Old_Platform', 'Month')
            ->selectRaw("SUM(-Amount_Expenses) / {$exchangeRate} as val, Old_Platform, Expenses.Id_Site, Month")
            ->get();
        $savingByMonth = [];
        foreach ($allSavingRaw as $r) {
            $savingByMonth[$r->Month][$r->Old_Platform][$r->Id_Site] = (float) $r->val;
        }

        foreach ($tiers as $m => $tierData) {
            $tierMaps = $tierData['tierMaps'];
            $mk = $currentDate->copy()->subMonths(12 * $m)->toDateString();
            $savingForMonth = $savingByMonth[$mk] ?? [];

            $totalPerTier = array_fill(0, $nbTier, 0.0);

            for ($i = 0; $i < $nPlat; $i++) {
                $platSaving = $savingForMonth[$platforms[$i]] ?? [];
                $tot = 0.0;
                for ($j = 0; $j < $nbTier; $j++) {
                    $val = 0.0;
                    foreach ($platSaving as $siteId => $sv) {
                        if (isset($tierMaps[$j][$siteId])) $val += $sv;
                    }
                    $totalPerTier[$j] += $val;
                    $tot += $val;
                    $this->writeCell($ws, $line + $j, $this->kpiCol($m, $i, $nPlat), $val, $this->borderStyle(), self::FMT_NUM);
                    $this->writeCell($ws, $line + $j, $this->kpiTotalCol($m, $nPlat), $totalPerTier[$j], $this->boldBorderStyle(), self::FMT_NUM);
                }
                $this->writeCell($ws, $line + $nbTier, $this->kpiCol($m, $i, $nPlat), $tot, $this->boldBorderStyle(), self::FMT_NUM);
            }

            $this->writeCell($ws, $line + $nbTier, $this->kpiTotalCol($m, $nPlat), array_sum($totalPerTier), $this->boldBorderStyle(), self::FMT_NUM);
        }

        if ($hide) {
            $this->groupRowBlock($ws, $line, $nbTier + 1);
        }
    }

    /** Collection rate (with debt settlement). */
    public function kpiCollectionRate(Worksheet $ws, int $line, Carbon $currentDate, Carbon $date1, array $tiers, array $platforms, int $exchangeRate, bool $hide = false): void
    {
        $date1 = Carbon::create($currentDate->year - 1, 12, 1); // YTD only
        $nPlat  = count($platforms);
        $nbTier = 7;
        $this->writeTierLabels($ws, $line, array_merge(self::LABELS_7, ['Total']), $this->boldBorderStyle(), self::FMT_PCT);
        $dateRange = $this->dateRangeLabel($date1, $currentDate);
        $this->mergeWrite($ws, $line, 0, $line + 7, 0, "Collection Rate (with debt Settlement) \n{$dateRange}", $this->titleStyle());

        $crRefs = ['stock_ts', 'bottle_invoice', 'entrepreneur_contribution', 'water quality alert', 'technical intervention', 'delivery_program_fee'];
        $numTiers = count($tiers);
        $minDateStart = $date1->copy()->subMonths(12 * ($numTiers - 1));

        // Batch crData — one query, Month in GROUP BY, indexed by month
        $crAll = DB::table('Expenses')->join('Sites', 'Sites.Id_Site', '=', 'Expenses.Id_Site')
            ->whereIn('Ref_expenses', $crRefs)
            ->where('Month', '<=', $currentDate)->where('Month', '>', $minDateStart)
            ->groupBy('Expenses.Id_Site', 'Sites.Old_Platform', 'Month')
            ->selectRaw("SUM(Amount_Expenses) / {$exchangeRate} as due, Old_Platform, Expenses.Id_Site, IFNULL(SUM(Paid),0) / {$exchangeRate} as paid, Month")
            ->get();
        $crByMonth = [];
        foreach ($crAll as $r) { $crByMonth[$r->Month][] = $r; }

        // Batch debtPaid — same approach
        $dpAll = DB::table('Expenses')->join('Sites', 'Sites.Id_Site', '=', 'Expenses.Id_Site')
            ->where('Ref_expenses', 'debt')->where('Amount_Expenses', '>', 0)
            ->where('Month', '<=', $currentDate)->where('Month', '>', $minDateStart)
            ->groupBy('Expenses.Id_Site', 'Sites.Old_Platform', 'Month')
            ->selectRaw("IFNULL(SUM(CASE WHEN Paid > Amount_Expenses THEN Amount_Expenses ELSE Paid END),0) / {$exchangeRate} as val, Old_Platform, Expenses.Id_Site, Month")
            ->get();
        $dpByMonth = [];
        foreach ($dpAll as $r) { $dpByMonth[$r->Month][] = $r; }

        // Batch debtJanv — specific months via whereIn
        $djMonths = [];
        foreach (array_keys($tiers) as $m) {
            $djMonths[] = $date1->copy()->subMonths(12 * $m)->addMonth()->toDateString();
        }
        $djAll = DB::table('Expenses')->join('Sites', 'Sites.Id_Site', '=', 'Expenses.Id_Site')
            ->where('Ref_expenses', 'debt')->where('Amount_Expenses', '>', 0)
            ->whereIn('Month', $djMonths)
            ->selectRaw("Amount_Expenses / {$exchangeRate} as val, Old_Platform, Expenses.Id_Site, Month")
            ->get();
        $djByMonthSite = [];
        foreach ($djAll as $r) {
            $djByMonthSite[$r->Month][$r->Id_Site] = ($djByMonthSite[$r->Month][$r->Id_Site] ?? 0.0) + (float) $r->val;
        }

        foreach ($tiers as $m => $tierData) {
            $tierMaps = $tierData['tierMaps'];
            $dateEnd   = $currentDate->copy()->subMonths(12 * $m)->toDateString();
            $dateStart = $date1->copy()->subMonths(12 * $m)->toDateString();
            $djMonth   = $date1->copy()->subMonths(12 * $m)->addMonth()->toDateString();
            $djSiteMap = $djByMonthSite[$djMonth] ?? [];

            // Re-aggregate crData for this offset from batch, indexed by [platform]
            $crByPlat = [];
            foreach ($crByMonth as $month => $rows) {
                if ($month > $dateEnd || $month <= $dateStart) continue;
                foreach ($rows as $r) {
                    $id = $r->Id_Site;
                    if (!isset($crByPlat[$r->Old_Platform][$id])) {
                        $crByPlat[$r->Old_Platform][$id] = (object) ['paid' => 0.0, 'due' => 0.0];
                    }
                    $crByPlat[$r->Old_Platform][$id]->paid += (float) $r->paid;
                    $crByPlat[$r->Old_Platform][$id]->due  += (float) $r->due;
                }
            }

            // Re-aggregate debtPaid for this offset, indexed by siteId
            $dpBySite = [];
            foreach ($dpByMonth as $month => $rows) {
                if ($month > $dateEnd || $month <= $dateStart) continue;
                foreach ($rows as $r) {
                    $dpBySite[$r->Id_Site] = ($dpBySite[$r->Id_Site] ?? 0.0) + (float) $r->val;
                }
            }

            $tPaid = array_fill(0, $nbTier, 0.0);
            $tDue  = array_fill(0, $nbTier, 0.0);
            $tDebt = array_fill(0, $nbTier, 0.0);
            $tDJ   = array_fill(0, $nbTier, 0.0);

            for ($i = 0; $i < $nPlat; $i++) {
                $paidTot = 0.0; $dueTot = 0.0; $dTot = 0.0; $djTot = 0.0;
                $platCr = $crByPlat[$platforms[$i]] ?? [];

                for ($j = 0; $j < $nbTier; $j++) {
                    $paidP = 0.0; $dueP = 0.0; $dP = 0.0; $djP = 0.0;
                    foreach ($platCr as $siteId => $cr) {
                        if (isset($tierMaps[$j][$siteId])) {
                            $paidP += $cr->paid;
                            $dueP  += $cr->due;
                            $dP    += $dpBySite[$siteId] ?? 0.0;
                            $djP   += $djSiteMap[$siteId] ?? 0.0;
                        }
                    }

                    $this->writeCell($ws, $line + $j, $this->kpiCol($m, $i, $nPlat),
                        "=IFERROR(({$paidP}+{$dP})/({$dueP}+{$djP}),\"\")", $this->borderStyle(), self::FMT_PCT);
                    $paidTot += $paidP; $dueTot += $dueP; $dTot += $dP; $djTot += $djP;
                    $tPaid[$j] += $paidP; $tDue[$j] += $dueP; $tDebt[$j] += $dP; $tDJ[$j] += $djP;
                    $this->writeCell($ws, $line + $j, $this->kpiTotalCol($m, $nPlat),
                        "=IFERROR(({$tPaid[$j]}+{$tDebt[$j]})/({$tDue[$j]}+{$tDJ[$j]}),\"\")", $this->boldBorderStyle(), self::FMT_PCT);
                }

                $this->writeCell($ws, $line + $nbTier, $this->kpiCol($m, $i, $nPlat),
                    "=IFERROR(({$paidTot}+{$dTot})/({$dueTot}+{$djTot}),\"\")", $this->boldBorderStyle(), self::FMT_PCT);
            }

            $this->writeCell($ws, $line + $nbTier, $this->kpiTotalCol($m, $nPlat),
                "=IFERROR((" . array_sum($tPaid) . "+" . array_sum($tDebt) . ")/(" . array_sum($tDue) . "+" . array_sum($tDJ) . "),\"\")",
                $this->boldBorderStyle(), self::FMT_PCT);
        }

        if ($hide) {
            $this->groupRowBlock($ws, $line, $nbTier + 1);
        }
    }

    /** Number of O‑we jobs created (operators). */
    public function kpiNumberOperator(Worksheet $ws, int $line, Carbon $currentDate, Carbon $date1, array $tiers, array $platforms, int $exchangeRate): void
    {
        $nPlat  = count($platforms);
        $nbTier = 6; // ST1, T1, T2, T3, New, Reopen (excludes Inactive, Closed, Dead)
        $labels = ['Super Tier 1', 'Tier 1', 'Tier 2', 'Tier 3', 'New', 'Reopen', 'Total'];
        $this->writeTierLabels($ws, $line, $labels, $this->boldBorderStyle(), self::FMT_NUM);
        $dateRange = $this->dateRangeLabel($date1, $currentDate);
        $this->mergeWrite($ws, $line, 0, $line + 6, 0, "Nb O-we Jobs Created \n{$dateRange}", $this->titleStyle());

        foreach ($tiers as $m => $tierData) {
            $tierMaps = $tierData['tierMaps'];
            $opData = DB::table('Indicators')->join('Sites', 'Sites.Id_Site', '=', 'Indicators.Id_Site')
                ->where('Month', '<=', $currentDate->copy()->subMonths(12 * $m))
                ->where('Month', '>', $date1->copy()->subMonths(12 * $m))
                ->groupBy('Indicators.Id_Site', 'Sites.Old_Platform')
                ->selectRaw('SUM(Number_of_Operator) as val, Old_Platform, Indicators.Id_Site')
                ->get();

            // Pre-group by platform for O(1) access
            $opByPlat = [];
            foreach ($opData as $r) { $opByPlat[$r->Old_Platform][] = $r; }

            $totalPerTier = array_fill(0, $nbTier, 0.0);

            for ($i = 0; $i < $nPlat; $i++) {
                $platOp = $opByPlat[$platforms[$i]] ?? [];
                $tot = 0.0;
                for ($j = 0; $j < $nbTier; $j++) {
                    $val = 0.0;
                    foreach ($platOp as $r) {
                        if (isset($tierMaps[$j][$r->Id_Site])) $val += (float) ($r->val ?? 0);
                    }
                    $totalPerTier[$j] += $val;
                    $tot += $val;
                    $this->writeCell($ws, $line + $j, $this->kpiCol($m, $i, $nPlat), $val, $this->borderStyle(), self::FMT_NUM);
                    $this->writeCell($ws, $line + $j, $this->kpiTotalCol($m, $nPlat), $totalPerTier[$j], $this->boldBorderStyle(), self::FMT_NUM);
                }
                $this->writeCell($ws, $line + $nbTier, $this->kpiCol($m, $i, $nPlat), $tot, $this->boldBorderStyle(), self::FMT_NUM);
            }

            $this->writeCell($ws, $line + $nbTier, $this->kpiTotalCol($m, $nPlat), array_sum($totalPerTier), $this->boldBorderStyle(), self::FMT_NUM);
        }
    }

    // ═══════════════════════════════════════════════════════════════
    //  COMPOSITE — Write a full KPI sheet (used by CreateKPI/ActivityKPI)
    // ═══════════════════════════════════════════════════════════════

    /**
     * Pre-compute tiers for all years to avoid redundant DB queries
     * when building multiple KPI sheets.
     */
    public function precomputeTiers(Carbon $currentDate, int $yearStart = 2018): array
    {
        $nbYear = min($currentDate->year - $yearStart + 1, self::KPI_YEARS_SHOWN);
        $tiers = [];
        for ($i = 0; $i < $nbYear; $i++) {
            $date = Carbon::create($currentDate->year - $i, $currentDate->month, 1);
            $tiers[] = $this->tierService->calculateTiers($date);
        }
        return $tiers;
    }

    /**
     * Write a complete KPI sheet with all standard blocks.
     * Matches Python's CreateKPI / WriteKPIF2F / ActivityKPI.
     */
    public function writeFullKpiSheet(
        Worksheet $ws,
        Carbon $currentDate,
        Carbon $date1,
        array $platforms,
        int $exchangeRate,
        int $yearStart = 2018,
        bool $includeOperators = false,
        ?array $precomputedTiers = null,
    ): array {
        $tiers = $this->kpiFormat($ws, $currentDate, $date1, $yearStart, $platforms, $precomputedTiers);
        $this->kpiNbSite($ws, 2, $currentDate, $date1, $tiers, $platforms);
        $this->kpiNbSitePercentage($ws, 12, $currentDate, $date1, $tiers, $platforms);
        $this->kpiBeneficiaries($ws, 21, $currentDate, $date1, $tiers, $platforms);
        $this->kpiBotDay($ws, 30, $currentDate, $date1, $tiers, $platforms, false);
        $this->kpiBotDay($ws, 40, $currentDate, $date1, $tiers, $platforms, true);
        $this->kpiTotBot($ws, 50, $currentDate, $date1, $tiers, $platforms, true, true);
        $this->kpiTotBot($ws, 59, $currentDate, $date1, $tiers, $platforms, false, true);
        $this->kpiTotLit($ws, 68, $currentDate, $date1, $tiers, $platforms, true, false);
        $this->kpiTotLit($ws, 77, $currentDate, $date1, $tiers, $platforms, false, false);
        $this->kpiTotInc($ws, 86, $currentDate, $date1, $tiers, $platforms, $exchangeRate, false, true);
        $this->kpiTotInc($ws, 95, $currentDate, $date1, $tiers, $platforms, $exchangeRate, true);
        $this->kpiPrice($ws, 104, $currentDate, $date1, $tiers, $platforms, $exchangeRate, false);
        $this->kpiSalaryEnt($ws, 114, $currentDate, $date1, $tiers, $platforms, $exchangeRate, true);
        $this->kpiIncomeEnt($ws, 123, $currentDate, $date1, $tiers, $platforms, $exchangeRate);
        $this->kpiPL($ws, 132, $currentDate, $date1, $tiers, $platforms, $exchangeRate);

        if ($includeOperators) {
            $this->kpiNumberOperator($ws, 141, $currentDate, $date1, $tiers, $platforms, $exchangeRate);
        }

        return $tiers;
    }

    // ═══════════════════════════════════════════════════════════════
    //  GENERIC HELPERS (private)
    // ═══════════════════════════════════════════════════════════════

    /**
     * Generic simple‑sum KPI block (used by TotBot, TotLit, TotInc).
     */
    private function writeSimpleSumBlock(
        Worksheet $ws, int $line, Carbon $currentDate, Carbon $date1,
        array $tiers, array $platforms, string $title, string $cacheField,
        float $multiplier, string $numFormat, int $nbTier,
    ): void {
        $nPlat = count($platforms);
        $this->writeTierLabels($ws, $line, array_merge(self::LABELS_7, ['Total']), $this->boldBorderStyle(), $numFormat);
        $dateRange = $this->dateRangeLabel($date1, $currentDate);
        $this->mergeWrite($ws, $line, 0, $line + 7, 0, "{$title} \n{$dateRange}", $this->titleStyle());

        foreach ($tiers as $m => $tierData) {
            $tierMaps = $tierData['tierMaps'];
            $data = $this->getCachedSales($currentDate, $date1, $m);

            // Pre-group by platform for O(1) access
            $dataByPlatform = [];
            foreach ($data as $row) {
                $dataByPlatform[$row->Old_Platform][] = $row;
            }

            $totalPerTier = array_fill(0, $nbTier, 0.0);

            for ($i = 0; $i < $nPlat; $i++) {
                $platData = $dataByPlatform[$platforms[$i]] ?? [];
                $tot = 0.0;

                for ($j = 0; $j < $nbTier; $j++) {
                    $val = 0.0;
                    foreach ($platData as $r) {
                        if (isset($tierMaps[$j][$r->Id_Site])) {
                            $val += (float) ($r->$cacheField ?? 0) * $multiplier;
                        }
                    }
                    $totalPerTier[$j] += $val;
                    $tot += $val;
                    $this->writeCell($ws, $line + $j, $this->kpiCol($m, $i, $nPlat), $val, $this->borderStyle(), $numFormat);
                    $this->writeCell($ws, $line + $j, $this->kpiTotalCol($m, $nPlat), $totalPerTier[$j], $this->boldBorderStyle(), $numFormat);
                }

                $this->writeCell($ws, $line + $nbTier, $this->kpiCol($m, $i, $nPlat), $tot, $this->boldBorderStyle(), $numFormat);
            }

            $this->writeCell($ws, $line + $nbTier, $this->kpiTotalCol($m, $nPlat), array_sum($totalPerTier), $this->boldBorderStyle(), $numFormat);
        }
    }

    /** Column index (0‑based) for platform i in year m. */
    private function kpiCol(int $m, int $i, int $nPlat): int
    {
        return $m * ($nPlat + 2) + $i + 2;
    }

    /** Column index (0‑based) for the "Total" column in year m. */
    private function kpiTotalCol(int $m, int $nPlat): int
    {
        return $m * ($nPlat + 2) + $nPlat + 2;
    }

    /**
     * Apply Excel outline grouping (level 1, collapsed+hidden) to a block of rows.
     * Matches Python's set_row(..., {'level':1, 'hidden':True}).
     */
    private function groupRowBlock(Worksheet $ws, int $startRow, int $count): void
    {
        for ($i = 0; $i < $count; $i++) {
            $r = $startRow + $i + 1; // 1-based row
            $ws->getRowDimension($r)->setOutlineLevel(1);
            $ws->getRowDimension($r)->setCollapsed(true);
            $ws->getRowDimension($r)->setVisible(false);
        }
    }

    /** "Jan 2024 – Dec 2024" style date range label. */
    private function dateRangeLabel(Carbon $date1, Carbon $currentDate): string
    {
        $from = $date1->copy()->addMonth();
        return $from->format('M Y') . ' - ' . $currentDate->format('M Y');
    }

    // ── Cell‑writing helpers ──────────────────────────────────────

    private function writeCell(Worksheet $ws, int $row0, int $col0, $value, array $style = [], string $numFormat = ''): void
    {
        $cell = Coordinate::stringFromColumnIndex($col0 + 1) . ($row0 + 1);
        $ws->setCellValue($cell, $value);
        if ($style) {
            $ws->getStyle($cell)->applyFromArray($style);
        }
        if ($numFormat) {
            $ws->getStyle($cell)->getNumberFormat()->setFormatCode($numFormat);
        }
    }

    private function mergeWrite(Worksheet $ws, int $r1, int $c1, int $r2, int $c2, $value, array $style = []): void
    {
        $cell1 = Coordinate::stringFromColumnIndex($c1 + 1) . ($r1 + 1);
        $cell2 = Coordinate::stringFromColumnIndex($c2 + 1) . ($r2 + 1);
        $ws->mergeCells("{$cell1}:{$cell2}");
        $ws->setCellValue($cell1, $value);
        if ($style) {
            $ws->getStyle("{$cell1}:{$cell2}")->applyFromArray($style);
        }
    }

    private function cell(int $row0, int $col0): string
    {
        return Coordinate::stringFromColumnIndex($col0 + 1) . ($row0 + 1);
    }

    private function writeTierLabels(Worksheet $ws, int $line, array $labels, array $style, string $numFormat = ''): void
    {
        foreach ($labels as $i => $label) {
            $this->writeCell($ws, $line + $i, 1, $label, $style, $numFormat);
        }
    }

    // ── Style arrays ─────────────────────────────────────────────

    private function borderStyle(): array
    {
        return [
            'borders' => ['allBorders' => ['borderStyle' => Border::BORDER_THIN]],
        ];
    }

    private function boldBorderStyle(): array
    {
        return [
            'font'    => ['bold' => true],
            'borders' => ['allBorders' => ['borderStyle' => Border::BORDER_THIN]],
        ];
    }

    private function boldStyle(): array
    {
        return ['font' => ['bold' => true]];
    }

    private function titleStyle(): array
    {
        return [
            'font'      => ['bold' => true, 'color' => ['rgb' => 'FFFFFF']],
            'fill'      => ['fillType' => Fill::FILL_SOLID, 'startColor' => ['rgb' => '4472C4']],
            'alignment' => [
                'vertical'   => Alignment::VERTICAL_CENTER,
                'horizontal' => Alignment::HORIZONTAL_CENTER,
                'wrapText'   => true,
            ],
        ];
    }
}
