<?php

namespace App\Jobs;

use Carbon\Carbon;
use Illuminate\Support\Collection;
use Illuminate\Support\Facades\Log;

class ComputeTreatmentProcess extends BaseComputeJob
{
    private const SPREADSHEET_ID = '1D7oK04IHDy_XV2RapbAHkHI0S-H57Cc2';

    private const GID = '331185019';

    private const SKIP_ROWS = 5;

    protected function prepareData(Collection $siteMap, Collection $months, array $siteNames): array
    {
        $csvData = $this->fetchSheet();
        if ($csvData === null) {
            return [];
        }

        $siteNameLookup = [];
        foreach ($siteMap as $name => $id) {
            $siteNameLookup[strtolower(trim($name))] = $name;
        }

        $siteHistory = [];
        $rows = explode("\n", $csvData);
        $inputLine = 0;

        foreach ($rows as $row) {
            $inputLine++;
            $row = trim($row);

            if ($row === '' || $inputLine <= self::SKIP_ROWS) {
                continue;
            }

            $fields = str_getcsv($row);
            $siteName = trim($fields[0] ?? '');
            $startDate = trim($fields[2] ?? '');
            $treatment = trim($fields[$this->columnLetterToIndex('ED')] ?? '');

            if ($siteName === '' || $startDate === '' || $treatment === '') {
                continue;
            }

            $normalized = strtolower($siteName);
            if (! isset($siteNameLookup[$normalized])) {
                continue;
            }

            try {
                $date = Carbon::parse($startDate)->startOfDay();
            } catch (\Exception) {
                continue;
            }

            $siteHistory[$normalized][] = [
                'date' => $date,
                'treatment' => $treatment,
            ];
        }

        foreach ($siteHistory as &$entries) {
            usort($entries, fn ($a, $b) => $a['date']->timestamp <=> $b['date']->timestamp);
        }
        unset($entries);

        $map = [];
        foreach ($months as $month) {
            $monthEnd = $month->copy()->endOfMonth();
            $monthKey = $month->format('Y-m-d');

            foreach ($siteMap as $siteName => $siteId) {
                $key = $siteName.'|'.$monthKey;

                $normalized = strtolower(trim($siteName));
                $history = $siteHistory[$normalized] ?? [];

                $activeTreatment = null;
                foreach ($history as $entry) {
                    if ($entry['date']->lte($monthEnd)) {
                        $activeTreatment = $entry['treatment'];
                    } else {
                        break;
                    }
                }

                $map[$key] = [
                    'treatment_process' => $activeTreatment,
                ];
            }
        }

        return $map;
    }

    private function columnLetterToIndex(string $letter): int
    {
        $letter = strtoupper($letter);
        $index = 0;

        for ($i = 0; $i < strlen($letter); $i++) {
            $index = $index * 26 + (ord($letter[$i]) - ord('A') + 1);
        }

        return $index - 1;
    }

    private function fetchSheet(): ?string
    {
        $url = 'https://docs.google.com/spreadsheets/d/'.self::SPREADSHEET_ID.'/export?format=csv&gid='.self::GID;

        $context = stream_context_create([
            'http' => [
                'method' => 'GET',
                'header' => "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36\r\n",
                'timeout' => 30,
            ],
        ]);

        $csvData = @file_get_contents($url, false, $context);
        if ($csvData === false) {
            Log::warning(static::class.': Failed to fetch Google Sheet');

            return null;
        }

        return $csvData;
    }
}
