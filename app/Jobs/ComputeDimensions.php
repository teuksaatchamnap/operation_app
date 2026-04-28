<?php

namespace App\Jobs;

use App\Models\Advisor;
use App\Models\Platform;
use App\Models\Sims3\Site as Sims3Site;
use Carbon\Carbon;
use Illuminate\Support\Collection;

class ComputeDimensions extends BaseComputeJob
{
    protected function prepareData(Collection $siteMap, Collection $months, array $siteNames): array
    {
        $sims3Sites = Sims3Site::query()
            ->select(['Id_Site', 'Platform', 'Advisor'])
            ->whereIn('Id_Site', $siteNames)
            ->get();

        $dimensionsPerSite = [];
        foreach ($sims3Sites as $sims3Site) {
            $siteName = trim($sims3Site->Id_Site);

            if (!isset($siteMap[$siteName])) {
                continue;
            }

            $platformId = null;
            $advisorId = null;

            $platformName = trim($sims3Site->Platform);
            if (!empty($platformName) && $platformName !== 'Dead') {
                $platform = Platform::firstOrCreate(['name' => $platformName]);
                $platformId = $platform->id;
            }

            $advisorName = trim($sims3Site->Advisor);
            if (!empty($advisorName) && $advisorName !== 'Stop') {
                $advisor = Advisor::firstOrCreate(['name' => $advisorName]);
                $advisorId = $advisor->id;
            }

            $dimensionsPerSite[$siteName] = [
                'platform_id' => $platformId,
                'advisor_id' => $advisorId,
            ];
        }

        $map = [];
        foreach ($months as $month) {
            $monthKey = $month->copy()->startOfMonth()->format('Y-m-d');

            foreach ($siteMap as $siteName => $siteId) {
                $key = $siteName . '|' . $monthKey;
                $map[$key] = $dimensionsPerSite[$siteName] ?? ['platform_id' => null, 'advisor_id' => null];
            }
        }

        return $map;
    }
}
