<?php

namespace App\Console\Commands;

use App\Models\Configuration;
use Illuminate\Console\Command;

class CreateDefaultConfig extends Command
{
    /**
     * The name and signature of the console command.
     *
     * @var string
     */
    protected $signature = 'config:create';

    /**
     * The console command description.
     *
     * @var string
     */
    protected $description = 'Create the lines in Configuration tables';

    /**
     * Execute the console command.
     */
    public function handle()
    {
        /* Configuration for Mission app*/
        Configuration::create([
            "app" => "mission",
            "name" => "cashiers",
            "value" => '[{"name":"yes - I dont know","value":"yes"},{"name":"yes - Sorvy","value":"sorvy.m@teuksaat1001.com"},{"name":"yes - Sreyrath","value":"sreyrath.h@teuksaat1001.com"},{"name":"yes - Chamroeun","value":"chamreoun.no@teuksaat1001.com"},{"name":"no","value":"no"}]'
        ]);
        Configuration::create([
            "app" => "mission",
            "name" => "transportation",
            "value" => '["TS moto", "TS car", "other"]'
        ]);
        Configuration::create([
            "app" => "mission",
            "name" => "cost",
            "value" => '{"per_diem_10_to_40":"1.5","per_diem_more_than_40":"6","accomodation":"6","manager_per_diem_10_to_40":"0","manager_per_diem_more_than_40":"7","manager_accomodation":"7","excom_accomodation":"12","excom_per_diem_more_than_40":"7","ed_accomodation":"20","ed_per_diem":"0","km_per_liter":"37","km_per_liter_car":"9","gasoline_price":"1"}'
        ]);
    }
}
