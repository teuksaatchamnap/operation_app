<?php

namespace App\Http\Controllers;

use App\Models\FactMonthly;
use App\Models\Kpi;
use App\Models\Objective;
use App\Models\Sims3\Expense as Sims3Expense;
use App\Models\Sims3\Platform as Sims3Platform;
use App\Models\Sims3\Sale as Sims3Sale;
use App\Models\Sims3\Site as Sims3Site;
use App\Models\Site;
use Carbon\Carbon;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;

class SiteAnalysisController extends Controller
{
    public function show(Site $site, Request $request): JsonResponse
    {
        $sims3Site = Sims3Site::where('Id_Site', $site->name)->first();

        if (! $sims3Site) {
            return response()->json(['error' => 'Site not found in Sims3 database'], 404);
        }

        $romName = $sims3Site->Platform
            ? Sims3Platform::where('Code_Platform', $sims3Site->Platform)->value('Mail_ROM')
            : null;

        $monthStr = $request->query('month', now()->format('Y-m'));
        $month = Carbon::parse($monthStr.'-01');

        $fact = FactMonthly::where('site_id', $site->id)
            ->where('month', $month)
            ->first();

        $kpiRows = Kpi::whereIn('col_name', [
            'bottles_per_day',
            'sales_volume',
            'tier',
            'days_open',
            'water_loss',
            'operators',
            'consumers',
            'penetration',
            'who_compliance',
        ])->get()->keyBy('col_name');

        $kpiDefinitions = [];

        if (isset($kpiRows['bottles_per_day'])) {
            $kpiDefinitions[] = [
                'key' => 'bottles_per_day_ytd',
                'label' => $kpiRows['bottles_per_day']->name.' (YTD)',
                'col_name' => 'bottles_per_day',
                'periodicity' => 'ytd',
            ];
        }

        $displayColNames = [
            'bottles_per_day',
            'sales_volume',
            'tier',
            'days_open',
            'water_loss',
            'operators',
            'consumers',
            'penetration',
            'who_compliance',
        ];

        foreach ($displayColNames as $colName) {
            $kpi = $kpiRows[$colName] ?? null;
            if (! $kpi) {
                continue;
            }

            $kpiDefinitions[] = [
                'key' => $colName,
                'label' => $kpi->name,
                'col_name' => $colName,
                'periodicity' => $kpi->periodicity === 'year to date' ? 'ytd' : 'monthly',
            ];
        }

        $kpiData = [];
        foreach ($kpiDefinitions as $def) {
            $value = null;
            $objective = null;

            if ($fact) {
                if ($def['periodicity'] === 'ytd') {
                    $ytdRecords = FactMonthly::where('site_id', $site->id)
                        ->whereYear('month', $month->year)
                        ->where('month', '<=', $month)
                        ->whereNotNull($def['col_name'])
                        ->pluck($def['col_name']);

                    if ($ytdRecords->isNotEmpty()) {
                        $value = round($ytdRecords->avg());
                    }
                } else {
                    $value = $fact->{$def['col_name']};
                }

                $kpi = $kpiRows[$def['col_name']] ?? null;
                if ($kpi) {
                    $matchingObjective = Objective::where('kpi_id', $kpi->id)
                        ->where('start_date', '<=', $month)
                        ->where(fn ($q) => $q->whereNull('end_date')->orWhere('end_date', '>=', $month))
                        ->orderByRaw("CASE WHEN type = 'individual' THEN 0 ELSE 1 END")
                        ->first();
                    $objective = $matchingObjective ? (float) $matchingObjective->value : null;
                }
            }

            if ($def['col_name'] === 'who_compliance' && $value !== null) {
                $value = $value ? 'Safe' : 'Unsafe';
            } elseif ($def['col_name'] === 'penetration' && is_numeric($value)) {
                $value = round((float) $value * 100);
            } elseif (is_numeric($value)) {
                $value = round((float) $value);
            }

            $kpiData[$def['key']] = [
                'label' => $def['label'],
                'value' => $value ?? 0,
                'objective' => $objective ?? 0,
                'description' => $kpi?->description,
            ];
        }

        return response()->json([
            'platform' => $sims3Site->Platform,
            'entrepreneur_name' => $sims3Site->Entrepreneur_English_Name,
            'start_working_date' => $sims3Site->Date_start_working,
            'advisor_name' => $sims3Site->Advisor_email,
            'rom_name' => $romName,
            'commune_name' => $sims3Site->Commune,
            'population_commune' => $sims3Site->Population,
            'households' => $sims3Site->Households,
            'kpis' => $kpiData,
        ]);
    }

    public function expenseBreakdown(Site $site, Request $request): JsonResponse
    {
        $monthStr = $request->query('month', now()->format('Y-m'));
        $month = Carbon::parse($monthStr.'-01');

        $sims3Site = Sims3Site::where('Id_Site', $site->name)->first();

        if (! $sims3Site) {
            return response()->json(['error' => 'Site not found in Sims3 database'], 404);
        }

        $categoryRefs = [
            'Production' => ['consumable_production', 'stock_ts', 'bottle_invoice', 'electricity', 'gasoline_waterpump', 'raw_water'],
            'Salary' => ['fix_salary_entrepreneurs', 'variable_salary_entrepreneurs', 'fix_salary_operators', 'variable_salary_operators'],
            'Delivery' => ['maintenance_delivery', 'gasoline_delivery'],
            'Contribution' => ['commune_contribution', 'entrepreneur_contribution'],
            'Intervention' => ['technical intervention', 'water quality alert'],
            'Investment' => ['investment'],
        ];

        $allRefs = collect($categoryRefs)->values()->flatten()->all();

        $expensesToIgnore = ['WinS_invoice', 'debt', 'withdrawal', 'adjustment'];

        $siteExpenses = Sims3Expense::where('Id_Site', $sims3Site->Id_Site)
            ->whereYear('Month', $month->year)
            ->whereMonth('Month', $month->month)
            ->whereNotIn('Ref_expenses', $expensesToIgnore)
            ->whereIn('Ref_expenses', $allRefs)
            ->get(['Ref_expenses', 'Amount_expenses'])
            ->groupBy(fn ($e) => collect($categoryRefs)->search(fn ($refs) => in_array($e->Ref_expenses, $refs)))
            ->map(fn ($group) => round($group->sum('Amount_expenses')));

        $allMonthly = Sims3Expense::whereYear('Month', $month->year)
            ->whereMonth('Month', $month->month)
            ->whereNotIn('Ref_expenses', $expensesToIgnore)
            ->whereIn('Ref_expenses', $allRefs)
            ->get(['Id_Site', 'Ref_expenses', 'Amount_expenses'])
            ->groupBy(fn ($e) => collect($categoryRefs)->search(fn ($refs) => in_array($e->Ref_expenses, $refs)));

        $expenses = [];
        foreach ($categoryRefs as $category => $refs) {
            $expenses[] = [
                'category' => $category,
                'site_amount' => $siteExpenses->get($category, 0),
                'avg_amount' => $allMonthly->has($category)
                    ? round($allMonthly->get($category)->avg('Amount_expenses'))
                    : 0,
            ];
        }

        return response()->json(['expenses' => $expenses]);
    }

    public function monthlySalesBreakdown(Site $site, Request $request): JsonResponse
    {
        $monthStr = $request->query('month', now()->format('Y-m'));
        $month = Carbon::parse($monthStr.'-01');

        $sims3Site = Sims3Site::where('Id_Site', $site->name)->first();

        if (! $sims3Site) {
            return response()->json(['error' => 'Site not found in Sims3 database'], 404);
        }

        $sale = Sims3Sale::where('Id_Site', $sims3Site->Id_Site)
            ->whereYear('Month', $month->year)
            ->whereMonth('Month', $month->month)
            ->first();

        $categories = [
            ['key' => 'Hod_Sales', 'label' => 'Home Delivery'],
            ['key' => 'Shopkeeper_Sales', 'label' => 'Shopkeeper'],
            ['key' => 'WiS_Sales', 'label' => 'Water in school'],
            ['key' => 'Onsite_Sales', 'label' => 'On site'],
            ['key' => 'Free_Sales', 'label' => 'Free'],
            ['key' => 'Bottle_Sales', 'label' => 'Bottle'],
            ['key' => 'Emergency_Sales', 'label' => 'Emergency'],
            ['key' => 'Other_Sales', 'label' => 'Other'],
        ];

        $breakdown = $sale
            ? array_map(fn ($c) => [
                'label' => $c['label'],
                'value' => (float) ($sale->{$c['key']} ?? 0),
            ], $categories)
            : [];

        return response()->json(['breakdown' => $breakdown]);
    }

    public function monthlyPerformance(Site $site): JsonResponse
    {
        $currentYear = now()->year;
        $years = range($currentYear - 5, $currentYear);

        $records = FactMonthly::where('site_id', $site->id)
            ->whereYear('month', '>=', $currentYear - 5)
            ->whereNotNull('bottles_per_day')
            ->orderBy('month')
            ->get(['month', 'bottles_per_day']);

        $series = [];
        $monthLabels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

        foreach ($years as $year) {
            $data = array_fill(0, 12, null);
            $yearRecords = $records->filter(fn ($r) => Carbon::parse($r->month)->year === $year);
            foreach ($yearRecords as $r) {
                $m = Carbon::parse($r->month);
                $data[$m->month - 1] = round($r->bottles_per_day);
            }
            $series[] = [
                'name' => (string) $year,
                'data' => $data,
            ];
        }

        return response()->json([
            'categories' => $monthLabels,
            'series' => $series,
        ]);
    }
}
