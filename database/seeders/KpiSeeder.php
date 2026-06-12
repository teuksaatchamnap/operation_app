<?php

namespace Database\Seeders;

use App\Models\Kpi;
use App\Models\Objective;
use Carbon\Carbon;
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
                'legend' => [
                    ['value' => 'ST1', 'color' => '#1B5E20'],
                    ['value' => '1', 'color' => '#4CAF50'],
                    ['value' => '2', 'color' => '#FFC107'],
                    ['value' => '3', 'color' => '#F44336'],
                    ['value' => 'New', 'color' => '#00BCD4'],
                    ['value' => 'Reopen', 'color' => '#FF9800'],
                    ['value' => 'Closed', 'color' => '#795548'],
                    ['value' => 'Inactive', 'color' => '#BDBDBD'],
                    ['value' => 'Dead', 'color' => '#616161'],
                ],
            ],
            [
                'name' => 'Sales Volume',
                'col_name' => 'sales_volume',
                'unit' => 'bottles',
                'periodicity' => 'monthly',
                'type' => 'quantitative',
                'description' => 'This is the total sales excluding WiS and new bottles',
                'aggregate' => 'sum',
                'default_objective' => 1968988,
                'individual_objective' => 3000,
            ],
            [
                'name' => 'Sales Volume LfL',
                'col_name' => 'sales_volume_lfl',
                'unit' => 'bottles',
                'periodicity' => 'monthly',
                'type' => 'quantitative',
                'description' => 'Like to like sales, this is the total sales excluding WiS and new bottles for sites who were opened on january of the reference year',
                'aggregate' => 'sum',
                'default_objective' => 1834049,
            ],
            [
                'name' => 'Days Open',
                'col_name' => 'days_open',
                'unit' => 'days',
                'periodicity' => 'monthly',
                'type' => 'quantitative',
                'description' => 'The number of days the site reported at least one sale',
                'aggregate' => 'avg',
                'default_objective' => 26,
            ],
            [
                'name' => 'Active sites',
                'col_name' => 'active',
                'unit' => 'sites',
                'periodicity' => 'monthly',
                'type' => 'quantitative',
                'description' => 'The number of active sites (site reported at least one sale for the period)',
                'aggregate' => 'sum',
                'default_objective' => 372,
                'legend' => [
                    ['value' => 'Active', 'color' => '#4CAF50'],
                    ['value' => 'Inactive', 'color' => '#E0E0E0'],
                ],
            ],
            [
                'name' => 'Super Tier 1',
                'col_name' => 'super_tier_1',
                'unit' => 'sites',
                'periodicity' => 'monthly',
                'type' => 'quantitative',
                'description' => 'The number of sites with more that 110 sales per day (exclude WinS and new bottles)',
                'aggregate' => 'sum',
                'default_objective' => 125,
            ],
            [
                'name' => 'Bottles per day',
                'col_name' => 'bottles_per_day',
                'unit' => 'bottles',
                'periodicity' => 'monthly',
                'type' => 'quantitative',
                'description' => 'The average number of bottles sold per days excluding WinS',
                'aggregate' => 'avg',
                'default_objective' => 101,
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
                'default_objective' => 347,
            ],
            [
                'name' => 'Number of Operators',
                'col_name' => 'operators',
                'unit' => 'operators',
                'periodicity' => 'monthly',
                'type' => 'quantitative',
                'description' => 'The number of operators working at the site',
                'aggregate' => 'avg',
                'default_objective' => 3,
            ],
            [
                'name' => 'Consumers',
                'col_name' => 'consumers',
                'unit' => 'consumers',
                'periodicity' => 'monthly',
                'type' => 'quantitative',
                'description' => 'The number of consumers who bought from sites',
                'aggregate' => 'sum',
                'default_objective' => 1100100,
                'individual_objective' => 3000,
            ],
            [
                'name' => 'Penetration',
                'col_name' => 'penetration',
                'unit' => '%',
                'periodicity' => 'monthly',
                'type' => 'quantitative',
                'description' => 'Market penetration: number of consumers divided by the total population of the commune',
                'aggregate' => 'avg',
                'default_objective' => 45,
            ],
            [
                'name' => 'WHO Compliance',
                'col_name' => 'who_compliance',
                'unit' => '%',
                'periodicity' => 'monthly',
                'type' => 'qualitative',
                'description' => 'WHO compliance E.Coli and Coliform 0 CFU/100ml',
                'aggregate' => 'pct_active',
                'default_objective' => 99.5,
            ],
            [
                'name' => 'Contamination level',
                'col_name' => 'contamination_level',
                'unit' => '%',
                'periodicity' => 'monthly',
                'type' => 'qualitative',
                'description' => '0=safe, 1,2,3',
                'aggregate' => 'pct_active',
                'legend' => [
                    ['value' => 'Safe', 'color' => '#4CAF50'],
                    ['value' => '1', 'color' => '#f4f136'],
                    ['value' => '2', 'color' => '#f4b836'],
                    ['value' => '3', 'color' => '#F44336'],
                ],
                'individual_objective' => 0,
            ],
            [
                'name' => 'Profitable',
                'col_name' => 'is_profitable',
                'unit' => '%',
                'periodicity' => 'monthly',
                'type' => 'qualitative',
                'description' => 'True if site revenue - site expense + salary entrepreneur >= 200',
                'aggregate' => 'pct_active',
                'default_objective' => 100,
                'legend' => [
                    ['value' => 'Profitable', 'color' => '#4CAF50'],
                    ['value' => 'Not Profitable', 'color' => '#F44336'],
                ],
            ],
            [
                'name' => 'EC Collection',
                'col_name' => 'ec_collection',
                'unit' => '%',
                'periodicity' => 'monthly',
                'type' => 'qualitative',
                'description' => 'Percentage of active sites where paid >= amount_expenses for entrepreneur_contribution expenses',
                'aggregate' => 'pct_active',
                'default_objective' => 100,
            ],
            [
                'name' => 'Water Loss',
                'col_name' => 'water_loss',
                'unit' => '%',
                'periodicity' => 'monthly',
                'type' => 'quantitative',
                'description' => 'Water loss percentage: (Water_Consume - (Total_Sales * 20)) / Water_Consume * 100',
                'aggregate' => 'avg',
                'default_objective' => 20,
            ],
            [
                'name' => 'Water Loss OK',
                'col_name' => 'is_water_loss_ok',
                'unit' => '%',
                'periodicity' => 'monthly',
                'type' => 'qualitative',
                'description' => '0 if water_loss is between 15-25%, 1 otherwise, null if no data',
                'aggregate' => 'pct_active',
                'default_objective' => 100,
                'legend' => [
                    ['value' => 'OK', 'color' => '#4CAF50'],
                    ['value' => 'Not OK', 'color' => '#F44336'],
                ],
            ],
            [
                'name' => 'Data Collection Status',
                'col_name' => 'data_collection',
                'unit' => '%',
                'periodicity' => 'monthly',
                'type' => 'qualitative',
                'description' => '0=no data, 1=partial (expense+sales+water), 2=all collected',
                'aggregate' => 'avg',
                'legend' => [
                    ['value' => 'Complete', 'color' => '#4CAF50'],
                    ['value' => 'Partial', 'color' => '#FFC107'],
                    ['value' => 'None', 'color' => '#F44336'],
                ],
            ],
            [
                'name' => 'Water Source',
                'col_name' => 'water_source',
                'unit' => '%',
                'periodicity' => 'monthly',
                'type' => 'qualitative',
                'description' => 'Normalized water source: pond, river, well, pipe',
                'aggregate' => 'avg',
                'legend' => [
                    ['value' => 'pipe', 'color' => '#2196F3'],
                    ['value' => 'well', 'color' => '#795548'],
                    ['value' => 'river', 'color' => '#00BCD4'],
                    ['value' => 'pond', 'color' => '#009688'],
                ],
            ],
            [
                'name' => 'Treatment Process',
                'col_name' => 'treatment_process',
                'unit' => 'type',
                'periodicity' => 'monthly',
                'type' => 'qualitative',
                'description' => 'Treatment process used at the site',
                'aggregate' => 'avg',
                'legend' => [
                    ['value' => 'Blue Tank', 'color' => '#2196F3'],
                    ['value' => 'Cement Tank', 'color' => '#795548'],
                    ['value' => 'Kiosk 2.0', 'color' => '#4CAF50'],
                    ['value' => '600+', 'color' => '#009688'],
                ],
            ],
        ];

        foreach ($kpis as $kpi) {
            $objective = null;
            if (isset($kpi['default_objective'])) {
                $objective = $kpi['default_objective'];
                unset($kpi['default_objective']);
            }
            $individual_objective = null;
            if (isset($kpi['individual_objective'])) {
                $individual_objective = $kpi['individual_objective'];
                unset($kpi['individual_objective']);
            }
            $kpiModel = Kpi::updateOrCreate(
                ['col_name' => $kpi['col_name']],
                $kpi
            );
            if ($objective && ! $kpiModel->objectives()->where('value', $objective)->exists()) {
                $kpiModel->objectives()->save(new Objective([
                    'start_date' => Carbon::now()->addYears(-20),
                    'value' => $objective,
                ]));
            }
            if ($individual_objective && ! $kpiModel->objectives()->where('value', $individual_objective)->exists()) {
                $kpiModel->objectives()->save(new Objective([
                    'start_date' => Carbon::now()->addYears(-20),
                    'value' => $individual_objective,
                    'type' => 'individual',
                ]));
            }
        }

        Artisan::call('sims3:import-dimensions');
    }
}
