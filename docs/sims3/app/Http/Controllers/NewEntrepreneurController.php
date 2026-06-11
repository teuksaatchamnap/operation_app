<?php

namespace App\Http\Controllers;

use App\Models\EntrepreneurProfile;
use App\Models\NewEntrepreneur;
use App\Models\Site;
use Illuminate\Http\Request;
use Google\Cloud\Datastore\DatastoreClient;
use Google\Cloud\Datastore\Query\Query;
class NewEntrepreneurController extends Controller
{
    public $projectId = "sims-2-140009";

    public function __construct()
    {
        $this->projectId = "sims-2-140009";
        putenv('GOOGLE_APPLICATION_CREDENTIALS=' . storage_path('app/datastore_writer_appengine.json'));
    }
    public function show()
    {
        $data= Site::with("siteContract:Id_Site,path")
                ->select('Id_Site','Platform','Entrepreneur_English_Name','Entrepreneur_Khmer_Name','Sex','Province_Entrepreneur','Phone_Number','Date_start_working',
                            'Previous_Job','Education_Background','Why_working_as_entrepreneur')
                ->whereNotIn('Platform',['Dead','Stop'])
                ->whereNotIn('Id_Site', ['A3','A4','A5'])
                ->orderBy("Id_Site")
                ->get();
        // $data = Site::with(['entrepreneurProfiles' => function($query) {
        //     $query->where('Status', 'new_entrepreneur_coming');
        // }])
        // ->select('Id_Site', 'Platform')
        // ->whereNotIn('Platform', ['Dead', 'Stop'])
        // ->whereNotIn('Id_Site', ['A3', 'A4', 'A5'])
        // ->get()
        // ->map(function($site) {
        //     return [
        //         'Id_Site' => $site->Id_Site,
        //         'Platform' => $site->Platform,
        //         'En_Data' => $site->entrepreneurProfiles->first() // Get first matching profile
        //     ];
        // });

        return $data;
    }
    public function getEntrepreneur(Request $request)
    {
        $sites = Site::all();
            $siteMap = [];
            foreach ($sites as $site) 
            {
                $siteMap[$site->Id_Site] = $site->Platform;
            }
        $datastore = new DatastoreClient(['projectId' => $this->projectId]);
        $query = $datastore->query()
            ->kind('Pivot')
            // ->filter('month', '=', $request->month)
            ->filter('form', '=', '8. Entrepreneur Form')
            ->order('integration_date', Query::ORDER_DESCENDING);
        $result = $datastore->runQuery($query);
        $re = array();
        foreach ($result as $entity)
        {
            $data = json_decode($entity->get()["data"]);
            $siteName = $data->form->site_name;
            //if( $data->form->site_confirmed->what_do_you_want_to_do == "new_entrepreneur_coming")
            if (isset($data->form->site_confirmed->what_do_you_want_to_do) && $data->form->site_confirmed->what_do_you_want_to_do == "new_entrepreneur_coming")
            //if($siteName=='K26')
            {
                if (!isset($latestRecords[$siteName])) {
                    $latestRecords[$siteName] = [
                        "Id_Site" => $siteName,
                        "platform" => $siteMap[$siteName] ?? null,
                        "sex" => $data->form->site_confirmed->new_entrepreneur_recruitment->sex ?? "",
                        "date_entre_work" => $data->form->site_confirmed->new_entrepreneur_recruitment->date_start_working_in_station ?? "",
                        "entre_name" => $data->form->site_confirmed->new_entrepreneur_recruitment->entrepreneur_name_english ?? "",
                        "dob" => $data->form->site_confirmed->new_entrepreneur_recruitment->date_of_birth ?? "",
                        "phone_number" => $data->form->site_confirmed->new_entrepreneur_recruitment->first_phone_number ?? "",
                        "education" => $data->form->site_confirmed->new_entrepreneur_recruitment->education ?? "",
                        "previous_job" => $data->form->site_confirmed->new_entrepreneur_recruitment->what_does_he_do_before_joining_ts ?? "",
                        "commune_entrepreneur" => $data->form->site_confirmed->new_entrepreneur_recruitment->what_does_he_do_before_joining_ts ?? "",
                        "previous_job" => $data->form->site_confirmed->new_entrepreneur_recruitment->commune__village ?? "",
                        "entre_kh_name" => $data->form->site_confirmed->new_entrepreneur_recruitment->entrepreneur_khmer_name ?? "",
                    ];
                }
                // $re[] = [
                //     "Id_Site" => $siteName,
                //     "platform" => $siteMap[$siteName] ?? null,
                //     "sex" => $data->form->site_confirmed->new_entrepreneur_recruitment->sex ??"",
                //     "date_entre_work" =>$data->form->site_confirmed->new_entrepreneur_recruitment->date_start_working_in_station ??"",
                //     "entre_name" =>$data->form->site_confirmed->new_entrepreneur_recruitment->entrepreneur_name_english ??"",
                //     "dob" =>$data->form->site_confirmed->new_entrepreneur_recruitment->date_of_birth ??"",
                //     "phone_number" =>$data->form->site_confirmed->new_entrepreneur_recruitment->first_phone_number ??"",
                //     "education" =>$data->form->site_confirmed->new_entrepreneur_recruitment->education ??"",
                //     "previous_job" =>$data->form->site_confirmed->new_entrepreneur_recruitment->what_does_he_do_before_joining_ts ??"",
                // ];
            }
            
        }
        
        if ($request->has("excel")) {
            $inputFileName = storage_path('app/templates/siteStatus.xlsx');
            $TBS = new \clsTinyButStrong();
            $ok = class_exists('clsOpenTBS', true); // hack to force class loading of TBS
            $TBS->Plugin(\TBS_INSTALL, \OPENTBS_PLUGIN);
            $TBS->OtbsMsExcelExplicitRef = false;
            $TBS->LoadTemplate($inputFileName, \OPENTBS_ALREADY_UTF8);
            $TBS->SetOption("noerr", true);
            $TBS->MergeBlock('a', $re);
            $TBS->MergeField('month', ["month" => $request->month]);
            //$TBS->PlugIn(OPENTBS_DEBUG_XML_CURRENT);
            $filename = $request->month . "_siteStatus.xlsx";
            $TBS->Show(OPENTBS_DOWNLOAD, $filename);
        }
        $re = array_values($latestRecords);
        // foreach ($re as $record) {
        //     Site::where('Id_Site', $record['Id_Site'])
        //         ->update(
        //         [
        //             'Platform' => $record['platform'],
        //             'Sex' => $record['sex'],
        //             'Date_start_working' => $record['date_entre_work'],
        //             'Entrepreneur_English_Name' => $record['entre_name'],
        //             'Date_of_Birth' => $record['dob'],
        //             'Phone_Number' => $record['phone_number'],
        //             'Education_Background' => $record['education'],
        //             'Previous_Job' => $record['previous_job'],
        //             'Commune_Entrepreneur' => $record['commune_entrepreneur'],
        //             'Entrepreneur_Khmer_Name' => $record['entre_kh_name'],
        //         ]
        //     );
        // }
        return response()->json([
            'total_records' => count($re),
            'data' => $re
        ]);
    }
    public function detailEntrepreneur1(string $site)
    {
            return NewEntrepreneur::where("Id_Site", "=", $site)->orderBy('Resignation', 'ASC')->get();   
    }
    public function detailEntrepreneur(string $site)
    {
       
        $datastore = new DatastoreClient(['projectId' => $this->projectId]);
        $query = $datastore->query()
            ->kind('Pivot')
            ->filter('site', '=', $site)
            ->filter('form', '=', '8. Entrepreneur Form')
            ->order('integration_date', Query::ORDER_DESCENDING);
        $result = $datastore->runQuery($query);
        $re = array();
        foreach ($result as $entity)
        {
            $data = json_decode($entity->get()["data"]);
            $siteName = $data->form->site_name;
            if (isset($data->form->site_confirmed->what_do_you_want_to_do) && $data->form->site_confirmed->what_do_you_want_to_do == "entrepreneur_resignation")
            {
                $re[] = 
                [
                    "Id_Site" => $siteName,
                    "Entrepreneur_Khmer_name" => $data->form->site_confirmed->entrepreneur_resignation->entrepreneur_khmer_name ?? null,
                    "Entrepreneur_English_name" => $data->form->site_confirmed->entrepreneur_resignation->entrepreneur_english_name ?? null,
                    "Sex" => $data->form->site_confirmed->entrepreneur_resignation->sex ?? null,
                    "Reason_Resign" => $data->form->site_confirmed->entrepreneur_resignation->reason_for_leaving ?? null,
                    "Detail_Resign" => $data->form->site_confirmed->entrepreneur_resignation->detail_reason ?? null,
                    "Resignation_Date" => $data->form->site_confirmed->entrepreneur_resignation->when_did_heshe_resign ?? null,
                ];
            }
            
        }
        return response()->json([
            'getData' => $re
        ]);
    }       
}
