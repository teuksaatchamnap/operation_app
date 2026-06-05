<?php

namespace App\Services;

use App\Models\Sims3\CashierSale;
use App\Models\Sims3\DailySale;
use Carbon\Carbon;
use Illuminate\Support\Collection;

class DailySalesProvider
{
    private const TYPE_MAP = [
        'free' => 'Free_Sales',
        'hod' => 'Hod_Sales',
        'shop' => 'Shopkeeper_Sales',
        'wis' => 'WiS_Sales',
        'onsite' => 'Onsite_Sales',
        'bottle' => 'Bottle_Sales',
    ];

    private const CHANNEL_KEYS = [
        'Free_Sales', 'Hod_Sales', 'Shopkeeper_Sales', 'WiS_Sales',
        'Onsite_Sales', 'Bottle_Sales',
    ];

    public function getDailySales(string $sims3SiteId, Carbon $month): Collection
    {
        $rows = DailySale::where('Id_Site', $sims3SiteId)
            ->whereYear('Month', $month->year)
            ->whereMonth('Month', $month->month)
            ->get()
            ->sortBy('Day');

        if ($rows->isNotEmpty()) {
            return $this->normalizeDailySaleRows($rows);
        }

        return $this->buildFromCashier($sims3SiteId, $month);
    }

    public function getDayTotals(string $sims3SiteId, Carbon $month): Collection
    {
        return $this->getDailySales($sims3SiteId, $month)
            ->mapWithKeys(fn ($row) => [$row['date'] => $row['Total_Sales']]);
    }

    public function getDailySalesInRange(string $sims3SiteId, Carbon $startDate, Carbon $endDate): Collection
    {
        $rows = DailySale::where('Id_Site', $sims3SiteId)
            ->whereDate('Day', '>=', $startDate)
            ->whereDate('Day', '<=', $endDate)
            ->get()
            ->sortBy('Day');

        if ($rows->isNotEmpty()) {
            return $this->normalizeDailySaleRows($rows);
        }

        return $this->buildFromCashierInRange($sims3SiteId, $startDate, $endDate);
    }

    public function getDayTotalsInRange(string $sims3SiteId, Carbon $startDate, Carbon $endDate): Collection
    {
        return $this->getDailySalesInRange($sims3SiteId, $startDate, $endDate)
            ->mapWithKeys(fn ($row) => [$row['date'] => $row['Total_Sales']]);
    }

    private function normalizeDailySaleRows(Collection $rows): Collection
    {
        return $rows->map(function ($r) {
            $knownSum = collect(self::CHANNEL_KEYS)->sum(fn ($c) => (float) ($r->{$c} ?? 0));
            $otherSales = max(0, (float) ($r->Total_Sales ?? 0) - $knownSum);

            $day = [];
            foreach (self::CHANNEL_KEYS as $c) {
                $day[$c] = (float) ($r->{$c} ?? 0);
            }

            return [
                'date' => $r->Day ? Carbon::parse($r->Day)->format('Y-m-d') : null,
                ...$day,
                'Other_Sales' => $otherSales,
                'Total_Sales' => (float) ($r->Total_Sales ?? 0),
            ];
        });
    }

    private function buildFromCashier(string $sims3SiteId, Carbon $month): Collection
    {
        $rows = CashierSale::where('site', $sims3SiteId)
            ->whereYear('sale_date', $month->year)
            ->whereMonth('sale_date', $month->month)
            ->get();

        return $this->groupCashierRows($rows);
    }

    private function buildFromCashierInRange(string $sims3SiteId, Carbon $startDate, Carbon $endDate): Collection
    {
        $rows = CashierSale::where('site', $sims3SiteId)
            ->whereDate('sale_date', '>=', $startDate)
            ->whereDate('sale_date', '<=', $endDate)
            ->get();

        return $this->groupCashierRows($rows);
    }

    private function groupCashierRows(Collection $rows): Collection
    {
        if ($rows->isEmpty()) {
            return collect();
        }

        $grouped = $rows->groupBy(fn ($r) => Carbon::parse($r->sale_date)->format('Y-m-d'));

        return $grouped->sortKeys()->map(function ($dayRows, $date) {
            $byType = $dayRows->groupBy('type');

            $day = [];
            foreach (self::CHANNEL_KEYS as $channel) {
                $day[$channel] = 0;
            }
            $day['Other_Sales'] = 0;
            $day['Total_Sales'] = 0;
            $day['date'] = $date;

            foreach ($byType as $type => $items) {
                $column = self::TYPE_MAP[$type] ?? null;
                if ($column !== null) {
                    $total = (float) $items->sum('quantity');
                    $day[$column] = $total;
                    $day['Total_Sales'] += $total;
                }
            }

            return $day;
        })->values();
    }
}
