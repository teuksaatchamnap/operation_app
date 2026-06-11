<?php

namespace App\Http\Controllers;

use App\Imports\AssessmentImport;
use App\Models\Assessment;
use App\Models\Rountine;
use App\Models\TransportationAssessment;
use Illuminate\Http\Request;
use Maatwebsite\Excel\Facades\Excel;
class AssessmentController extends Controller
{
    /**
     * Display a listing of the resource.
     */
    public function index(Request $request)
    {
        $query = "";
        $limit = 1000;
        if ($request->has('excel')) {
            $limit = 999999;
        }
        if ($request->has("assessment")) {
                $query = Assessment::select([
                    'id',
                    'site',
                    'date_form',
                    'technician',
                    'first_site_assessment',
                    'main_source_of_water',
                    'main_source_of_electricity',
                    'solar_panel',
                    'condition_batteries',
                    'condition_inverter_dc_to_ac',
                    'type_of_raw_water_tank',
                    'type_of_sand_filter_tank',
                    'type_of_ac_filter_tank',
                ]);
            } 

        else if ($request->has("routine")) {
            $query = Rountine::select([ 'id',
                'site', 
                'date',
                'technician',
                'main_person_the_water_kiosk_with_you',
                'condition_of_raw_water_tank',
                'condition_of_sand_filter_tank',
                'condition_of_ac_filter_tank',
                'condition_of_resin_filter_tank',
                'condition_of_ro',
                'condition_of_ultrafiltration',
                'are_pre_treatment_pipes_leaking',
                'is_the_pre_treatment_clean',
            ]);
        }
        return $query->orderBy("created_at", "desc")
            ->skip(($request->page - 1) * 15)
            ->take($limit)
            ->get();
    }
    public function record(Request $request)
    {
        return Assessment::where('site',$request->site)
                        ->orderBy('created_at','asc')->first();
    }
    public function showformAssessment (Request $request)
    {
        $result = Assessment::find($request->id);
        return $result;
    }
    public function transportation ()
    {
        return TransportationAssessment::get();
    }
    public function assessmentDownloadAll(Request $request)
    {
        $Excel ="";
        $template = "";
        $data= array();
        $dataBySite = array();
        $Excel = "";
        $ExcelBySite = array();
        $transportation="";
        $dataTransportation = array();
        if($request->tab =="assessment")
        {
            $Excel = Assessment::get();
            $ExcelBySite = Assessment::select('*')
                ->whereIn('id', function($query) {
                    $query->selectRaw('MAX(id)')
                        ->from('assessments')
                        ->groupBy('site');
                })
                ->orderBy('created_at', 'desc')
                ->get();
            $transportation = TransportationAssessment::get();
            $template = storage_path('app/templates/assessmentTemplate.xlsx');
           // $template = storage_path('app/templates/assessment.xlsx');
        }
        else
        {
            $Excel = Rountine::get();
            $template = storage_path('app/templates/routineTemplate.xlsx');
        }
        $st= "https://www.commcarehq.org/a/teuk-saat-test/api/form/attachment/";
        
        foreach ($Excel as $ex)
        {
            $data1 = $ex->toArray(); // Convert the record to an array
        
            $firstFourCharacters = substr($ex->please_take_a_picture_in_front_of_kiosk, 0, 4); // Extract the first 4 characters
        
            if (empty($firstFourCharacters)) { // Check for empty or null value
                $data1["row41"] = "";
                $data1["row44"] = "";
                $data1["row47"] = "";
                $data1["row50"] = "";
                $data1["row53"] = "";
                $data1["row100"] = "";
                $data1["row103"] = "";
            } else if (strtolower($firstFourCharacters) !== 'http') { // Check for "http" (case-insensitive)
                $data1['row41'] = $st . $ex->formid . "/" . $ex->please_take_a_picture_in_front_of_kiosk; // Build the URL
                $data1['row44'] = $st . $ex->formid . "/" . $ex->take_a_picture_behind_kiosk;
                $data1['row47'] = $st . $ex->formid . "/" . $ex->please_take_a_picture_of_pre_treatment;
                $data1['row50'] = $st . $ex->formid . "/" . $ex->take_a_photo_of_washing_bottle_area;
                $data1['row53'] = $st . $ex->formid . "/" . $ex->take_a_picture_of_bottling_area;
                $data1['row100'] = $st . $ex->formid . "/" . $ex->take_a_picture_micro_filtration;
                $data1['row103'] = $st . $ex->formid . "/" . $ex->take_a_picture_raw_water_pump;
            } else {
                $data1['row41'] = $ex->please_take_a_picture_in_front_of_kiosk; // Keep the original value if it starts with "http"
                $data1['row44'] = $ex->take_a_picture_behind_kiosk;
                $data1['row47'] = $ex->please_take_a_picture_of_pre_treatment;
                $data1['row50'] = $ex->take_a_photo_of_washing_bottle_area;
                $data1['row53'] = $ex->take_a_picture_of_bottling_area;
                $data1['row100'] = $ex->take_a_picture_micro_filtration;
                $data1['row103'] = $ex->take_a_picture_raw_water_pump;
            }
        
            $data[] = $data1; // Add the modified record to the results array
        }
        foreach ($ExcelBySite as $ex)
        {
            $data1 = $ex->toArray(); // Convert the record to an array
        
            $firstFourCharacters = substr($ex->please_take_a_picture_in_front_of_kiosk, 0, 4); // Extract the first 4 characters
        
            if (empty($firstFourCharacters)) { // Check for empty or null value
                $data1["row41"] = "";
                $data1["row44"] = "";
                $data1["row47"] = "";
                $data1["row50"] = "";
                $data1["row53"] = "";
                $data1["row100"] = "";
                $data1["row103"] = "";
            } else if (strtolower($firstFourCharacters) !== 'http') { // Check for "http" (case-insensitive)
                $data1['row41'] = $st . $ex->formid . "/" . $ex->please_take_a_picture_in_front_of_kiosk; // Build the URL
                $data1['row44'] = $st . $ex->formid . "/" . $ex->take_a_picture_behind_kiosk;
                $data1['row47'] = $st . $ex->formid . "/" . $ex->please_take_a_picture_of_pre_treatment;
                $data1['row50'] = $st . $ex->formid . "/" . $ex->take_a_photo_of_washing_bottle_area;
                $data1['row53'] = $st . $ex->formid . "/" . $ex->take_a_picture_of_bottling_area;
                $data1['row100'] = $st . $ex->formid . "/" . $ex->take_a_picture_micro_filtration;
                $data1['row103'] = $st . $ex->formid . "/" . $ex->take_a_picture_raw_water_pump;
            } else {
                $data1['row41'] = $ex->please_take_a_picture_in_front_of_kiosk; // Keep the original value if it starts with "http"
                $data1['row44'] = $ex->take_a_picture_behind_kiosk;
                $data1['row47'] = $ex->please_take_a_picture_of_pre_treatment;
                $data1['row50'] = $ex->take_a_photo_of_washing_bottle_area;
                $data1['row53'] = $ex->take_a_picture_of_bottling_area;
                $data1['row100'] = $ex->take_a_picture_micro_filtration;
                $data1['row103'] = $ex->take_a_picture_raw_water_pump;
            }
        
            $dataBySite[] = $data1; // Add the modified record to the results array
        }
        if($request->tab =="assessment")
        {
            foreach($transportation as $tr)
            {
                $dataTrain = $tr->toArray();
                $dataTransportation[] = $dataTrain;
            }
        }
        if($request->tab =="assessment")
{
    $TBS = new \clsTinyButStrong;
    $ok = class_exists('clsOpenTBS', true);
    $TBS->OtbsMsExcelExplicitRef = false;
    $TBS->Plugin(\TBS_INSTALL, \OPENTBS_PLUGIN);
    $TBS->LoadTemplate($template, OPENTBS_ALREADY_UTF8);

$TBS->SetOption("noerr", true);

// Sheet 1 - Assessment
$TBS->PlugIn(OPENTBS_SELECT_SHEET, 'Assessment');
$TBS->MergeBlock('a', $data);

// Sheet 3 - Transportation
$TBS->PlugIn(OPENTBS_SELECT_SHEET, 'Transportation');
$TBS->MergeBlock('b', $dataTransportation);

// Sheet 2 - Lastes
$TBS->PlugIn(OPENTBS_SELECT_SHEET, 'Lastes');
$TBS->MergeBlock('c', $dataBySite);

$TBS->Show(OPENTBS_DOWNLOAD, "assessmentDownload.xlsx");

}
        else
        {
            $TBS = new \clsTinyButStrong;
            $ok = class_exists('clsOpenTBS', true);
            $TBS->OtbsMsExcelExplicitRef = false;
            $TBS->Plugin(\TBS_INSTALL, \OPENTBS_PLUGIN);
            $TBS->LoadTemplate($template, \OPENTBS_ALREADY_UTF8);
            $TBS->PlugIn(OPENTBS_SELECT_SHEET, 1);
            $TBS->SetOption("noerr", true);
            $TBS->MergeBlock('a', $data);
            $TBS->Show(OPENTBS_DOWNLOAD, "routineDownload.xlsx");
        }
    } 

    public function excelDownload(Request $request)
    {
        $Excel ="";
        $template = "";
        $data= array();
        $Excel = "";
        if($request->tab =="assessment")
        {
            $Excel = Assessment::where("site",$request->site)->get();
            $template = storage_path('app/templates/assessment.xlsx');
        }
        else
        {
            $Excel = Rountine::where("site",$request->site)->get();
            $template = storage_path('app/templates/routine.xlsx');
        }
        $st= "https://www.commcarehq.org/a/teuk-saat-test/api/form/attachment/";
        foreach ($Excel as $ex)
        {
            $data1 = $ex->toArray(); // Convert the record to an array
        
            $firstFourCharacters = substr($ex->please_take_a_picture_in_front_of_kiosk, 0, 4); // Extract the first 4 characters
        
           if (empty($firstFourCharacters)) { // Check for empty or null value
                $data1["row41"] = "";
                $data1["row44"] = "";
                $data1["row47"] = "";
                $data1["row50"] = "";
                $data1["row53"] = "";
                $data1["row100"] = "";
                $data1["row103"] = "";
            } else if (strtolower($firstFourCharacters) !== 'http') { // Check for "http" (case-insensitive)
                $data1['row41'] = $st . $ex->formid . "/" . $ex->please_take_a_picture_in_front_of_kiosk; // Build the URL
                $data1['row44'] = $st . $ex->formid . "/" . $ex->take_a_picture_behind_kiosk;
                $data1['row47'] = $st . $ex->formid . "/" . $ex->please_take_a_picture_of_pre_treatment;
                $data1['row50'] = $st . $ex->formid . "/" . $ex->take_a_photo_of_washing_bottle_area;
                $data1['row53'] = $st . $ex->formid . "/" . $ex->take_a_picture_of_bottling_area;
                $data1['row100'] = $st . $ex->formid . "/" . $ex->take_a_picture_micro_filtration;
                $data1['row103'] = $st . $ex->formid . "/" . $ex->take_a_picture_raw_water_pump;
            } else {
                $data1['row41'] = $ex->please_take_a_picture_in_front_of_kiosk; // Keep the original value if it starts with "http"
                $data1['row44'] = $ex->take_a_picture_behind_kiosk;
                $data1['row47'] = $ex->please_take_a_picture_of_pre_treatment;
                $data1['row50'] = $ex->take_a_photo_of_washing_bottle_area;
                $data1['row53'] = $ex->take_a_picture_of_bottling_area;
                $data1['row100'] = $ex->take_a_picture_micro_filtration;
                $data1['row103'] = $ex->take_a_picture_raw_water_pump;
            }
        
            $data[] = $data1; // Add the modified record to the results array
        }
       // dd($data['row42']);
        $TBS = new \clsTinyButStrong;
        $ok = class_exists('clsOpenTBS', true);
        $TBS->OtbsMsExcelExplicitRef = false;
        $TBS->Plugin(\TBS_INSTALL, \OPENTBS_PLUGIN);
        $TBS->LoadTemplate($template, \OPENTBS_ALREADY_UTF8);
        $TBS->PlugIn(OPENTBS_SELECT_SHEET, 1);
        $TBS->SetOption("noerr", true);
        $TBS->MergeBlock('a', $data);
        $TBS->Show(OPENTBS_DOWNLOAD, "assessmentDownload.xlsx");
    } 

    public function importData(Request $request)
    {
        if($request->file('file')){
            $import =  Excel::import(new AssessmentImport, request()->file('file'));
            
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
    public function show(string $id)
    {
        //
    }

    /**
     * Update the specified resource in storage.
     */
    public function update(Request $request)
    {
        $ass = Assessment::find($request->id);
        $ass->fill($request->all());
        $ass->save();
        return response()->json(['message' => "Update Successfully"], 200);
    }

    /**
     * Remove the specified resource from storage.
     */
    public function destroy(string $id)
    {
        //
    }
}
