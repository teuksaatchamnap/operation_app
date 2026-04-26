<?php

namespace App\Http\Controllers;

use App\Models\Kpi;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;

class KpiController extends Controller
{
    public function index(Request $request): JsonResponse
    {
        return response()->json(Kpi::all());
    }

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

    public function show(int $id): JsonResponse
    {
        return response()->json(Kpi::findOrFail($id));
    }

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

    public function destroy(int $id): JsonResponse
    {
        $kpi = Kpi::findOrFail($id);
        $kpi->delete();

        return response()->json(null, 204);
    }
}
