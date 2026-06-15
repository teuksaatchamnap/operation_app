<?php

namespace Tests\Feature;

use App\Models\Kpi;
use App\Models\User;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Tests\TestCase;

class ObjectiveControllerTest extends TestCase
{
    use RefreshDatabase;

    public function test_unauthenticated_request_fails(): void
    {
        $kpi = Kpi::create([
            'name' => 'Revenue',
            'col_name' => 'revenue',
            'unit' => 'USD',

            'type' => 'quantitative',
        ]);

        $this->postJson("/api/kpis/{$kpi->id}/objectives", [
            'start_date' => '2026-01-01',
            'end_date' => '2026-12-31',
            'value' => 100,
            'type' => 'global',
        ])->assertUnauthorized();
    }

    public function test_can_create_an_objective(): void
    {
        $user = User::factory()->create();

        $kpi = Kpi::create([
            'name' => 'Revenue',
            'col_name' => 'revenue',
            'unit' => 'USD',

            'type' => 'quantitative',
        ]);

        $payload = [
            'start_date' => '2026-01-01',
            'end_date' => '2026-12-31',
            'value' => 100000,
            'type' => 'global',
        ];

        $response = $this->actingAs($user)->postJson("/api/kpis/{$kpi->id}/objectives", $payload);

        $response->assertStatus(201);
        $response->assertJsonFragment([
            'kpi_id' => $kpi->id,
            'start_date' => '2026-01-01T00:00:00.000000Z',
            'end_date' => '2026-12-31T00:00:00.000000Z',
            'value' => 100000,
            'type' => 'global',
        ]);
        $this->assertDatabaseHas('objectives', [
            'kpi_id' => $kpi->id,
            'start_date' => '2026-01-01',
            'end_date' => '2026-12-31',
            'value' => '100000.00',
            'type' => 'global',
        ]);
    }

    public function test_cannot_create_objective_for_nonexistent_kpi(): void
    {
        $user = User::factory()->create();

        $response = $this->actingAs($user)->postJson('/api/kpis/999/objectives', [
            'start_date' => '2026-01-01',
            'end_date' => '2026-12-31',
            'value' => 100,
        ]);

        $response->assertStatus(404);
    }

    public function test_cannot_create_objective_with_invalid_dates(): void
    {
        $user = User::factory()->create();

        $kpi = Kpi::create([
            'name' => 'Revenue',
            'col_name' => 'revenue',
            'unit' => 'USD',

            'type' => 'quantitative',
        ]);

        $response = $this->actingAs($user)->postJson("/api/kpis/{$kpi->id}/objectives", [
            'start_date' => '2026-12-31',
            'end_date' => '2026-01-01',
            'value' => 100,
            'type' => 'global',
        ]);

        $response->assertStatus(422);
    }

    public function test_can_update_an_objective(): void
    {
        $user = User::factory()->create();

        $kpi = Kpi::create([
            'name' => 'Revenue',
            'col_name' => 'revenue',
            'unit' => 'USD',

            'type' => 'quantitative',
        ]);

        $objective = $kpi->objectives()->create([
            'start_date' => '2026-01-01',
            'end_date' => '2026-12-31',
            'value' => 100000,
            'type' => 'global',
        ]);

        $response = $this->actingAs($user)->putJson("/api/kpis/{$kpi->id}/objectives/{$objective->id}", [
            'value' => 150000,
        ]);

        $response->assertStatus(200);
        $response->assertJsonFragment([
            'id' => $objective->id,
            'kpi_id' => $kpi->id,
            'value' => 150000,
        ]);
        $this->assertDatabaseHas('objectives', [
            'id' => $objective->id,
            'value' => '150000.00',
        ]);
    }

    public function test_cannot_update_objective_for_nonexistent_kpi(): void
    {
        $user = User::factory()->create();

        $response = $this->actingAs($user)->putJson('/api/kpis/999/objectives/1', [
            'value' => 200,
            'type' => 'global',
        ]);

        $response->assertStatus(404);
    }

    public function test_can_delete_an_objective(): void
    {
        $user = User::factory()->create();

        $kpi = Kpi::create([
            'name' => 'Revenue',
            'col_name' => 'revenue',
            'unit' => 'USD',

            'type' => 'quantitative',
        ]);

        $objective = $kpi->objectives()->create([
            'start_date' => '2026-01-01',
            'end_date' => '2026-12-31',
            'value' => 100000,
            'type' => 'global',
        ]);

        $response = $this->actingAs($user)->deleteJson("/api/kpis/{$kpi->id}/objectives/{$objective->id}");

        $response->assertStatus(204);
        $this->assertDatabaseMissing('objectives', ['id' => $objective->id]);
    }

    public function test_cannot_delete_objective_for_nonexistent_kpi(): void
    {
        $user = User::factory()->create();

        $response = $this->actingAs($user)->deleteJson('/api/kpis/999/objectives/1');

        $response->assertStatus(404);
    }
}
