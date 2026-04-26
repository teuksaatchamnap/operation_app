<?php

namespace Database\Factories;

use App\Models\FactMonthly;
use App\Models\Site;
use App\Models\Platform;
use App\Models\Advisor;
use Illuminate\Database\Eloquent\Factories\Factory;

/**
 * @extends Factory<FactMonthly>
 */
class FactMonthlyFactory extends Factory
{
    protected $model = FactMonthly::class;

    public function definition(): array
    {
        return [
            'site_id' => Site::factory(),
            'platform_id' => Platform::factory(),
            'advisor_id' => Advisor::factory(),
            'month' => fake()->date(),
            'tier' => fake()->word(),
            'sales_volume' => fake()->randomNumber(),
            'days_open' => fake()->randomNumber(),
            'expenses' => fake()->randomFloat(2),
            'revenue' => fake()->randomFloat(2),
            'workers' => fake()->randomNumber(),
            'consumers' => fake()->randomNumber(),
            'who_compliance' => fake()->boolean(),
            'profitable' => fake()->boolean(),
        ];
    }
}
