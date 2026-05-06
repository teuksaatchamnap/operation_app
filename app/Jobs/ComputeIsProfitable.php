<?php

namespace App\Jobs;

use App\Models\Sims3\Expense;
use App\Models\Sims3\Sale;
use Carbon\Carbon;
use Illuminate\Support\Collection;

class ComputeIsProfitable extends BaseComputeJob
{
    protected function prepareData(Collection $siteMap, Collection $months, array $siteNames): array
    {
        $from = $months->first()->copy()->startOfMonth();
        $to = $months->last()->copy()->endOfMonth();

        $revenue = Sale::query()
            ->select(['Id_Site', 'Month', 'Total_Income'])
            ->whereBetween('Month', [$from, $to])
            ->whereIn('Id_Site', $siteNames)
            ->get()
            ->groupBy(fn ($s) => trim($s->Id_Site).'|'.Carbon::parse($s->Month)->startOfMonth()->format('Y-m-d'))
            ->map(fn ($rows) => $rows->sum('Total_Income'));

        $expenses = Expense::query()
            ->select(['Id_Site', 'Month', 'Amount_expenses'])
            ->whereBetween('Month', [$from, $to])
            ->whereIn('Id_Site', $siteNames)
            ->get()
            ->groupBy(fn ($e) => trim($e->Id_Site).'|'.Carbon::parse($e->Month)->startOfMonth()->format('Y-m-d'))
            ->map(fn ($rows) => $rows->sum('Amount_expenses'));

        $salaryEntrepreneur = Expense::query()
            ->select(['Id_Site', 'Month', 'Amount_expenses'])
            ->whereBetween('Month', [$from, $to])
            ->whereIn('Id_Site', $siteNames)
            ->whereIn('Ref_expenses', ['variable_salary_entrepreneurs', 'fix_salary_entrepreneurs'])
            ->get()
            ->groupBy(fn ($e) => trim($e->Id_Site).'|'.Carbon::parse($e->Month)->startOfMonth()->format('Y-m-d'))
            ->map(fn ($rows) => $rows->sum('Amount_expenses'));

        $allKeys = array_unique(array_merge(
            array_keys($revenue->toArray()),
            array_keys($expenses->toArray()),
            array_keys($salaryEntrepreneur->toArray())
        ));

        $map = [];
        foreach ($allKeys as $key) {
            $rev = (float) ($revenue[$key] ?? 0);
            $exp = (float) ($expenses[$key] ?? 0);
            $salary = (float) ($salaryEntrepreneur[$key] ?? 0);

            $map[$key] = [
                'is_profitable' => ($rev - $exp + $salary) >= 200 ? 1 : 0,
            ];
        }

        return $map;
    }
}
