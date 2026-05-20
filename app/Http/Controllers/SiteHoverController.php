<?php

namespace App\Http\Controllers;

use App\Models\Advisor;
use App\Models\FactMonthly;
use App\Models\Platform;
use App\Models\Sims3\Site as Sims3Site;
use App\Models\Site;
use Carbon\Carbon;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;

class SiteHoverController extends Controller
{
    public function index(Request $request): JsonResponse
    {
        $validated = $request->validate([
            'month' => 'required|date_format:Y-m',
            'site_ids' => 'sometimes|array',
            'site_ids.*' => 'integer',
            'platform_ids' => 'sometimes|array',
            'platform_ids.*' => 'integer',
            'advisor_ids' => 'sometimes|array',
            'advisor_ids.*' => 'integer',
            'include_unassigned' => 'sometimes|boolean',
        ]);

        $month = $validated['month'];

        $factQuery = FactMonthly::whereYear('month', '=', substr($month, 0, 4))
            ->whereMonth('month', '=', substr($month, 5, 2));

        if (! $request->boolean('include_unassigned')) {
            $factQuery->whereNotNull('platform_id');
        }

        if ($request->filled('site_ids')) {
            $factQuery->whereIn('site_id', $validated['site_ids']);
        }
        if ($request->filled('platform_ids')) {
            $factQuery->whereIn('platform_id', $validated['platform_ids']);
        }
        if ($request->filled('advisor_ids')) {
            $factQuery->whereIn('advisor_id', $validated['advisor_ids']);
        }

        $factRows = $factQuery->get()->keyBy('site_id');

        $sims3Sites = Sims3Site::all()->keyBy('Id_Site');

        $localSites = Site::all()->keyBy('id');

        $platformMap = Platform::all()->keyBy('id');
        $advisorMap = Advisor::all()->keyBy('id');

        $result = [];

        foreach ($localSites as $site) {
            $fact = $factRows->get($site->id);
            $s3 = $sims3Sites->get($site->name);

            $tier = $fact?->tier;
            if ($tier === null && $s3 !== null) {
                $tier = $s3->Last_Tier;
            }

            $platform = $s3?->Platform;
            if ($platform === null && $fact !== null) {
                $platform = $platformMap->get($fact->platform_id)?->name;
            }

            $advisor = $s3?->Advisor;
            if ($advisor === null && $fact !== null) {
                $advisor = $advisorMap->get($fact->advisor_id)?->name;
            }

            $yearConstruction = null;
            if ($s3 !== null && $s3->Project_Date !== null) {
                $yearConstruction = Carbon::parse($s3->Project_Date)->format('Y');
            }

            $result[] = [
                'site_id' => $site->id,
                'site_name' => $s3->Site_Name ?? $site->name,
                'status' => $s3?->Status_Site,
                'platform' => $platform,
                'entrepreneur' => $s3?->Entrepreneur_English_Name,
                'advisor' => $advisor,
                'technician' => $s3?->technician_site,
                'tier' => $tier,
                'year_construction' => $yearConstruction,
            ];
        }

        return response()->json($result);
    }
}
