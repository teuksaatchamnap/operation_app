<?php

namespace App\Console\Commands;

use App\Mail\CheckBottleOver;
use App\Models\Consumable;
use Illuminate\Console\Command;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Mail;

class CheckBottleLimit extends Command
{
    /**
     * The name and signature of the console command.
     *
     * @var string
     */
    protected $signature = 'app:check-bottle-limit';

    /**
     * The console command description.
     *
     * @var string
     */
    protected $description = 'Command description';

    /**
     * Execute the console command.
     */
    public function handle()
    {
        $startDate = '2025-01-01';
        $endDate = now()->toDateString();

        $results = Consumable::where('English_name', 'Blue 20L bottle with big neck (O-We bottle) and tap - PET 530g')
            ->whereBetween('Month', [$startDate, $endDate])
            ->select(DB::raw('SUM(Number_Item) as total_qty'))
            ->having('total_qty', '>', 5000)
            ->get(); 
            $recipients = ['chamnap.keo@teuksaat1001.com'];
            
        if ($results->isNotEmpty()) {
            $m= "over 5000 bottle 530g";
            Mail::to($recipients)->send(new CheckBottleOver($m));
        }
       
    }
}
