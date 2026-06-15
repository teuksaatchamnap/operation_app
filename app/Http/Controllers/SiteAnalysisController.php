<?php

namespace App\Http\Controllers;

use App\Models\FactMonthly;
use App\Models\Kpi;
use App\Models\Objective;
use App\Models\Platform;
use App\Models\Sims3\Expense as Sims3Expense;
use App\Models\Sims3\Platform as Sims3Platform;
use App\Models\Sims3\Sale as Sims3Sale;
use App\Models\Sims3\Site as Sims3Site;
use App\Models\Sims3\WaterMeter;
use App\Models\Site;
use App\Services\DailySalesProvider;
use Carbon\Carbon;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;

class SiteAnalysisController extends Controller
{
    public function __construct(
        private readonly DailySalesProvider $dailySalesProvider,
    ) {}

    public function show(Site $site, Request $request): JsonResponse
    {
        $sims3Site = $this->resolveSims3Site($site);

        if (! $sims3Site) {
            return response()->json(['error' => 'Site not found in Sims3 database'], 404);
        }

        $month = $this->resolveMonth($request);

        $romName = $sims3Site->Platform
            ? Sims3Platform::where('Code_Platform', $sims3Site->Platform)->value('Mail_ROM')
            : null;

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
                    if ($def['col_name'] === 'bottles_per_day') {
                        $totals = DB::table('fact_monthly')
                            ->where('site_id', $site->id)
                            ->whereYear('month', $month->year)
                            ->where('month', '<=', $month)
                            ->selectRaw('SUM(sales_volume) as total_volume, SUM(days_open) as total_days')
                            ->first();

                        $value = $totals && $totals->total_days > 0
                            ? round($totals->total_volume / $totals->total_days)
                            : 0;
                    } else {
                        $ytdRecords = FactMonthly::where('site_id', $site->id)
                            ->whereYear('month', $month->year)
                            ->where('month', '<=', $month)
                            ->whereNotNull($def['col_name'])
                            ->pluck($def['col_name']);

                        $value = $ytdRecords->isNotEmpty() ? round($ytdRecords->avg()) : 0;
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
        $sims3Site = $this->resolveSims3Site($site);

        if (! $sims3Site) {
            return response()->json(['error' => 'Site not found in Sims3 database'], 404);
        }

        $month = $this->resolveMonth($request);

        $categoryRefs = $this->getExpenseCategories();
        $allRefs = collect($categoryRefs)->values()->flatten()->all();
        $expensesToIgnore = $this->getExpensesToIgnore();

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
        $sims3Site = $this->resolveSims3Site($site);

        if (! $sims3Site) {
            return response()->json(['error' => 'Site not found in Sims3 database'], 404);
        }

        $month = $this->resolveMonth($request);

        $sale = $this->resolveSale($sims3Site, $month);

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

    public function channelPrices(Site $site, Request $request): JsonResponse
    {
        $sims3Site = $this->resolveSims3Site($site);

        if (! $sims3Site) {
            return response()->json(['error' => 'Site not found in Sims3 database'], 404);
        }

        $month = $this->resolveMonth($request);

        $sale = $this->resolveSale($sims3Site, $month);

        $channels = [
            ['key' => 'Hod_Price', 'label' => 'Home Delivery'],
            ['key' => 'Shopkeeper_Price', 'label' => 'Shopkeeper'],
            ['key' => 'Onsite_Price', 'label' => 'On site'],
            ['key' => 'WiS_Price', 'label' => 'Water in school'],
        ];

        $prices = $sale
            ? array_map(fn ($c) => [
                'label' => $c['label'],
                'price' => round((float) ($sale->{$c['key']} ?? 0), 2),
            ], $channels)
            : [];

        return response()->json(['prices' => $prices]);
    }

    public function bottlePurchases(Site $site, Request $request): JsonResponse
    {
        $sims3Site = $this->resolveSims3Site($site);

        if (! $sims3Site) {
            return response()->json(['error' => 'Site not found in Sims3 database'], 404);
        }

        $month = $this->resolveMonth($request);

        $ytdStart = $month->copy()->startOfYear();
        $ytdEnd = $month->copy()->endOfMonth();
        $lastYearStart = $month->copy()->subYear()->startOfYear();
        $lastYearEnd = $month->copy()->subYear()->endOfMonth();

        $ytd = (float) Sims3Sale::where('Id_Site', $sims3Site->Id_Site)
            ->where('Month', '>=', $ytdStart)
            ->where('Month', '<=', $ytdEnd)
            ->sum('Bottle_Sales');

        $lastYear = (float) Sims3Sale::where('Id_Site', $sims3Site->Id_Site)
            ->where('Month', '>=', $lastYearStart)
            ->where('Month', '<=', $lastYearEnd)
            ->sum('Bottle_Sales');

        return response()->json([
            'ytd' => round($ytd),
            'last_year' => round($lastYear),
        ]);
    }

    public function profitLoss(Site $site, Request $request): JsonResponse
    {
        $sims3Site = $this->resolveSims3Site($site);

        if (! $sims3Site) {
            return response()->json(['error' => 'Site not found in Sims3 database'], 404);
        }

        $month = $this->resolveMonth($request);

        $categories = $this->getExpenseCategories();

        $currentStart = $month->copy()->startOfMonth();
        $currentEnd = $month->copy()->endOfMonth();
        $previousStart = $month->copy()->subMonth()->startOfMonth();
        $previousEnd = $month->copy()->subMonth()->endOfMonth();
        $ytdStart = $month->copy()->startOfYear();
        $ytdEnd = $month->copy()->endOfMonth();
        $lastYearStart = $month->copy()->subYear()->startOfMonth();
        $lastYearEnd = $month->copy()->subYear()->endOfMonth();

        $periods = [
            'current' => [$currentStart, $currentEnd],
            'previous' => [$previousStart, $previousEnd],
            'ytd' => [$ytdStart, $ytdEnd],
            'last_year' => [$lastYearStart, $lastYearEnd],
        ];

        $revenue = [];
        $expenseCategories = [];
        $expenseSubTotals = [];
        $entrepreneurSalaries = [];

        foreach ($periods as $key => [$start, $end]) {
            $rev = $this->getRevenueForPeriod($sims3Site, $start, $end);
            $revenue[$key] = $rev;

            $exp = $this->getExpensesForPeriod($sims3Site, $start, $end);
            $expenseSubTotals[$key] = $exp['sub_total'];
            $entrepreneurSalaries[$key] = $exp['entrepreneur_salary'];
            foreach ($exp['categoryAmounts'] as $cat => $amt) {
                $expenseCategories[$cat][$key] = $amt;
            }
        }

        $expenseCategoriesList = [];
        foreach ($categories as $cat => $refs) {
            $expenseCategoriesList[] = [
                'category' => $cat,
                'current' => $expenseCategories[$cat]['current'] ?? 0,
                'previous' => $expenseCategories[$cat]['previous'] ?? 0,
                'ytd' => $expenseCategories[$cat]['ytd'] ?? 0,
                'last_year' => $expenseCategories[$cat]['last_year'] ?? 0,
            ];
        }

        $periodLabels = [
            'current' => $currentStart->format('M Y'),
            'previous' => $previousStart->format('M Y'),
            'ytd' => $ytdStart->format('Y').' YTD',
            'last_year' => $lastYearStart->format('M Y'),
        ];

        return response()->json([
            'labels' => $periodLabels,
            'revenue' => [
                'sales' => [
                    'current' => $revenue['current']['sales'],
                    'previous' => $revenue['previous']['sales'],
                    'ytd' => $revenue['ytd']['sales'],
                    'last_year' => $revenue['last_year']['sales'],
                ],
                'water_in_school' => [
                    'current' => $revenue['current']['water_in_school'],
                    'previous' => $revenue['previous']['water_in_school'],
                    'ytd' => $revenue['ytd']['water_in_school'],
                    'last_year' => $revenue['last_year']['water_in_school'],
                ],
                'sub_total' => [
                    'current' => $revenue['current']['sub_total'],
                    'previous' => $revenue['previous']['sub_total'],
                    'ytd' => $revenue['ytd']['sub_total'],
                    'last_year' => $revenue['last_year']['sub_total'],
                ],
            ],
            'expenses' => [
                'categories' => $expenseCategoriesList,
                'sub_total' => [
                    'current' => $expenseSubTotals['current'],
                    'previous' => $expenseSubTotals['previous'],
                    'ytd' => $expenseSubTotals['ytd'],
                    'last_year' => $expenseSubTotals['last_year'],
                ],
            ],
            'result' => [
                'current' => $revenue['current']['sub_total'] - $expenseSubTotals['current'],
                'previous' => $revenue['previous']['sub_total'] - $expenseSubTotals['previous'],
                'ytd' => $revenue['ytd']['sub_total'] - $expenseSubTotals['ytd'],
                'last_year' => $revenue['last_year']['sub_total'] - $expenseSubTotals['last_year'],
            ],
            'entrepreneur_salary' => [
                'current' => $entrepreneurSalaries['current'],
                'previous' => $entrepreneurSalaries['previous'],
                'ytd' => $entrepreneurSalaries['ytd'],
                'last_year' => $entrepreneurSalaries['last_year'],
            ],
        ]);
    }

    public function monthlyExpenseByCategory(Site $site, Request $request): JsonResponse
    {
        $sims3Site = $this->resolveSims3Site($site);

        if (! $sims3Site) {
            return response()->json(['error' => 'Site not found in Sims3 database'], 404);
        }

        $month = $this->resolveMonth($request);
        $start = $month->copy()->subMonths(11)->startOfMonth();
        $end = $month->copy()->endOfMonth();

        $categories = $this->getExpenseCategories();
        $allRefs = collect($categories)->values()->flatten()->all();

        $rows = Sims3Expense::where('Id_Site', $sims3Site->Id_Site)
            ->where('Month', '>=', $start)
            ->where('Month', '<=', $end)
            ->whereNotIn('Ref_expenses', $this->getExpensesToIgnore())
            ->whereIn('Ref_expenses', $allRefs)
            ->get(['Month', 'Ref_expenses', 'Amount_expenses']);

        $months = [];
        for ($d = $start->copy(); $d <= $end; $d->addMonth()) {
            $months[] = $d->format('Y-m');
        }

        $monthLabels = [];
        $seriesData = [];

        foreach ($categories as $cat => $refs) {
            $seriesData[$cat] = array_fill(0, count($months), 0);
        }

        foreach ($rows as $row) {
            $monthKey = Carbon::parse($row->Month)->format('Y-m');
            $monthIndex = array_search($monthKey, $months);
            if ($monthIndex === false) {
                continue;
            }

            foreach ($categories as $cat => $refs) {
                if (in_array($row->Ref_expenses, $refs)) {
                    $seriesData[$cat][$monthIndex] += (float) $row->Amount_expenses;
                    break;
                }
            }
        }

        $series = [];
        foreach ($categories as $cat => $refs) {
            $series[] = [
                'name' => $cat,
                'data' => array_map(fn ($v) => round($v), $seriesData[$cat]),
            ];
        }

        $monthLabels = array_map(fn ($m) => Carbon::parse($m.'-01')->format('M Y'), $months);

        return response()->json([
            'months' => $monthLabels,
            'series' => $series,
        ]);
    }

    public function monthlyProfitLoss(Site $site, Request $request): JsonResponse
    {
        $month = $this->resolveMonth($request);
        $start = $month->copy()->subMonths(11)->startOfMonth();
        $end = $month->copy()->endOfMonth();

        $records = FactMonthly::where('site_id', $site->id)
            ->where('month', '>=', $start)
            ->where('month', '<=', $end)
            ->orderBy('month')
            ->get(['month', 'revenue', 'expenses']);

        $months = [];
        for ($d = $start->copy(); $d <= $end; $d->addMonth()) {
            $months[] = $d->format('Y-m');
        }

        $revenueData = [];
        $expensesData = [];
        $netProfitData = [];

        $recordsByMonth = $records->keyBy(fn ($r) => Carbon::parse($r->month)->format('Y-m'));

        foreach ($months as $m) {
            $rec = $recordsByMonth->get($m);
            $rev = (float) ($rec->revenue ?? 0);
            $exp = (float) ($rec->expenses ?? 0);
            $revenueData[] = round($rev);
            $expensesData[] = round($exp);
            $netProfitData[] = round($rev - $exp);
        }

        $monthLabels = array_map(fn ($m) => Carbon::parse($m.'-01')->format('M Y'), $months);

        return response()->json([
            'months' => $monthLabels,
            'revenue' => $revenueData,
            'expenses' => $expensesData,
            'net_profit' => $netProfitData,
        ]);
    }

    public function siteProfile(Site $site): JsonResponse
    {
        $sims3Site = $this->resolveSims3Site($site);

        if (! $sims3Site) {
            return response()->json(['error' => 'Site not found in Sims3 database'], 404);
        }

        $romName = $sims3Site->Platform
            ? Sims3Platform::where('Code_Platform', $sims3Site->Platform)->value('Mail_ROM')
            : null;

        $saleDate = $sims3Site->Sale_Starting_Date
            ? Carbon::parse($sims3Site->Sale_Starting_Date)->format('M Y')
            : null;

        $startDate = $sims3Site->Date_start_working
            ? Carbon::parse($sims3Site->Date_start_working)->format('M Y')
            : null;

        $lat = $sims3Site->Latitude;
        $lng = $sims3Site->Longitude;

        return response()->json([
            'profile' => [
                'lat' => $lat ? round((float) $lat, 4) : null,
                'lng' => $lng ? round((float) $lng, 4) : null,
                'entrepreneur' => $sims3Site->Entrepreneur_English_Name,
                'advisor' => $sims3Site->Advisor,
                'rom' => $romName,
                'technician' => $sims3Site->technician_site,
                'installation_date' => $saleDate,
                'start_working_date' => $startDate,
                'phone' => $sims3Site->Phone_Number,
                'education' => $sims3Site->Education,
                'previous_job' => $sims3Site->Previous_Job,
            ],
            'location' => [
                'village' => [
                    'en' => $sims3Site->Village,
                    'km' => $sims3Site->Village_khmer,
                ],
                'commune' => [
                    'en' => $sims3Site->Commune,
                    'km' => $sims3Site->Commune_khmer,
                ],
                'district' => [
                    'en' => $sims3Site->District,
                    'km' => $sims3Site->District_khmer,
                ],
                'province' => [
                    'en' => $sims3Site->Province,
                    'km' => $sims3Site->Province_khmer,
                ],
            ],
            'demographics' => [
                'villages_in_commune' => $sims3Site->Number_Village ? (int) $sims3Site->Number_Village : null,
                'families' => $sims3Site->Number_Family ? (int) $sims3Site->Number_Family : (int) ($sims3Site->Family ?? null),
                'households' => $sims3Site->Households ? (int) $sims3Site->Households : null,
                'population' => $sims3Site->Number_Population ? (int) $sims3Site->Number_Population : (int) ($sims3Site->Population ?? null),
            ],
        ]);
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

        $bottlesPerDayKpi = Kpi::where('col_name', 'bottles_per_day')->first();
        $objectiveData = [];
        if ($bottlesPerDayKpi) {
            $currentMonth = now()->startOfMonth();
            /** @var Objective|null $matchingObjective */
            $matchingObjective = $bottlesPerDayKpi->objectives()
                ->where('start_date', '<=', $currentMonth)
                ->where(fn ($q) => $q->whereNull('end_date')->orWhere('end_date', '>=', $currentMonth))
                ->orderByRaw("CASE WHEN type = 'individual' THEN 0 ELSE 1 END")
                ->first();
            $objectiveValue = $matchingObjective ? (int) $matchingObjective->value : null;
            $objectiveData = array_fill(0, 12, $objectiveValue);
        }
        $series[] = ['name' => 'Objectives', 'data' => $objectiveData];

        return response()->json([
            'categories' => $monthLabels,
            'series' => $series,
        ]);
    }

    public function salesComparison(Site $site): JsonResponse
    {
        $sims3Site = $this->resolveSims3Site($site);

        if (! $sims3Site) {
            return response()->json(['error' => 'Site not found in Sims3 database'], 404);
        }

        $platformName = $sims3Site->Platform;
        $localPlatform = $platformName
            ? Platform::where('name', $platformName)->first()
            : null;

        $startDate = now()->subMonths(11)->startOfMonth();
        $months = [];
        for ($i = 0; $i < 12; $i++) {
            $months[] = $startDate->copy()->addMonths($i);
        }

        $records = FactMonthly::where('month', '>=', $startDate)
            ->whereNotNull('sales_volume')
            ->get(['site_id', 'platform_id', 'month', 'sales_volume']);

        $recordsByMonth = $records->groupBy(fn ($r) => Carbon::parse($r->month)->format('Y-m'));

        $salesVolumeKpi = Kpi::where('col_name', 'sales_volume')->first();

        $categories = [];
        $siteData = [];
        $platformData = [];
        $networkData = [];
        $objectiveData = [];

        foreach ($months as $month) {
            $monthKey = $month->format('Y-m');
            $categories[] = $month->format('M Y');

            $monthRecs = $recordsByMonth->get($monthKey, collect());

            $siteRec = $monthRecs->firstWhere('site_id', $site->id);
            $siteData[] = $siteRec ? round($siteRec->sales_volume) : null;

            if ($localPlatform) {
                $platRecs = $monthRecs->where('platform_id', $localPlatform->id);
                $platformData[] = $platRecs->isNotEmpty() ? round($platRecs->avg('sales_volume')) : null;
            } else {
                $platformData[] = null;
            }

            $networkData[] = $monthRecs->isNotEmpty() ? round($monthRecs->avg('sales_volume')) : null;

            $objectiveValue = null;
            if ($salesVolumeKpi) {
                /** @var Objective|null $matchingObjective */
                $matchingObjective = $salesVolumeKpi->objectives()
                    ->where('start_date', '<=', $month)
                    ->where(fn ($q) => $q->whereNull('end_date')->orWhere('end_date', '>=', $month))
                    ->orderByRaw("CASE WHEN type = 'individual' THEN 0 ELSE 1 END")
                    ->first();
                if ($matchingObjective) {
                    $objectiveValue = (int) $matchingObjective->value;
                }
            }
            $objectiveData[] = $objectiveValue;
        }

        return response()->json([
            'categories' => $categories,
            'series' => [
                ['name' => 'This Kiosk', 'data' => $siteData],
                ['name' => 'Platform Avg', 'data' => $platformData],
                ['name' => 'Network Avg', 'data' => $networkData],
                ['name' => 'Objective', 'data' => $objectiveData],
            ],
        ]);
    }

    public function dailySales(Site $site, Request $request): JsonResponse
    {
        $sims3Site = $this->resolveSims3Site($site);

        if (! $sims3Site) {
            return response()->json(['error' => 'Site not found in Sims3 database'], 404);
        }

        $month = $this->resolveMonth($request);

        $sales = $this->dailySalesProvider->getDailySales($sims3Site->Id_Site, $month);

        $monthlySale = $this->resolveSale($sims3Site, $month);

        $channelKeys = ['Free_Sales', 'Hod_Sales', 'WiS_Sales', 'Onsite_Sales', 'Shopkeeper_Sales', 'Bottle_Sales'];

        $prices = ['Free_Price' => 0];
        $income = ['Free_Income' => 0];
        $totals = [];

        if ($monthlySale) {
            $priceMap = [
                'Hod_Sales' => 'Hod_Price', 'Shopkeeper_Sales' => 'Shopkeeper_Price',
                'WiS_Sales' => 'WiS_Price', 'Onsite_Sales' => 'Onsite_Price',
                'Bottle_Sales' => 'Bottle_Price', 'Emergency_Sales' => 'Emergency_Price',
            ];
            $incomeMap = [
                'Hod_Sales' => 'Hod_Income', 'Shopkeeper_Sales' => 'Shopkeeper_Income',
                'WiS_Sales' => 'WiS_Income', 'Onsite_Sales' => 'Onsite_Income',
                'Bottle_Sales' => 'Bottle_Income', 'Emergency_Sales' => 'Emergency_Income',
            ];

            foreach ($priceMap as $salesCol => $priceCol) {
                $prices[$priceCol] = round((float) ($monthlySale->{$priceCol} ?? 0));
            }
            foreach ($incomeMap as $salesCol => $incomeCol) {
                $income[$incomeCol] = round((float) ($monthlySale->{$incomeCol} ?? 0));
            }

            $totalSales = (float) $monthlySale->Total_Sales;
            $totalIncome = (float) $monthlySale->Total_Income;
            $knownSales = collect($channelKeys)->sum(fn ($c) => (float) ($monthlySale->{$c} ?? 0))
                + (float) ($monthlySale->Emergency_Sales ?? 0);
            $knownIncomeSum = collect($incomeMap)->sum(fn ($ic) => (float) ($monthlySale->{$ic} ?? 0));
            $otherSales = max(0, $totalSales - $knownSales);
            $otherIncome = max(0, $totalIncome - $knownIncomeSum);

            $prices['Other_Price'] = $otherSales > 0 ? round($otherIncome / $otherSales) : 0;
            $income['Other_Income'] = round($otherIncome);
            $income['Total_Income'] = round($totalIncome);

            $totals = [
                'Free_Sales' => (float) ($monthlySale->Free_Sales ?? 0),
                'Hod_Sales' => (float) ($monthlySale->Hod_Sales ?? 0),
                'WiS_Sales' => (float) ($monthlySale->WiS_Sales ?? 0),
                'Onsite_Sales' => (float) ($monthlySale->Onsite_Sales ?? 0),
                'Shopkeeper_Sales' => (float) ($monthlySale->Shopkeeper_Sales ?? 0),
                'Bottle_Sales' => (float) ($monthlySale->Bottle_Sales ?? 0),
                'Emergency_Sales' => (float) ($monthlySale->Emergency_Sales ?? 0),
                'Other_Sales' => round($otherSales),
                'Total_Sales' => round($totalSales),
            ];
        }

        return response()->json([
            'sales' => $sales,
            'totals' => $totals,
            'prices' => $prices,
            'income' => $income,
        ]);
    }

    public function waterLossByWeek(Site $site, Request $request): JsonResponse
    {
        $sims3Site = $this->resolveSims3Site($site);

        if (! $sims3Site) {
            return response()->json(['error' => 'Site not found in Sims3 database'], 404);
        }

        $month = $this->resolveMonth($request);
        $monthStart = $month->copy()->startOfMonth();
        $monthEnd = $month->copy()->endOfMonth();

        $queryStart = $monthStart->copy()->subDays(30);
        $queryEnd = $monthEnd->copy()->addDays(30);

        $meters = WaterMeter::where('site', $sims3Site->Id_Site)
            ->whereBetween('date', [$queryStart, $queryEnd])
            ->orderBy('date')
            ->get();

        $dayTotals = $this->dailySalesProvider->getDayTotals($sims3Site->Id_Site, $month);

        $weeks = [];
        $weekNum = 0;

        for ($i = 0; $i < $meters->count() - 1; $i++) {
            $startMeter = $meters[$i];
            $endMeter = $meters[$i + 1];

            $startDate = Carbon::parse($startMeter->date);
            $endDate = Carbon::parse($endMeter->date);

            if ($endDate < $monthStart || $startDate > $monthEnd) {
                continue;
            }

            $weekNum++;

            $startValue = (float) $startMeter->value;
            $endValue = (float) $endMeter->value;

            $consumed = null;
            if ($endValue > $startValue) {
                $consumed = round(($endValue - $startValue) * 1000, 2);
            }

            $totalBottles = 0;
            $cursor = $startDate->copy();
            while ($cursor < $endDate) {
                $key = $cursor->format('Y-m-d');
                $totalBottles += (float) ($dayTotals[$key] ?? 0);
                $cursor->addDay();
            }

            $waterSold = round($totalBottles * 20, 2);

            $waterLoss = null;
            $waterLossPct = null;
            if ($consumed !== null && $consumed > 0) {
                $waterLoss = round($consumed - $waterSold, 2);
                $waterLossPct = round(($waterLoss / $consumed) * 100, 2);
            }

            $weeks[] = [
                'week' => $weekNum,
                'meter_start' => $startValue,
                'meter_end' => $endValue,
                'consumed' => $consumed,
                'sold' => $waterSold,
                'loss' => $waterLoss,
                'loss_pct' => $waterLossPct,
            ];
        }

        return response()->json(['weeks' => $weeks]);
    }

    public function pnlExpenses(Site $site, Request $request): JsonResponse
    {
        $sims3Site = $this->resolveSims3Site($site);

        if (! $sims3Site) {
            return response()->json(['error' => 'Site not found in Sims3 database'], 404);
        }

        $month = $this->resolveMonth($request);
        $categories = $this->getExpenseCategories();
        $labels = $this->getExpenseLabels();

        $rows = Sims3Expense::where('Id_Site', $sims3Site->Id_Site)
            ->whereYear('Month', $month->year)
            ->whereMonth('Month', $month->month)
            ->whereNotIn('Ref_expenses', $this->getExpensesToIgnore())
            ->whereIn('Ref_expenses', collect($categories)->values()->flatten()->all())
            ->get(['Ref_expenses', 'Amount_expenses']);

        $result = [];
        $grandTotal = 0;

        foreach ($categories as $cat => $refs) {
            $catRows = $rows->filter(fn ($r) => in_array($r->Ref_expenses, $refs));
            $catTotal = 0;
            $items = [];

            foreach ($refs as $ref) {
                $amount = (float) ($catRows->firstWhere('Ref_expenses', $ref)->Amount_expenses ?? 0);
                if ($amount > 0) {
                    $items[] = [
                        'ref' => $ref,
                        'label' => $labels[$ref] ?? $ref,
                        'amount' => round($amount),
                    ];
                    $catTotal += $amount;
                }
            }

            $catTotal = round($catTotal);

            if ($catTotal > 0 || count($items) > 0) {
                $result[] = [
                    'category' => $cat,
                    'sub_total' => $catTotal,
                    'items' => $items,
                ];
            }

            $grandTotal += $catTotal;
        }

        return response()->json([
            'categories' => $result,
            'grand_total' => round($grandTotal),
        ]);
    }

    private function getExpenseCategories(): array
    {
        return [
            'Production' => ['consumable_production', 'stock_ts', 'bottle_invoice', 'electricity', 'gasoline_waterpump', 'raw_water'],
            'Salary' => ['fix_salary_entrepreneurs', 'variable_salary_entrepreneurs', 'fix_salary_operators', 'variable_salary_operators'],
            'Delivery' => ['maintenance_delivery', 'gasoline_delivery'],
            'Contribution' => ['commune_contribution', 'entrepreneur_contribution'],
            'Intervention' => ['technical intervention', 'water quality alert'],
            'Investment' => ['investment'],
        ];
    }

    private function getExpensesToIgnore(): array
    {
        return ['WinS_invoice', 'debt', 'withdrawal', 'adjustment'];
    }

    private function getExpenseLabels(): array
    {
        return [
            'consumable_production' => 'Consumable Production',
            'stock_ts' => 'Stock TS',
            'bottle_invoice' => 'Bottle Invoice',
            'electricity' => 'Electricity',
            'gasoline_waterpump' => 'Gasoline (Water Pump)',
            'raw_water' => 'Raw Water',
            'fix_salary_entrepreneurs' => 'Fix Salary (Entrepreneur)',
            'variable_salary_entrepreneurs' => 'Variable Salary (Entrepreneur)',
            'fix_salary_operators' => 'Fix Salary (Operators)',
            'variable_salary_operators' => 'Variable Salary (Operators)',
            'maintenance_delivery' => 'Maintenance (Delivery)',
            'gasoline_delivery' => 'Gasoline (Delivery)',
            'commune_contribution' => 'Commune Contribution',
            'entrepreneur_contribution' => 'Entrepreneur Contribution',
            'technical intervention' => 'Technical Intervention',
            'water quality alert' => 'Water Quality Alert',
            'investment' => 'Investment',
        ];
    }

    private function resolveMonth(Request $request): Carbon
    {
        return Carbon::parse($request->query('month', now()->format('Y-m')).'-01');
    }

    private function resolveSims3Site(Site $site): ?Sims3Site
    {
        return Sims3Site::where('Id_Site', $site->name)->first();
    }

    private function resolveSale(Sims3Site $sims3Site, Carbon $month): ?Sims3Sale
    {
        return Sims3Sale::where('Id_Site', $sims3Site->Id_Site)
            ->whereYear('Month', $month->year)
            ->whereMonth('Month', $month->month)
            ->first();
    }

    private function getRevenueForPeriod(Sims3Site $sims3Site, Carbon $start, Carbon $end): array
    {
        $query = Sims3Sale::where('Id_Site', $sims3Site->Id_Site)
            ->where('Month', '>=', $start)
            ->where('Month', '<=', $end);

        $totalIncome = (float) $query->sum('Total_Income');
        $wisIncome = (float) $query->sum('WiS_Income');

        return [
            'sales' => round($totalIncome - $wisIncome),
            'water_in_school' => round($wisIncome),
            'sub_total' => round($totalIncome),
        ];
    }

    private function getExpensesForPeriod(Sims3Site $sims3Site, Carbon $start, Carbon $end): array
    {
        $categories = $this->getExpenseCategories();
        $allRefs = collect($categories)->values()->flatten()->all();

        $rows = Sims3Expense::where('Id_Site', $sims3Site->Id_Site)
            ->where('Month', '>=', $start)
            ->where('Month', '<=', $end)
            ->whereNotIn('Ref_expenses', $this->getExpensesToIgnore())
            ->whereIn('Ref_expenses', $allRefs)
            ->get(['Ref_expenses', 'Amount_expenses']);

        $categoryAmounts = [];
        foreach ($categories as $cat => $refs) {
            $categoryAmounts[$cat] = round($rows->filter(fn ($r) => in_array($r->Ref_expenses, $refs))->sum('Amount_expenses'));
        }

        $entrepreneurSalaryRefs = ['fix_salary_entrepreneurs', 'variable_salary_entrepreneurs'];
        $entrepreneurSalary = round($rows->filter(fn ($r) => in_array($r->Ref_expenses, $entrepreneurSalaryRefs))->sum('Amount_expenses'));

        return [
            'categoryAmounts' => $categoryAmounts,
            'sub_total' => round($rows->sum('Amount_expenses')),
            'entrepreneur_salary' => $entrepreneurSalary,
        ];
    }
}
