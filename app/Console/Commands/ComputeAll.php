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
        $totalIterations = $totalYears * 12;

        $bar = $this->output->createProgressBar($totalIterations);
        $bar->setFormat(' %current%/%max% [%bar%] %percent:3s%% -- %message%');
        $bar->setMessage('Starting...');
        $bar->start();

        for ($year = $startYear; $year <= $endYear; $year++) {
            $bar->setMessage("ComputeDimensions $year");
            Artisan::call('job:run', ['job' => "App\Jobs\ComputeDimensions", '--year' => $year]);
            $bar->advance();

            $bar->setMessage("ComputeSalesVolume $year");
            Artisan::call('job:run', ['job' => "App\Jobs\ComputeSalesVolume", '--year' => $year]);
            $bar->advance();

            $bar->setMessage("ComputeHas3Workers $year");
            Artisan::call('job:run', ['job' => "App\Jobs\ComputeHas3Workers", '--year' => $year]);
            $bar->advance();

            $bar->setMessage("ComputeConsumers $year");
            Artisan::call('job:run', ['job' => "App\Jobs\ComputeConsumers", '--year' => $year]);
            $bar->advance();

            $bar->setMessage("ComputeWhoCompliance $year");
            Artisan::call('job:run', ['job' => "App\Jobs\ComputeWhoCompliance", '--year' => $year]);
            $bar->advance();

            $bar->setMessage("ComputeExpenses $year");
            Artisan::call('job:run', ['job' => "App\Jobs\ComputeExpenses", '--year' => $year]);
            $bar->advance();

            $bar->setMessage("ComputeIsProfitable $year");
            Artisan::call('job:run', ['job' => "App\Jobs\ComputeIsProfitable", '--year' => $year]);
            $bar->advance();

            $bar->setMessage("ComputeEcCollection $year");
            Artisan::call('job:run', ['job' => "App\Jobs\ComputeEcCollection", '--year' => $year]);
            $bar->advance();

            $bar->setMessage("ComputeWaterLoss $year");
            Artisan::call('job:run', ['job' => "App\Jobs\ComputeWaterLoss", '--year' => $year]);
            $bar->advance();

            $bar->setMessage("ComputeDataCollection $year");
            Artisan::call('job:run', ['job' => "App\Jobs\ComputeDataCollection", '--year' => $year]);
            $bar->advance();

            $bar->setMessage("ComputeWaterSource $year");
            Artisan::call('job:run', ['job' => "App\Jobs\ComputeWaterSource", '--year' => $year]);
            $bar->advance();

            $bar->setMessage("ComputeTreatmentProcess $year");
            Artisan::call('job:run', ['job' => "App\Jobs\ComputeTreatmentProcess", '--year' => $year]);
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
