<?php

namespace App\Jobs;

use App\Models\FactMonthly;
use App\Models\Sims3\Sale;
use App\Models\Site;
use Carbon\Carbon;
use Illuminate\Bus\Queueable;
use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Foundation\Bus\Dispatchable;
use Illuminate\Queue\InteractsWithQueue;
use Illuminate\Queue\SerializesModels;
use Illuminate\Support\Collection;
use Illuminate\Support\Facades\Log;

abstract class BaseComputeJob implements ShouldQueue
{
    use Dispatchable, InteractsWithQueue, Queueable, SerializesModels;

    public function __construct(
        public ?Carbon $month = null,
        public ?int $year = null,
        public ?string $site = null,
    ) {}

    final public function handle(): void
    {
        $siteMap = $this->resolveSites();
        $months = $this->resolveMonths();

        if ($siteMap->isEmpty()) {
            Log::warning(static::class.': no local sites found'.($this->site ? " matching '{$this->site}'" : ''));

            return;
        }

        if ($months->isEmpty()) {
            Log::warning(static::class.': no months found to process');

            return;
        }

        $siteNames = $siteMap->keys()->toArray();

        Log::info(static::class.": processing {$months->count()} months for sites: ".implode(', ', $siteNames));

        $data = $this->prepareData($siteMap, $months, $siteNames);

        $recordsToUpsert = [];
        $batchSize = 500;
        $processed = 0;

        foreach ($months as $month) {
            $monthStart = $month->copy()->startOfMonth();
            $monthKey = $monthStart->format('Y-m-d');

            foreach ($siteMap as $siteName => $siteId) {
                $key = $siteName.'|'.$monthKey;
                $recordData = $data[$key] ?? [];

                // Skip empty records - no data to update
                if (empty($recordData)) {
                    continue;
                }

                $recordsToUpsert[] = array_merge(
                    ['site_id' => $siteId, 'month' => $monthStart->format('Y-m-d')],
                    $recordData
                );

                $processed++;

                if ($processed >= $batchSize) {
                    $this->upsertBatch($recordsToUpsert);
                    $recordsToUpsert = [];
                    $processed = 0;
                }
            }
        }

        if (! empty($recordsToUpsert)) {
            $this->upsertBatch($recordsToUpsert);
        }
    }

    abstract protected function prepareData(Collection $siteMap, Collection $months, array $siteNames): array;

    private function upsertBatch(array $records): void
    {
        if (empty($records)) {
            return;
        }

        // Deduplicate records by site_id + month (keep last)
        $deduped = [];
        foreach ($records as $record) {
            $key = $record['site_id'].'|'.$record['month'];
            $deduped[$key] = $record;
        }
        $records = array_values($deduped);

        // Collect all unique keys from all records for normalization
        $allKeys = [];
        foreach ($records as $record) {
            $allKeys = array_merge($allKeys, array_keys($record));
        }
        $allKeys = array_unique($allKeys);

        // Normalize all records to have the same keys
        $normalizedRecords = [];
        foreach ($records as $record) {
            $normalizedRecords[] = array_merge(
                array_fill_keys($allKeys, null),
                $record
            );
        }

        $updateColumns = array_diff($allKeys, ['site_id', 'month']);

        FactMonthly::upsert(
            $normalizedRecords,
            ['site_id', 'month'],
            $updateColumns
        );
    }

    protected function resolveSites(): Collection
    {
        $query = Site::query();

        if ($this->site !== null) {
            $query->where('name', $this->site);
        }

        return $query->pluck('id', 'name');
    }

    protected function resolveMonths(): Collection
    {
        if ($this->month !== null) {
            return collect([$this->month->copy()->startOfMonth()]);
        }

        if ($this->year !== null) {
            $months = collect();
            for ($m = 1; $m <= 12; $m++) {
                $months->push(Carbon::create($this->year, $m, 1));
            }

            return $months;
        }

        $minDate = Sale::query()->min('Month');
        $maxDate = Sale::query()->max('Month');

        if ($minDate === null || $maxDate === null) {
            return collect();
        }

        $start = Carbon::parse($minDate)->startOfMonth();
        $end = Carbon::parse($maxDate)->startOfMonth();

        $months = collect();
        $current = $start->copy();
        while ($current->lte($end)) {
            $months->push($current->copy());
            $current->addMonth();
        }

        return $months;
    }
}
