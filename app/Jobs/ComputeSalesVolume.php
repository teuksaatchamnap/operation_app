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
                    'sales_volume' => (int) round($volume),
                    'days_open' => $sale->Number_Open_Days !== null ? (int) $sale->Number_Open_Days : null,
                ];
            }
        }

        return $map;
    }
}
