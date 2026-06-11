<?php

namespace App\Console\Commands;

use App\Models\CashierSale;
use App\Models\Site;
use Carbon\Carbon;
use Illuminate\Console\Command;

class CreateCashierData extends Command
{
    protected $signature = 'cashier:create-data';

    protected $description = 'Create fake data for cashier app';

    public function handle()
    {
        $site = Site::select('Id_Site', 'Advisor', 'Platform')
            ->where("is_pilot", true)
            ->orderBy('Id_Site')
            ->first();

        CashierSale::where('site', $site->Id_Site)->delete();
        $types = ['free', 'hod', 'wis', 'onsite', 'shop', 'bottle', 'other', 'hod'];
        foreach ($types as $index => $type) {
            $sale = new CashierSale();
            $sale->fill([
                'site' => $site->Id_Site,
                'sale_date' => Carbon::now(),
                'quantity' => rand(1, 100),
                'unit_price' => $index * 1000,
                'type' => $type,
                'index' => $index
            ]);
            $sale->save();
        }
    }
}
