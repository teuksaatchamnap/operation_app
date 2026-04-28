<?php

namespace App\Jobs;

use App\Models\FactMonthly;
use App\Models\Site;
use App\Models\Sims3\Sale;
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
            Log::warning(static::class . ': no local sites found' . ($this->site ? " matching '{$this->site}'" : ''));
            return;
        }

        if ($months->isEmpty()) {
            Log::warning(static::class . ': no months found to process');
            return;
        }

        $siteNames = $siteMap->keys()->toArray();

        Log::info(static::class . ": processing {$months->count()} months for sites: " . implode(', ', $siteNames));

        $data = $this->prepareData($siteMap, $months, $siteNames);

        foreach ($months as $month) {
            $monthStart = $month->copy()->startOfMonth();
            $monthKey = $monthStart->format('Y-m-d');

            foreach ($siteMap as $siteName => $siteId) {
                $key = $siteName . '|' . $monthKey;

                FactMonthly::updateOrCreate(
                    ['site_id' => $siteId, 'month' => $monthStart],
                    $data[$key] ?? [],
                );
            }
        }
    }

    abstract protected function prepareData(Collection $siteMap, Collection $months, array $siteNames): array;

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
