<?php

namespace App\Jobs;

use App\Models\Sims3\Expense;
use Carbon\Carbon;
use Illuminate\Support\Collection;

class ComputeCollectionRate extends BaseComputeJob
{
    private const REF_EXPENSES = [
        'stock_ts',
        'bottle_invoice',
        'entrepreneur_contribution',
        'water quality alert',
        'technical intervention',
        'delivery_program_fee',
    ];

    protected function prepareData(Collection $siteMap, Collection $months, array $siteNames): array
    {
        $from = $months->first()->copy()->startOfMonth();
        $to = $months->last()->copy()->endOfMonth();

        $expenses = Expense::query()
            ->select(['Id_Site', 'Month', 'Amount_expenses', 'Paid'])
            ->whereBetween('Month', [$from, $to])
            ->whereIn('Id_Site', $siteNames)
            ->whereIn('Ref_expenses', self::REF_EXPENSES)
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
            if ($amount > 0) {
                $map[$key] = [
                    'collection_rate' => round(($paid / $amount) * 100, 2),
                ];
            }
        }

        return $map;
    }
}
