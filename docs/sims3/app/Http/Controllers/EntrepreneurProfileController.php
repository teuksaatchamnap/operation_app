<?php

namespace App\Http\Controllers;

use App\Models\EntrepreneurProfile;
use App\Models\Site;
use Illuminate\Http\Request;
use Google\Cloud\Datastore\DatastoreClient;
use Google\Cloud\Datastore\Query\Query;
use Illuminate\Support\Facades\Storage;

class EntrepreneurProfileController extends Controller
{
    /**
     * Display a listing of the resource.
     */
 public $projectId = "sims-2-140009";

    public function __construct()
    {
        $this->projectId = "sims-2-140009";
        putenv('GOOGLE_APPLICATION_CREDENTIALS=' . storage_path('app/datastore_writer_appengine.json'));
    }
    public function index()
    {
        $datastore = new DatastoreClient(['projectId' => $this->projectId]);
        $query = $datastore->query()
            ->kind('Pivot')
            ->filter('form', '=', '8. Entrepreneur Form')
            ->order('integration_date', Query::ORDER_ASCENDING);
        $result = $datastore->runQuery($query);
        foreach ($result as $entity)
        {
            $data = json_decode($entity->get()["data"]);
            $siteName = $data->form->site_name;
            if (isset($data->form->site_confirmed->what_do_you_want_to_do) && $data->form->site_confirmed->what_do_you_want_to_do == "entrepreneur_resignation")
            {
                // Insert data to EntrepreneurProfile
                $profile = new EntrepreneurProfile();
                $profile->Id_Site = $siteName;
                $profile->Entrepreneur_Khmer_name = $data->form->site_confirmed->entrepreneur_resignation->entrepreneur_khmer_name ?? null;
                $profile->Entrepreneur_English_name = $data->form->site_confirmed->entrepreneur_resignation->entrepreneur_english_name ?? null;
                $profile->Sex = $data->form->site_confirmed->entrepreneur_resignation->sex ?? null;
                $profile->Reason_Resign = $data->form->site_confirmed->entrepreneur_resignation->reason_for_leaving ?? null;
                $profile->Detail_Resign = $data->form->site_confirmed->entrepreneur_resignation->detail_reason ?? null;
                $profile->Resignation_Date = \Carbon\Carbon::parse($data->form->site_confirmed->entrepreneur_resignation->when_did_heshe_resign) ?? null;
                $profile->Submitted_Date = \Carbon\Carbon::parse($data->form->site_confirmed->entrepreneur_resignation->when_did_heshe_resign) ?? null;
                $profile->Site_Status = $data->form->site_confirmed->entrepreneur_resignation->site_status ?? null;
                $profile->Status = $data->form->site_confirmed->what_do_you_want_to_do ?? null;
                $profile->save();

                
            }
            else if (isset($data->form->site_confirmed->what_do_you_want_to_do) && 
            $data->form->site_confirmed->what_do_you_want_to_do == "new_entrepreneur_coming")
            {
                // Insert data to EntrepreneurProfile
                $profile = new EntrepreneurProfile();
                $profile->Id_Site = $siteName;
                $profile->Status = $data->form->site_confirmed->what_do_you_want_to_do ?? null;
                $profile->Entrepreneur_Khmer_name = $data->form->site_confirmed->new_entrepreneur_recruitment->entrepreneur_khmer_name ?? null;
                $profile->Entrepreneur_English_name = $data->form->site_confirmed->new_entrepreneur_recruitment->entrepreneur_name_english ?? null;
                $profile->Sex = $data->form->site_confirmed->new_entrepreneur_recruitment->sex ?? null;
                $profile->Commune = $data->form->site_confirmed->new_entrepreneur_recruitment->commune__village ?? null;
                $profile->DOB = \Carbon\Carbon::parse($data->form->site_confirmed->new_entrepreneur_recruitment->date_of_birth) ?? null;
                $profile->Working_Date = \Carbon\Carbon::parse($data->form->site_confirmed->new_entrepreneur_recruitment->date_start_working_in_station) ?? null;
                $profile->Submitted_Date = \Carbon\Carbon::parse($data->form->site_confirmed->new_entrepreneur_recruitment->date_start_working_in_station) ?? null;
                $profile->Education = $data->form->site_confirmed->new_entrepreneur_recruitment->education ?? null;
                $profile->Entrepreneur_Phone = $data->form->site_confirmed->new_entrepreneur_recruitment->first_phone_number ?? null;
                $profile->Province = $data->form->site_confirmed->new_entrepreneur_recruitment->province ?? null;
                $profile->Previous_Job = $data->form->site_confirmed->new_entrepreneur_recruitment->what_does_he_do_before_joining_ts ?? null;
                $profile->save();
            }
            else if (isset($data->form->site_confirmed->what_do_you_want_to_do) && 
            $data->form->site_confirmed->what_do_you_want_to_do == "site_closure")
            {
                // Insert data to EntrepreneurProfile
                $profile = new EntrepreneurProfile();
                $profile->Id_Site = $siteName;
                $profile->Status = $data->form->site_confirmed->what_do_you_want_to_do ?? null;
                $profile->Closed_Date = \Carbon\Carbon::parse($data->form->site_confirmed->site_closure->closed_date) ?? null;
                $profile->Close_Description = $data->form->site_confirmed->site_closure->close_description ?? null;
                $profile->Reason_Closed_Site = $data->form->site_confirmed->site_closure->reason_closed_site ?? null;
                $profile->Submitted_Date = \Carbon\Carbon::parse($data->form->site_confirmed->site_closure->closed_date) ?? null;
                $profile->save();
            }
            else if (isset($data->form->site_confirmed->what_do_you_want_to_do) && 
            $data->form->site_confirmed->what_do_you_want_to_do == "site_reopen")
            {
                // Insert data to EntrepreneurProfile
                $profile = new EntrepreneurProfile();
                $profile->Id_Site = $siteName;
                $profile->Status = $data->form->site_confirmed->what_do_you_want_to_do ?? null;
                $profile->Reopen_Date = \Carbon\Carbon::parse($data->form->site_confirmed->site_reopen->reopen_date) ?? null;
                $profile->Submitted_Date = \Carbon\Carbon::parse($data->form->site_confirmed->site_reopen->reopen_date) ?? null;
                $profile->save();
            }
            
        }
        if ($profile->wasRecentlyCreated ?? false) {
            return response()->json(['status' => 'success']);
        } else {
            return response()->json(['status' => 'not success']);
        }
    }
    public function downloadEntrepreneurContract1($path)
    {
        $filePath = urldecode($path);

        if (Storage::exists($filePath)) {
            return Storage::download($filePath);
        }

        return response()->json(['message' => 'File not found.'], 404);
    }
    public function downloadEntrepreneurContract($filename)
{
    $path = storage_path('app/public/En_Contract/' . $filename);

    if (!file_exists($path)) {
        return response()->json(['error' => 'File not found.'], 404);
    }

    return response()->download($path);
}

    /**
     * Show the form for creating a new resource.
     */
    public function create()
    {
         $updated="";
            $sitesWithEnName = Site::whereNotNull('Entrepreneur_English_Name')->get();
            foreach ($sitesWithEnName as $site)
            {
                // Try to find the most recent entrepreneurProfile for this site
                $latestProfile = EntrepreneurProfile::where('Id_Site', $site->Id_Site)
                    ->latest('Submitted_Date')
                    ->first();    
                if ($latestProfile) 
                {
                  $updated=  $latestProfile->update([
                    'Entrepreneur_English_name' => $site->Entrepreneur_English_Name
                ]);
                } 
                else 
                {
                    // Create new record if doesn't exist
                   $updated= EntrepreneurProfile::create([
                        'Id_Site' => $site->Id_Site,
                        'Entrepreneur_English_name' => $site->Entrepreneur_English_Name,
                    ]);
                }
            }
            
                if ($updated) 
                {
                    return response()->json(['status' => 'success', 'message' => 'Profile updated']);
                } 
                else 
                {
                    return response()->json(['status' => 'error', 'message' => 'Update failed']);
                }
            
    }

public function uploadEntrepreneurContract(Request $request)
{
    // $request->validate([
    //     'file' => 'required|file|max:5120|mimetypes:application/pdf,application/zip',
    //     'site_id' => 'required|exists:entrepreneur_profiles,id',
    // ]);

    $file = $request->file('file');
    $filename = time() . '_' . $file->getClientOriginalName();
    $file->storeAs('En_Contract', $filename, 'public'); // stored in storage/app/public/En_Contract

    // Save only the filename in the database
    EntrepreneurProfile::where('id', $request->site_id)
        ->update(['Contract' => $filename]);

    return response()->json(['message' => 'Contract uploaded and saved.']);
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
    public function show()
    {
        $data = Site::with(['entrepreneurProfiles' => function($query) {
            $query->where('Status', 'new_entrepreneur_coming')
             ->orderBy('Submitted_Date', 'desc');
        }])
        ->select('Id_Site', 'Platform','Advisor')
        ->whereNotIn('Platform', ['Dead', 'Stop'])
        ->whereNotIn('Id_Site', ['A3', 'A4', 'A5','C12','A6','A7'])
        ->get()
        ->map(function($site) {
            return [
                'Id_Site' => $site->Id_Site,
                'Platform' => $site->Platform,
                'Advisor' => $site->Advisor,
                'En_Data' => $site->entrepreneurProfiles->first() // Get first matching profile
            ];
        });

        return response()->json($data);
    }

    /**
     * Show the form for editing the specified resource.
     */
    public function edit($id)
    {
        $entrepreneurProfile = EntrepreneurProfile::find($id);
        if ($entrepreneurProfile) {
            return response()->json(['status' => 'success', 'data' => $entrepreneurProfile]);
        } else {
            return response()->json(['status' => 'error', 'message' => 'Entrepreneur profile not found.'], 404);
        }
        
    }

    /**
     * Update the specified resource in storage.
     */
    public function update(Request $request, int $id)
    {
        $en = EntrepreneurProfile::find($id);
        $en->fill($request->all());
        $en->save();
        return response()->json(['status' => 'success', 'data' => $en]);
    }

    /**
     * Remove the specified resource from storage.
     */
    public function destroy($id)
    {
        $entrepreneurProfile = EntrepreneurProfile::find($id);
        if ($entrepreneurProfile) {
            $entrepreneurProfile->delete();
            return response()->json(['status' => 'success', 'message' => 'Entrepreneur profile deleted successfully.']);
        } else {
            return response()->json(['status' => 'error', 'message' => 'Entrepreneur profile not found.'], 404);
        }
    }
    public function detailEntrepreneur ($id, Request $request)
    {
        $entrepreneurProfile = EntrepreneurProfile::where('Id_Site', $id)
        ->where('Status', 'entrepreneur_resignation')
        ->orderBy('Submitted_Date', 'desc')
        ->get();
       // dd($entrepreneurProfile);
        // if ($entrepreneurProfile) {
        //     return response()->json(['status' => 'success', 'data' => $entrepreneurProfile]);
        // } else {
        //     return response()->json(['status' => 'error', 'message' => 'Profile not found']);
        // }
        return response()->json($entrepreneurProfile);
    }
}
