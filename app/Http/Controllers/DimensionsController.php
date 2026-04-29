<?php

namespace App\Http\Controllers;

use App\Models\Advisor;
use App\Models\Platform;
use App\Models\Site;
use Illuminate\Http\JsonResponse;

class DimensionsController extends Controller
{
    /**
     * Get all advisors.
     *
     * @return JsonResponse
     */
    public function getAdvisors(): JsonResponse
    {
        return response()->json(Advisor::all());
    }

    /**
     * Get all platforms.
     *
     * @return JsonResponse
     */
    public function getPlatforms(): JsonResponse
    {
        return response()->json(Platform::all());
    }

    /**
     * Get all sites.
     *
     * @return JsonResponse
     */
    public function getSites(): JsonResponse
    {
        return response()->json(Site::all());
    }
}
