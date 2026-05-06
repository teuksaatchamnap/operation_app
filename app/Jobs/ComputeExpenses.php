<?php

namespace App\Jobs;

use App\Models\Sims3\Expense;
use Carbon\Carbon;
use Illuminate\Support\Collection;

class ComputeExpenses extends BaseComputeJob
{
    protected function prepareData(Collection $siteMap, Collection $months, array $siteNames): array
    {
        $from = $months->first()->copy()->startOfMonth();
        $to = $months->last()->copy()->endOfMonth();

        $expenses = Expense::query()
            ->select(['Id_Site', 'Month', 'Amount_expenses'])
            ->whereBetween('Month', [$from, $to])
            ->whereIn('Id_Site', $siteNames)
            ->where('Ref_expenses', '<>', 'debt')
            ->get();

        $map = [];
        foreach ($expenses as $expense) {
            $monthKey = Carbon::parse($expense->Month)->startOfMonth()->format('Y-m-d');
            $site = trim($expense->Id_Site);
            $key = $site.'|'.$monthKey;

            if (! isset($map[$key])) {
                $map[$key] = ['expenses' => 0];
            }

            $map[$key]['expenses'] += (float) ($expense->Amount_expenses ?? 0);
        }

        foreach ($map as $key => $record) {
            $map[$key]['expenses'] = (int) round($record['expenses']);
        }

        return $map;
    }
}
