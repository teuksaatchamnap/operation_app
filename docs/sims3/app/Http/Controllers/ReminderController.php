<?php

namespace App\Http\Controllers;

use App\Models\Reminder;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Storage;

class ReminderController extends Controller
{
    public function index()
    {
        return Reminder::all();
    }

    public function store(Request $request)
    {
        $request->validate([
            'name' => 'required|string',
            'message' => 'required|string',
            'day_of_month' => 'required|integer|min:-2|max:31',
            'time' => 'required|string|date_format:H:i',
            'target' => 'required|string',
            'active' => 'boolean',
            'audio' => 'nullable|file|mimes:ogg|max:10240'
        ]);

        $data = $request->all();
        
        if ($request->hasFile('audio')) {
            $audioPath = $request->file('audio')->store('audio/reminders', 'public');
            $data['audio'] = $audioPath;
        }

        return Reminder::create($data);
    }

    public function show(string $id)
    {
        return Reminder::findOrFail($id);
    }

    public function update(Request $request, string $id)
    {
        $reminder = Reminder::findOrFail($id);

        $request->validate([
            'name' => 'sometimes|required|string',
            'message' => 'sometimes|required|string',
            'day_of_month' => 'sometimes|required|integer|min:-2|max:31',
            'time' => 'sometimes|required|string|date_format:H:i',
            'target' => 'sometimes|required|string',
            'active' => 'boolean',
            'audio' => 'nullable|file|mimes:ogg|max:10240'
        ]);

        $data = $request->all();
        
        if ($request->hasFile('audio')) {
            if ($reminder->audio) {
                Storage::disk('public')->delete($reminder->audio);
            }
            $audioPath = $request->file('audio')->store('audio/reminders', 'public');
            $data['audio'] = $audioPath;
        }

        $reminder->update($data);
        return $reminder;
    }

    public function destroy(string $id)
    {
        $reminder = Reminder::findOrFail($id);
        $reminder->delete();
        return response()->json(null, 204);
    }
}
