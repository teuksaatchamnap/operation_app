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

    public function test_can_filter_by_multiple_platform_ids(): void
    {
        $user = User::factory()->create();
        $this->actingAs($user)
            ->getJson('/api/fact-monthly?platform_ids[]=1&platform_ids[]=2')
            ->assertSuccessful();
    }

    public function test_can_filter_by_multiple_advisor_ids(): void
    {
        $user = User::factory()->create();
        $this->actingAs($user)
            ->getJson('/api/fact-monthly?advisor_ids[]=1&advisor_ids[]=2')
            ->assertSuccessful();
    }

    public function test_can_filter_by_multiple_site_ids(): void
    {
        $user = User::factory()->create();
        $this->actingAs($user)
            ->getJson('/api/fact-monthly?site_ids[]=1&site_ids[]=2&site_ids[]=3')
            ->assertSuccessful();
    }

    public function test_can_select_kpi_columns(): void
    {
        $user = User::factory()->create();
        $this->actingAs($user)
            ->getJson('/api/fact-monthly?kpis=revenue,sales_volume')
            ->assertSuccessful();
    }

    public function test_can_combine_array_filters_and_kpis(): void
    {
        $user = User::factory()->create();
        $this->actingAs($user)
            ->getJson('/api/fact-monthly?year=2025&platform_ids[]=1&platform_ids[]=2&site_ids[]=5&advisor_ids[]=1&kpis=revenue,sales_volume,consumers')
            ->assertSuccessful();
    }

    public function test_platform_ids_must_be_array(): void
    {
        $user = User::factory()->create();
        $this->actingAs($user)
            ->getJson('/api/fact-monthly?platform_ids=1')
            ->assertUnprocessable();
    }

    public function test_advisor_ids_must_be_array(): void
    {
        $user = User::factory()->create();
        $this->actingAs($user)
            ->getJson('/api/fact-monthly?advisor_ids=1')
            ->assertUnprocessable();
    }

    public function test_site_ids_must_be_array(): void
    {
        $user = User::factory()->create();
        $this->actingAs($user)
            ->getJson('/api/fact-monthly?site_ids=1')
            ->assertUnprocessable();
    }
}
