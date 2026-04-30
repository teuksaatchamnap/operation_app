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
        for ($year = 2005; $year <= date('Y'); $year++) {
            Artisan::call("job:run", ["job" => "App\Jobs\ComputeDimensions", "--year" => $year]);
            Artisan::call("job:run", ["job" => "App\Jobs\ComputeSalesVolume", "--year" => $year]);
        }
    }
}
