<?php

namespace Tests\Feature;

use App\Models\FactMonthly;
use App\Models\Site;
use App\Models\User;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Tests\TestCase;

class FactMonthlyControllerTest extends TestCase
{
    use RefreshDatabase;

    public function test_unauthenticated_request_fails(): void
    {
        $this->getJson('/api/fact-monthly')->assertUnauthorized();
    }

    public function test_can_fetch_fact_monthly_without_filters(): void
    {
        $user = User::factory()->create();
        $this->actingAs($user)->getJson('/api/fact-monthly?kpis=revenue')->assertSuccessful();
    }

    public function test_can_filter_by_year(): void
    {
        $user = User::factory()->create();
        $this->actingAs($user)
            ->getJson('/api/fact-monthly?year=2026&kpis=revenue')
            ->assertSuccessful();
    }

    public function test_can_filter_by_month(): void
    {
        $user = User::factory()->create();
        $this->actingAs($user)
            ->getJson('/api/fact-monthly?month=2025-01&kpis=revenue')
            ->assertSuccessful();
    }

    public function test_can_filter_by_multiple_platform_ids(): void
    {
        $user = User::factory()->create();
        $this->actingAs($user)
            ->getJson('/api/fact-monthly?platform_ids[]=1&platform_ids[]=2&kpis=revenue')
            ->assertSuccessful();
    }

    public function test_can_filter_by_multiple_advisor_ids(): void
    {
        $user = User::factory()->create();
        $this->actingAs($user)
            ->getJson('/api/fact-monthly?advisor_ids[]=1&advisor_ids[]=2&kpis=revenue')
            ->assertSuccessful();
    }

    public function test_can_filter_by_multiple_site_ids(): void
    {
        $user = User::factory()->create();
        $this->actingAs($user)
            ->getJson('/api/fact-monthly?site_ids[]=1&site_ids[]=2&site_ids[]=3&kpis=revenue')
            ->assertSuccessful();
    }

    public function test_can_combine_array_filters_and_kpi(): void
    {
        $user = User::factory()->create();
        $this->actingAs($user)
            ->getJson('/api/fact-monthly?year=2025&platform_ids[]=1&platform_ids[]=2&site_ids[]=5&advisor_ids[]=1&kpis=revenue')
            ->assertSuccessful();
    }

    public function test_platform_ids_must_be_array(): void
    {
        $user = User::factory()->create();
        $this->actingAs($user)
            ->getJson('/api/fact-monthly?platform_ids=1&kpis=revenue')
            ->assertUnprocessable();
    }

    public function test_advisor_ids_must_be_array(): void
    {
        $user = User::factory()->create();
        $this->actingAs($user)
            ->getJson('/api/fact-monthly?advisor_ids=1&kpis=revenue')
            ->assertUnprocessable();
    }

    public function test_site_ids_must_be_array(): void
    {
        $user = User::factory()->create();
        $this->actingAs($user)
            ->getJson('/api/fact-monthly?site_ids=1&kpis=revenue')
            ->assertUnprocessable();
    }

    public function test_kpis_is_required(): void
    {
        $user = User::factory()->create();
        $this->actingAs($user)
            ->getJson('/api/fact-monthly')
            ->assertUnprocessable();
    }

    // -- year_to_date tests --

    public function test_year_to_date_requires_month_or_year(): void
    {
        $user = User::factory()->create();
        $this->actingAs($user)
            ->getJson('/api/fact-monthly?kpis=revenue&year_to_date=1')
            ->assertUnprocessable();
    }

    public function test_year_to_date_without_aggregate_groups_by_dimensions(): void
    {
        $user = User::factory()->create();
        $this->actingAs($user)
            ->getJson('/api/fact-monthly?month=2025-06&kpis=revenue&year_to_date=1')
            ->assertSuccessful();
    }

    public function test_year_to_date_with_aggregate_returns_single_result(): void
    {
        $user = User::factory()->create();
        $this->actingAs($user)
            ->getJson('/api/fact-monthly?month=2025-06&kpis=revenue&aggregate=sum&year_to_date=1')
            ->assertSuccessful();
    }

    public function test_year_to_date_with_year_filters_full_year(): void
    {
        $user = User::factory()->create();
        $this->actingAs($user)
            ->getJson('/api/fact-monthly?year=2025&kpis=revenue&year_to_date=1')
            ->assertSuccessful();
    }

    // -- latest_available tests --

    public function test_latest_available_requires_aggregate(): void
    {
        $user = User::factory()->create();
        $this->actingAs($user)
            ->getJson('/api/fact-monthly?kpis=revenue&latest_available=1&year=2025')
            ->assertUnprocessable();
    }

    public function test_latest_available_requires_month_or_year(): void
    {
        $user = User::factory()->create();
        $this->actingAs($user)
            ->getJson('/api/fact-monthly?kpis=revenue&latest_available=1&aggregate=sum')
            ->assertUnprocessable();
    }

    public function test_latest_available_mutually_exclusive_with_year_to_date(): void
    {
        $user = User::factory()->create();
        $this->actingAs($user)
            ->getJson('/api/fact-monthly?kpis=revenue&latest_available=1&year_to_date=1&aggregate=sum&year=2025')
            ->assertUnprocessable();
    }

    public function test_latest_available_returns_sum_of_latest_non_null_per_site(): void
    {
        $site1 = Site::factory()->create();
        $site2 = Site::factory()->create();

        FactMonthly::factory()->create([
            'site_id' => $site1->id,
            'month' => '2025-01-01',
            'revenue' => 1000,
            'active' => 1,
        ]);
        FactMonthly::factory()->create([
            'site_id' => $site1->id,
            'month' => '2025-02-01',
            'revenue' => 2000,
            'active' => 1,
        ]);
        FactMonthly::factory()->create([
            'site_id' => $site1->id,
            'month' => '2025-03-01',
            'revenue' => null,
            'active' => 1,
        ]);
        FactMonthly::factory()->create([
            'site_id' => $site2->id,
            'month' => '2025-01-01',
            'revenue' => null,
            'active' => 1,
        ]);
        FactMonthly::factory()->create([
            'site_id' => $site2->id,
            'month' => '2025-02-01',
            'revenue' => 500,
            'active' => 1,
        ]);

        $user = User::factory()->create();
        $response = $this->actingAs($user)
            ->getJson('/api/fact-monthly?kpis=revenue&latest_available=1&aggregate=sum&year=2025')
            ->assertSuccessful();

        $data = $response->json();
        $this->assertEquals(2500.0, $data[0]['revenue']);
    }

    public function test_latest_available_ignores_month_and_uses_year(): void
    {
        $site = Site::factory()->create();

        FactMonthly::factory()->create([
            'site_id' => $site->id,
            'month' => '2025-03-01',
            'revenue' => 3000,
            'active' => 1,
        ]);

        $user = User::factory()->create();
        $response = $this->actingAs($user)
            ->getJson('/api/fact-monthly?kpis=revenue&latest_available=1&aggregate=sum&month=2025-01')
            ->assertSuccessful();

        $data = $response->json();
        $this->assertEquals(3000.0, $data[0]['revenue']);
    }

    public function test_latest_available_with_avg(): void
    {
        $site1 = Site::factory()->create();
        $site2 = Site::factory()->create();

        FactMonthly::factory()->create([
            'site_id' => $site1->id,
            'month' => '2025-02-01',
            'revenue' => 2000,
            'active' => 1,
        ]);
        FactMonthly::factory()->create([
            'site_id' => $site2->id,
            'month' => '2025-01-01',
            'revenue' => 4000,
            'active' => 1,
        ]);

        $user = User::factory()->create();
        $response = $this->actingAs($user)
            ->getJson('/api/fact-monthly?kpis=revenue&latest_available=1&aggregate=avg&year=2025')
            ->assertSuccessful();

        $data = $response->json();
        $this->assertEquals(3000.0, $data[0]['revenue']);
    }

    public function test_latest_available_skips_sites_with_all_null(): void
    {
        $site1 = Site::factory()->create();
        $site2 = Site::factory()->create();

        FactMonthly::factory()->create([
            'site_id' => $site1->id,
            'month' => '2025-01-01',
            'revenue' => 1000,
            'active' => 1,
        ]);
        FactMonthly::factory()->create([
            'site_id' => $site2->id,
            'month' => '2025-01-01',
            'revenue' => null,
            'active' => 1,
        ]);

        $user = User::factory()->create();
        $response = $this->actingAs($user)
            ->getJson('/api/fact-monthly?kpis=revenue&latest_available=1&aggregate=sum&year=2025')
            ->assertSuccessful();

        $data = $response->json();
        $this->assertEquals(1000.0, $data[0]['revenue']);
    }

    // -- pct_active tests --

    public function test_pct_active_returns_percentage_of_active_sites(): void
    {
        $site1 = Site::factory()->create();
        $site2 = Site::factory()->create();
        $site3 = Site::factory()->create();

        // Site 1: active with who_compliance = 1
        FactMonthly::factory()->create([
            'site_id' => $site1->id,
            'month' => '2025-01-01',
            'who_compliance' => 1,
            'active' => 1,
        ]);

        // Site 2: active with who_compliance = 0
        FactMonthly::factory()->create([
            'site_id' => $site2->id,
            'month' => '2025-01-01',
            'who_compliance' => 0,
            'active' => 1,
        ]);

        // Site 3: not active (should be excluded from calculation)
        FactMonthly::factory()->create([
            'site_id' => $site3->id,
            'month' => '2025-01-01',
            'who_compliance' => 1,
            'active' => null,
        ]);

        $user = User::factory()->create();
        $response = $this->actingAs($user)
            ->getJson('/api/fact-monthly?kpis=who_compliance&aggregate=pct_active&month=2025-01')
            ->assertSuccessful();

        $data = $response->json();
        // 1 out of 2 active sites has who_compliance = 1 -> 50%
        $this->assertEquals(50.0, $data[0]['who_compliance']);
    }

    public function test_pct_active_with_latest_available_returns_percentage(): void
    {
        $site1 = Site::factory()->create();
        $site2 = Site::factory()->create();
        $site3 = Site::factory()->create();

        // Site 1: active, latest who_compliance = 1 (in March)
        FactMonthly::factory()->create([
            'site_id' => $site1->id,
            'month' => '2025-01-01',
            'who_compliance' => 0,
            'active' => 1,
        ]);
        FactMonthly::factory()->create([
            'site_id' => $site1->id,
            'month' => '2025-03-01',
            'who_compliance' => 1,
            'active' => 1,
        ]);

        // Site 2: active, latest who_compliance = 0 (in February)
        FactMonthly::factory()->create([
            'site_id' => $site2->id,
            'month' => '2025-02-01',
            'who_compliance' => 0,
            'active' => 1,
        ]);

        // Site 3: has who_compliance but never active (should be excluded by the fix)
        FactMonthly::factory()->create([
            'site_id' => $site3->id,
            'month' => '2025-01-01',
            'who_compliance' => 1,
            'active' => null,
        ]);

        $user = User::factory()->create();
        $response = $this->actingAs($user)
            ->getJson('/api/fact-monthly?kpis=who_compliance&aggregate=pct_active&latest_available=1&year=2025')
            ->assertSuccessful();

        $data = $response->json();
        // 1 out of 2 active sites has who_compliance = 1 (50%), site3 is excluded
        $this->assertEquals(50.0, $data[0]['who_compliance']);
    }

    public function test_pct_active_excludes_sites_without_active_data(): void
    {
        $site1 = Site::factory()->create();
        $site2 = Site::factory()->create();

        // Site 1: active with is_profitable = 1
        FactMonthly::factory()->create([
            'site_id' => $site1->id,
            'month' => '2025-06-01',
            'is_profitable' => 1,
            'active' => 1,
        ]);

        // Site 2: has is_profitable but no active data (would have caused 5200% before fix)
        FactMonthly::factory()->create([
            'site_id' => $site2->id,
            'month' => '2025-06-01',
            'is_profitable' => 1,
            'active' => null,
        ]);

        $user = User::factory()->create();
        $response = $this->actingAs($user)
            ->getJson('/api/fact-monthly?kpis=is_profitable&aggregate=pct_active&month=2025-06')
            ->assertSuccessful();

        $data = $response->json();
        // Only site1 is active, it has is_profitable = 1 -> 100%
        // Site2 is excluded because active is null
        $this->assertEquals(100.0, $data[0]['is_profitable']);
    }
}
