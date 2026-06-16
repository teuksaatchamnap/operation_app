<?php

namespace App\Console\Commands;

use App\Models\Advisor;
use App\Models\Platform;
use App\Models\Sims3\Site as Sims3Site;
use App\Models\Site;
use Illuminate\Console\Command;

class ImportFromSims3 extends Command
{
    protected $signature = 'sims3:import-dimensions';

    protected $description = 'Import distinct sites, platforms and advisors from SIMS3 into local database';

    public function handle(): int
    {
        $this->importSites();
        $this->importPlatforms();
        $this->importAdvisors();

        return self::SUCCESS;
    }

    private function importSites(): void
    {
        $this->info('Importing sites from SIMS3...');

        $sitesGeo = Sims3Site::select(['Id_Site', 'Latitude', 'Longitude'])
            ->whereNotNull('Id_Site')
            ->get()
            ->keyBy('Id_Site');

        $distinctSites = $sitesGeo->keys();

        $this->info("Found {$distinctSites->count()} distinct sites");

        $created = 0;
        $skipped = 0;
        $updated = 0;

        foreach ($distinctSites as $siteName) {
            $siteName = trim($siteName);

            if (empty($siteName)) {
                $skipped++;

                continue;
            }

            $geoData = $sitesGeo[$siteName] ?? null;
            $siteAttributes = [
                'name' => $siteName,
                'latitude' => $geoData?->Latitude,
                'longitude' => $geoData?->Longitude,
            ];

            $site = Site::firstOrCreate(
                ['name' => $siteName],
                $siteAttributes
            );

            if ($site->wasRecentlyCreated) {
                $created++;
                $this->info("  Created site: {$siteName}");
            } else {
                // Update geolocation for existing sites if available
                $updatedGeo = false;
                if ($geoData !== null) {
                    $updateData = [];
                    if ($geoData->Latitude !== null && $site->latitude !== $geoData->Latitude) {
                        $updateData['latitude'] = $geoData->Latitude;
                    }
                    if ($geoData->Longitude !== null && $site->longitude !== $geoData->Longitude) {
                        $updateData['longitude'] = $geoData->Longitude;
                    }
                    if (! empty($updateData)) {
                        $site->update($updateData);
                        $updated++;
                        $updatedGeo = true;
                        $this->info("  Updated geolocation: {$siteName}");
                    }
                }
                if (! $updatedGeo) {
                    $skipped++;
                    $this->line("  Skipped existing site: {$siteName}");
                }
            }
        }

        $this->info("Sites import complete! Created: {$created}, Updated: {$updated}, Skipped: {$skipped}");
    }

    private function importAdvisors(): void
    {
        $this->info('Importing advisors from SIMS3...');

        $distinctAdvisors = Sims3Site::select('Advisor')
            ->distinct()
            ->whereNotNull('Advisor')
            ->pluck('Advisor');

        $this->info("Found {$distinctAdvisors->count()} distinct advisors");

        $created = 0;
        $skipped = 0;

        foreach ($distinctAdvisors as $advisorName) {
            $advisorName = trim($advisorName);

            if (empty($advisorName) || $advisorName == 'Stop') {
                $skipped++;

                continue;
            }

            $advisor = Advisor::firstOrCreate(
                ['name' => $advisorName],
                ['name' => $advisorName]
            );

            if ($advisor->wasRecentlyCreated) {
                $created++;
                $this->info("  Created advisor: {$advisorName}");
            } else {
                $skipped++;
                $this->line("  Skipped advisor site: {$advisorName}");
            }
        }

        $this->info("Sites import complete! Created: {$created}, Skipped: {$skipped}");
    }

    private function importPlatforms(): void
    {
        $this->info('Importing platforms from SIMS3...');

        $distinctPlatforms = Sims3Site::select('Platform')
            ->distinct()
            ->whereNotNull('Platform')
            ->pluck('Platform');

        $this->info("Found {$distinctPlatforms->count()} distinct platforms");

        $created = 0;
        $skipped = 0;

        foreach ($distinctPlatforms as $platformName) {
            $platformName = trim($platformName);

            if (empty($platformName) || $platformName == 'Dead') {
                $skipped++;

                continue;
            }

            $platform = Platform::firstOrCreate(
                ['name' => $platformName],
                ['name' => $platformName]
            );

            if ($platform->wasRecentlyCreated) {
                $created++;
                $this->info("  Created platform: {$platformName}");
            } else {
                $skipped++;
                $this->line("  Skipped existing platform: {$platformName}");
            }
        }

        $this->info("Platforms import complete! Created: {$created}, Skipped: {$skipped}");
    }
}
