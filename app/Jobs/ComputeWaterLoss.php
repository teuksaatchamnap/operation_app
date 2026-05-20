<?php

namespace App\Jobs;

use App\Models\Sims3\Indicator;
use App\Models\Sims3\Sale;
use App\Models\Sims3\WaterMeter;
use Carbon\Carbon;
use Illuminate\Support\Collection;

class ComputeWaterLoss extends BaseComputeJob
{
    protected function prepareData(Collection $siteMap, Collection $months, array $siteNames): array
    {
        $from = $months->first()->copy()->startOfMonth();
        $to = $months->last()->copy()->endOfMonth();

        $indicators = Indicator::query()
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

        $keysNeedingMeter = [];
        foreach ($indicators as $indicator) {
            $monthKey = Carbon::parse($indicator->Month)->startOfMonth()->format('Y-m-d');
            $site = trim($indicator->Id_Site);
            $key = $site.'|'.$monthKey;

            if (empty($indicator->Water_Consume) || (float) $indicator->Water_Consume <= 0) {
                $keysNeedingMeter[$key] = [
                    'site' => $site,
                    'month' => Carbon::parse($indicator->Month)->startOfMonth(),
                ];
            }
        }

        $meterWaterConsume = [];
        if (! empty($keysNeedingMeter)) {
            $sitesNeedingMeter = array_unique(array_column($keysNeedingMeter, 'site'));

            $meters = WaterMeter::query()
                ->select(['site', 'date', 'value'])
                ->whereIn('site', $sitesNeedingMeter)
                ->where('date', '<=', $to)
                ->orderBy('site')
                ->orderBy('date')
                ->get()
                ->groupBy(fn ($m) => trim($m->site));

            foreach ($keysNeedingMeter as $key => $info) {
                $siteMeters = $meters[$info['site']] ?? collect();

                $monthEnd = $info['month']->copy()->endOfMonth();
                $monthStart = $info['month']->copy()->startOfMonth();

                $endReading = (float) ($siteMeters
                    ->filter(fn ($m) => Carbon::parse($m->date)->lte($monthEnd))
                    ->max('value') ?? 0);

                $startReading = (float) ($siteMeters
                    ->filter(fn ($m) => Carbon::parse($m->date)->lte($monthStart))
                    ->max('value') ?? 0);

                if ($endReading > 0 && $endReading > $startReading) {
                    $meterWaterConsume[$key] = ($endReading - $startReading) * 1000;
                }
            }
        }

        $map = [];
        foreach ($indicators as $indicator) {
            $monthKey = Carbon::parse($indicator->Month)->startOfMonth()->format('Y-m-d');
            $site = trim($indicator->Id_Site);
            $key = $site.'|'.$monthKey;

            if (isset($map[$key])) {
                continue;
            }

            $wc = (float) ($indicator->Water_Consume ?? 0);

            if ($wc <= 0 && isset($meterWaterConsume[$key])) {
                $wc = (float) $meterWaterConsume[$key];
            }

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
