<?php

namespace Tests\Feature;

use App\Models\FactMonthly;
use App\Models\Kpi;
use App\Models\Platform;
use App\Models\Site;
use App\Models\User;
use Illuminate\Database\Eloquent\Builder;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Mockery;
use PHPUnit\Framework\Attributes\PreserveGlobalState;
use PHPUnit\Framework\Attributes\RunTestsInSeparateProcesses;
use Tests\TestCase;

#[RunTestsInSeparateProcesses]
#[PreserveGlobalState(false)]
class SiteAnalysisControllerTest extends TestCase
{
    use RefreshDatabase;

    /**
     * Set up a Sims3Site overload mock and return the data mock that
     * handles both static ::where() calls and instance getAttribute() calls.
     */
    private function mockSims3Site(string $siteName, array $attributes = []): object
    {
        $defaults = [
            'Id_Site' => $siteName,
            'Platform' => 'SW',
            'Entrepreneur_English_Name' => 'John Doe',
            'Date_start_working' => '2020-01-15',
            'Advisor_email' => 'advisor@test.com',
            'Commune' => 'Test Commune',
            'Population' => 5000,
            'Households' => 1000,
        ];
        $attrs = array_merge($defaults, $attributes);

        $mock = Mockery::mock('overload:App\Models\Sims3\Site');

        foreach ($attrs as $key => $value) {
            $mock->{$key} = $value;
        }

        $builderMock = Mockery::mock(Builder::class);
        $builderMock->shouldReceive('first')->andReturn($mock);
        $mock->shouldReceive('where')->with('Id_Site', $siteName)->andReturn($builderMock);

        return $mock;
    }

    // ------------------------------------------------------------------
    //  show()
    // ------------------------------------------------------------------

    public function test_show_unauthenticated(): void
    {
        $site = Site::factory()->create();

        $this->getJson("/api/sites/{$site->id}/analysis")->assertUnauthorized();
    }

    public function test_show_site_not_found_returns_404(): void
    {
        $user = User::factory()->create();
        $site = Site::factory()->create(['name' => 'NONEXISTENT']);

        $builderMock = Mockery::mock(Builder::class);
        $builderMock->shouldReceive('first')->andReturn(null);
        Mockery::mock('overload:App\Models\Sims3\Site')
            ->shouldReceive('where')->with('Id_Site', 'NONEXISTENT')->andReturn($builderMock);

        $this->actingAs($user)
            ->getJson("/api/sites/{$site->id}/analysis?month=2025-01")
            ->assertStatus(404)
            ->assertJson(['error' => 'Site not found in Sims3 database']);
    }

    public function test_show_returns_site_analysis_structure(): void
    {
        $user = User::factory()->create();
        $site = Site::factory()->create(['name' => 'SITE01']);

        FactMonthly::factory()->create([
            'site_id' => $site->id,
            'month' => '2025-01-01',
            'sales_volume' => 50000,
            'tier' => 'Gold',
            'days_open' => 26,
            'water_loss' => 5.0,
            'operators' => 2,
            'consumers' => 300,
            'penetration' => 0.45,
            'who_compliance' => 1,
        ]);

        Kpi::factory()->create(['col_name' => 'sales_volume', 'name' => 'Sales Volume']);
        Kpi::factory()->create(['col_name' => 'tier', 'name' => 'Tier']);
        Kpi::factory()->create(['col_name' => 'days_open', 'name' => 'Days Open']);
        Kpi::factory()->create(['col_name' => 'water_loss', 'name' => 'Water Loss']);
        Kpi::factory()->create(['col_name' => 'operators', 'name' => 'Operators']);
        Kpi::factory()->create(['col_name' => 'consumers', 'name' => 'Consumers']);
        Kpi::factory()->create(['col_name' => 'penetration', 'name' => 'Penetration']);
        Kpi::factory()->create(['col_name' => 'who_compliance', 'name' => 'WHO Compliance']);
        Kpi::factory()->create(['col_name' => 'bottles_per_day', 'name' => 'Bottles Per Day']);

        $this->mockSims3Site('SITE01');

        $platformBuilderMock = Mockery::mock(Builder::class);
        $platformBuilderMock->shouldReceive('value')->with('Mail_ROM')->andReturn('test@rom.com');
        Mockery::mock('overload:App\Models\Sims3\Platform')
            ->shouldReceive('where')->with('Code_Platform', 'SW')->andReturn($platformBuilderMock);

        $response = $this->actingAs($user)
            ->getJson("/api/sites/{$site->id}/analysis?month=2025-01");

        $response->assertSuccessful();
        $response->assertJsonStructure([
            'platform', 'entrepreneur_name', 'start_working_date', 'advisor_name',
            'rom_name', 'commune_name', 'population_commune', 'households', 'kpis',
        ]);
        $this->assertEquals('SW', $response->json('platform'));
        $this->assertEquals('John Doe', $response->json('entrepreneur_name'));
        $this->assertEquals('test@rom.com', $response->json('rom_name'));
        $this->assertEquals(5000, $response->json('population_commune'));
        $this->assertEquals(1000, $response->json('households'));
        $this->assertArrayHasKey('bottles_per_day_ytd', $response->json('kpis'));
        $this->assertArrayHasKey('sales_volume', $response->json('kpis'));
        $this->assertEquals(50000, $response->json('kpis.sales_volume.value'));
    }

    public function test_show_formats_who_compliance_as_safe_unsafe(): void
    {
        $user = User::factory()->create();
        $site = Site::factory()->create(['name' => 'SITE02']);

        FactMonthly::factory()->create([
            'site_id' => $site->id,
            'month' => '2025-01-01',
            'who_compliance' => 0,
        ]);
        Kpi::factory()->create(['col_name' => 'who_compliance', 'name' => 'WHO']);

        $this->mockSims3Site('SITE02', ['Platform' => null]);

        $response = $this->actingAs($user)
            ->getJson("/api/sites/{$site->id}/analysis?month=2025-01");

        $response->assertSuccessful();
        $this->assertEquals('Unsafe', $response->json('kpis.who_compliance.value'));
    }

    public function test_show_converts_penetration_to_percentage(): void
    {
        $user = User::factory()->create();
        $site = Site::factory()->create(['name' => 'SITE03']);

        FactMonthly::factory()->create([
            'site_id' => $site->id,
            'month' => '2025-01-01',
            'penetration' => 0.35,
        ]);
        Kpi::factory()->create(['col_name' => 'penetration', 'name' => 'Pen']);

        $this->mockSims3Site('SITE03', ['Platform' => null]);

        $response = $this->actingAs($user)
            ->getJson("/api/sites/{$site->id}/analysis?month=2025-01");

        $response->assertSuccessful();
        $this->assertEquals(35, $response->json('kpis.penetration.value'));
    }

    public function test_show_ytd_bottles_per_day_averages_year_to_date(): void
    {
        $user = User::factory()->create();
        $site = Site::factory()->create(['name' => 'SITE04']);

        FactMonthly::factory()->create([
            'site_id' => $site->id, 'month' => '2025-01-01',
            'sales_volume' => 1000, 'days_open' => 10, 'bottles_per_day' => 100,
        ]);
        FactMonthly::factory()->create([
            'site_id' => $site->id, 'month' => '2025-02-01',
            'sales_volume' => 1100, 'days_open' => 10, 'bottles_per_day' => 110,
        ]);
        FactMonthly::factory()->create([
            'site_id' => $site->id, 'month' => '2025-03-01',
            'sales_volume' => 1200, 'days_open' => 10, 'bottles_per_day' => 120,
        ]);
        Kpi::factory()->create(['col_name' => 'bottles_per_day', 'name' => 'BPD']);

        $this->mockSims3Site('SITE04', ['Platform' => null]);

        $response = $this->actingAs($user)
            ->getJson("/api/sites/{$site->id}/analysis?month=2025-03");

        $response->assertSuccessful();
        $this->assertEquals(110, $response->json('kpis.bottles_per_day_ytd.value'));
    }

    public function test_show_objective_individual_takes_priority(): void
    {
        $user = User::factory()->create();
        $site = Site::factory()->create(['name' => 'SITE05']);

        FactMonthly::factory()->create([
            'site_id' => $site->id,
            'month' => '2025-01-01',
            'sales_volume' => 50000,
        ]);
        $kpi = Kpi::factory()->create(['col_name' => 'sales_volume', 'name' => 'SV']);
        $kpi->objectives()->create(['start_date' => '2025-01-01', 'end_date' => null, 'value' => '45000', 'type' => 'general']);
        $kpi->objectives()->create(['start_date' => '2025-01-01', 'end_date' => null, 'value' => '48000', 'type' => 'individual']);

        $this->mockSims3Site('SITE05', ['Platform' => null]);

        $response = $this->actingAs($user)
            ->getJson("/api/sites/{$site->id}/analysis?month=2025-01");

        $response->assertSuccessful();
        $this->assertEquals(48000, $response->json('kpis.sales_volume.objective'));
    }

    // ------------------------------------------------------------------
    //  expenseBreakdown()
    // ------------------------------------------------------------------

    public function test_expense_breakdown_unauthenticated(): void
    {
        $site = Site::factory()->create();

        $this->getJson("/api/sites/{$site->id}/expense-breakdown")->assertUnauthorized();
    }

    public function test_expense_breakdown_site_not_found_returns_404(): void
    {
        $user = User::factory()->create();
        $site = Site::factory()->create(['name' => 'MISSING']);

        $builderMock = Mockery::mock(Builder::class);
        $builderMock->shouldReceive('first')->andReturn(null);
        Mockery::mock('overload:App\Models\Sims3\Site')
            ->shouldReceive('where')->with('Id_Site', 'MISSING')->andReturn($builderMock);

        $this->actingAs($user)
            ->getJson("/api/sites/{$site->id}/expense-breakdown?month=2025-01")
            ->assertStatus(404)
            ->assertJson(['error' => 'Site not found in Sims3 database']);
    }

    public function test_expense_breakdown_returns_all_categories(): void
    {
        $user = User::factory()->create();
        $site = Site::factory()->create(['name' => 'SITE10']);

        $this->mockSims3Site('SITE10');

        $expenseCollection = collect([
            (object) ['Ref_expenses' => 'electricity', 'Amount_expenses' => 100],
            (object) ['Ref_expenses' => 'raw_water', 'Amount_expenses' => 50],
            (object) ['Ref_expenses' => 'fix_salary_entrepreneurs', 'Amount_expenses' => 200],
        ]);

        $allExpenseCollection = collect([
            (object) ['Id_Site' => 'SITE10', 'Ref_expenses' => 'electricity', 'Amount_expenses' => 100],
            (object) ['Id_Site' => 'SITE10', 'Ref_expenses' => 'raw_water', 'Amount_expenses' => 50],
            (object) ['Id_Site' => 'SITE10', 'Ref_expenses' => 'fix_salary_entrepreneurs', 'Amount_expenses' => 200],
            (object) ['Id_Site' => 'OTHER', 'Ref_expenses' => 'electricity', 'Amount_expenses' => 80],
        ]);

        $expenseBuilder = Mockery::mock(Builder::class);
        $expenseBuilder->shouldReceive('whereYear')->andReturnSelf();
        $expenseBuilder->shouldReceive('whereMonth')->andReturnSelf();
        $expenseBuilder->shouldReceive('whereNotIn')->andReturnSelf();
        $expenseBuilder->shouldReceive('whereIn')->andReturnSelf();
        $expenseBuilder->shouldReceive('get')->andReturn($expenseCollection, $allExpenseCollection);

        $expenseMock = Mockery::mock('overload:App\Models\Sims3\Expense');
        $expenseMock->shouldReceive('where')->with('Id_Site', 'SITE10')->andReturn($expenseBuilder);
        $expenseMock->shouldReceive('whereYear')->andReturn($expenseBuilder);

        $response = $this->actingAs($user)
            ->getJson("/api/sites/{$site->id}/expense-breakdown?month=2025-01");

        $response->assertSuccessful();
        $response->assertJsonStructure(['expenses' => [['category', 'site_amount', 'avg_amount']]]);

        $categories = array_column($response->json('expenses'), 'category');
        $this->assertContains('Production', $categories);
        $this->assertContains('Salary', $categories);
        $this->assertContains('Delivery', $categories);
        $this->assertContains('Contribution', $categories);
        $this->assertContains('Intervention', $categories);
        $this->assertContains('Investment', $categories);
    }

    // ------------------------------------------------------------------
    //  monthlySalesBreakdown()
    // ------------------------------------------------------------------

    public function test_monthly_sales_breakdown_unauthenticated(): void
    {
        $site = Site::factory()->create();
        $this->getJson("/api/sites/{$site->id}/monthly-sales-breakdown")->assertUnauthorized();
    }

    public function test_monthly_sales_breakdown_site_not_found_returns_404(): void
    {
        $user = User::factory()->create();
        $site = Site::factory()->create(['name' => 'MISSING']);

        $builderMock = Mockery::mock(Builder::class);
        $builderMock->shouldReceive('first')->andReturn(null);
        Mockery::mock('overload:App\Models\Sims3\Site')
            ->shouldReceive('where')->with('Id_Site', 'MISSING')->andReturn($builderMock);

        $this->actingAs($user)
            ->getJson("/api/sites/{$site->id}/monthly-sales-breakdown")
            ->assertStatus(404);
    }

    public function test_monthly_sales_breakdown_returns_all_channels(): void
    {
        $user = User::factory()->create();
        $site = Site::factory()->create(['name' => 'SITE20']);

        $this->mockSims3Site('SITE20');

        $saleMock = Mockery::mock('overload:App\Models\Sims3\Sale');
        $saleMock->Hod_Sales = 100;
        $saleMock->Shopkeeper_Sales = 200;
        $saleMock->WiS_Sales = 50;
        $saleMock->Onsite_Sales = 75;
        $saleMock->Free_Sales = 10;
        $saleMock->Bottle_Sales = 300;
        $saleMock->Emergency_Sales = 25;
        $saleMock->Other_Sales = 5;

        $saleBuilder = Mockery::mock(Builder::class);
        $saleBuilder->shouldReceive('whereYear')->andReturnSelf();
        $saleBuilder->shouldReceive('whereMonth')->andReturnSelf();
        $saleBuilder->shouldReceive('first')->andReturn($saleMock);

        $saleMock->shouldReceive('where')->with('Id_Site', 'SITE20')->andReturn($saleBuilder);

        $response = $this->actingAs($user)
            ->getJson("/api/sites/{$site->id}/monthly-sales-breakdown?month=2025-01");

        $response->assertSuccessful();
        $response->assertJsonStructure(['breakdown' => [['label', 'value']]]);
        $this->assertCount(8, $response->json('breakdown'));
        $labels = array_column($response->json('breakdown'), 'label');
        $this->assertContains('Home Delivery', $labels);
        $this->assertContains('Shopkeeper', $labels);
        $this->assertContains('Bottle', $labels);
    }

    public function test_monthly_sales_breakdown_no_sale_returns_empty(): void
    {
        $user = User::factory()->create();
        $site = Site::factory()->create(['name' => 'SITE21']);

        $this->mockSims3Site('SITE21');

        $saleBuilder = Mockery::mock(Builder::class);
        $saleBuilder->shouldReceive('whereYear')->andReturnSelf();
        $saleBuilder->shouldReceive('whereMonth')->andReturnSelf();
        $saleBuilder->shouldReceive('first')->andReturnNull();

        Mockery::mock('overload:App\Models\Sims3\Sale')
            ->shouldReceive('where')->with('Id_Site', 'SITE21')->andReturn($saleBuilder);

        $response = $this->actingAs($user)
            ->getJson("/api/sites/{$site->id}/monthly-sales-breakdown?month=2025-01");

        $response->assertSuccessful();
        $this->assertEquals([], $response->json('breakdown'));
    }

    // ------------------------------------------------------------------
    //  channelPrices()
    // ------------------------------------------------------------------

    public function test_channel_prices_unauthenticated(): void
    {
        $site = Site::factory()->create();
        $this->getJson("/api/sites/{$site->id}/channel-prices")->assertUnauthorized();
    }

    public function test_channel_prices_site_not_found_returns_404(): void
    {
        $user = User::factory()->create();
        $site = Site::factory()->create(['name' => 'MISSING']);

        $builderMock = Mockery::mock(Builder::class);
        $builderMock->shouldReceive('first')->andReturn(null);
        Mockery::mock('overload:App\Models\Sims3\Site')
            ->shouldReceive('where')->with('Id_Site', 'MISSING')->andReturn($builderMock);

        $this->actingAs($user)
            ->getJson("/api/sites/{$site->id}/channel-prices")
            ->assertStatus(404);
    }

    public function test_channel_prices_returns_prices(): void
    {
        $user = User::factory()->create();
        $site = Site::factory()->create(['name' => 'SITE30']);

        $this->mockSims3Site('SITE30');

        $saleMock = Mockery::mock('overload:App\Models\Sims3\Sale');
        $saleMock->Hod_Price = 1.25;
        $saleMock->Shopkeeper_Price = 2.50;
        $saleMock->Onsite_Price = 1.00;
        $saleMock->WiS_Price = 0.75;

        $saleBuilder = Mockery::mock(Builder::class);
        $saleBuilder->shouldReceive('whereYear')->andReturnSelf();
        $saleBuilder->shouldReceive('whereMonth')->andReturnSelf();
        $saleBuilder->shouldReceive('first')->andReturn($saleMock);

        $saleMock->shouldReceive('where')->with('Id_Site', 'SITE30')->andReturn($saleBuilder);

        $response = $this->actingAs($user)
            ->getJson("/api/sites/{$site->id}/channel-prices?month=2025-01");

        $response->assertSuccessful();
        $response->assertJsonStructure(['prices' => [['label', 'price']]]);
        $this->assertCount(4, $response->json('prices'));
        $this->assertEquals(1.25, $response->json('prices')[0]['price']);
        $this->assertEquals(2.50, $response->json('prices')[1]['price']);
    }

    public function test_channel_prices_no_sale_returns_empty(): void
    {
        $user = User::factory()->create();
        $site = Site::factory()->create(['name' => 'SITE31']);

        $this->mockSims3Site('SITE31');

        $saleBuilder = Mockery::mock(Builder::class);
        $saleBuilder->shouldReceive('whereYear')->andReturnSelf();
        $saleBuilder->shouldReceive('whereMonth')->andReturnSelf();
        $saleBuilder->shouldReceive('first')->andReturnNull();

        Mockery::mock('overload:App\Models\Sims3\Sale')
            ->shouldReceive('where')->with('Id_Site', 'SITE31')->andReturn($saleBuilder);

        $response = $this->actingAs($user)
            ->getJson("/api/sites/{$site->id}/channel-prices?month=2025-01");

        $response->assertSuccessful();
        $this->assertEquals([], $response->json('prices'));
    }

    // ------------------------------------------------------------------
    //  bottlePurchases()
    // ------------------------------------------------------------------

    public function test_bottle_purchases_unauthenticated(): void
    {
        $site = Site::factory()->create();
        $this->getJson("/api/sites/{$site->id}/bottle-purchases")->assertUnauthorized();
    }

    public function test_bottle_purchases_site_not_found_returns_404(): void
    {
        $user = User::factory()->create();
        $site = Site::factory()->create(['name' => 'MISSING']);

        $builderMock = Mockery::mock(Builder::class);
        $builderMock->shouldReceive('first')->andReturn(null);
        Mockery::mock('overload:App\Models\Sims3\Site')
            ->shouldReceive('where')->with('Id_Site', 'MISSING')->andReturn($builderMock);

        $this->actingAs($user)
            ->getJson("/api/sites/{$site->id}/bottle-purchases")
            ->assertStatus(404);
    }

    public function test_bottle_purchases_returns_ytd_and_last_year(): void
    {
        $user = User::factory()->create();
        $site = Site::factory()->create(['name' => 'SITE40']);

        $this->mockSims3Site('SITE40');

        $saleBuilder = Mockery::mock(Builder::class);
        $saleBuilder->shouldReceive('where')->with(Mockery::any(), Mockery::any(), Mockery::any())->andReturnSelf();
        $saleBuilder->shouldReceive('sum')->with('Bottle_Sales')->andReturn(1500, 1200);

        Mockery::mock('overload:App\Models\Sims3\Sale')
            ->shouldReceive('where')->with('Id_Site', 'SITE40')->andReturn($saleBuilder);

        $response = $this->actingAs($user)
            ->getJson("/api/sites/{$site->id}/bottle-purchases?month=2025-01");

        $response->assertSuccessful();
        $this->assertEquals(1500, $response->json('ytd'));
        $this->assertEquals(1200, $response->json('last_year'));
    }

    // ------------------------------------------------------------------
    //  profitLoss()
    // ------------------------------------------------------------------

    public function test_profit_loss_unauthenticated(): void
    {
        $site = Site::factory()->create();
        $this->getJson("/api/sites/{$site->id}/profit-loss")->assertUnauthorized();
    }

    public function test_profit_loss_site_not_found_returns_404(): void
    {
        $user = User::factory()->create();
        $site = Site::factory()->create(['name' => 'MISSING']);

        $builderMock = Mockery::mock(Builder::class);
        $builderMock->shouldReceive('first')->andReturn(null);
        Mockery::mock('overload:App\Models\Sims3\Site')
            ->shouldReceive('where')->with('Id_Site', 'MISSING')->andReturn($builderMock);

        $this->actingAs($user)
            ->getJson("/api/sites/{$site->id}/profit-loss")
            ->assertStatus(404);
    }

    public function test_profit_loss_returns_all_periods(): void
    {
        $user = User::factory()->create();
        $site = Site::factory()->create(['name' => 'SITE50']);

        $this->mockSims3Site('SITE50');

        // Revenue builder: called via Sims3Sale::where('Id_Site', ..)->where(Month>=)->where(Month<=)
        $revenueBuilder = Mockery::mock(Builder::class);
        $revenueBuilder->shouldReceive('where')->andReturnSelf();
        $revenueBuilder->shouldReceive('sum')->with('Total_Income')->andReturn(10000, 9000, 50000, 48000);
        $revenueBuilder->shouldReceive('sum')->with('WiS_Income')->andReturn(1000, 800, 5000, 4000);

        // Expense builder: called via Sims3Expense::where('Id_Site', ..)->where(Month>=)->where(Month<=)
        $expenseBuilder = Mockery::mock(Builder::class);
        $expenseBuilder->shouldReceive('where')->andReturnSelf();
        $expenseBuilder->shouldReceive('whereNotIn')->andReturnSelf();
        $expenseBuilder->shouldReceive('whereIn')->andReturnSelf();
        $expenseBuilder->shouldReceive('get')->andReturn(collect([
            (object) ['Ref_expenses' => 'electricity', 'Amount_expenses' => 500],
            (object) ['Ref_expenses' => 'fix_salary_entrepreneurs', 'Amount_expenses' => 1000],
        ]));

        // Sale: two where() calls per period (Month>=, Month<=) after initial Id_Site where
        Mockery::mock('overload:App\Models\Sims3\Sale')
            ->shouldReceive('where')->with('Id_Site', 'SITE50')->andReturn($revenueBuilder);

        // Expense: whereNotIn/whereIn after Id_Site where and Month range wheres
        $expenseMock = Mockery::mock('overload:App\Models\Sims3\Expense');
        $expenseMock->shouldReceive('where')->with('Id_Site', 'SITE50')->andReturn($expenseBuilder);

        $response = $this->actingAs($user)
            ->getJson("/api/sites/{$site->id}/profit-loss?month=2025-03");

        $response->assertSuccessful();
        $response->assertJsonStructure([
            'labels' => ['current', 'previous', 'ytd', 'last_year'],
            'revenue' => ['sales', 'water_in_school', 'sub_total'],
            'expenses' => ['categories', 'sub_total'],
            'result',
            'entrepreneur_salary',
        ]);

        $data = $response->json();
        $this->assertArrayHasKey('current', $data['labels']);
        $this->assertArrayHasKey('current', $data['revenue']['sales']);
        $this->assertArrayHasKey('current', $data['revenue']['water_in_school']);
        $this->assertArrayHasKey('current', $data['revenue']['sub_total']);
        $this->assertArrayHasKey('current', $data['expenses']['sub_total']);
        $this->assertArrayHasKey('current', $data['result']);
        $this->assertArrayHasKey('current', $data['entrepreneur_salary']);

        $categories = array_column($data['expenses']['categories'], 'category');
        $this->assertContains('Production', $categories);
        $this->assertContains('Salary', $categories);
        $this->assertContains('Delivery', $categories);
    }

    // ------------------------------------------------------------------
    //  monthlyPerformance()
    // ------------------------------------------------------------------

    public function test_monthly_performance_unauthenticated(): void
    {
        $site = Site::factory()->create();
        $this->getJson("/api/sites/{$site->id}/monthly-performance")->assertUnauthorized();
    }

    public function test_monthly_performance_returns_6_year_series(): void
    {
        $user = User::factory()->create();
        $site = Site::factory()->create();

        $currentYear = now()->year;

        FactMonthly::factory()->create([
            'site_id' => $site->id,
            'month' => "{$currentYear}-06-01",
            'bottles_per_day' => 150,
        ]);

        $response = $this->actingAs($user)
            ->getJson("/api/sites/{$site->id}/monthly-performance");

        $response->assertSuccessful();
        $response->assertJsonStructure(['categories' => [], 'series' => [['name', 'data']]]);

        $series = $response->json('series');
        $this->assertCount(7, $series);
        $this->assertEquals(12, count($series[0]['data']));
        $this->assertEquals((string) $currentYear, $series[count($series) - 2]['name']);
    }

    public function test_monthly_performance_fills_gaps_with_null(): void
    {
        $user = User::factory()->create();
        $site = Site::factory()->create();

        $currentYear = now()->year;

        FactMonthly::factory()->create([
            'site_id' => $site->id,
            'month' => "{$currentYear}-01-01",
            'bottles_per_day' => 100,
        ]);
        FactMonthly::factory()->create([
            'site_id' => $site->id,
            'month' => "{$currentYear}-03-01",
            'bottles_per_day' => 200,
        ]);

        $response = $this->actingAs($user)
            ->getJson("/api/sites/{$site->id}/monthly-performance");

        $response->assertSuccessful();
        $series = $response->json('series');
        $currentYearSeries = $series[count($series) - 2];
        $this->assertEquals(100, $currentYearSeries['data'][0]);
        $this->assertNull($currentYearSeries['data'][1]);
        $this->assertEquals(200, $currentYearSeries['data'][2]);
    }

    public function test_monthly_performance_no_data_returns_empty_series(): void
    {
        $user = User::factory()->create();
        $site = Site::factory()->create();

        $response = $this->actingAs($user)
            ->getJson("/api/sites/{$site->id}/monthly-performance");

        $response->assertSuccessful();
        $this->assertCount(7, $response->json('series'));

        $yearSeries = array_slice($response->json('series'), 0, 6);
        foreach ($yearSeries as $s) {
            $this->assertCount(12, $s['data']);
            $this->assertContainsOnly('null', $s['data']);
        }
    }

    // ------------------------------------------------------------------
    //  salesComparison()
    // ------------------------------------------------------------------

    public function test_sales_comparison_unauthenticated(): void
    {
        $site = Site::factory()->create();

        $this->getJson("/api/sites/{$site->id}/sales-comparison")->assertUnauthorized();
    }

    public function test_sales_comparison_site_not_found_returns_404(): void
    {
        $user = User::factory()->create();
        $site = Site::factory()->create(['name' => 'MISSING']);

        $builderMock = Mockery::mock(Builder::class);
        $builderMock->shouldReceive('first')->andReturn(null);
        Mockery::mock('overload:App\Models\Sims3\Site')
            ->shouldReceive('where')->with('Id_Site', 'MISSING')->andReturn($builderMock);

        $this->actingAs($user)
            ->getJson("/api/sites/{$site->id}/sales-comparison")
            ->assertStatus(404)
            ->assertJson(['error' => 'Site not found in Sims3 database']);
    }

    public function test_sales_comparison_returns_structure(): void
    {
        $user = User::factory()->create();
        $site = Site::factory()->create(['name' => 'SITE01']);
        $platform = Platform::factory()->create(['name' => 'SW']);

        $this->mockSims3Site('SITE01');

        FactMonthly::factory()->create([
            'site_id' => $site->id,
            'platform_id' => $platform->id,
            'month' => now()->startOfMonth(),
            'sales_volume' => 50000,
        ]);

        $response = $this->actingAs($user)
            ->getJson("/api/sites/{$site->id}/sales-comparison");

        $response->assertSuccessful();
        $response->assertJsonStructure([
            'categories',
            'series' => [
                ['name', 'data'],
                ['name', 'data'],
                ['name', 'data'],
                ['name', 'data'],
            ],
        ]);

        $series = $response->json('series');
        $this->assertCount(4, $series);
        $this->assertEquals('This Kiosk', $series[0]['name']);
        $this->assertEquals('Platform Avg', $series[1]['name']);
        $this->assertEquals('Network Avg', $series[2]['name']);
        $this->assertEquals('Objective', $series[3]['name']);
        $this->assertCount(12, $series[0]['data']);
        $this->assertCount(12, $response->json('categories'));
    }

    public function test_sales_comparison_includes_objective_line(): void
    {
        $user = User::factory()->create();
        $site = Site::factory()->create(['name' => 'SITE01']);
        $platform = Platform::factory()->create(['name' => 'SW']);

        $this->mockSims3Site('SITE01');

        $kpi = Kpi::factory()->create([
            'col_name' => 'sales_volume',
            'name' => 'Sales Volume',
        ]);
        $kpi->objectives()->create([
            'start_date' => now()->startOfYear(),
            'value' => 3000,
            'type' => 'individual',
        ]);

        FactMonthly::factory()->create([
            'site_id' => $site->id,
            'platform_id' => $platform->id,
            'month' => now()->startOfMonth(),
            'sales_volume' => 50000,
        ]);

        $response = $this->actingAs($user)
            ->getJson("/api/sites/{$site->id}/sales-comparison");

        $response->assertSuccessful();
        $series = $response->json('series');

        $this->assertCount(4, $series);
        $this->assertEquals('Objective', $series[3]['name']);

        $categories = $response->json('categories');
        $targetLabel = now()->startOfMonth()->format('M Y');
        $monthIndex = array_search($targetLabel, $categories);
        $this->assertNotFalse($monthIndex);
        $this->assertEquals(3000, $series[3]['data'][$monthIndex]);
    }

    // ------------------------------------------------------------------
    //  waterLossByWeek()
    // ------------------------------------------------------------------

    public function test_water_loss_by_week_unauthenticated(): void
    {
        $site = Site::factory()->create();

        $this->getJson("/api/sites/{$site->id}/water-loss-by-week")->assertUnauthorized();
    }

    public function test_water_loss_by_week_site_not_found_returns_404(): void
    {
        $user = User::factory()->create();
        $site = Site::factory()->create(['name' => 'MISSING']);

        $builderMock = Mockery::mock(Builder::class);
        $builderMock->shouldReceive('first')->andReturn(null);
        Mockery::mock('overload:App\Models\Sims3\Site')
            ->shouldReceive('where')->with('Id_Site', 'MISSING')->andReturn($builderMock);

        $this->actingAs($user)
            ->getJson("/api/sites/{$site->id}/water-loss-by-week")
            ->assertStatus(404)
            ->assertJson(['error' => 'Site not found in Sims3 database']);
    }

    public function test_water_loss_by_week_returns_weekly_data(): void
    {
        $user = User::factory()->create();
        $site = Site::factory()->create(['name' => 'SITE01']);

        $this->mockSims3Site('SITE01');

        $meterData = collect([
            (object) ['site' => 'SITE01', 'date' => '2025-01-01', 'value' => 10.0],
            (object) ['site' => 'SITE01', 'date' => '2025-01-08', 'value' => 25.0],
            (object) ['site' => 'SITE01', 'date' => '2025-01-15', 'value' => 45.0],
            (object) ['site' => 'SITE01', 'date' => '2025-01-22', 'value' => 70.0],
            (object) ['site' => 'SITE01', 'date' => '2025-01-29', 'value' => 100.0],
            (object) ['site' => 'SITE01', 'date' => '2025-02-01', 'value' => 135.0],
        ]);

        $meterBuilder = Mockery::mock(Builder::class);
        $meterBuilder->shouldReceive('whereBetween')->andReturnSelf();
        $meterBuilder->shouldReceive('orderBy')->with('date')->andReturnSelf();
        $meterBuilder->shouldReceive('get')->andReturn($meterData);

        Mockery::mock('overload:App\Models\Sims3\WaterMeter')
            ->shouldReceive('where')->with('site', 'SITE01')->andReturn($meterBuilder);

        $dailySalesData = collect();
        for ($day = 1; $day <= 31; $day++) {
            $dailySalesData->push((object) [
                'Day' => sprintf('2025-01-%02d', $day),
                'Total_Sales' => 50,
            ]);
        }

        $dailySaleBuilder = Mockery::mock(Builder::class);
        $dailySaleBuilder->shouldReceive('whereYear')->andReturnSelf();
        $dailySaleBuilder->shouldReceive('whereMonth')->andReturnSelf();
        $dailySaleBuilder->shouldReceive('get')->andReturn($dailySalesData);

        Mockery::mock('overload:App\Models\Sims3\DailySale')
            ->shouldReceive('where')->with('Id_Site', 'SITE01')->andReturn($dailySaleBuilder);

        $response = $this->actingAs($user)
            ->getJson("/api/sites/{$site->id}/water-loss-by-week?month=2025-01");

        $response->assertSuccessful();
        $response->assertJsonStructure([
            'weeks' => [
                '*' => ['week', 'start_date', 'end_date', 'meter_start', 'meter_end', 'consumed', 'sold', 'loss', 'loss_pct'],
            ],
        ]);

        $weeks = $response->json('weeks');
        $this->assertCount(4, $weeks);

        // Pair 1: Jan 1 -> Jan 8, days 1-7 (7 days), meter (10.0 -> 25.0)
        $this->assertEquals(1, $weeks[0]['week']);
        $this->assertEquals('2025-01-01', $weeks[0]['start_date']);
        $this->assertEquals('2025-01-08', $weeks[0]['end_date']);
        $this->assertEquals(10.0, $weeks[0]['meter_start']);
        $this->assertEquals(25.0, $weeks[0]['meter_end']);
        $this->assertEquals(15000.0, $weeks[0]['consumed']);
        $this->assertEquals(7000.0, $weeks[0]['sold']);
        $this->assertEquals(8000.0, $weeks[0]['loss']);
        $this->assertEquals(53.33, $weeks[0]['loss_pct']);

        // Pair 2: Jan 8 -> Jan 15, days 8-14 (7 days), meter (25.0 -> 45.0)
        $this->assertEquals(2, $weeks[1]['week']);
        $this->assertEquals('2025-01-08', $weeks[1]['start_date']);
        $this->assertEquals('2025-01-15', $weeks[1]['end_date']);
        $this->assertEquals(25.0, $weeks[1]['meter_start']);
        $this->assertEquals(45.0, $weeks[1]['meter_end']);
        $this->assertEquals(20000.0, $weeks[1]['consumed']);
        $this->assertEquals(7000.0, $weeks[1]['sold']);
        $this->assertEquals(13000.0, $weeks[1]['loss']);
        $this->assertEquals(65.0, $weeks[1]['loss_pct']);

        // Pair 3: Jan 15 -> Jan 22, days 15-21 (7 days), meter (45.0 -> 70.0)
        $this->assertEquals(3, $weeks[2]['week']);
        $this->assertEquals('2025-01-15', $weeks[2]['start_date']);
        $this->assertEquals('2025-01-22', $weeks[2]['end_date']);
        $this->assertEquals(45.0, $weeks[2]['meter_start']);
        $this->assertEquals(70.0, $weeks[2]['meter_end']);
        $this->assertEquals(25000.0, $weeks[2]['consumed']);
        $this->assertEquals(7000.0, $weeks[2]['sold']);
        $this->assertEquals(18000.0, $weeks[2]['loss']);
        $this->assertEquals(72.0, $weeks[2]['loss_pct']);

        // Pair 4: Jan 22 -> Jan 29, days 22-28 (7 days), meter (70.0 -> 100.0)
        $this->assertEquals(4, $weeks[3]['week']);
        $this->assertEquals('2025-01-22', $weeks[3]['start_date']);
        $this->assertEquals('2025-01-29', $weeks[3]['end_date']);
        $this->assertEquals(70.0, $weeks[3]['meter_start']);
        $this->assertEquals(100.0, $weeks[3]['meter_end']);
        $this->assertEquals(30000.0, $weeks[3]['consumed']);
        $this->assertEquals(7000.0, $weeks[3]['sold']);
        $this->assertEquals(23000.0, $weeks[3]['loss']);
        $this->assertEqualsWithDelta(76.67, $weeks[3]['loss_pct'], 0.01);
    }

    public function test_water_loss_by_week_no_meter_data(): void
    {
        $user = User::factory()->create();
        $site = Site::factory()->create(['name' => 'SITE02']);

        $this->mockSims3Site('SITE02');

        $meterBuilder = Mockery::mock(Builder::class);
        $meterBuilder->shouldReceive('whereBetween')->andReturnSelf();
        $meterBuilder->shouldReceive('orderBy')->with('date')->andReturnSelf();
        $meterBuilder->shouldReceive('get')->andReturn(collect());

        Mockery::mock('overload:App\Models\Sims3\WaterMeter')
            ->shouldReceive('where')->with('site', 'SITE02')->andReturn($meterBuilder);

        $dailySaleBuilder = Mockery::mock(Builder::class);
        $dailySaleBuilder->shouldReceive('whereYear')->andReturnSelf();
        $dailySaleBuilder->shouldReceive('whereMonth')->andReturnSelf();
        $dailySaleBuilder->shouldReceive('get')->andReturn(collect());

        Mockery::mock('overload:App\Models\Sims3\DailySale')
            ->shouldReceive('where')->with('Id_Site', 'SITE02')->andReturn($dailySaleBuilder);

        $cashierBuilder = Mockery::mock(Builder::class);
        $cashierBuilder->shouldReceive('whereYear')->andReturnSelf();
        $cashierBuilder->shouldReceive('whereMonth')->andReturnSelf();
        $cashierBuilder->shouldReceive('get')->andReturn(collect());

        Mockery::mock('overload:App\Models\Sims3\CashierSale')
            ->shouldReceive('where')->with('site', 'SITE02')->andReturn($cashierBuilder);

        $response = $this->actingAs($user)
            ->getJson("/api/sites/{$site->id}/water-loss-by-week?month=2025-01");

        $response->assertSuccessful();
        $response->assertJson(['weeks' => []]);
    }

    // ------------------------------------------------------------------
    //  dailySales()
    // ------------------------------------------------------------------

    public function test_daily_sales_unauthenticated(): void
    {
        $site = Site::factory()->create();

        $this->getJson("/api/sites/{$site->id}/daily-sales")
            ->assertUnauthorized();
    }

    public function test_water_loss_by_week_readings_not_on_aligned_dates(): void
    {
        $user = User::factory()->create();
        $site = Site::factory()->create(['name' => 'SITE03']);

        $this->mockSims3Site('SITE03');

        $meterData = collect([
            (object) ['site' => 'SITE03', 'date' => '2026-05-07', 'value' => 703],
            (object) ['site' => 'SITE03', 'date' => '2026-05-14', 'value' => 729],
            (object) ['site' => 'SITE03', 'date' => '2026-05-21', 'value' => 742],
            (object) ['site' => 'SITE03', 'date' => '2026-05-28', 'value' => 760],
            (object) ['site' => 'SITE03', 'date' => '2026-06-04', 'value' => 785],
        ]);

        $meterBuilder = Mockery::mock(Builder::class);
        $meterBuilder->shouldReceive('whereBetween')->andReturnSelf();
        $meterBuilder->shouldReceive('orderBy')->with('date')->andReturnSelf();
        $meterBuilder->shouldReceive('get')->andReturn($meterData);

        Mockery::mock('overload:App\Models\Sims3\WaterMeter')
            ->shouldReceive('where')->with('site', 'SITE03')->andReturn($meterBuilder);

        $dailySalesData = collect();
        for ($day = 1; $day <= 31; $day++) {
            $dailySalesData->push((object) [
                'Day' => sprintf('2026-05-%02d', $day),
                'Total_Sales' => 50,
            ]);
        }
        $dailySalesData->push((object) ['Day' => '2026-06-01', 'Total_Sales' => 50]);
        $dailySalesData->push((object) ['Day' => '2026-06-02', 'Total_Sales' => 50]);
        $dailySalesData->push((object) ['Day' => '2026-06-03', 'Total_Sales' => 50]);

        $dailySaleBuilder = Mockery::mock(Builder::class);
        $dailySaleBuilder->shouldReceive('whereYear')->andReturnSelf();
        $dailySaleBuilder->shouldReceive('whereMonth')->andReturnSelf();
        $dailySaleBuilder->shouldReceive('get')->andReturn($dailySalesData);

        Mockery::mock('overload:App\Models\Sims3\DailySale')
            ->shouldReceive('where')->with('Id_Site', 'SITE03')->andReturn($dailySaleBuilder);

        $response = $this->actingAs($user)
            ->getJson("/api/sites/{$site->id}/water-loss-by-week?month=2026-05");

        $response->assertSuccessful();
        $response->assertJsonStructure([
            'weeks' => [
                '*' => ['week', 'start_date', 'end_date', 'meter_start', 'meter_end', 'consumed', 'sold', 'loss', 'loss_pct'],
            ],
        ]);

        $weeks = $response->json('weeks');
        $this->assertCount(3, $weeks);

        // Pair 1: May 7 -> May 14, days 7-13 (7 days), meter (703 -> 729)
        $this->assertEquals(1, $weeks[0]['week']);
        $this->assertEquals('2026-05-07', $weeks[0]['start_date']);
        $this->assertEquals('2026-05-14', $weeks[0]['end_date']);
        $this->assertEquals(703, $weeks[0]['meter_start']);
        $this->assertEquals(729, $weeks[0]['meter_end']);
        $this->assertEquals(26000.0, $weeks[0]['consumed']);
        $this->assertEquals(7000.0, $weeks[0]['sold']);
        $this->assertEquals(19000.0, $weeks[0]['loss']);
        $this->assertEqualsWithDelta(73.08, $weeks[0]['loss_pct'], 0.01);

        // Pair 2: May 14 -> May 21, days 14-20 (7 days), meter (729 -> 742)
        $this->assertEquals(2, $weeks[1]['week']);
        $this->assertEquals('2026-05-14', $weeks[1]['start_date']);
        $this->assertEquals('2026-05-21', $weeks[1]['end_date']);
        $this->assertEquals(729, $weeks[1]['meter_start']);
        $this->assertEquals(742, $weeks[1]['meter_end']);
        $this->assertEquals(13000.0, $weeks[1]['consumed']);
        $this->assertEquals(7000.0, $weeks[1]['sold']);
        $this->assertEquals(6000.0, $weeks[1]['loss']);
        $this->assertEqualsWithDelta(46.15, $weeks[1]['loss_pct'], 0.01);

        // Pair 3: May 21 -> May 28, days 21-27 (7 days), meter (742 -> 760)
        $this->assertEquals(3, $weeks[2]['week']);
        $this->assertEquals('2026-05-21', $weeks[2]['start_date']);
        $this->assertEquals('2026-05-28', $weeks[2]['end_date']);
        $this->assertEquals(742, $weeks[2]['meter_start']);
        $this->assertEquals(760, $weeks[2]['meter_end']);
        $this->assertEquals(18000.0, $weeks[2]['consumed']);
        $this->assertEquals(7000.0, $weeks[2]['sold']);
        $this->assertEquals(11000.0, $weeks[2]['loss']);
        $this->assertEqualsWithDelta(61.11, $weeks[2]['loss_pct'], 0.01);
    }

    public function test_daily_sales_site_not_found_returns_404(): void
    {
        $user = User::factory()->create();
        $site = Site::factory()->create(['name' => 'NONEXISTENT']);

        $builderMock = Mockery::mock(Builder::class);
        $builderMock->shouldReceive('first')->andReturn(null);
        Mockery::mock('overload:App\Models\Sims3\Site')
            ->shouldReceive('where')->with('Id_Site', 'NONEXISTENT')->andReturn($builderMock);

        $response = $this->actingAs($user)
            ->getJson("/api/sites/{$site->id}/daily-sales?month=2025-01");

        $response->assertNotFound();
    }

    public function test_daily_sales_returns_full_structure(): void
    {
        $user = User::factory()->create();
        $site = Site::factory()->create(['name' => 'SITE30']);

        $this->mockSims3Site('SITE30');

        $dailySalesData = collect([
            (object) [
                'Day' => '2025-01-01',
                'Total_Sales' => 160,
                'Hod_Sales' => 100,
                'Shopkeeper_Sales' => 50,
                'WiS_Sales' => 0,
                'Onsite_Sales' => 0,
                'Free_Sales' => 10,
                'Bottle_Sales' => 0,
            ],
            (object) [
                'Day' => '2025-01-15',
                'Total_Sales' => 200,
                'Hod_Sales' => 80,
                'Shopkeeper_Sales' => 60,
                'WiS_Sales' => 20,
                'Onsite_Sales' => 30,
                'Free_Sales' => 0,
                'Bottle_Sales' => 10,
            ],
        ]);

        $dailySaleBuilder = Mockery::mock(Builder::class);
        $dailySaleBuilder->shouldReceive('whereYear')->andReturnSelf();
        $dailySaleBuilder->shouldReceive('whereMonth')->andReturnSelf();
        $dailySaleBuilder->shouldReceive('get')->andReturn($dailySalesData);

        Mockery::mock('overload:App\Models\Sims3\DailySale')
            ->shouldReceive('where')->with('Id_Site', 'SITE30')->andReturn($dailySaleBuilder);

        $saleMock = Mockery::mock('overload:App\Models\Sims3\Sale');
        $saleMock->Total_Sales = 360;
        $saleMock->Total_Income = 180000;
        $saleMock->Hod_Sales = 180;
        $saleMock->Hod_Price = 500;
        $saleMock->Hod_Income = 90000;
        $saleMock->Shopkeeper_Sales = 110;
        $saleMock->Shopkeeper_Price = 600;
        $saleMock->Shopkeeper_Income = 66000;
        $saleMock->WiS_Sales = 20;
        $saleMock->WiS_Price = 400;
        $saleMock->WiS_Income = 8000;
        $saleMock->Onsite_Sales = 30;
        $saleMock->Onsite_Price = 300;
        $saleMock->Onsite_Income = 9000;
        $saleMock->Free_Sales = 10;
        $saleMock->Bottle_Sales = 10;
        $saleMock->Bottle_Price = 700;
        $saleMock->Bottle_Income = 7000;
        $saleMock->Emergency_Sales = 0;
        $saleMock->Emergency_Price = 0;
        $saleMock->Emergency_Income = 0;

        $saleBuilder = Mockery::mock(Builder::class);
        $saleBuilder->shouldReceive('whereYear')->andReturnSelf();
        $saleBuilder->shouldReceive('whereMonth')->andReturnSelf();
        $saleBuilder->shouldReceive('first')->andReturn($saleMock);

        $saleMock->shouldReceive('where')->with('Id_Site', 'SITE30')->andReturn($saleBuilder);

        $response = $this->actingAs($user)
            ->getJson("/api/sites/{$site->id}/daily-sales?month=2025-01");

        $response->assertSuccessful();
        $response->assertJsonStructure([
            'sales' => [
                '*' => ['date', 'Free_Sales', 'Hod_Sales', 'WiS_Sales', 'Onsite_Sales', 'Shopkeeper_Sales', 'Bottle_Sales', 'Other_Sales', 'Total_Sales'],
            ],
            'totals' => ['Free_Sales', 'Hod_Sales', 'WiS_Sales', 'Onsite_Sales', 'Shopkeeper_Sales', 'Bottle_Sales', 'Emergency_Sales', 'Other_Sales', 'Total_Sales'],
            'prices' => ['Free_Price', 'Hod_Price', 'Shopkeeper_Price', 'WiS_Price', 'Onsite_Price', 'Bottle_Price', 'Emergency_Price', 'Other_Price'],
            'income' => ['Free_Income', 'Hod_Income', 'Shopkeeper_Income', 'WiS_Income', 'Onsite_Income', 'Bottle_Income', 'Emergency_Income', 'Other_Income', 'Total_Income'],
        ]);

        $sales = $response->json('sales');
        $this->assertCount(2, $sales);
        $this->assertEquals('2025-01-01', $sales[0]['date']);
        $this->assertEquals(100, $sales[0]['Hod_Sales']);
        $this->assertEquals(50, $sales[0]['Shopkeeper_Sales']);
        $this->assertEquals(0, $sales[0]['Other_Sales']);
        $this->assertEquals(160, $sales[0]['Total_Sales']);

        $this->assertEquals('2025-01-15', $sales[1]['date']);
        $this->assertEquals(80, $sales[1]['Hod_Sales']);
        $this->assertEquals(20, $sales[1]['WiS_Sales']);
        $this->assertEquals(0, $sales[1]['Other_Sales']);
        $this->assertEquals(200, $sales[1]['Total_Sales']);

        $this->assertEquals(180, $response->json('totals.Hod_Sales'));
        $this->assertEquals(500, $response->json('prices.Hod_Price'));
        $this->assertEquals(90000, $response->json('income.Hod_Income'));
    }

    public function test_daily_sales_falls_back_to_cashier_sale(): void
    {
        $user = User::factory()->create();
        $site = Site::factory()->create(['name' => 'SITE31']);

        $this->mockSims3Site('SITE31');

        $dailySaleBuilder = Mockery::mock(Builder::class);
        $dailySaleBuilder->shouldReceive('whereYear')->andReturnSelf();
        $dailySaleBuilder->shouldReceive('whereMonth')->andReturnSelf();
        $dailySaleBuilder->shouldReceive('get')->andReturn(collect());

        Mockery::mock('overload:App\Models\Sims3\DailySale')
            ->shouldReceive('where')->with('Id_Site', 'SITE31')->andReturn($dailySaleBuilder);

        $cashierData = collect([
            (object) ['sale_date' => '2025-01-01', 'quantity' => 10, 'unit_price' => 500, 'type' => 'hod'],
            (object) ['sale_date' => '2025-01-01', 'quantity' => 5, 'unit_price' => 600, 'type' => 'shop'],
            (object) ['sale_date' => '2025-01-02', 'quantity' => 8, 'unit_price' => 500, 'type' => 'hod'],
            (object) ['sale_date' => '2025-01-02', 'quantity' => 3, 'unit_price' => 400, 'type' => 'onsite'],
            (object) ['sale_date' => '2025-01-02', 'quantity' => 2, 'unit_price' => 300, 'type' => 'bottle'],
        ]);

        $cashierBuilder = Mockery::mock(Builder::class);
        $cashierBuilder->shouldReceive('whereYear')->andReturnSelf();
        $cashierBuilder->shouldReceive('whereMonth')->andReturnSelf();
        $cashierBuilder->shouldReceive('get')->andReturn($cashierData);

        Mockery::mock('overload:App\Models\Sims3\CashierSale')
            ->shouldReceive('where')->with('site', 'SITE31')->andReturn($cashierBuilder);

        $saleMock = Mockery::mock('overload:App\Models\Sims3\Sale');
        $saleMock->Total_Sales = 28;
        $saleMock->Total_Income = 14000;
        $saleMock->Hod_Sales = 18;
        $saleMock->Hod_Price = 500;
        $saleMock->Hod_Income = 9000;
        $saleMock->Shopkeeper_Sales = 5;
        $saleMock->Shopkeeper_Price = 600;
        $saleMock->Shopkeeper_Income = 3000;
        $saleMock->WiS_Sales = 0;
        $saleMock->WiS_Price = 0;
        $saleMock->WiS_Income = 0;
        $saleMock->Onsite_Sales = 3;
        $saleMock->Onsite_Price = 400;
        $saleMock->Onsite_Income = 1200;
        $saleMock->Free_Sales = 0;
        $saleMock->Bottle_Sales = 2;
        $saleMock->Bottle_Price = 300;
        $saleMock->Bottle_Income = 600;
        $saleMock->Emergency_Sales = 0;
        $saleMock->Emergency_Price = 0;
        $saleMock->Emergency_Income = 0;

        $saleBuilder = Mockery::mock(Builder::class);
        $saleBuilder->shouldReceive('whereYear')->andReturnSelf();
        $saleBuilder->shouldReceive('whereMonth')->andReturnSelf();
        $saleBuilder->shouldReceive('first')->andReturn($saleMock);

        $saleMock->shouldReceive('where')->with('Id_Site', 'SITE31')->andReturn($saleBuilder);

        $response = $this->actingAs($user)
            ->getJson("/api/sites/{$site->id}/daily-sales?month=2025-01");

        $response->assertSuccessful();

        $sales = $response->json('sales');
        $this->assertCount(2, $sales);

        $this->assertEquals('2025-01-01', $sales[0]['date']);
        $this->assertEquals(0, $sales[0]['Free_Sales']);
        $this->assertEquals(10, $sales[0]['Hod_Sales']);
        $this->assertEquals(5, $sales[0]['Shopkeeper_Sales']);
        $this->assertEquals(0, $sales[0]['WiS_Sales']);
        $this->assertEquals(0, $sales[0]['Onsite_Sales']);
        $this->assertEquals(0, $sales[0]['Bottle_Sales']);
        $this->assertEquals(0, $sales[0]['Other_Sales']);
        $this->assertEquals(15, $sales[0]['Total_Sales']);

        $this->assertEquals('2025-01-02', $sales[1]['date']);
        $this->assertEquals(0, $sales[1]['Free_Sales']);
        $this->assertEquals(8, $sales[1]['Hod_Sales']);
        $this->assertEquals(0, $sales[1]['Shopkeeper_Sales']);
        $this->assertEquals(0, $sales[1]['WiS_Sales']);
        $this->assertEquals(3, $sales[1]['Onsite_Sales']);
        $this->assertEquals(2, $sales[1]['Bottle_Sales']);
        $this->assertEquals(0, $sales[1]['Other_Sales']);
        $this->assertEquals(13, $sales[1]['Total_Sales']);
    }

    public function test_daily_sales_no_data_returns_empty(): void
    {
        $user = User::factory()->create();
        $site = Site::factory()->create(['name' => 'SITE32']);

        $this->mockSims3Site('SITE32');

        $dailySaleBuilder = Mockery::mock(Builder::class);
        $dailySaleBuilder->shouldReceive('whereYear')->andReturnSelf();
        $dailySaleBuilder->shouldReceive('whereMonth')->andReturnSelf();
        $dailySaleBuilder->shouldReceive('get')->andReturn(collect());

        Mockery::mock('overload:App\Models\Sims3\DailySale')
            ->shouldReceive('where')->with('Id_Site', 'SITE32')->andReturn($dailySaleBuilder);

        $cashierBuilder = Mockery::mock(Builder::class);
        $cashierBuilder->shouldReceive('whereYear')->andReturnSelf();
        $cashierBuilder->shouldReceive('whereMonth')->andReturnSelf();
        $cashierBuilder->shouldReceive('get')->andReturn(collect());

        Mockery::mock('overload:App\Models\Sims3\CashierSale')
            ->shouldReceive('where')->with('site', 'SITE32')->andReturn($cashierBuilder);

        $saleBuilder = Mockery::mock(Builder::class);
        $saleBuilder->shouldReceive('whereYear')->andReturnSelf();
        $saleBuilder->shouldReceive('whereMonth')->andReturnSelf();
        $saleBuilder->shouldReceive('first')->andReturnNull();

        Mockery::mock('overload:App\Models\Sims3\Sale')
            ->shouldReceive('where')->with('Id_Site', 'SITE32')->andReturn($saleBuilder);

        $response = $this->actingAs($user)
            ->getJson("/api/sites/{$site->id}/daily-sales?month=2025-01");

        $response->assertSuccessful();
        $this->assertEquals([], $response->json('sales'));
        $this->assertEquals([], $response->json('totals'));
        $this->assertEquals(['Free_Price' => 0], $response->json('prices'));
        $this->assertEquals(['Free_Income' => 0], $response->json('income'));
    }

    public function test_sales_comparison_computes_averages_correctly(): void
    {
        $user = User::factory()->create();
        $site = Site::factory()->create(['name' => 'SITE01']);
        $platform = Platform::factory()->create(['name' => 'SW']);
        $otherPlatform = Platform::factory()->create(['name' => 'OT']);

        $this->mockSims3Site('SITE01');

        $samePlatformSite = Site::factory()->create();
        $otherPlatformSite = Site::factory()->create();

        $targetMonth = now()->startOfMonth();

        FactMonthly::factory()->create([
            'site_id' => $site->id,
            'platform_id' => $platform->id,
            'month' => $targetMonth,
            'sales_volume' => 100,
        ]);

        FactMonthly::factory()->create([
            'site_id' => $samePlatformSite->id,
            'platform_id' => $platform->id,
            'month' => $targetMonth,
            'sales_volume' => 80,
        ]);

        FactMonthly::factory()->create([
            'site_id' => $otherPlatformSite->id,
            'platform_id' => $otherPlatform->id,
            'month' => $targetMonth,
            'sales_volume' => 60,
        ]);

        $response = $this->actingAs($user)
            ->getJson("/api/sites/{$site->id}/sales-comparison");

        $response->assertSuccessful();
        $series = $response->json('series');
        $categories = $response->json('categories');

        $targetLabel = $targetMonth->format('M Y');
        $monthIndex = array_search($targetLabel, $categories);
        $this->assertNotFalse($monthIndex);

        $this->assertEquals(100, $series[0]['data'][$monthIndex]);
        $this->assertEquals(90, $series[1]['data'][$monthIndex]);
        $this->assertEquals(80, $series[2]['data'][$monthIndex]);
    }
}
