<?php

namespace App\Http\Controllers;

use App\Models\TelegramGroup;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Log;
use Illuminate\Support\Facades\Storage;

/*
*    UPDATE `telegram_groups` SET `chat_id` = '5049756594';
*/

class TelegramController extends Controller
{
    public function index(Request $request)
    {
        if ($request->has('site')) {
            return TelegramGroup::where('site', $request->site)->first();
        }
        return TelegramGroup::get();
    }

    public function store(Request $request)
    {
        $validated = $request->validate([
            'site' => 'required|exists:Sites,Id_Site|unique:telegram_groups,site',
            'chat_id' => 'required|numeric',
            'invite_url' => 'nullable|url'
        ]);

        $telegramGroup = TelegramGroup::create($validated);
        return $telegramGroup;
    }

    public function show(TelegramGroup $telegramGroup)
    {
        return $telegramGroup;
    }

    public function update(Request $request, TelegramGroup $telegramGroup)
    {
        $validated = $request->validate([
            'site' => 'required|exists:Sites,Id_Site|unique:telegram_groups,site,' . $telegramGroup->id,
            'chat_id' => 'required|numeric',
            'invite_url' => 'nullable|url'
        ]);

        $telegramGroup->fill($validated);
        $telegramGroup->save();
        return $telegramGroup;
    }

    public function destroy(TelegramGroup $telegramGroup)
    {
        $telegramGroup->delete();
        return response()->json(['message' => 'Telegram group deleted successfully']);
    }

    public function sendImageToSite(Request $request)
    {
        $request->validate([
            'site' => 'required|exists:telegram_groups,site',
            'file' => 'required|file|mimes:png,jpg,jpeg',
            'message' => 'nullable|string|max:1000',
            'audio' => 'nullable|string'
        ]);
        $r1 = Http::attach(
            'photo',
            file_get_contents($request->file->getRealPath()),
            $request->file->getClientOriginalName()
        )->post("https://api.telegram.org/bot" . config('telegram.bot_token') . "/sendPhoto", [
            'chat_id' => TelegramGroup::where("site", $request->site)->first()->chat_id,
            'caption' => str_replace('\n', "\n", $request->message ?? "")
        ]);
        if ($request->has("audio")) {
            $r2 = $this->sendAudioToSite($request->site, Storage::disk("public")->path($request->audio));
            return response()->json([$r1->json(), $r2 instanceof \Illuminate\Http\Client\Response ? $r2->json() : $r2]);
        }
        return $r1;
    }

    public function sendMessageToSite($site, $message)
    {
        $telegramGroup = TelegramGroup::where("site", $site)->first();
        if (!$telegramGroup) {
            Log::error("Telegram group not found for site " . $site);
            return false;
        }
        return Http::post("https://api.telegram.org/bot" . config('telegram.bot_token') . "/sendMessage", [
            'chat_id' => $telegramGroup->chat_id,
            'text' => $message
        ]);
    }

    public function sendAudioToSite($site, $audio_file_path)
    {
        $telegramGroup = TelegramGroup::where("site", $site)->first();
        if (!$telegramGroup) {
            return response("Telegram group not found for site " . $site, 404);
        }

        if (!file_exists($audio_file_path)) {
            return response("Audio file not found: " . $audio_file_path, 404);
        }

        return Http::attach(
            'audio',
            file_get_contents($audio_file_path),
            basename($audio_file_path)
        )->post("https://api.telegram.org/bot" . config('telegram.bot_token') . "/sendAudio", [
            'chat_id' => $telegramGroup->chat_id
        ]);
    }

    public function sendTestMessage(Request $request)
    {
        $request->validate([
            'site' => 'required|exists:telegram_groups,site',
            'message' => 'nullable|string|max:1000'
        ]);
        $r1 = $this->sendAudioToSite($request->site, base_path("tests" . DIRECTORY_SEPARATOR . "Samples" . DIRECTORY_SEPARATOR . "sample.ogg"));
        $r2 = $this->sendMessageToSite($request->site, $request->message ?? "Test message");
        return response()->json([$r1->json(), $r2->json()]);
    }
}
