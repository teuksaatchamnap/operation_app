<?php

namespace Tests\Feature;

use App\Models\Kpi;
use App\Models\User;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Tests\TestCase;

class KpiControllerTest extends TestCase
{
    use RefreshDatabase;

    public function test_unauthenticated_request_fails(): void
    {
        $this->getJson('/api/kpis')->assertUnauthorized();
    }

    public function test_can_list_all_kpis(): void
    {
        $user = User::factory()->create();

        Kpi::create([
            'name' => 'Revenue',
            'col_name' => 'revenue',
            'unit' => 'USD',
            'periodicity' => 'monthly',
            'type' => 'quantitative',
        ]);

        Kpi::create([
            'name' => 'Customer Satisfaction',
            'col_name' => 'csat',
            'unit' => 'score',
            'periodicity' => 'year to date',
            'type' => 'qualitative',
        ]);

        $response = $this->actingAs($user)->getJson('/api/kpis');

        $response->assertStatus(200);
        $response->assertJsonCount(2);
        $response->assertJsonFragment(['name' => 'Revenue']);
        $response->assertJsonFragment(['name' => 'Customer Satisfaction']);
    }

    public function test_can_create_a_kpi(): void
    {
        $user = User::factory()->create();

        $payload = [
            'name' => 'Churn Rate',
            'col_name' => 'churn_rate',
            'unit' => 'percentage',
            'periodicity' => 'monthly',
            'type' => 'calculated',
        ];

        $response = $this->actingAs($user)->postJson('/api/kpis', $payload);

        $response->assertStatus(201);
        $response->assertJsonFragment($payload);
        $this->assertDatabaseHas('kpis', $payload);
    }

    public function test_can_show_a_kpi(): void
    {
        $user = User::factory()->create();

        $kpi = Kpi::create([
            'name' => 'NPS',
            'col_name' => 'nps',
            'unit' => 'score',
            'periodicity' => 'year to date',
            'type' => 'qualitative',
        ]);

        $response = $this->actingAs($user)->getJson("/api/kpis/{$kpi->id}");

        $response->assertStatus(200);
        $response->assertJsonFragment(['name' => 'NPS']);
    }

    public function test_can_update_a_kpi(): void
    {
        $user = User::factory()->create();

        $kpi = Kpi::create([
            'name' => 'Revenue',
            'col_name' => 'revenue',
            'unit' => 'USD',
            'periodicity' => 'monthly',
            'type' => 'quantitative',
        ]);

        $response = $this->actingAs($user)->putJson("/api/kpis/{$kpi->id}", [
            'name' => 'Gross Revenue',
            'unit' => 'EUR',
        ]);

        $response->assertStatus(200);
        $response->assertJsonFragment(['name' => 'Gross Revenue', 'unit' => 'EUR']);
        $this->assertDatabaseHas('kpis', ['id' => $kpi->id, 'name' => 'Gross Revenue', 'unit' => 'EUR']);
    }

    public function test_can_delete_a_kpi(): void
    {
        $user = User::factory()->create();

        $kpi = Kpi::create([
            'name' => 'Revenue',
            'col_name' => 'revenue',
            'unit' => 'USD',
            'periodicity' => 'monthly',
            'type' => 'quantitative',
        ]);

        $response = $this->actingAs($user)->deleteJson("/api/kpis/{$kpi->id}");

        $response->assertStatus(204);
        $this->assertDatabaseMissing('kpis', ['id' => $kpi->id]);
    }
}
