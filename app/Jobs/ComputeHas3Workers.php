<?php

namespace App\Jobs;

use App\Models\Sims3\Indicator;
use Carbon\Carbon;
use Illuminate\Support\Collection;

class ComputeHas3Workers extends BaseComputeJob
{
    protected function prepareData(Collection $siteMap, Collection $months, array $siteNames): array
    {
        $from = $months->first()->copy()->startOfMonth();
        $to = $months->last()->copy()->endOfMonth();

        $indicators = Indicator::query()
            ->select(['Id_Site', 'Month', 'Number_of_Operator'])
            ->whereBetween('Month', [$from, $to])
            ->whereIn('Id_Site', $siteNames)
            ->get();

        $map = [];
        foreach ($indicators as $indicator) {
            $monthKey = Carbon::parse($indicator->Month)->startOfMonth()->format('Y-m-d');
            $site = trim($indicator->Id_Site);
            $key = $site.'|'.$monthKey;

            if (! isset($map[$key])) {
                $operators = $indicator->Number_of_Operator;
                $map[$key] = [
                    'has_3_workers' => $operators !== null ? ((int) $operators >= 3 ? 1 : 0) : null,
                    'operators' => $operators !== null ? (int) $operators : null,
                ];
            }
        }

        return $map;
    }
}
