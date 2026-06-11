<?php

namespace App\Http\Controllers;

use App\Imports\RountineImport;
use App\Models\Rountine;
use Illuminate\Http\Request;
use Maatwebsite\Excel\Facades\Excel;

class RountineController extends Controller
{
    /**
     * Display a listing of the resource.
     */
    public function index()
    {
        //
    }
    public function importData(Request $request)
    {
        if($request->file('file')){
            $import =  Excel::import(new RountineImport, request()->file('file'));
            
            if ($import) {
                return  "Data Uploaded Succesfully! ";
            }
            else
            {
               return "Data Uploaded failed! ";
            }
        }
    }
    /**
     * Store a newly created resource in storage.
     */
    public function store(Request $request)
    {
        //
    }

    /**
     * Display the specified resource.
     */
    public function show(Request $request)
    {
        $result = Rountine::find($request->id);
        return response()->json(['result' => $result], 200);
    }

    /**
     * Update the specified resource in storage.
     */
    public function update(Request $request, string $id)
    {
        $routine = Rountine::find($request->id);
        $routine->fill($request->all());
        $routine->save();
        return response()->json(['result' => "Update Successfully"], 200);
    }

    /**
     * Remove the specified resource from storage.
     */
    public function destroy(string $id)
    {
        //
    }
}
