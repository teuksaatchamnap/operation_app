<?php

namespace App\Jobs;

use App\Models\Sims3\Beneficiary;
use App\Models\Sims3\Site as Sims3Site;
use Carbon\Carbon;
use Illuminate\Support\Collection;

class ComputeConsumers extends BaseComputeJob
{
    protected function prepareData(Collection $siteMap, Collection $months, array $siteNames): array
    {
        $from = $months->first()->copy()->startOfMonth();
        $to = $months->last()->copy()->endOfMonth();

        $populations = Sims3Site::query()
            ->select(['Id_Site', 'Number_Population'])
            ->whereIn('Id_Site', $siteNames)
            ->get()
            ->mapWithKeys(fn ($s) => [trim($s->Id_Site) => $s->Number_Population]);

        $beneficiaries = Beneficiary::query()
            ->select(['Id_Site', 'Month', 'Beneficiaries'])
            ->whereBetween('Month', [$from, $to])
            ->whereIn('Id_Site', $siteNames)
            ->get();

        $map = [];
        foreach ($beneficiaries as $beneficiary) {
            $monthKey = Carbon::parse($beneficiary->Month)->startOfMonth()->format('Y-m-d');
            $site = trim($beneficiary->Id_Site);
            $key = $site.'|'.$monthKey;

            if (! isset($map[$key])) {
                $consumers = $beneficiary->Beneficiaries !== null
                    ? (int) round($beneficiary->Beneficiaries)
                    : null;
                $population = $populations[$site] ?? null;
                $penetration = null;
                if ($consumers !== null && $population !== null && $population > 0) {
                    $penetration = round($consumers / $population, 4);
                }

                $map[$key] = [
                    'consumers' => $consumers,
                    'penetration' => $penetration,
                ];
            }
        }

        return $map;
    }
}
