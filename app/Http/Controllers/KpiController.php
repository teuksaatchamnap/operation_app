<?php

namespace App\Http\Controllers;

use App\Models\Kpi;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;

class KpiController extends Controller
{
    /**
     * List all KPIs.
     *
     * @response [
     *     {"id": 1, "name": "Revenue", "col_name": "revenue", "unit": "$", "periodicity": "monthly", "type": "currency"}
     * ]
     */
    public function index(Request $request): JsonResponse
    {
        return response()->json(Kpi::all());
    }

    /**
     * Create a new KPI.
     *
     * @response status=201 [
     *     {"id": 1, "name": "Revenue", "col_name": "revenue", "unit": "$", "periodicity": "monthly", "type": "currency"}
     * ]
     * @response status=422 {"message": "The name field is required.", "errors": {"name": ["The name field is required."]}}
     */
    public function store(Request $request): JsonResponse
    {
        $validated = $request->validate([
            'name' => 'required|string',
            'col_name' => 'required|string',
            'unit' => 'required|string',
            'periodicity' => 'required|string',
            'type' => 'required|string',
        ]);

        $kpi = Kpi::create($validated);

        return response()->json($kpi, 201);
    }

    /**
     * Get a single KPI by ID.
     *
     * @response {"id": 1, "name": "Revenue", "col_name": "revenue", "unit": "$", "periodicity": "monthly", "type": "currency"}
     * @response status=404 {"message": "No query results for model [App\\Models\\Kpi] 1"}
     */
    public function show(int $id): JsonResponse
    {
        return response()->json(Kpi::findOrFail($id));
    }

    /**
     * Update an existing KPI.
     *
     * @response {"id": 1, "name": "Updated Revenue", "col_name": "revenue", "unit": "$", "periodicity": "monthly", "type": "currency"}
     * @response status=404 {"message": "No query results for model [App\\Models\\Kpi] 1"}
     * @response status=422 {"message": "The name field is required.", "errors": {"name": ["The name field is required."]}}
     */
    public function update(Request $request, int $id): JsonResponse
    {
        $kpi = Kpi::findOrFail($id);

        $validated = $request->validate([
            'name' => 'sometimes|required|string',
            'col_name' => 'sometimes|required|string',
            'unit' => 'sometimes|required|string',
            'periodicity' => 'sometimes|required|string',
            'type' => 'sometimes|required|string',
        ]);

        $kpi->update($validated);

        return response()->json($kpi);
    }

    /**
     * Delete a KPI.
     *
     * @response status=204
     * @response status=404 {"message": "No query results for model [App\\Models\\Kpi] 1"}
     */
    public function destroy(int $id): JsonResponse
    {
        $kpi = Kpi::findOrFail($id);
        $kpi->delete();

        return response()->json(null, 204);
    }
}
