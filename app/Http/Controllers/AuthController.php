<?php

namespace App\Http\Controllers;

use App\Models\User;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Auth;
use Illuminate\Support\Facades\Http;

class AuthController extends Controller
{
    public function login(Request $request): JsonResponse
    {
        $request->validate([
            'token' => 'required|array',
        ]);

        $token = $request->input('token');
        $clientId = $token['client_id'] ?? config('services.google.client_id');

        $response = Http::asForm()->post('https://oauth2.googleapis.com/tokeninfo', [
            'id_token' => $token['credential'],
        ]);

        if (! $response->successful()) {
            return response()->json(['error' => 'Invalid Google token'], 401);
        }

        $googleUser = $response->json();
        $email = $googleUser['email'] ?? null;

        if (! $email || ! in_array(explode('@', $email)[1] ?? '', ['teuksaat1001.com', '1001fontaines.com'])) {
            return response()->json(['error' => 'Unauthorized domain'], 403);
        }

        $user = User::firstOrCreate(
            ['google_id' => $googleUser['sub']],
            [
                'name' => $googleUser['name'] ?? $googleUser['given_name'] ?? 'Unknown',
                'email' => $email,
                'password' => '',
            ]
        );

        Auth::login($user);

        return response()->json(['message' => 'Authenticated']);
    }

    public function getAuth(Request $request): JsonResponse
    {
        $user = $request->user();

        if (! $user) {
            return response()->json(['error' => 'Unauthenticated'], 401);
        }

        return response()->json([
            'id' => $user->id,
            'name' => $user->name,
            'email' => $user->email,
        ]);
    }

    public function logout(Request $request): JsonResponse
    {
        Auth::guard('web')->logout();

        $request->session()->invalidate();
        $request->session()->regenerateToken();

        return response()->json(['message' => 'Logged out']);
    }
}
