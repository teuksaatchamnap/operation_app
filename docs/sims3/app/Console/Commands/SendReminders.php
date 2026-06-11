<?php

namespace App\Console\Commands;

use App\Http\Controllers\TelegramController;
use App\Models\Reminder;
use App\Models\TelegramGroup;
use Illuminate\Console\Command;
use Illuminate\Support\Facades\Log;
use Illuminate\Support\Facades\Storage;

class SendReminders extends Command
{
    /**
     * The name and signature of the console command.
     *
     * @var string
     */
    protected $signature = 'app:send-reminders';

    /**
     * The console command description.
     *
     * @var string
     */
    protected $description = 'Send scheduled reminders to telegram groups';

    /**
     * Execute the console command.
     */
    public function handle(TelegramController $telegramController)
    {
        // For testing
        // $telegramController->sendMessageToSite("M27", Reminder::get()->first()->message);
        // dd("ok");

        $now = now();
        $currentTime = $now->format('H:i');
        $dayOfMonth = $now->day;
        $lastDayOfMonth = $now->endOfMonth()->day;

        $reminders = Reminder::where('time', $currentTime)->where('active', true)->get();

        foreach ($reminders as $reminder) {
            $this->processReminder($reminder, $telegramController, $dayOfMonth, $lastDayOfMonth);
        }

        $this->info('Reminders sent successfully.');
    }

    private function processReminder($reminder, $telegramController, $dayOfMonth, $lastDayOfMonth)
    {
        $shouldSend = false;

        if ($reminder->day_of_month == -1) {
            $shouldSend = $dayOfMonth == $lastDayOfMonth;
        } elseif ($reminder->day_of_month == -2) {
            $shouldSend = $dayOfMonth == ($lastDayOfMonth - 1);
        } elseif ($reminder->day_of_month == $dayOfMonth) {
            $shouldSend = true;
        }

        if ($shouldSend) {
            if ($reminder->target == 'ALL SITES') {
                $sites = TelegramGroup::pluck('site')->unique();
                foreach ($sites as $site) {
                    $telegramController->sendMessageToSite($site, $reminder->message);
                    if ($reminder->audio && Storage::disk("public")->exists($reminder->audio)) {
                        $telegramController->sendAudioToSite($site, Storage::disk("public")->path($reminder->audio));
                    }
                    $this->info("Sent reminder to site: " . $site);
                    Log::info("Sent reminder " . $reminder->id . " to site " . $site);
                    usleep(30000);
                }
            } else {
                $telegramController->sendMessageToSite($reminder->target, $reminder->message);
                if ($reminder->audio && Storage::disk("public")->exists($reminder->audio)) {
                    $telegramController->sendAudioToSite($reminder->target, Storage::disk("public")->path($reminder->audio));
                }
                $this->info("Sent reminder to site: " . $reminder->target);
                Log::info("Sent reminder " . $reminder->id . " to site " . $reminder->target);
            }
        }
    }
}
