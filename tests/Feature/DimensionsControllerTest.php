<?php

namespace Tests\Feature;

use App\Models\Advisor;
use App\Models\Platform;
use App\Models\Site;
use App\Models\User;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Tests\TestCase;

class DimensionsControllerTest extends TestCase
{
    use RefreshDatabase;

    public function test_get_advisors_unauthenticated_request_fails(): void
    {
        $this->getJson('/api/advisors')->assertUnauthorized();
    }

    public function test_get_advisors_authenticated_request_succeeds(): void
    {
        $user = User::factory()->create();
        $advisor = Advisor::create(['name' => 'John Doe']);
        $advisor2 = Advisor::create(['name' => 'Jane Smith']);

        $response = $this->actingAs($user)->getJson('/api/advisors');

        $response->assertStatus(200);
        $response->assertJsonCount(2);
        $response->assertJsonFragment(['name' => 'John Doe']);
        $response->assertJsonFragment(['name' => 'Jane Smith']);
    }

    public function test_get_advisors_returns_empty_array_when_no_advisors(): void
    {
        $user = User::factory()->create();

        $response = $this->actingAs($user)->getJson('/api/advisors');

        $response->assertStatus(200);
        $response->assertJsonCount(0);
    }

    public function test_get_platforms_unauthenticated_request_fails(): void
    {
        $this->getJson('/api/platforms')->assertUnauthorized();
    }

    public function test_get_platforms_authenticated_request_succeeds(): void
    {
        $user = User::factory()->create();
        $platform = Platform::create(['name' => 'Web Platform']);
        $platform2 = Platform::create(['name' => 'Mobile Platform']);

        $response = $this->actingAs($user)->getJson('/api/platforms');

        $response->assertStatus(200);
        $response->assertJsonCount(2);
        $response->assertJsonFragment(['name' => 'Web Platform']);
        $response->assertJsonFragment(['name' => 'Mobile Platform']);
    }

    public function test_get_platforms_returns_empty_array_when_no_platforms(): void
    {
        $user = User::factory()->create();

        $response = $this->actingAs($user)->getJson('/api/platforms');

        $response->assertStatus(200);
        $response->assertJsonCount(0);
    }

    public function test_get_sites_unauthenticated_request_fails(): void
    {
        $this->getJson('/api/sites')->assertUnauthorized();
    }

    public function test_get_sites_authenticated_request_succeeds(): void
    {
        $user = User::factory()->create();
        $site = Site::create(['name' => 'New York']);
        $site2 = Site::create(['name' => 'Paris']);

        $response = $this->actingAs($user)->getJson('/api/sites');

        $response->assertStatus(200);
        $response->assertJsonCount(2);
        $response->assertJsonFragment(['name' => 'New York']);
        $response->assertJsonFragment(['name' => 'Paris']);
    }

    public function test_get_sites_returns_empty_array_when_no_sites(): void
    {
        $user = User::factory()->create();

        $response = $this->actingAs($user)->getJson('/api/sites');

        $response->assertStatus(200);
        $response->assertJsonCount(0);
    }
}
