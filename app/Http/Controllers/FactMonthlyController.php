<?php

namespace App\Http\Controllers;

use App\Models\FactMonthly;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;

class FactMonthlyController extends Controller
{
    /**
     * Get fact monthly data with optional filters, column selection, and aggregation.
     *
     * @authenticated
     *
     * @queryParam month string Optional. Filter by month in YYYY-MM format. Example: 2025-01
     * @queryParam year int Optional. Filter by year (4 digits). Example: 2025
     * @queryParam platform_ids int[] Optional. Filter by platform IDs (array). Example: [1, 2, 3]
     * @queryParam advisor_ids int[] Optional. Filter by advisor IDs (array). Example: [1, 2]
     * @queryParam site_ids int[] Optional. Filter by site IDs (array). Example: [5, 6]
     * @queryParam kpis string required. Single KPI column name.
     *   Available: tier, sales_volume, days_open, active, super_tier_1, bottles_per_day, expenses, revenue, workers, consumers, who_compliance, profitable, water_loss, is_water_loss_ok, data_collection, water_source.
     *   Example: revenue
     * @queryParam aggregate string Optional. Aggregate function to apply to KPI column. Options: sum, avg, count, pct_active.
     *   pct_active returns SUM(kpi) / NULLIF(SUM(active), 0) * 100 (percentage of active sites).
     *   When provided, returns a single aggregated result instead of multiple rows.
     *   Required when using latest_available.
     * @queryParam year_to_date bool Optional. When true, aggregates values from January 1 to the selected month
     *   (or full year if only year is given). Requires the month or year parameter.
     *   Without the aggregate parameter, groups results by site_id, platform_id, advisor_id and sums the KPI column.
     *   Mutually exclusive with latest_available.
     * @queryParam latest_available bool Optional. When true, for each site finds the latest month in the selected year
     *   where the KPI is not null, then aggregates across sites. Ignores the month filter (falls back to year).
     *   Requires aggregate and at least month or year. Mutually exclusive with year_to_date.
     *
     * @response [
     *   {"id": 1, "month": "2025-01-01", "site_id": 5, "platform_id": 3, "advisor_id": 1, "revenue": 15000},
     *   {"id": 2, "month": "2025-02-01", "site_id": 6, "platform_id": 3, "advisor_id": 1, "revenue": 18000}
     * ]
     */
    public function index(Request $request): JsonResponse
    {
        $validated = $request->validate([
            'month' => 'sometimes|date_format:Y-m',
            'year' => 'sometimes|integer|digits:4',
            'platform_ids' => 'sometimes|array',
            'platform_ids.*' => 'integer',
            'advisor_ids' => 'sometimes|array',
            'advisor_ids.*' => 'integer',
            'site_ids' => 'sometimes|array',
            'site_ids.*' => 'integer',
            'kpis' => 'required|string',
            'aggregate' => 'sometimes|string|in:sum,avg,count,pct_active',
            'year_to_date' => 'sometimes|boolean',
            'latest_available' => 'sometimes|boolean',
        ]);

        $yearToDate = $request->boolean('year_to_date');
        $latestAvailable = $request->boolean('latest_available');
        $kpi = $validated['kpis'];

        if ($yearToDate && $latestAvailable) {
            return response()->json(['error' => 'year_to_date and latest_available cannot be used together.'], 422);
        }

        if ($latestAvailable && ! $request->filled('aggregate')) {
            return response()->json(['error' => 'The latest_available parameter requires aggregate.'], 422);
        }

        if (($yearToDate || $latestAvailable) && ! $request->filled('month') && ! $request->filled('year')) {
            return response()->json(['error' => 'This parameter requires at least month or year.'], 422);
        }

        $query = FactMonthly::query();

        if ($latestAvailable) {
            $year = $request->filled('month')
                ? substr($validated['month'], 0, 4)
                : $validated['year'];

            $baseQuery = FactMonthly::query()
                ->whereYear('month', '=', $year)
                ->where('active', 1)
                ->whereNotNull($kpi);

            if ($request->filled('site_ids')) {
                $baseQuery->whereIn('site_id', $validated['site_ids']);
            }
            if ($request->filled('platform_ids')) {
                $baseQuery->whereIn('platform_id', $validated['platform_ids']);
            }
            if ($request->filled('advisor_ids')) {
                $baseQuery->whereIn('advisor_id', $validated['advisor_ids']);
            }

            $latestSubquery = $baseQuery
                ->select('site_id', DB::raw('MAX(month) as latest_month'))
                ->groupBy('site_id')
                ->toSql();

            $bindings = $baseQuery->getBindings();

            $aggregateFunc = $validated['aggregate'];

            $rawExpr = $aggregateFunc === 'pct_active'
                ? "SUM(fm.{$kpi}) / NULLIF(SUM(fm.active), 0) * 100"
                : "{$aggregateFunc}(fm.{$kpi})";

            $result = FactMonthly::query()
                ->from(DB::raw("({$latestSubquery}) as latest"))
                ->join('fact_monthly as fm', function ($join) {
                    $join->on('fm.site_id', '=', 'latest.site_id')
                        ->on('fm.month', '=', 'latest.latest_month');
                })
                ->selectRaw("{$rawExpr} as {$kpi}")
                ->setBindings($bindings)
                ->first();

            if (isset($result->$kpi)) {
                $result->$kpi = (float) $result->$kpi;
            }

            return response()->json([$result]);
        }

        if ($yearToDate) {
            if ($request->filled('month')) {
                $year = substr($validated['month'], 0, 4);
                $endMonth = (int) substr($validated['month'], 5, 2);
                $query->whereYear('month', '=', $year)
                    ->whereMonth('month', '<=', $endMonth);
            } elseif ($request->filled('year')) {
                $query->whereYear('month', '=', $validated['year']);
            }
        } else {
            if ($request->filled('month')) {
                $query->whereMonth('month', '=', substr($validated['month'], 5, 2))
                    ->whereYear('month', '=', substr($validated['month'], 0, 4));
            }

            if ($request->filled('year')) {
                $query->whereYear('month', '=', $validated['year']);
            }
        }

        if ($request->filled('platform_ids')) {
            $query->whereIn('platform_id', $validated['platform_ids']);
        }

        if ($request->filled('advisor_ids')) {
            $query->whereIn('advisor_id', $validated['advisor_ids']);
        }

        if ($request->filled('site_ids')) {
            $query->whereIn('site_id', $validated['site_ids']);
        }

        if ($request->filled('aggregate')) {
            $aggregateFunc = $validated['aggregate'];

            if ($aggregateFunc === 'pct_active') {
                $query->where('active', 1);
            }

            $rawExpr = $aggregateFunc === 'pct_active'
                ? "SUM({$kpi}) / NULLIF(SUM(active), 0) * 100"
                : "{$aggregateFunc}({$kpi})";

            $query->selectRaw("{$rawExpr} as {$kpi}");
            $result = $query->first();

            if (isset($result->$kpi)) {
                $result->$kpi = (float) $result->$kpi;
            }

            return response()->json([$result]);
        }

        if ($yearToDate) {
            $query->selectRaw('site_id, platform_id, advisor_id, SUM('.$kpi.') as '.$kpi)
                ->groupBy('site_id', 'platform_id', 'advisor_id');

            return response()->json($query->get());
        }

        $baseColumns = ['id', 'month', 'site_id', 'platform_id', 'advisor_id'];
        $columns = array_values(array_unique(array_merge($baseColumns, [$kpi])));
        $query->select($columns);

        return response()->json($query->get());
    }
}
