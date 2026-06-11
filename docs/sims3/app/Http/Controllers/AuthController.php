<?php

namespace App\Http\Controllers;

use App\Models\User;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Auth;

class AuthController extends Controller
{
    public function __construct() {
        putenv('GOOGLE_APPLICATION_CREDENTIALS='.storage_path('app/client_secret_appengine.json'));
    }

    public function login(Request $request) {
        try {
            $client = new \Google_Client(['client_id' => $request->token["client_id"]]); 
            $payload = $client->verifyIdToken($request->token["credential"]);
            // show email of user from $payload
            if($payload["hd"] === "1001fontaines.com" || $payload["hd"] === "teuksaat1001.com") {
                $user = User::where("email", $payload["email"])->firstOrFail();
                Auth::login($user, true);
                return $user;
            }
        } catch (\Exception $e) {
            return response()->json(['error' => 'Invalid token', 'message' => $e->getMessage()], 400);
        }
        return response()->json(['error' => 'Login error', 'message' => 'Your google address must ends with @1001fontaines.com or @teuksaat1001.com'], 400);
    }

    public function getAuth(Request $request) {
        return Auth::user();
    }

    public function logout(Request $request) {
        Auth::logout();
        $request->session()->invalidate();    
        $request->session()->regenerateToken();    
        return "logged out";
    }
}
