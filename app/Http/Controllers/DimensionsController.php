<?php

namespace App\Http\Controllers;

use App\Models\Advisor;
use App\Models\Platform;
use App\Models\Site;
use Illuminate\Http\JsonResponse;

class DimensionsController extends Controller
{
    public function getAdvisors(): JsonResponse
    {
        return response()->json(Advisor::all());
    }

    public function getPlatforms(): JsonResponse
    {
        return response()->json(Platform::all());
    }

    public function getSites(): JsonResponse
    {
        $excludedNames = collect(range(1, 20))->map(fn (int $n) => "A{$n}");

        $sites = Site::whereHas('factMonthlies', fn ($query) => $query->whereNotNull('platform_id'))
            ->whereNotIn('name', $excludedNames)
            ->get();

        return response()->json($sites);
    }
}
