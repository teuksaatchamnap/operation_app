<?php

namespace Tests\Feature;

use App\Models\User;
use Tests\TestCase;

class FactMonthlyControllerTest extends TestCase
{

    public function test_unauthenticated_request_fails(): void
    {
        $this->getJson('/api/fact-monthly')->assertUnauthorized();
    }

    public function test_can_fetch_fact_monthly_without_filters(): void
    {
        $user = User::factory()->create();
        $this->actingAs($user)->getJson('/api/fact-monthly')->assertSuccessful();
    }

    public function test_can_filter_by_year(): void
    {
        $user = User::factory()->create();
        $this->actingAs($user)
            ->getJson('/api/fact-monthly?year=2026')
            ->assertSuccessful();
    }

    public function test_can_filter_by_month(): void
    {
        $user = User::factory()->create();
        $this->actingAs($user)
            ->getJson('/api/fact-monthly?month=2025-01')
            ->assertSuccessful();
    }

    public function test_can_filter_by_platform_id(): void
    {
        $user = User::factory()->create();
        $this->actingAs($user)
            ->getJson('/api/fact-monthly?platform_id=1')
            ->assertSuccessful();
    }

    public function test_can_filter_by_advisor_id(): void
    {
        $user = User::factory()->create();
        $this->actingAs($user)
            ->getJson('/api/fact-monthly?advisor_id=1')
            ->assertSuccessful();
    }

    public function test_can_filter_by_site_id(): void
    {
        $user = User::factory()->create();
        $this->actingAs($user)
            ->getJson('/api/fact-monthly?site_id=1')
            ->assertSuccessful();
    }

    public function test_can_select_kpi_columns(): void
    {
        $user = User::factory()->create();
        $this->actingAs($user)
            ->getJson('/api/fact-monthly?kpis=revenue,sales_volume')
            ->assertSuccessful();
    }

    public function test_can_combine_filters_and_kpis(): void
    {
        $user = User::factory()->create();
        $this->actingAs($user)
            ->getJson('/api/fact-monthly?year=2025&platform_id=1&kpis=revenue,consumers')
            ->assertSuccessful();
    }
}
