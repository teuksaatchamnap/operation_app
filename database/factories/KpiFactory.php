<?php

namespace Database\Factories;

use App\Models\Kpi;
use Illuminate\Database\Eloquent\Factories\Factory;

/**
 * @extends Factory<Kpi>
 */
class KpiFactory extends Factory
{
    protected $model = Kpi::class;

    public function definition(): array
    {
        return [
            'name' => fake()->word(),
            'col_name' => fake()->word(),
            'unit' => fake()->word(),
            'periodicity' => fake()->word(),
            'type' => fake()->word(),
        ];
    }
}
