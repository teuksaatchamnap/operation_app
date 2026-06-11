<?php

namespace App\Http\Controllers;

use App\Imports\KpiImport;
use App\Imports\PAimportData;
use App\Imports\TrainingImport;
use App\Models\Training;
use Illuminate\Http\Request;
use Maatwebsite\Excel\Facades\Excel;

class KpiController extends Controller
{
    /**
     * Display a listing of the resource.
     */
    public function index(Request $request)
    {
        return Training::get();
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
    public function show(string $id)
    {
        //
    }

    /**
     * Update the specified resource in storage.
     */
    public function update(Request $request, string $id)
    {
        //
    }

    /**
     * Remove the specified resource from storage.
     */
    public function destroy(string $id)
    {
        //
    }
    public function importDataPA(Request $request)
    {
        if($request->file('file')){
            $import =  Excel::import(new PAimportData, request()->file('file'));
            
            if ($import) {
                return  "Data Uploaded Succesfully! ";
            }
            else
            {
               return "Data Uploaded failed! ";
            }
        }
    }
    public function importData(Request $request)
    {
       
        if($request->file('file')){
            $import = new KpiImport();
            // Perform the import
            Excel::import($import, $request->file('file'));

            // Retrieve created and updated counts
            $counts = $import->getCounts();
            $createdCount = $counts['created'];
            $updatedCount = $counts['updated'];
            if ($import) {
                return  [
                    'created' => $createdCount,
                    'updated' => $updatedCount,
                ];
            }
            else
            {
               return "Data Uploaded failed! ";
            }
        }
    }
    public function importDataTraining(Request $request)
    {
        if($request->file('file')){
            $import =  Excel::import(new TrainingImport, request()->file('file'));
            
            if ($import) {
                return  "Data Uploaded Succesfully! ";
            }
            else
            {
               return "Data Uploaded failed! ";
            }
        }

    }
}
