<?php

namespace App\Http\Controllers;

use App\Models\CashierNotification;
use Illuminate\Http\Request;

class CashierNotificationController extends Controller
{
    public function index()
    {
        return CashierNotification::all();
    }

    public function store(Request $request)
    {
        $request->validate([
            'key' => 'required|string|unique:cashier_notifications,key',
            'message' => 'required|string',
            'audio' => 'nullable|file|mimes:ogg|max:10240'
        ]);
        $data = $request->all();
        if ($request->hasFile('audio')) {
            $data['audio'] = $request->file('audio')->store('audio/cashier_notifications', 'public');
        }
        return CashierNotification::create($data);
    }

    public function show(string $id)
    {
        return CashierNotification::findOrFail($id);
    }

    public function update(Request $request, string $id)
    {
        $notification = CashierNotification::findOrFail($id);

        $request->validate([
            'key' => 'sometimes|required|string|unique:cashier_notifications,key,' . $id,
            'message' => 'sometimes|required|string',
            'audio' => 'nullable|file|mimes:ogg|max:10240'
        ]);

        $notification->update($request->all());

        if ($request->hasFile('audio')) {
            $notification->audio = $request->file('audio')->store('audio/cashier_notifications', 'public');
            $notification->save();
        }

        return $notification;
    }

    public function destroy(string $id)
    {
        $notification = CashierNotification::findOrFail($id);
        $notification->delete();
        return response()->json(null, 204);
    }
}
