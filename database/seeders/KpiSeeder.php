<?php

namespace Database\Seeders;

use App\Models\Kpi;
use Illuminate\Database\Console\Seeds\WithoutModelEvents;
use Illuminate\Database\Seeder;
use Illuminate\Support\Facades\Artisan;

class KpiSeeder extends Seeder
{
    use WithoutModelEvents;

    /**
     * Run the database seeds.
     */
    public function run(): void
    {
        $kpis = [
            [
                'name' => 'Tier',
                'col_name' => 'tier',
                'unit' => 'tier level',
                'periodicity' => 'monthly',
                'type' => 'qualitative',
            ],
            [
                'name' => 'Sales Volume',
                'col_name' => 'sales_volume',
                'unit' => 'count',
                'periodicity' => 'monthly',
                'type' => 'quantitative',
            ],
            [
                'name' => 'Days Open',
                'col_name' => 'days_open',
                'unit' => 'days',
                'periodicity' => 'monthly',
                'type' => 'quantitative',
            ],
            [
                'name' => 'Expenses',
                'col_name' => 'expenses',
                'unit' => 'Riels',
                'periodicity' => 'monthly',
                'type' => 'quantitative',
            ],
            [
                'name' => 'Revenue',
                'col_name' => 'revenue',
                'unit' => 'Riels',
                'periodicity' => 'monthly',
                'type' => 'quantitative',
            ],
            [
                'name' => 'Workers',
                'col_name' => 'workers',
                'unit' => 'workers',
                'periodicity' => 'monthly',
                'type' => 'quantitative',
            ],
            [
                'name' => 'Consumers',
                'col_name' => 'consumers',
                'unit' => 'consumers',
                'periodicity' => 'monthly',
                'type' => 'quantitative',
            ],
            [
                'name' => 'WHO Compliance',
                'col_name' => 'who_compliance',
                'unit' => 'yes/no',
                'periodicity' => 'monthly',
                'type' => 'qualitative',
            ],
            [
                'name' => 'Profitable',
                'col_name' => 'profitable',
                'unit' => 'yes/no',
                'periodicity' => 'monthly',
                'type' => 'qualitative',
            ],
        ];

        foreach ($kpis as $kpi) {
            Kpi::firstOrCreate(
                ['col_name' => $kpi['col_name']],
                $kpi
            );
        }

        Artisan::call("sims3:import-dimensions");
    }
}
