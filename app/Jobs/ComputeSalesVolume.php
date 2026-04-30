<?php

namespace App\Jobs;

use App\Models\Sims3\Sale;
use Carbon\Carbon;
use Illuminate\Support\Collection;

class ComputeSalesVolume extends BaseComputeJob
{
    protected function prepareData(Collection $siteMap, Collection $months, array $siteNames): array
    {
        $from = $months->first()->copy()->startOfMonth();
        $to = $months->last()->copy()->endOfMonth();

        $sales = Sale::query()
            ->select(['Id_Site', 'Month', 'Total_Sales', 'WiS_Sales', 'Bottle_Sales', 'Code_Sales', 'Number_Open_Days'])
            ->whereBetween('Month', [$from, $to])
            ->whereIn('Id_Site', $siteNames)
            ->orderBy('Code_Sales')
            ->get();

        $map = [];
        foreach ($sales as $sale) {
            $monthKey = Carbon::parse($sale->Month)->startOfMonth()->format('Y-m-d');
            $key = trim($sale->Id_Site) . '|' . $monthKey;

            if (!isset($map[$key])) {
                $volume = ($sale->Total_Sales ?? 0) - ($sale->WiS_Sales ?? 0) - ($sale->Bottle_Sales ?? 0);
                $map[$key] = [
                    'sales_volume' => (int) round($volume) ?? 0,
                    'days_open' => $sale->Number_Open_Days !== null ? (int) $sale->Number_Open_Days : 0,
                ];
                $map[$key]['active'] = $map[$key]['sales_volume'] > 0 ? 1 : 0;
                $map[$key]['super_tier_1'] = 0;
                $map[$key]['bottles_per_day'] = 0;
                if ($map[$key]['days_open'] > 0) {
                    $map[$key]['super_tier_1'] = ($map[$key]['sales_volume'] / $map[$key]['days_open']) > 110 ? 1 : 0;
                    $map[$key]['bottles_per_day'] = $map[$key]['sales_volume'] / $map[$key]['days_open'];
                }
            }
        }
        return $map;
    }
}
