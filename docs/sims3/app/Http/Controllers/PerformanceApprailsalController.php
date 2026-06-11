<?php

namespace App\Http\Controllers;

use App\Mail\Pa;
use App\Models\Kpi;
use App\Models\PerformanceApprailsal;
use App\Models\Training;
use App\Models\User;
use Carbon\Carbon;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Mail;
use Maatwebsite\Excel\Concerns\ToArray;

use function Laravel\Prompts\select;

class PerformanceApprailsalController extends Controller
{
    public function index(Request $request)
    {
        $query = PerformanceApprailsal::query();
        $user= User::select("position")->where('email',auth()->user()->email)->get();
        $limit = 500;
        if($request->has('excel')) {
            $limit = 999999;
        }
        if($request->has("manager")) {
           // $query->where("supervisor_email", auth()->user()->email);
            $query->where("staff_supervisor_by", auth()->user()->email);
                //   ->where("score_last_time",">=",0);
        } 
        else if($request->has("admin")) {
            // admin can view all, no where clause defined
            $query->where("score_last_time",">=",0);
        } 
        else {
            // show 1 user when match with email.
            $query->where("staff_email", auth()->user()->email);
                // ->where("score_last_time",">=",0);
        }
        // $query->orderBy("staff_do_pa_date", "DESC")
        //                 ->skip(($request->page - 1)*15)
        //                 ->take($limit)
        //                 ->get();
        // $result = $query->merge($user) ;

        // $result1= $result->all();
        return ["pa"=>$query->orderBy("staff_do_pa_date", "DESC")
                        ->skip(($request->page - 1)*15)
                        ->take($limit)
                        ->get(),
                "user"=> $user
    ];  
       // return $result1;
    }
    public function show($id)
    {
        return PerformanceApprailsal::find($id);
    }
    public function printExcel($id)
    {
        $paExcel1 = PerformanceApprailsal::findOrFail($id);
        $name = User::findOrFail($paExcel1->staff_email);
        $a['sup_email']= $name->staff_supervisor_by;
        $template = storage_path('app/templates/paExcel.xlsx');
        $paExcel1 = $paExcel1->toArray();
        $paExcel= array_merge($paExcel1,$a);
       // dd($paExcel);
        $TBS = new \clsTinyButStrong();
        $ok = class_exists('clsOpenTBS', true); // hack to force class loading of TBS
        $TBS->Plugin(TBS_INSTALL, OPENTBS_PLUGIN);
        $TBS->OtbsMsExcelExplicitRef = false;
        $TBS->LoadTemplate($template, OPENTBS_ALREADY_UTF8);
        $TBS->SetOption("noerr", true);
        $TBS->MergeField('pa', $paExcel);
        //$TBS->PlugIn(OPENTBS_DEBUG_XML_CURRENT);
        $filename = "PA.xlsx";
        $TBS->Show(OPENTBS_DOWNLOAD, $filename);
    } 
    public function newPrintExcel($id)
    {
        $paExcel1 = PerformanceApprailsal::findOrFail($id);
        $name = User::findOrFail($paExcel1->staff_email);
        $a['sup_email']= $name->staff_supervisor_by;
        $template = storage_path('app/templates/NewpaExcel.xlsx');
        $paExcel1 = $paExcel1->toArray();
        $paExcel= array_merge($paExcel1,$a);
       // dd($paExcel);
        $TBS = new \clsTinyButStrong();
        $ok = class_exists('clsOpenTBS', true); // hack to force class loading of TBS
        $TBS->Plugin(TBS_INSTALL, OPENTBS_PLUGIN);
        $TBS->OtbsMsExcelExplicitRef = false;
        $TBS->LoadTemplate($template, OPENTBS_ALREADY_UTF8);
        $TBS->SetOption("noerr", true);
        $TBS->MergeField('pa', $paExcel);
        //$TBS->PlugIn(OPENTBS_DEBUG_XML_CURRENT);
        $filename = "PA.xlsx";
        $TBS->Show(OPENTBS_DOWNLOAD, $filename);
    } 
    public function exportExcel1()
    {
        // $data = PerformanceApprailsal::select('staff_name','staff_id','staff_email','previous_year_obj1_quantitative','previous_year_obj2_quantitative','previous_year_obj3_quantitative'
        // ,'previous_year_obj4_quantitative','previous_year_obj5_quantitative','previous_target_obj1_quantitative','previous_target_obj2_quantitative',
        // 'previous_target_obj3_quantitative','previous_target_obj4_quantitative'
        // ,'previous_target_obj5_quantitative','previous_result_obj1_quantitative','previous_result_obj2_quantitative','previous_result_obj3_quantitative'
        // ,'previous_result_obj4_quantitative','previous_result_obj5_quantitative')
        // ->groupBy('staff_name','staff_email','previous_year_obj1_quantitative','previous_year_obj2_quantitative','previous_year_obj3_quantitative'
        // ,'previous_year_obj4_quantitative','previous_year_obj5_quantitative'
        // ,'previous_target_obj1_quantitative','previous_target_obj2_quantitative','previous_target_obj3_quantitative','previous_target_obj4_quantitative'
        // ,'previous_target_obj5_quantitative','previous_result_obj1_quantitative','previous_result_obj2_quantitative'
        // ,'previous_result_obj3_quantitative','previous_result_obj4_quantitative','previous_result_obj5_quantitative','staff_id')                                
        // ->orderBy('updated_at','desc')
        // ->where("score_last_time",">=",0)
        // ->get();
        //$data = PerformanceApprailsal::get();
        $data = Kpi::orderBy('updated_at', 'desc')
    ->get()
    ->unique('staff_email') // Or use 'staff_id' if more reliable
    ->values(); 


        $dataExport = array();
        foreach ($data as $dataExcel)
        {
            $dataExport[] = $dataExcel->toArray();
        }
        $template = storage_path('app/templates/PA_Data.xlsx');
       // dd($dataExport);
       $TBS = new \clsTinyButStrong;
       $ok = class_exists('clsOpenTBS', true);
       $TBS->OtbsMsExcelExplicitRef = false;
       $TBS->Plugin(\TBS_INSTALL, \OPENTBS_PLUGIN);
       $TBS->LoadTemplate($template, \OPENTBS_ALREADY_UTF8);
       $TBS->PlugIn(OPENTBS_SELECT_SHEET, 1);
       $TBS->SetOption("noerr", true);
       $TBS->MergeBlock('a', $dataExport);
       $TBS->Show(OPENTBS_DOWNLOAD, "PA.xlsx");
    }
    public function staffInfo()
    {
        $user= User::select("users.*")->where('manager',auth()->user()->email)->get();
       
        // return User::where("manager",auth()->user()->email)->get();
        // $currentYear = Carbon::now()->year;
        // $previosYear = now()->subYear(3);
        // $last = $previosYear->format('Y');
        // $query= User::join('Kpi','kpi.staff_email','=','users.email')
        //          //->join('performance_apprailsals','users.email','=','performance_apprailsals.staff_email')
        //          //->select('users.*','kpi.*')
        //          ->where('users.manager',auth()->user()->email)
        //          //->whereBetween("kpi.year",[$last,$currentYear])
        //          ->get(['users.*','kpi.*']);
        // //dd($last);
        return $user;
    }
    public function getTraining($training_email)
    {
        //  $query= User::Rightjoin('training','users.email','=','training.staff_email')
        //          //->join('training','users.email','=','training.staff_email')
        //          ->where("training.staff_email","=",$training_email)
        //          ->select('users.*','training.*')
        //          ->get();
        $query = Training::query();
        $query ->where("staff_email","=",$training_email);
        return $query->get();
                    
    }
    public function test()
    {
        return "i love you";
    }
    public function getKPI($staff_email)
    {
        $result = Kpi::where("staff_email",$staff_email)->exists(); // condition staff_type_pa
        $current ='';
        if ($result)
        {
            $current= Kpi::where("staff_email",$staff_email)
                ->orderBy('created_at', 'desc')->take(1)->get();
        }
        else
        {
            $current= Kpi::select('kpi1','kpi2','target1' ,'target2','result_kpi1','result_kpi2' )
                       ->orderBy('year', 'desc')->take(1)->get();
        }
        return [
            "current" =>$current                
        ];
    }
    public function getPreviousPA($staff_email)
    {    
        $year = request()->query('year');
        $current= Kpi::where("staff_email",$staff_email)
        ->where("year",$year)
        ->take(1)->get();

        $query= PerformanceApprailsal::where("staff_email",$staff_email)
                ->orderBy("updated_at", "DESC")
                ->take(1)
                ->get();
        return [
            "current" =>$current ,
            "previousPA" => $query
        ];
    }
    public function staffAgree(Request $request)
    {
        $pa = PerformanceApprailsal::find($request->id);
        if (!$pa) {
            return response()->json(['message' => 'Record not found'], 404);
        }
        $pa->staff_agree = "agree";
        $pa->save();
        return response()->json(['message' => 'Thank you for your agreement']);
    }
    public function store(Request $request)
    {
        // before I use $pa = $request->all(); and it can store as array and you can write $pa['staff_email']= $request->staff_email;
        $pa = $request->input("pa");
        $message = $request->input("additionalVariable");
        $pa["report_by"] = auth()->user()->email;
        if($message == "withEmail")
        {
            $pa['validate'] = "validated";
        }
        $pa= PerformanceApprailsal::create($pa);
        if ($pa->total_score > 0) {
            $pa->score_this_time = $pa->total_score;
        } else {
            $pa->score_this_time = $pa->score_last_time;
        }
        if($message == "withEmail")
        {
            $this->sendMailPa($pa);
        }    
        return $pa;
    }
    public function update(Request $request, int $id)
    {
        $pa = PerformanceApprailsal::find($id); // Find the record by ID
        $message = $request->input("additionalVariable");
        
        if ($pa) {
            // Update the model with the data from the request
            $pa->fill($request->input("pa"));
            if ($message === "withEmail") {
                $pa->validate = "validated";
            }
            else {
                $pa->validate = "";
            }
            // Save the changes to the model (excluding score_this_time)
            $pa->save();
            // Dynamically add `score_this_time` without saving it
            if ($pa->total_score > 0) {
                $pa->score_this_time = $pa->total_score;
            } else {
                $pa->score_this_time = $pa->score_last_time;
            }
            // Send email if needed
            if ($message === "withEmail") {
                $this->sendMailPa($pa); // `score_this_time` will be available in the email template
            }
        }
        // Return the model as a JSON response
        return response()->json($pa);
        
    }
    Private function sendMailPa($pa)
    {
        $recipients = [$pa->supervisor_email,$pa->staff_email,"yady.l@teuksaat1001.com"];
        //$recipients = ['chamnap.keo@teuksaat1001.com'];
        Mail::to($recipients)->send(new Pa($pa));
    }
    public function deleteRecord($id)
    {
        $record = PerformanceApprailsal::findOrFail($id);
        if ($record->delete())
        {
            return "Delete Successfully";
        } 
        else{
            return "no record delete";
        }
    }
}
