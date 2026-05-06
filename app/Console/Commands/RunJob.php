<?php

namespace App\Console\Commands;

use Carbon\Carbon;
use Illuminate\Console\Command;

class RunJob extends Command
{
    protected $signature = 'job:run
        {job : The job class to run}
        {--month= : Year-month to compute (YYYY-MM)}
        {--year= : Year to compute (YYYY)}
        {--site= : Site name}';

    protected $description = 'Run a job synchronously from the command line';

    public function handle(): int
    {
        $jobClass = $this->argument('job');

        if (! class_exists($jobClass)) {
            $this->error("Class {$jobClass} does not exist.");

            return self::FAILURE;
        }

        $month = null;
        if ($this->option('month')) {
            $month = Carbon::createFromFormat('Y-m', $this->option('month'));
        }

        $year = $this->option('year') !== null ? (int) $this->option('year') : null;
        $site = $this->option('site');

        $this->info("Running job: {$jobClass}");

        $job = new $jobClass($month, $year, $site);
        $job->handle();

        $this->info('Job completed.');

        return self::SUCCESS;
    }
}
