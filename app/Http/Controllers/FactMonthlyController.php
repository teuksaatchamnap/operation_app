<?php

namespace App\Http\Controllers;

use App\Models\FactMonthly;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;

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
     * @queryParam kpis string required. Comma-separated list of KPI columns.
     *   Available: tier, sales_volume, days_open, expenses, revenue, workers, consumers, who_compliance, profitable.
     *   Example: revenue,sales_volume,consumers
     * @queryParam aggregate string Optional. Aggregate function to apply to KPI columns. Options: sum, avg.
     *   When provided, returns a single aggregated result instead of multiple rows.
     * @queryParam year_to_date bool Optional. When true, aggregates values from January 1 to the selected month
     *   (or full year if only year is given). Requires the month or year parameter.
     *   Without the aggregate parameter, groups results by site_id, platform_id, advisor_id and sums each KPI column.
     *
     * @response [
     *   {"id": 1, "month": "2025-01-01", "site_id": 5, "platform_id": 3, "advisor_id": 1, "revenue": 15000, "sales_volume": 200},
     *   {"id": 2, "month": "2025-02-01", "site_id": 5, "platform_id": 3, "advisor_id": 1, "revenue": 18000, "sales_volume": 250}
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
            'aggregate' => 'sometimes|string|in:sum,avg',
            'year_to_date' => 'sometimes|boolean',
        ]);

        $yearToDate = $request->boolean('year_to_date');

        if ($yearToDate && ! $request->filled('month') && ! $request->filled('year')) {
            return response()->json(['error' => 'The year_to_date parameter requires at least month or year.'], 422);
        }

        $query = FactMonthly::query();

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

        $kpiColumns = explode(',', $validated['kpis']);

        if ($request->filled('aggregate')) {
            $aggregateFunc = $validated['aggregate'];

            $selectColumns = [];
            foreach ($kpiColumns as $col) {
                $selectColumns[] = "{$aggregateFunc}({$col}) as {$col}";
            }

            $query->selectRaw(implode(', ', $selectColumns));
            $result = $query->first();

            foreach ($kpiColumns as $col) {
                if (isset($result->$col)) {
                    $result->$col = (float) $result->$col;
                }
            }
            return response()->json([$result]);
        }

        $baseColumns = ['id', 'month', 'site_id', 'platform_id', 'advisor_id'];
        $columns = array_values(array_unique(array_merge($baseColumns, $kpiColumns)));
        $query->select($columns);

        return response()->json($query->get());
    }
}
