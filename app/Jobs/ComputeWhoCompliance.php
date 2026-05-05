<?php

namespace App\Jobs;

use App\Models\Sims3\Sample;
use Carbon\Carbon;
use Illuminate\Support\Collection;

class ComputeWhoCompliance extends BaseComputeJob
{
    protected function prepareData(Collection $siteMap, Collection $months, array $siteNames): array
    {
        $from = $months->first()->copy()->startOfMonth();
        $to = $months->last()->copy()->endOfMonth();

        $samples = Sample::query()
            ->select(['site', 'analysis_date', 'sample_date', 'escherichia', 'total_coliform'])
            ->whereBetween('sample_date', [$from, $to])
            ->whereIn('site', $siteNames)
            ->orderBy('analysis_date', 'desc')
            ->get();

        $latestBySiteMonth = [];
        foreach ($samples as $sample) {
            $site = trim($sample->site);
            $monthKey = Carbon::parse($sample->sample_date)->startOfMonth()->format('Y-m-d');
            $key = $site . '|' . $monthKey;

            if (!isset($latestBySiteMonth[$key])) {
                $latestBySiteMonth[$key] = $sample;
            }
        }

        $map = [];
        foreach ($latestBySiteMonth as $key => $sample) {
            $escherichiaOk = in_array($sample->escherichia, [null, '', '0'], true);
            $totalColiformOk = in_array($sample->total_coliform, [null, '', '0'], true);
            $compliant = $escherichiaOk && $totalColiformOk ? 1 : 0;

            $map[$key] = [
                'who_compliance' => $compliant,
            ];
        }

        return $map;
    }
}
