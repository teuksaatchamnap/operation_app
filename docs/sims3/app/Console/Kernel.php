<?php

namespace App\Console;

use Illuminate\Console\Scheduling\Schedule;
use Illuminate\Foundation\Console\Kernel as ConsoleKernel;

class Kernel extends ConsoleKernel
{
    /**
     * Define the application's command schedule.
     * IN CRONTAB : * * * * * cd /var/www/sims3 && php artisan schedule:run >> /dev/null 2>&1
     */
    protected function schedule(Schedule $schedule): void
    {
        // $schedule->command('app:send-emails-with-attachment')->everyMinute();
        // $schedule->command('app:send-emails-with-attachment')->monthlyOn(2, '15:00');
        //$schedule->command('app:check-bottle-limit')->everyTenMinutes();
        $schedule->command('app:send-emails-with-attachment')
            ->monthlyOn(2, '9:00') // 6:40 PM in 24-hour format
            ->timezone('Asia/Phnom_Penh');
        $schedule->command('app:send-reminders')->everyMinute();
    }

    /**
     * Register the commands for the application.
     */
    protected function commands(): void
    {
        $this->load(__DIR__ . '/Commands');

        require base_path('routes/console.php');
    }
}
