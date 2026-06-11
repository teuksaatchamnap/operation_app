<?php

namespace App\Http\Controllers;

use App\Models\User;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Log;

class UserController extends Controller
{
    public function index(Request $request)
    {
        return User::select('*')->get();
    }

    /**
     * Store a newly created resource in storage.
     */
    public function store(Request $request)
    {
        return User::create($request->all());
    }

    public function destroy(Request $request, User $user)
    {
        return $user->delete();
    }

    /**
     * Update the specified resource in storage.
     */
    public function update(Request $request)
    {
        // Find the user by email
        $user = User::find($request->email);

        if (!$user) {
            Log::error('User not found for email: ' . $request->email);
            return response()->json(['error' => 'User not found'], 404);
        }

        // Validate the request
        try {
            // $validated = $request->validate([
            //     'email' => 'required|email|unique:users,email,' . $request->email,
            //     'permissions' => 'nullable|array',
            //     'permissions.*' => 'nullable', // Allow mixed types (strings or objects)
            //     'manager' => 'nullable|string',
            //     'position' => 'nullable|string',
            //     'staff_id' => 'nullable|string',
            //     'staff_name' => 'nullable|string',
            //     'staff_sex' => 'nullable|string|in:Male,Female',
            //     'staff_position' => 'nullable|string',
            //     'staff_dept' => 'nullable|string',
            //     'staff_join_date' => 'nullable|date',
            //     'staff_supervisor_by' => 'nullable|string',
            // ]);
        } catch (\Illuminate\Validation\ValidationException $e) {
            Log::error('Validation failed: ' . json_encode($e->errors()));
            return response()->json(['error' => 'Validation failed', 'details' => $e->errors()], 422);
        }

        // Process permissions to extract only the name as strings
        $processedPermissions = array_map(function ($permission) {
            if (is_string($permission)) {
                // Handle strings (e.g., "edit_permissions", "Sale:receive_sale_monthly_report")
                if (strpos($permission, ':') !== false) {
                    [, $name] = explode(':', $permission, 2); // Extract name after colon
                    return $name;
                }
                return $permission; // Keep simple strings like "edit_permissions"
            } elseif (is_array($permission)) {
                // Handle objects (e.g., ["app_name" => "Sale", "name" => "receive_sale_monthly_report"])
                if (!isset($permission['name'])) {
                    Log::warning('Missing name in permission: ' . json_encode($permission));
                    return $permission['app_name'] ?? ''; // Fallback to app_name if name is missing
                }
                return $permission['name'];
            } else {
                Log::warning('Invalid permission type: ' . json_encode($permission));
                throw new \InvalidArgumentException("Invalid permission format: " . json_encode($permission));
            }
        }, $request->permissions ?? []);

        // Remove empty or invalid permissions
        $processedPermissions = array_filter($processedPermissions, function ($perm) {
            return !empty($perm);
        });

        // Log processed permissions
        Log::info('Processed permissions for user ' . $request->email . ': ' . json_encode($processedPermissions));

        // Update user
        try {
            $user->permissions = $processedPermissions;
            $user->manager = $request->manager;
            $user->position = $request->position;
            $user->staff_id = $request->staff_id;
            $user->staff_name = $request->staff_name;
            $user->staff_sex = $request->staff_sex;
            $user->staff_position = $request->staff_position;
            $user->staff_dept = $request->staff_dept;
            $user->staff_join_date = $request->staff_join_date;
            $user->staff_supervisor_by = $request->staff_supervisor_by;
            $user->save();

            Log::info('User updated successfully: ' . $request->email);
        } catch (\Exception $e) {
            Log::error('Failed to save user: ' . $e->getMessage());
            return response()->json(['error' => 'Failed to save user', 'message' => $e->getMessage()], 500);
        }

        return response()->json($user);
    }
    public function getPermissions()
    {
        return DB::table('permissions')->orderBy("name")->get()->pluck("name");
    }
    public function getAllPermissions()
    {
        return DB::table('permissions')->orderBy("name")->get();
    }
}
