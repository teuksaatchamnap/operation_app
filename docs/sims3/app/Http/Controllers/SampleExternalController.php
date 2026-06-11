<?php

namespace App\Http\Controllers;

use App\Models\SampleExternal;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Log;
use Illuminate\Support\Facades\Storage;

class SampleExternalController extends Controller
{
    public function saveSamplesExternal (Request $request)
    {
       
        // // $request->validate([
        // //     'site' => 'required|string',
        // //     'test_date' => 'required|date',
        // //     'file' => 'required|file|mimes:jpg,jpeg,png,pdf' // Adjust mime types as needed
        // // ]);

        $file = $request->File('file');
        $filename = time() . '_' . $file->getClientOriginalName();
        $filePath = $file->storeAs('uploads', $filename, 'public');

        SampleExternal::create([
            'site' => $request->input('site'),
            'test_date' => $request->input('test_date'),
            'upload_path' => $filePath
        ]);
        return response()->json([
            'message' => "successful upload"
        ]);
    }
    public function destroy($id)
    {
        // Retrieve the record by ID
    $sample = SampleExternal::find($id);

    if (!$sample) {
        return response()->json(['message' => 'Record not found'], 404);
    }

    // Delete the associated file from storage
    $filePath = $sample->upload_path;
    if (Storage::disk('public')->exists($filePath)) {
        Storage::disk('public')->delete($filePath);
    }

    // Delete the record from the database
    $sample->delete();

    return response()->json(['message' => 'Record and file deleted successfully!']);
    }

    public function downloadFile($filename)
            {
                $filePath = "uploads/{$filename}";

                if (Storage::disk('public')->exists($filePath)) {
                    return response()->download(storage_path("app/public/{$filePath}"));
                }

                return response()->json(['message' => 'File not found'], 404);
            }
}
