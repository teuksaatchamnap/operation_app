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
        return response()->json(Site::all());
    }
}
