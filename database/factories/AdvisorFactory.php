<?php

namespace Database\Factories;

use App\Models\Advisor;
use Illuminate\Database\Eloquent\Factories\Factory;

/**
 * @extends Factory<Advisor>
 */
class AdvisorFactory extends Factory
{
    protected $model = Advisor::class;

    public function definition(): array
    {
        return [
            'name' => fake()->name(),
        ];
    }
}
