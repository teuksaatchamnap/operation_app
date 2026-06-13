<?php

namespace App\Jobs;

use App\Models\Sims3\Sale;
use App\Models\Sims3\Site as Sims3Site;
use Carbon\Carbon;
use Illuminate\Support\Collection;

class ComputeSalesVolume extends BaseComputeJob
{
    protected function prepareData(Collection $siteMap, Collection $months, array $siteNames): array
    {
        $from = $months->first()->copy()->startOfMonth();
        $to = $months->last()->copy()->endOfMonth();

        $sales = Sale::query()
            ->select(['Id_Site', 'Month', 'Total_Sales', 'Total_Income', 'WiS_Sales', 'Bottle_Sales', 'Code_Sales', 'Number_Open_Days'])
            ->whereBetween('Month', [$from, $to])
            ->whereIn('Id_Site', $siteNames)
            ->orderBy('Code_Sales')
            ->get();

        $allSales = Sale::query()
            ->select(['Id_Site', 'Month', 'Total_Sales', 'WiS_Sales', 'Bottle_Sales', 'Number_Open_Days'])
            ->whereIn('Id_Site', $siteNames)
            ->where('Month', '<=', $to)
            ->get();

        $januarySitesByYear = [];

        foreach ($allSales as $sale) {
            $carbon = Carbon::parse($sale->Month)->startOfMonth();
            if ($carbon->month === 1) {
                $volume = ($sale->Total_Sales ?? 0) - ($sale->WiS_Sales ?? 0) - ($sale->Bottle_Sales ?? 0);
                if ($volume > 0) {
                    $januarySitesByYear[$carbon->year][trim($sale->Id_Site)] = true;
                }
            }
        }

        $allSales = $allSales->groupBy(fn ($s) => trim($s->Id_Site));

        $deadSites = Sims3Site::query()
            ->where('Platform', 'Dead')
            ->pluck('Id_Site')
            ->map(fn ($v) => trim($v))
            ->toArray();

        $map = [];
        foreach ($sales as $sale) {
            $carbon = Carbon::parse($sale->Month)->startOfMonth();
            $monthKey = $carbon->format('Y-m-d');
            $site = trim($sale->Id_Site);
            $key = $site.'|'.$monthKey;

            if (! isset($map[$key])) {
                $volume = ($sale->Total_Sales ?? 0) - ($sale->WiS_Sales ?? 0) - ($sale->Bottle_Sales ?? 0);
                $map[$key] = [
                    'sales_volume' => (int) round($volume),
                    'sales_volume_lfl' => isset($januarySitesByYear[$carbon->year - 1][$site])
                        ? (int) round($volume)
                        : null,
                    'days_open' => $sale->Number_Open_Days !== null ? (int) $sale->Number_Open_Days : 0,
                    'revenue' => (int) round($sale->Total_Income ?? 0),
                ];
                $map[$key]['active'] = $map[$key]['sales_volume'] > 0 ? 1 : 0;
                $map[$key]['super_tier_1'] = 0;
                $map[$key]['bottles_per_day'] = 0;
                if ($map[$key]['days_open'] > 0) {
                    $map[$key]['bottles_per_day'] = $map[$key]['sales_volume'] / $map[$key]['days_open'];
                }

                $tierResult = $this->computeTier(
                    $site, $carbon, $allSales[$site] ?? collect(), $deadSites
                );
                $map[$key]['tier'] = $tierResult['tier'];
                $map[$key]['super_tier_1'] = $tierResult['avg_per_day'] > 110 ? 1 : 0;
            }
        }

        foreach ($months as $month) {
            $monthKey = $month->format('Y-m-d');
            foreach ($siteMap as $siteName => $siteId) {
                $key = $siteName.'|'.$monthKey;
                if (isset($map[$key])) {
                    continue;
                }
                $carbon = $month->copy()->startOfMonth();
                $tierResult = $this->computeTier(
                    $siteName, $carbon, $allSales[$siteName] ?? collect(), $deadSites
                );
                $map[$key] = [
                    'sales_volume' => 0,
                    'sales_volume_lfl' => null,
                    'days_open' => 0,
                    'revenue' => 0,
                    'active' => 0,
                    'super_tier_1' => $tierResult['avg_per_day'] > 110 ? 1 : 0,
                    'bottles_per_day' => 0,
                    'tier' => $tierResult['tier'],
                ];
            }
        }

        return $map;
    }

    private function computeTier(string $site, Carbon $month, Collection $siteSales, array $deadSites): array
    {
        if (in_array($site, $deadSites, true)) {
            return ['tier' => 'Dead', 'avg_per_day' => 0];
        }

        $monthStart = $month->copy()->startOfMonth();
        $twelveMonthsAgo = $monthStart->copy()->subMonths(12);
        $threeMonthsAgo = $monthStart->copy()->subMonths(3);

        $salesUpToMonth = $siteSales->filter(fn ($s) => Carbon::parse($s->Month)->startOfMonth()->lte($monthStart)
        );

        $trailingSales = $salesUpToMonth->filter(fn ($s) => Carbon::parse($s->Month)->startOfMonth()->gt($twelveMonthsAgo)
        );

        $hasThisMonth = $trailingSales->contains(fn ($s) => Carbon::parse($s->Month)->startOfMonth()->eq($monthStart)
        );

        $totalRecords = $salesUpToMonth->filter(fn ($s) => $s->Total_Sales !== null)->count();

        $recentCount = $salesUpToMonth->filter(fn ($s) => Carbon::parse($s->Month)->startOfMonth()->gte($threeMonthsAgo)
        )->filter(fn ($s) => $s->Total_Sales !== null)->count();

        $hasSalesBefore = $salesUpToMonth->filter(fn ($s) => Carbon::parse($s->Month)->startOfMonth()->lte($twelveMonthsAgo)
        )->filter(fn ($s) => $s->Total_Sales !== null)->isNotEmpty();

        if ($hasSalesBefore && $trailingSales->isEmpty()) {
            return ['tier' => 'Closed', 'avg_per_day' => 0];
        }

        if ($trailingSales->isNotEmpty() && ! $hasThisMonth) {
            return ['tier' => 'Inactive', 'avg_per_day' => 0];
        }

        if ($totalRecords <= 3) {
            return ['tier' => 'New', 'avg_per_day' => 0];
        }

        if ($recentCount < 4) {
            return ['tier' => 'Reopen', 'avg_per_day' => 0];
        }

        $totalVolume = 0;
        $totalDays = 0;
        foreach ($trailingSales as $s) {
            $totalVolume += ($s->Total_Sales ?? 0) - ($s->WiS_Sales ?? 0) - ($s->Bottle_Sales ?? 0);
            $totalDays += $s->Number_Open_Days ?? 0;
        }

        $avgPerDay = $totalDays > 0 ? $totalVolume / $totalDays : 0;

        if ($avgPerDay > 110) {
            return ['tier' => 'ST1', 'avg_per_day' => $avgPerDay];
        }
        if ($avgPerDay > 70) {
            return ['tier' => '1', 'avg_per_day' => $avgPerDay];
        }
        if ($avgPerDay >= 45) {
            return ['tier' => '2', 'avg_per_day' => $avgPerDay];
        }

        return ['tier' => '3', 'avg_per_day' => $avgPerDay];
    }
}
