<?php

namespace App\Jobs;

use App\Models\Sims3\Expense;
use App\Models\Sims3\Indicator;
use App\Models\Sims3\Sale;
use App\Models\Sims3\WaterMeter;
use Carbon\Carbon;
use Illuminate\Support\Collection;

class ComputeDataCollection extends BaseComputeJob
{
    protected function prepareData(Collection $siteMap, Collection $months, array $siteNames): array
    {
        $from = $months->first()->copy()->startOfMonth();
        $to = $months->last()->copy()->endOfMonth();

        $hasExpense = Expense::query()
            ->select(['Id_Site', 'Month'])
            ->whereBetween('Month', [$from, $to])
            ->whereIn('Id_Site', $siteNames)
            ->where('Amount_expenses', '>', 0)
            ->where('Ref_expenses', '<>', 'debt')
            ->get()
            ->unique(fn ($e) => trim($e->Id_Site).'|'.Carbon::parse($e->Month)->startOfMonth()->format('Y-m-d'))
            ->mapWithKeys(fn ($e) => [
                trim($e->Id_Site).'|'.Carbon::parse($e->Month)->startOfMonth()->format('Y-m-d') => true,
            ]);

        $hasSales = Sale::query()
            ->select(['Id_Site', 'Month'])
            ->whereBetween('Month', [$from, $to])
            ->whereIn('Id_Site', $siteNames)
            ->whereNotNull('Total_Sales')
            ->get()
            ->unique(fn ($s) => trim($s->Id_Site).'|'.Carbon::parse($s->Month)->startOfMonth()->format('Y-m-d'))
            ->mapWithKeys(fn ($s) => [
                trim($s->Id_Site).'|'.Carbon::parse($s->Month)->startOfMonth()->format('Y-m-d') => true,
            ]);

        $hasWaterFromIndicator = Indicator::query()
            ->select(['Id_Site', 'Month', 'Water_Consume'])
            ->whereBetween('Month', [$from, $to])
            ->whereIn('Id_Site', $siteNames)
            ->whereNotNull('Water_Consume')
            ->where('Water_Consume', '>', 0)
            ->get()
            ->unique(fn ($i) => trim($i->Id_Site).'|'.Carbon::parse($i->Month)->startOfMonth()->format('Y-m-d'))
            ->mapWithKeys(fn ($i) => [
                trim($i->Id_Site).'|'.Carbon::parse($i->Month)->startOfMonth()->format('Y-m-d') => true,
            ]);

        $allKeys = collect($hasExpense->keys())
            ->merge($hasSales->keys())
            ->merge($hasWaterFromIndicator->keys())
            ->unique();

        $keysNeedingMeterCheck = $allKeys
            ->diff($hasWaterFromIndicator->keys())
            ->values();

        $hasWaterFromMeter = collect();
        if ($keysNeedingMeterCheck->isNotEmpty()) {
            $meterKeys = [];
            foreach ($keysNeedingMeterCheck as $key) {
                [$site, $monthStr] = explode('|', $key, 2);
                $monthStart = Carbon::parse($monthStr)->startOfMonth();
                $monthEnd = $monthStart->copy()->endOfMonth();

                $exists = WaterMeter::query()
                    ->where('site', $site)
                    ->whereBetween('date', [$monthStart, $monthEnd])
                    ->exists();

                if ($exists) {
                    $meterKeys[$key] = true;
                }
            }
            $hasWaterFromMeter = collect($meterKeys);
        }

        $hasWater = $hasWaterFromIndicator->merge($hasWaterFromMeter);

        $map = [];
        foreach ($allKeys as $key) {
            $score = 0;
            if ($hasExpense->has($key)) {
                $score++;
            }
            if ($hasSales->has($key)) {
                $score++;
            }
            if ($hasWater->has($key)) {
                $score++;
            }

            $map[$key] = [
                'data_collection' => $score === 3 ? 2 : ($score === 0 ? 0 : 1),
            ];
        }

        foreach ($months as $month) {
            $monthKey = $month->format('Y-m-d');
            foreach ($siteMap as $siteName => $siteId) {
                $key = $siteName.'|'.$monthKey;
                if (! isset($map[$key])) {
                    $map[$key] = [
                        'data_collection' => 0,
                    ];
                }
            }
        }

        return $map;
    }
}
