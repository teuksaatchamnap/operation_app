<?php

namespace App\Http\Controllers;

use App\Imports\SitesImport;
use App\Imports\TechnicianSite;
use App\Mail\ChangeSiteToPlatform;
use App\Models\Site;
use App\Models\SiteContract;
use App\Models\User;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Log;
use Illuminate\Support\Facades\Mail;
use Illuminate\Support\Facades\Storage;
use Maatwebsite\Excel\Facades\Excel;
use Illuminate\Support\Str;

class SiteController extends Controller
{
    public function index(Request $request)
    {
        if ($request->has("siteAdmin")) {
            return Site::with("siteContract:Id_Site,path,commune_contract,training_contract")
                ->orderBy("Id_Site")
                ->whereNotIn("Platform", ["Dead", "Stop"])
                ->whereNotIn("Id_Site", [ "A7"])
                ->get();
        } else {
            return Site::with("siteContract:Id_Site,path,commune_contract,training_contract")
                ->select("Id_Site", "Platform", "Advisor")
                ->whereNotIn("Platform", ["Dead", "Stop"])
                ->whereNotIn("Id_Site", [ "A7"])
                ->orderBy("Id_Site")
                ->get();
        }
    }

    public function advisorsEmail()
    {
        $list= ['Advisor','Senior Advisor'];
        $result = User::select('email')
            ->distinct()
            ->whereNotNull('email')
            ->whereIn('staff_position', $list)
            ->get();
        return response()->json($result);
    }
    public function storeOrUpdateCommuneOrTrainingContract(Request $request)
    {
        $contract = SiteContract::firstOrNew(['Id_Site' => $request->site_id]);

        if ($request->hasFile('commune_contract')) {
            $file = $request->file('commune_contract');
            $filename = time() . '_' . $file->getClientOriginalName();
            $path = $file->storeAs('commune_contract', $filename, 'public');

            if ($contract->commune_contract && Storage::disk('public')->exists($contract->commune_contract)) {
                Storage::disk('public')->delete($contract->commune_contract);
            }

            $contract->commune_contract = $path;
        }

        if ($request->hasFile('training_contract')) {
            $file = $request->file('training_contract');
            $filename = time() . '_' . $file->getClientOriginalName();
            $path = $file->storeAs('training_contract', $filename, 'public');

            if ($contract->training_contract && Storage::disk('public')->exists($contract->training_contract)) {
                Storage::disk('public')->delete($contract->training_contract);
            }

            $contract->training_contract = $path;
        }

        $contract->save();

        // Debug after save
       // \Log::info('Contract after save (model):', $contract->toArray());

        // Fetch fresh from DB to confirm persisted values
        $fresh = SiteContract::find($contract->id);
       // \Log::info('Contract fresh from DB:', $fresh->toArray());

        return response()->json(['message' => 'Contract saved successfully.']);
    }

    public function getSites(Request $request)
    {
        // $site = Site::select('Id_Site')->get();
        // return response()->json(["site1" => $site]);
        return Site::select('Id_Site')->get();
    }
    public function editTechnicianSite(Request $request)
    {
        if ($request->file('file')) {
            $import =  Excel::import(new TechnicianSite, request()->file('file'));

            if ($import) {
                return  "Data Uploaded Succesfully! ";
            } else {
                return "Data Uploaded failed! ";
            }
        }
    }
    private function uploadEntreContract($s, $body)
    {
        $recipients = ['chamnap.keo@teuksaat1001.com'];
        // Mail::to($recipients)->send(new EntrepreneurEmail($title,$body));
        Mail::to($recipients)->send(new ChangeSiteToPlatform($s, $body));
    }

    public function updateSite(Request $request)
    {
        // dd(json_decode($request->input('data')));
        $siteData = json_decode($request->data, true);
        $s = $siteData['Id_Site'];
        $site = Site::where("Id_Site", $siteData['Id_Site'])->firstOrFail();
        $site->fill($siteData);
        // $updates = json_decode($site->last_updates, true) ?? [];
        // $updates->push(["user" => auth()->user()->email, "date" => date("Y-m-d H:i:s")]);
        // $site->last_updates = $updates; use this, we need to declare in model 'last_updates' => 'collection',
        $updates = json_decode($site->last_updates, true) ?? []; // Use null coalescing
        $updates[] = ["user" => auth()->user()->email, "date" => date("Y-m-d H:i:s")]; // Direct array push
        $site->last_updates = json_encode($updates); // Encode back to JSON string
        $site->save();
        return $site;
    }

    public function store(Request $request)
    {

        $siteData = json_decode($request->data, true);
        $s = $siteData['Id_Site'];
        // $request->validate([$siteData['Id_Site'] => 'required']);
        //dd($siteData);
        $site = new Site();
        //if (is_object($siteData)) {
        // foreach($siteData as $key => $value) {
        //     $site->{$key} = $value;
        // }
        $site->fill($siteData);
        $site["last_updates"] = collect([["user" => auth()->user()->email, "date" => date("Y-m-d H:i:s")]]);
        $site->save();

        if ($request->hasFile('files')) {
            foreach ($request->file('files') as $image) {
                // $filename = time() . '_' . $file->getClientOriginalName();
                // $filePath = $file->storeAs('uploads', $filename, 'public');
                $imageName = time() . '_' . Str::random(20) . '.' . $image->extension();
                $imagePath = $image->storeAs('siteContract/' . $siteData['Id_Site'], $imageName, 'public');
                SiteContract::create(['path' => $imagePath, 'Id_Site' => $siteData['Id_Site']]);
            }
            $this->uploadEntreContract($s, $imageName);
        }
        return $site;
    }

    public function downloadCommuneContract($filename)
    {
        $path = storage_path('app/public/commune_contract/' . $filename);

        if (!file_exists($path)) {
            return response()->json(['error' => 'File not found.'], 404);
        }

        return response()->download($path);
    }

    public function downloadTrainingContract($filename)
    {
        $path = storage_path('app/public/training_contract/' . $filename);

        if (!file_exists($path)) {
            return response()->json(['error' => 'File not found.'], 404);
        }

        return response()->download($path);
    }


    public function importExcel(Request $request)
    {
        $existingSites = Site::select(["Id_Site"])->get();
        $importedSites = collect(Excel::toArray(new SitesImport, $request->file)[0]);
        $importedSites = $importedSites->map(function ($site) use ($existingSites) {
            $cleanSite = [
                '_new' => $existingSites->where("Id_Site", trim($site["Id_Site"]))->first() == null
            ];
            foreach ($site as $key => $value) {
                if (is_string($key) && strlen($key) > 5) {
                    $cleanSite[$key] = $value;
                }
            }
            return $cleanSite;
        });
        if ($request->has("analyse")) {
            return $importedSites;
        } else {
            return $importedSites->map(function ($siteData) use ($existingSites) {
                if ($siteData["_new"] === false) {
                    $site = $existingSites->where("Id_Site", $siteData["Id_Site"])->first();
                } else {
                    $site = new Site();
                }
                unset($siteData["_new"]);
                foreach ($siteData as $key => $value) {
                    if (in_array($key, ["ProjectAgreement", "Sale_Starting_Date", "Date_of_birth", "Date_start_working"]) && $value) {
                        $site->{$key} = \PhpOffice\PhpSpreadsheet\Shared\Date::excelToDateTimeObject(intval($value));
                    } else {
                        if (!$value || $value == "") {
                            $site->{$key} = null;
                        } else {
                            $site->{$key} = $value;
                        }
                    }
                }
                $site->save();
                return $site;
            });
        }
    }

    public function downloadTemplate(Request $request)
    {
        $sites = [];
        $template = storage_path('app/templates/sites.xlsx');
        $TBS = new \clsTinyButStrong();
        $ok = class_exists('clsOpenTBS', true); // hack to force class loading of TBS
        $TBS->Plugin(TBS_INSTALL, OPENTBS_PLUGIN);
        $TBS->OtbsMsExcelExplicitRef = false;
        $TBS->LoadTemplate($template, OPENTBS_ALREADY_UTF8);
        $TBS->SetOption("noerr", true);
        $TBS->MergeBlock('a', $sites);
        $filename = "sites_template.xlsx";
        $TBS->Show(OPENTBS_DOWNLOAD, $filename);
    }

    public function exportFromCloudSQL(Request $request)
    {
        if (str_contains($request->headers->get('origin'), "dashboard.teuksaat1001.com") || str_contains($request->headers->get('origin'), "teuksaat.1001fontaines.com")) {
            header("Access-Control-Allow-Origin: *");
            $this->export($request);
        } else {
            return abort(401, "Only calls from cloud-sql server are allowed on this route (cannot work from " . $request->headers->get('origin') . ")");
        }
    }

    public function export(Request $request)
    {
        $sites = Site::get()->map(fn($row) => $row->toArray());
        $template = storage_path('app/templates/sites.xlsx');
        $TBS = new \clsTinyButStrong();
        $ok = class_exists('clsOpenTBS', true); // hack to force class loading of TBS
        $TBS->Plugin(TBS_INSTALL, OPENTBS_PLUGIN);
        $TBS->OtbsMsExcelExplicitRef = false;
        $TBS->LoadTemplate($template, OPENTBS_ALREADY_UTF8);
        $TBS->SetOption("noerr", true);
        $TBS->MergeBlock('a', $sites);
        //$TBS->PlugIn(OPENTBS_DEBUG_XML_CURRENT);
        $filename = "sites_" . time() . ".xlsx";
        $TBS->Show(OPENTBS_DOWNLOAD, $filename);
    }

    public function destroy(Site $site)
    {
        //
    }
}
