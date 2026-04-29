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
     * @queryParam kpis string Optional. Comma-separated list of columns to include in the response.
     *   Always includes: id, month, site_id, platform_id, advisor_id.
     *   Available: tier, sales_volume, days_open, expenses, revenue, workers, consumers, who_compliance, profitable.
     *   Example: revenue,sales_volume,consumers
     * @queryParam aggregate string Optional. Aggregate function to apply to KPI columns. Options: sum, avg.
     *   When provided, returns a single aggregated result instead of multiple rows.
     *
     * @response [
     *   {"id": 1, "month": "2025-01-01", "site_id": 5, "platform_id": 3, "advisor_id": 1, "revenue": 15000, "sales_volume": 200},
     *   {"id": 2, "month": "2025-02-01", "site_id": 5, "platform_id": 3, "advisor_id": 1, "revenue": 18000, "sales_volume": 250}
     * ]
     *
     * @return JsonResponse
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
            'kpis' => 'sometimes|string',
            'aggregate' => 'sometimes|string|in:sum,avg',
        ]);

        $query = FactMonthly::query();

        if ($request->filled('month')) {
            $query->whereMonth('month', '=', substr($validated['month'], 5, 2))
                ->whereYear('month', '=', substr($validated['month'], 0, 4));
        }

        if ($request->filled('year')) {
            $query->whereYear('month', '=', $validated['year']);
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

        $baseColumns = ['id', 'month', 'site_id', 'platform_id', 'advisor_id'];

        // Handle aggregation
        if ($request->filled('aggregate') && $request->filled('kpis')) {
            $kpiColumns = explode(',', $validated['kpis']);
            $aggregateFunc = $validated['aggregate'];

            $selectColumns = [];
            foreach ($kpiColumns as $col) {
                $selectColumns[] = "{$aggregateFunc}({$col}) as {$col}";
            }

            $query->selectRaw(implode(', ', $selectColumns));
            $result = $query->first();

            // Cast aggregated values to proper numeric types
            foreach ($kpiColumns as $col) {
                if (isset($result->$col)) {
                    $result->$col = (float) $result->$col;
                }
            }

            return response()->json([$result]);
        }

        if ($request->filled('kpis')) {
            $kpiColumns = explode(',', $validated['kpis']);
            $columns = array_values(array_unique(array_merge($baseColumns, $kpiColumns)));
            $query->select($columns);
        }

        return response()->json($query->get());
    }
}
