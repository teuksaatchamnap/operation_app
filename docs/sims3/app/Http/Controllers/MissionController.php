<?php

namespace App\Http\Controllers;

use App\Mail\MissionRequestEmail;
use App\Models\Mission;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Mail;

class MissionController extends Controller
{
    public function index(Request $request)
    {
        $query = Mission::query();
        $limit = 300;
        if($request->has('excel')) {
            $limit = 999999;
        }
        if($request->has("manager")) {
            $query->where("validator", auth()->user()->email);
        } 
        else if($request->has("admin") && array_search("mission_admin", auth()->user()->permissions)) {
            // admin can view all, no where clause defined
        } 
        else {
            // show 1 user when match with email.
            $query->where("requester", auth()->user()->email);
        }
        return $query->orderBy("start_date", "DESC")
                        ->skip(($request->page - 1)*15)
                        ->take($limit)
                        ->get();
    }

    public function show($id)
    {
        return Mission::find($id);
    }

    public function store(Request $request)
    {
        $mission = $request->all();
        $mission['other_expenses'] = json_encode($mission['other_expenses']);
        //dd($mission);
        $mission = Mission::create($mission);
        Mail::to([$mission->requester, $mission->validator])->send(new MissionRequestEmail($mission));
        return $mission;
    }

    public function update(Request $request, Mission $mission)
    {
        $mission->fill($request->all());
        $mission->save();
        return $mission;
    }

    public function destroy(Mission $mission)
    {
        return $mission->delete();
    }

    public function export(Request $request) {
        $missions = $this->index($request)->map(fn ($row) => $row->toArray());
        $template = storage_path('app/templates/missions.xlsx');
        $TBS = new \clsTinyButStrong();
        $ok = class_exists('clsOpenTBS', true); // hack to force class loading of TBS
        $TBS->Plugin(TBS_INSTALL, OPENTBS_PLUGIN);
        $TBS->OtbsMsExcelExplicitRef = false;
        $TBS->LoadTemplate($template, OPENTBS_ALREADY_UTF8);
        $TBS->SetOption("noerr", true);
        $TBS->MergeBlock('a', $missions);
        //$TBS->PlugIn(OPENTBS_DEBUG_XML_CURRENT);
        $filename = "missions_".time().".xlsx";
        $TBS->Show(OPENTBS_DOWNLOAD, $filename);
    }

    public function print(Mission $mission) {
        $template = storage_path('app/templates/mission.docx');
        $TBS = new \clsTinyButStrong();        
        $mission = $mission->toArray();
        $mission["start_date"] = substr($mission["start_date"], 0, 10);
        $mission["end_date"] = substr($mission["end_date"], 0, 10);
        $mission["requester"] = substr($mission["requester"], 0, strpos($mission["requester"], "@"));
        $daysInMission = array();
        $begin = new \DateTime( $mission["start_date"] );
        $end = new \DateTime( $mission["end_date"].' +1 day' );
        $interval = \DateInterval::createFromDateString('1 day');
        $period = new \DatePeriod($begin, $interval, $end);
        foreach ( $period as $dt ){
            $daysInMission[] = array(
                'day' => $dt->format( "Y-m-d" ),
                'purpose' => $mission["purpose"]
            );
        }

        $ok = class_exists('clsOpenTBS', true); // hack to force class loading of TBS
        $TBS->Plugin(TBS_INSTALL, OPENTBS_PLUGIN);
        $TBS->OtbsMsExcelExplicitRef = false;
        $TBS->LoadTemplate($template, OPENTBS_ALREADY_UTF8);
        $TBS->SetOption("noerr", true);
        $TBS->MergeField('mission', $mission);
        $TBS->MergeBlock('a', $daysInMission);
        //$TBS->PlugIn(OPENTBS_DEBUG_XML_CURRENT);
        $filename = "mission_" . $mission["id"] . ".docx";
        $TBS->Show(OPENTBS_DOWNLOAD, $filename);
    }
}
