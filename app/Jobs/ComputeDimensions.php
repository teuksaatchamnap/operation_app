<?php

namespace App\Jobs;

use App\Models\Advisor;
use App\Models\Platform;
use App\Models\Sims3\Site as Sims3Site;
use Illuminate\Support\Collection;
use Illuminate\Support\Facades\Cache;

class ComputeDimensions extends BaseComputeJob
{
    protected function prepareData(Collection $siteMap, Collection $months, array $siteNames): array
    {
        $dimensionsPerSite = Cache::remember('dimensions_per_site', 600, function () {
            $sims3Sites = Sims3Site::query()
                ->select(['Id_Site', 'Platform', 'Advisor'])
                ->get();

            $uniquePlatformNames = [];
            $uniqueAdvisorNames = [];

            foreach ($sims3Sites as $s) {
                $pn = trim($s->Platform);
                if (! empty($pn) && $pn !== 'Dead') {
                    $uniquePlatformNames[$pn] = true;
                }
                $an = trim($s->Advisor);
                if (! empty($an) && $an !== 'Stop') {
                    $uniqueAdvisorNames[$an] = true;
                }
            }

            $uniquePlatformNames = array_keys($uniquePlatformNames);
            $uniqueAdvisorNames = array_keys($uniqueAdvisorNames);

            if (! empty($uniquePlatformNames)) {
                Platform::insertOrIgnore(
                    array_map(fn ($n) => ['name' => $n], $uniquePlatformNames)
                );
            }

            if (! empty($uniqueAdvisorNames)) {
                Advisor::insertOrIgnore(
                    array_map(fn ($n) => ['name' => $n], $uniqueAdvisorNames)
                );
            }

            $platformLookup = ! empty($uniquePlatformNames)
                ? Platform::whereIn('name', $uniquePlatformNames)->pluck('id', 'name')->toArray()
                : [];

            $advisorLookup = ! empty($uniqueAdvisorNames)
                ? Advisor::whereIn('name', $uniqueAdvisorNames)->pluck('id', 'name')->toArray()
                : [];

            $result = [];

            foreach ($sims3Sites as $s) {
                $siteName = trim($s->Id_Site);
                $pn = trim($s->Platform);
                $an = trim($s->Advisor);

                $platformId = (! empty($pn) && $pn !== 'Dead')
                    ? ($platformLookup[$pn] ?? null)
                    : null;

                $advisorId = (! empty($an) && $an !== 'Stop')
                    ? ($advisorLookup[$an] ?? null)
                    : null;

                $result[$siteName] = [
                    'platform_id' => $platformId,
                    'advisor_id' => $advisorId,
                ];
            }

            return $result;
        });

        $map = [];
        foreach ($months as $month) {
            $monthKey = $month->copy()->startOfMonth()->format('Y-m-d');

            foreach ($siteMap as $siteName => $siteId) {
                $key = $siteName.'|'.$monthKey;
                $map[$key] = $dimensionsPerSite[$siteName] ?? ['platform_id' => null, 'advisor_id' => null];
            }
        }

        return $map;
    }
}
