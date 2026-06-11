<?php

namespace App\Http\Controllers;

use App\Mail\ValidateSchoolRequest;
use App\Models\SchoolProgram;
use App\Models\Site;
use Illuminate\Http\Request;
use Illuminate\Support\Carbon;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Mail;
use NumberFormatter;
use Illuminate\Support\Str;
class SchoolProgramController extends Controller
{
    public function index(Request $request)
{
    $year = $request->input('academy_year'); // get from Vue
    $data = SchoolProgram::where('academy_year', $year)
        ->orderBy("Id_Site", "ASC")
        ->get();
    return response()->json($data);
}
public function getAllYears()
{
    $years = SchoolProgram::select('academy_year')
        ->distinct()
        ->orderBy('academy_year', 'desc')
        ->pluck('academy_year');

    return response()->json($years);
}
    private static function convertToKhmer($number)
    {
        $formatter = new NumberFormatter('km', NumberFormatter::DECIMAL);
        return $formatter->format($number);
    }
    public function validateSchool( Request $request)
    {
        $p = $request->platform;
        $year = $request->year;
        if ($p == "All")
         {
            // SchoolProgram::query()->update([
            // 'status' => 'validation',
            // 'status_bottle' => 'ok'
            //  ]);           
             SchoolProgram::where('academy_year', $year)
                ->update([
                    'status' => 'validation',
                    'status_bottle' => 'ok'
                ]);
         }
        else{
            SchoolProgram::where('platform', $p)
                ->where('academy_year', $year)
                ->update([
        'status' => 'validation',
        'status_bottle' => 'ok'
                     ]); 
        }
        return response()->json(['message' => 'All school records updated successfully']);
        
    }
    public function schoolProgramDownloadExcel(Request $request)
    {
        //$year = $request->input('year');
      //  $year = $request->query('year');
        $year = $request->year;
        $Excel ="";
        $template = "";
        $data= array();
        $dataSchoolAll= array();
        $template = storage_path('app/templates/school_validation_check.xlsx');
       // $dataSchool= SchoolProgram::with('site:Id_Site,Advisor')->get();
        $schools = SchoolProgram::join('Sites', 'school_programs.Id_Site', '=', 'Sites.Id_Site')
            ->select('school_programs.*', 'Sites.Advisor')
            ->where('school_programs.academy_year', $year)
            ->get();
        $Excel = Site::leftJoin('school_programs', 'Sites.Id_Site', '=', 'school_programs.Id_Site')
    //->selectRaw('sites.Id_site,sites.school_program, SUM(school_programs.bottle_approved) as total_school_provide')
            ->select('Sites.Id_Site','Sites.Platform','Sites.Advisor','school_programs.status_bottle', 'Sites.school_program', DB::raw('SUM(school_programs.bottle_approved) as total_school_provide'))
            ->where('Sites.Platform','!=',"Dead")
            ->where('Sites.Platform','!=',"Stop")
            ->where('Sites.school_program','>',0)
            ->where('school_programs.academy_year', $year)
            ->groupBy('Sites.Id_Site','Sites.school_program','school_programs.status_bottle','Sites.Platform','Sites.Advisor')
            ->get();
        foreach ($Excel as $ex)
        {
            $data1 = $ex->toArray(); // Convert the record to an array
            //if ($ex->total_school_provide == NULL || $ex->total_school_provide == "NULL") $data1['']
            if ($ex->school_program >= $ex->total_school_provide) {
                $data1['status'] = 'ok';
            } else {
                $data1['status'] = 'over';
            }
            $data[] = $data1; // Add the modified record to the results array
        }
        foreach($schools as $sc)
        {
            $data2 = $sc->toArray();
            if($sc->bottle_approved > $sc->number_of_classes)
            {
                $data2['bottle_status'] = "over";
            }
            elseif($sc->bottle_approved == $sc->number_of_classes)
            {
                $data2['bottle_status'] = "ok";
            }
            else
            {
                $data2['bottle_status'] = "under";
            }
            $dataSchoolAll[] = $data2;

        }
       // dd($dataSchoolAll);
        $TBS = new \clsTinyButStrong;
        $ok = class_exists('clsOpenTBS', true);
        $TBS->OtbsMsExcelExplicitRef = false;
        $TBS->Plugin(\TBS_INSTALL, \OPENTBS_PLUGIN);
        $TBS->LoadTemplate($template, \OPENTBS_ALREADY_UTF8);
        $TBS->PlugIn(OPENTBS_SELECT_SHEET, 1);
        $TBS->SetOption("noerr", true);
        $TBS->MergeBlock('a', $data);
        $TBS->PlugIn(OPENTBS_SELECT_SHEET, 2);
        $TBS->SetOption("noerr", true);
        $TBS->MergeBlock('b', $dataSchoolAll);
        $TBS->Show(OPENTBS_DOWNLOAD, "school_validation.xlsx");
    }
    public function schoolQuery()
    {
        $summedSchoolProvide = Site::leftJoin('school_programs', 'sites.Id_site', '=', 'school_programs.Id_site')
    //->selectRaw('sites.Id_site,sites.school_program, SUM(school_programs.bottle_approved) as total_school_provide')
    ->select('siteS.Id_site', 'siteS.school_program', DB::raw('SUM(school_programs.bottle_approved) as total_school_provide'))
    ->where('sites.Platform','!=',"Dead")
    ->groupBy('sites.Id_site','sites.school_program')
    ->get();

     return $summedSchoolProvide;
    }
    public function searchRecord(Request $request)
    {
        return SchoolProgram::find($request->id);
    }
    public function update(Request $request, int $id)
    {
        $school = SchoolProgram::find($id);
        $school->fill($request->all());
        $updates = $school->last_updated;
       // $school->status = "waiting_validation";
        //$school['report_by']= auth()->user()->email;
       // dd($school);
        if($updates == null )
        {
            $school->last_updated = collect([["user" => auth()->user()->email, "date" => date("Y-m-d H:i:s")]]);
        }
        // else{
        //     $updates->push(["user" => auth()->user()->email, "date" => date("Y-m-d H:i:s")]);
        //     $school->last_updated = $updates;
           
        // }
        //dd($a);
        $school->save();
        if($school->status == "waiting_validation")
        {
          //  $this->validateSchoolRequest($school);
        }
        return $school;
    }
    public function schoolProgramDownload(Request $request)
    {
        $data = SchoolProgram::get();
        $template = storage_path('app/templates/site.docx');
        
        foreach ($data as $i)
        {
            $data1[]= $i->toArray();
            $data1[] = ['break' => ''];
        }
        //dd($data1);
        $TBS = new \clsTinyButStrong(); 
        $ok = class_exists('clsOpenTBS', true); // hack to force class loading of TBS
        $TBS->Plugin(TBS_INSTALL, OPENTBS_PLUGIN);
        $TBS->OtbsMsExcelExplicitRef = false;
        $TBS->LoadTemplate($template, OPENTBS_ALREADY_UTF8);
        $TBS->SetOption("noerr", true);
        $TBS->MergeBlock('a', $data1);
        $TBS->PlugIn(OPENTBS_SELECT_HEADER);
        //$TBS->PlugIn(OPENTBS_DEBUG_XML_CURRENT);
        $filename = "school_program_" . time() . ".docx";
        $TBS->Show(OPENTBS_DOWNLOAD, $filename);
    }
    public function schoolProgramDownload1(Request $request)
    {
        $id = $request->id;
        $data = SchoolProgram::findOrFail($id);
        $template = storage_path('app/templates/s.docx');
        $data['total_student'] = intval($data->number_of_boys) + intval($data->number_of_girls);
        $data->number_of_boys = convertEnglishToKhmer($data->number_of_boys);
        $data->number_of_girls = convertEnglishToKhmer($data->number_of_girls);
        $data->number_of_classes = convertEnglishToKhmer($data->number_of_classes);
        $data->bottle_approved = convertEnglishToKhmer($data->bottle_approved);
        $data->start_grade = convertEnglishToKhmer($data->start_grade);
        $data->end_grade = convertEnglishToKhmer($data->end_grade);
        $data->province = Str::after($data->province, '/');
        $data->school_code = convertEnglishToKhmer($data->school_code);
        $data['khmer_total_student'] =  convertEnglishToKhmer($data['total_student']);
        $data['start'] = Carbon::parse($data->academy_start)->format('d-m-Y');
        $data['end'] = Carbon::parse($data->academy_end)->format('d-m-Y');
        $data['today'] = Carbon::today()->format('d-m-Y');
        //$data['end_year_school'] = Carbon::parse($data->academy_end)->year;
        // foreach ($data as $ex)
        // {
        //     $data1= $ex->toArray();
        // }
        $data = $data->toArray();
        //dd($data);
        $TBS = new \clsTinyButStrong(); 
        $ok = class_exists('clsOpenTBS', true); // hack to force class loading of TBS
        $TBS->Plugin(TBS_INSTALL, OPENTBS_PLUGIN);
        $TBS->OtbsMsExcelExplicitRef = false;
        $TBS->LoadTemplate($template, OPENTBS_ALREADY_UTF8);
        $TBS->SetOption("noerr", true);
        $TBS->MergeField('a', $data);
       
        //$TBS->PlugIn(OPENTBS_DEBUG_XML_CURRENT);
        $filename = "school_program_" . time() . ".docx";
        $TBS->Show(OPENTBS_DOWNLOAD, $filename);
    }
    private function validateSchoolRequest($school)
    {
        $recipients = ['chamnap.keo@teuksaat1001.com'];   
        Mail::to($recipients)->send(new ValidateSchoolRequest($school));
    }
    public function schoolsContractPrint(Request $request)
    {
        $platform = $request->platform;
        $year= $request->query('year');
        $school = SchoolProgram::where('platform',$platform)
                    ->where('academy_year',$year)
                    ->orderBy('Id_Site','ASC')
                    ->get();
        $result =array();
        foreach ($school as $data)
        {
            $dataItem = [
                // Original school data (assuming you want to include all attributes)
                'school' => $data,
                // Calculated and converted fields
                'total_student' => intval($data->number_of_boys) + intval($data->number_of_girls),
                'boys' => convertEnglishToKhmer($data->number_of_boys),
                'girls' => convertEnglishToKhmer($data->number_of_girls),
                'classes' => convertEnglishToKhmer($data->number_of_classes),
                'b_approved' => convertEnglishToKhmer($data->bottle_approved),
                's_grade' => convertEnglishToKhmer($data->start_grade),
                'e_grade' => convertEnglishToKhmer($data->end_grade),
                'province_show' => Str::after($data->province, '/'),
                'code' => convertEnglishToKhmer($data->school_code),
                'khmer_total_student' => convertEnglishToKhmer(intval($data->number_of_boys) + intval($data->number_of_girls)),
                'start' => convertEnglishToKhmer(Carbon::parse($data->academy_start)->format('d-m-Y')),
                'end' => convertEnglishToKhmer(Carbon::parse($data->academy_end)->format('d-m-Y')),
                'today' => convertEnglishToKhmer(Carbon::today()->format('d-m-Y')),
            ];
            $result[] = $dataItem ; 
        }
        //dd($data1);
        return response()->json($result);
    }
    public function deleteSchoolProgram(Request $request)
    {
        $id = $request->id;
        $school = SchoolProgram::find($id);
        if ($school) {
            $school->delete();
            return response()->json(['message' => 'School program deleted successfully.'], 200);
        } else {
            return response()->json(['message' => 'School program not found.'], 404);
        }
    }
    
}
