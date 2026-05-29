<?php

namespace App\Http\Controllers;

use App\Models\Kpi;
use App\Models\Objective;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;

class ObjectiveController extends Controller
{
    /**
     * List all objectives.
     *
     * @authenticated
     *
     * @response [{"id": 1, "kpi_id": 1, "start_date": "2026-01-01", "end_date": "2026-12-31", "value": "100.00", "type": "global"}]
     */
    public function index(): JsonResponse
    {
        return response()->json(Objective::all());
    }

    /**
     * Create a new objective for a KPI.
     *
     * @authenticated
     *
     * @response status=201 {"id": 1, "kpi_id": 1, "start_date": "2026-01-01", "end_date": "2026-12-31", "value": "100.00", "type": "global"}
     * @response status=404 {"message": "No query results for model [App\\Models\\Kpi] 1"}
     * @response status=422 {"message": "The start date field is required.", "errors": {"start_date": ["The start date field is required."]}}
     */
    public function store(Request $request, int $kpiId): JsonResponse
    {
        Kpi::findOrFail($kpiId);

        $validated = $request->validate([
            'start_date' => 'required|date',
            'end_date' => 'required|date|after:start_date',
            'value' => 'required|numeric',
            'type' => 'required|in:individual,global',
        ]);

        $objective = Objective::create(array_merge(['kpi_id' => $kpiId], $validated));

        return response()->json($objective, 201);
    }

    /**
     * Update an existing objective.
     *
     * @authenticated
     *
     * @response {"id": 1, "kpi_id": 1, "start_date": "2026-01-01", "end_date": "2026-12-31", "value": "150.00", "type": "global"}
     * @response status=404 {"message": "No query results for model [App\\Models\\Kpi] 1"}
     * @response status=422 {"message": "The value field is required.", "errors": {"value": ["The value field is required."]}}
     */
    public function update(Request $request, int $kpiId, int $id): JsonResponse
    {
        Kpi::findOrFail($kpiId);

        $objective = Objective::where('kpi_id', $kpiId)->findOrFail($id);

        $validated = $request->validate([
            'start_date' => 'sometimes|required|date',
            'end_date' => 'sometimes|required|date|after:start_date',
            'value' => 'sometimes|required|numeric',
            'type' => 'sometimes|required|in:individual,global',
        ]);

        $objective->update($validated);

        return response()->json($objective);
    }

    /**
     * Delete an objective.
     *
     * @authenticated
     *
     * @response status=204
     * @response status=404 {"message": "No query results for model [App\\Models\\Kpi] 1"}
     */
    public function destroy(int $kpiId, int $id): JsonResponse
    {
        Kpi::findOrFail($kpiId);

        $objective = Objective::where('kpi_id', $kpiId)->findOrFail($id);
        $objective->delete();

        return response()->json(null, 204);
    }
}
