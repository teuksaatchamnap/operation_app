<?php

namespace App\Console\Commands;

use Illuminate\Console\Command;
use Illuminate\Support\Facades\Artisan;

class ComputeAll extends Command
{
    /**
     * The name and signature of the console command.
     *
     * @var string
     */
    protected $signature = 'compute:all';

    /**
     * The console command description.
     *
     * @var string
     */
    protected $description = 'Compute all data from 2005';

    /**
     * Execute the console command.
     */
    public function handle()
    {
        $startTime = microtime(true);
        $startDateTime = now()->toDateTimeString();
        $this->info("Starting computation at {$startDateTime}");

        $startYear = 2005;
        $endYear = date('Y');
        $totalYears = $endYear - $startYear + 1;
        $totalIterations = $totalYears * 2;

        $bar = $this->output->createProgressBar($totalIterations);
        $bar->setFormat('verbose');
        $bar->start();

        for ($year = $startYear; $year <= $endYear; $year++) {
            Artisan::call("job:run", ["job" => "App\Jobs\ComputeDimensions", "--year" => $year]);
            $bar->advance();

            Artisan::call("job:run", ["job" => "App\Jobs\ComputeSalesVolume", "--year" => $year]);
            $bar->advance();
        }

        $bar->finish();
        $this->newLine();

        $endTime = microtime(true);
        $elapsed = round($endTime - $startTime, 2);
        $endDateTime = now()->toDateTimeString();

        $this->info("Completed at {$endDateTime}");
        $this->info("Total time: {$elapsed} seconds");
    }
}
