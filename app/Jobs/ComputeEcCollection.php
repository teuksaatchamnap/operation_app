<?php

namespace App\Jobs;

use App\Models\Sims3\Expense;
use Carbon\Carbon;
use Illuminate\Support\Collection;

class ComputeEcCollection extends BaseComputeJob
{
    protected function prepareData(Collection $siteMap, Collection $months, array $siteNames): array
    {
        $from = $months->first()->copy()->startOfMonth();
        $to = $months->last()->copy()->endOfMonth();

        $expenses = Expense::query()
            ->select(['Id_Site', 'Month', 'Amount_expenses', 'Paid'])
            ->whereBetween('Month', [$from, $to])
            ->whereIn('Id_Site', $siteNames)
            ->where('Ref_expenses', 'entrepreneur_contribution')
            ->get();

        $paidBySiteMonth = [];
        $amountBySiteMonth = [];

        foreach ($expenses as $expense) {
            $monthKey = Carbon::parse($expense->Month)->startOfMonth()->format('Y-m-d');
            $site = trim($expense->Id_Site);
            $key = $site.'|'.$monthKey;

            $paidBySiteMonth[$key] = ($paidBySiteMonth[$key] ?? 0) + (float) ($expense->Paid ?? 0);
            $amountBySiteMonth[$key] = ($amountBySiteMonth[$key] ?? 0) + (float) ($expense->Amount_expenses ?? 0);
        }

        $map = [];
        foreach ($paidBySiteMonth as $key => $paid) {
            $amount = $amountBySiteMonth[$key] ?? 0;
            $map[$key] = [
                'ec_collection' => $paid >= $amount ? 1 : 0,
            ];
        }

        return $map;
    }
}
