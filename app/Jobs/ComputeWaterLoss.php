<?php

namespace App\Jobs;

use App\Models\Sims3\Indicator;
use App\Models\Sims3\Sale;
use Carbon\Carbon;
use Illuminate\Support\Collection;

class ComputeWaterLoss extends BaseComputeJob
{
    protected function prepareData(Collection $siteMap, Collection $months, array $siteNames): array
    {
        $from = $months->first()->copy()->startOfMonth();
        $to = $months->last()->copy()->endOfMonth();

        $waterConsume = Indicator::query()
            ->select(['Id_Site', 'Month', 'Water_Consume'])
            ->whereBetween('Month', [$from, $to])
            ->whereIn('Id_Site', $siteNames)
            ->get();

        $totalSales = Sale::query()
            ->select(['Id_Site', 'Month', 'Total_Sales'])
            ->whereBetween('Month', [$from, $to])
            ->whereIn('Id_Site', $siteNames)
            ->get()
            ->groupBy(fn ($s) => trim($s->Id_Site).'|'.Carbon::parse($s->Month)->startOfMonth()->format('Y-m-d'))
            ->map(fn ($rows) => $rows->sum('Total_Sales'));

        $map = [];
        foreach ($waterConsume as $indicator) {
            $monthKey = Carbon::parse($indicator->Month)->startOfMonth()->format('Y-m-d');
            $site = trim($indicator->Id_Site);
            $key = $site.'|'.$monthKey;

            if (isset($map[$key])) {
                continue;
            }

            $wc = (float) ($indicator->Water_Consume ?? 0);
            $sales = (float) ($totalSales[$key] ?? 0);

            if ($wc <= 0) {
                $map[$key] = [
                    'water_loss' => null,
                    'is_water_loss_ok' => null,
                ];

                continue;
            }

            $waterLoss = (($wc - ($sales * 20)) / $wc) * 100;

            $map[$key] = [
                'water_loss' => round($waterLoss, 2),
                'is_water_loss_ok' => ($waterLoss >= 15 && $waterLoss <= 25) ? 0 : 1,
            ];
        }

        return $map;
    }
}
