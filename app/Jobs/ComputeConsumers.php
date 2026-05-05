<?php

namespace App\Jobs;

use App\Models\Sims3\Beneficiary;
use Carbon\Carbon;
use Illuminate\Support\Collection;

class ComputeConsumers extends BaseComputeJob
{
    protected function prepareData(Collection $siteMap, Collection $months, array $siteNames): array
    {
        $from = $months->first()->copy()->startOfMonth();
        $to = $months->last()->copy()->endOfMonth();

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
                $map[$key] = [
                    'consumers' => $beneficiary->Beneficiaries !== null
                        ? (int) round($beneficiary->Beneficiaries)
                        : null,
                ];
            }
        }

        return $map;
    }
}
