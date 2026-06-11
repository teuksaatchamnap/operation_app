<?php

namespace App\Http\Controllers;

use App\Imports\SaleObjectionImport;
use App\Models\SaleObjection;
use Illuminate\Http\Request;
use Maatwebsite\Excel\Facades\Excel;

class SaleObjectionController extends Controller
{
    function import(Request $request){
        if($request->file('file')){
            $import =  Excel::import(new SaleObjectionImport, request()->file('file'));
            // return collect(head($import))
            //         ->each(function ($row, $key) {
            //             DB::table('test2')
            //                 ->where('site', $row['site'])
            //                 ->update(Arr::except($row, ['site']));
            //         });

            $msg_success = "Data Uploaded Succesfully! ";
            $msg_danger = "Data Uploaded failed! ";
            if ($import) {
                return  $msg_success;
            }else{
               return $msg_danger;
            }
        }
    }
    public function index()
    {
        return SaleObjection::get();
    }
}
