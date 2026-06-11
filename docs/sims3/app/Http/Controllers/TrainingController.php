<?php

namespace App\Http\Controllers;

use App\Models\Training;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;

class TrainingController extends Controller
{
    public function index(Request $request)
    {
       // return Training::select('*')->get();

       $query = DB::table('users')
                ->rightJoin('training','users.email','=','training.staff_email');
        
       $limit = 300;
       if($request->has('excel')) {
           $limit = 999999;
       }
       if($request->has("manager")) {
           $query->where("users.manager", auth()->user()->email);
       } 
       else if($request->has("admin")) {
           // admin can view all, no where clause defined
       } 
       else {
           // show 1 user when match with email.
           $query->where("users.email", auth()->user()->email);
       }
       return $query->skip(($request->page - 1)*15)
                    ->take($limit)
                    ->get();
    }
    public function show(string $id)
    {
        //dd($id);
        $training = Training::select('*')
                   ->where('staff_email','=',$id)
                   ->get();
       // $training['email']= auth()->user()->email;
        return $training;
    }
}
