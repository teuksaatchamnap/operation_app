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
                'description' => '',
            ],
            [
                'name' => 'Sales Volume',
                'col_name' => 'sales_volume',
                'unit' => 'bottles',
                'periodicity' => 'monthly',
                'type' => 'quantitative',
                'description' => 'This is the total sales excluding WiS and new bottles',
                'aggregate' => 'sum',
            ],
            [
                'name' => 'Sales Volume LfL',
                'col_name' => 'sales_volume_lfl',
                'unit' => 'bottles',
                'periodicity' => 'monthly',
                'type' => 'quantitative',
                'description' => 'Like to like sales, this is the total sales excluding WiS and new bottles for sites who were opened on january of the reference year',
                'aggregate' => 'sum',
            ],
            [
                'name' => 'Days Open',
                'col_name' => 'days_open',
                'unit' => 'days',
                'periodicity' => 'monthly',
                'type' => 'quantitative',
                'description' => 'The number of days the site reported at least one sale',
                'aggregate' => 'avg',
            ],
            [
                'name' => 'Active sites',
                'col_name' => 'active',
                'unit' => 'sites',
                'periodicity' => 'monthly',
                'type' => 'quantitative',
                'description' => 'The number of active sites (site reported at least one sale for the period)',
                'aggregate' => 'sum',
            ],
            [
                'name' => 'Super Tier 1',
                'col_name' => 'super_tier_1',
                'unit' => 'sites',
                'periodicity' => 'monthly',
                'type' => 'quantitative',
                'description' => 'The number of sites with more that 110 sales per day (exclude WinS and new bottles)',
                'aggregate' => 'sum',
            ],
            [
                'name' => 'Bottles per day',
                'col_name' => 'bottles_per_day',
                'unit' => 'bottles',
                'periodicity' => 'monthly',
                'type' => 'quantitative',
                'description' => 'The average number of bottles sold per days excluding WinS',
                'aggregate' => 'avg',
            ],
            [
                'name' => 'Expenses',
                'col_name' => 'expenses',
                'unit' => 'Riels',
                'periodicity' => 'monthly',
                'type' => 'quantitative',
                'aggregate' => 'sum',
            ],
            [
                'name' => 'Revenue',
                'col_name' => 'revenue',
                'unit' => 'Riels',
                'periodicity' => 'monthly',
                'type' => 'quantitative',
                'aggregate' => 'sum',
            ],
            [
                'name' => 'Has 3 Workers',
                'col_name' => 'has_3_workers',
                'unit' => 'sites',
                'periodicity' => 'monthly',
                'type' => 'quantitative',
                'description' => 'True if the site has 3 or more operators, null if no data',
                'aggregate' => 'sum',
            ],
            [
                'name' => 'Consumers',
                'col_name' => 'consumers',
                'unit' => 'consumers',
                'periodicity' => 'monthly',
                'type' => 'quantitative',
                'description' => 'The number of consumers who bought from sites',
                'aggregate' => 'sum',
            ],
            [
                'name' => 'WHO Compliance',
                'col_name' => 'who_compliance',
                'unit' => 'sites',
                'periodicity' => 'monthly',
                'type' => 'qualitative',
                'description' => 'WHO compliance E.Coli and Coliform 0 CFU/100ml',
                'aggregate' => 'sum',
            ],
            [
                'name' => 'Profitable',
                'col_name' => 'is_profitable',
                'unit' => 'sites',
                'periodicity' => 'monthly',
                'type' => 'qualitative',
                'description' => 'True if site revenue - site expense + salary entrepreneur >= 200',
                'aggregate' => 'sum',
            ],
            [
                'name' => 'EC Collection',
                'col_name' => 'ec_collection',
                'unit' => '%',
                'periodicity' => 'monthly',
                'type' => 'qualitative',
                'description' => 'Percentage of active sites where paid >= amount_expenses for entrepreneur_contribution expenses',
                'aggregate' => 'pct_active',
            ],
        ];

        foreach ($kpis as $kpi) {
            Kpi::firstOrCreate(
                ['col_name' => $kpi['col_name']],
                $kpi
            );
        }

        Artisan::call('sims3:import-dimensions');
    }
}
