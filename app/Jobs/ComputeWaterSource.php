<?php

namespace App\Jobs;

use App\Models\Sims3\Site as Sims3Site;
use Illuminate\Support\Collection;

class ComputeWaterSource extends BaseComputeJob
{
    protected function prepareData(Collection $siteMap, Collection $months, array $siteNames): array
    {
        $sites = Sims3Site::query()
            ->select(['Id_Site', 'Water_Source'])
            ->whereIn('Id_Site', $siteNames)
            ->get();

        $sourceMap = [];
        foreach ($sites as $site) {
            $siteName = trim($site->Id_Site);
            $sourceMap[$siteName] = $this->normalize($site->Water_Source);
        }

        $map = [];
        foreach ($months as $month) {
            $monthKey = $month->format('Y-m-d');
            foreach ($siteMap as $siteName => $siteId) {
                $key = $siteName.'|'.$monthKey;
                $map[$key] = [
                    'water_source' => $sourceMap[$siteName] ?? null,
                ];
            }
        }

        return $map;
    }

    private function normalize(?string $value): ?string
    {
        if ($value === null || trim($value) === '') {
            return null;
        }

        return match (strtolower(trim($value))) {
            'pond' => 'pond',
            'lake' => 'pond',
            'river' => 'river',
            'well', 'well water' => 'well',
            'pipe water', 'piped water', 'private pipe water', 'drinking water' => 'pipe',
            default => null,
        };
    }
}
