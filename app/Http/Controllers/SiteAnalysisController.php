<?php

namespace App\Http\Controllers;

use App\Models\Sims3\Platform as Sims3Platform;
use App\Models\Sims3\Site as Sims3Site;
use App\Models\Site;
use Illuminate\Http\JsonResponse;

class SiteAnalysisController extends Controller
{
    public function show(Site $site): JsonResponse
    {
        $sims3Site = Sims3Site::where('Id_Site', $site->name)->first();

        if (! $sims3Site) {
            return response()->json(['error' => 'Site not found in Sims3 database'], 404);
        }

        $platform = $sims3Site->Platform
            ? Sims3Platform::where('Code_Platform', $sims3Site->Platform)->value('Mail_ROM')
            : null;

        return response()->json([
            'platform' => $sims3Site->Platform,
            'entrepreneur_name' => $sims3Site->Entrepreneur_English_Name,
            'start_working_date' => $sims3Site->Date_start_working,
            'advisor_name' => $sims3Site->Advisor_email,
            'rom_name' => $platform,
            'commune_name' => $sims3Site->Commune,
            'population_commune' => $sims3Site->Population,
            'households' => $sims3Site->Households,
        ]);
    }
}
