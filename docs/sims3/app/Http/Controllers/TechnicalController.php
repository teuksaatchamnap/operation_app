<?php

namespace App\Http\Controllers;

use App\Imports\TechnicianSite;
use App\Imports\Test1Import;
use App\Mail\RequestTechnicalItem;
use App\Mail\TechnicalAlertEmail;
use App\Mail\ValidateTechnicalItem;
use App\Models\Consumable;
use App\Models\MinimumStock;
use App\Models\Site;
use App\Models\Technical;
use App\Models\TechnicalProblem;
use Illuminate\Http\Request;
use Illuminate\Support\Carbon;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Mail;
use Maatwebsite\Excel\Facades\Excel;
use Illuminate\Support\Facades\Log;
//use Mail;
class TechnicalController extends Controller
{
    /**
     * Display a listing of the resource.
     */
    public function index()
    {

        $result = Technical::with("site:Id_Site,technician_site")
            ->whereHas("site")
            ->where("site_platform", "!=", "Stop")
            ->where("site_platform", "!=", "Dead")
            ->orderBy('problem_date', 'desc')
            ->limit(1000)
            ->get();
        // $result = $result->map(function ($item) {
        //     $item->site_technical = $item['site'];
        //     return $item;
        // });
        return [
            'result' => $result,
            'email' => auth()->user()->email
        ];
    }
    public function minimumStock(Request $request)
    {
        $request->validate([
            'selectDate' => 'required|date_format:Y-m'
        ]);
        $data = MinimumStock::select('email', 'item_code', 'item_name', 'item_unit', DB::raw('SUM(use_qty) as total_qty'))
            ->whereMonth('month', date('m', strtotime($request->selectDate)))
            ->whereYear('month', date('Y', strtotime($request->selectDate)))
            ->orderBy('month', 'desc')
            ->groupBy('email', 'item_code', 'item_name', 'item_unit')
            ->get();

        return response()->json($data);
    }
    public function getDataMinimumStock(Request $request)
    {
        $data = Technical::select('site', 'quotation', 'technician')
            ->whereMonth('problem_date', date('m', strtotime($request->selectDate)))
            ->whereYear('problem_date', date('Y', strtotime($request->selectDate)))
            ->where('stock_type', 'minimum_stock')
            ->orderBy('problem_date', 'desc')
            ->get();
        $storeData = array();
        $codes = ['113002', '112002', '212010', '208009', '208011', '208004', '208005', '208010', '208012', '209009'];
        $technicianList = [
            'Ros Veasna' => 'veasna.r@teuksaat1001.com',
            'Pin Phalla' => 'phalla.p@teuksaat1001.com',
            'Morn Phanith' => 'phanith.m@teuksaat1001.com',
            'Pech Odom' => 'odom.p@teuksaat1001.com',
            'Neang Vuthy' => 'vuthy.n@teuksaat1001.com',
            'Men Pisak' => 'pisak.m@teuksaat1001.com',
            'Sok Dara' => 'dara.s@teuksaat1001.com',
            'Sok Darith' => 'darith.s@teuksaat1001.com',
            'Sen Sak' => 'sak.s@teuksaat1001.com',
            'Min Theary' => 'theary.m@teuksaat1001.com'
        ];
        foreach ($data as $item) {
            $t = $item->technician;
            $quotation = json_decode($item->quotation);
            foreach ($quotation as $q) {
                if (in_array($q->item_ref, $codes)) {
                    $minimum = new MinimumStock();
                    $minimum->site = $q->siteQuotation;
                    $minimum->month = $q->dateSend;
                    $minimum->use_qty = $q->quantity;
                    $minimum->item_code = $q->item_ref;
                    $minimum->item_name = $q->intervention_subcategory;
                    $minimum->item_unit = $q->unit;
                    $minimum->email = $t;
                    $minimum->pay_by = $q->who_pay;
                    $minimum->save();

                    if (array_key_exists($t, $technicianList)) {
                        $ta = $technicianList[$t];
                        $storeData[] = [
                            'site' => $q->siteQuotation,
                            'item_code' => $q->item_ref,
                            'item_name' => $q->intervention_subcategory,
                            'item_unit' => $q->unit,
                            'use_qty' => $q->quantity,
                            'who_pay' => $q->who_pay,
                            'technician' => $t,
                            'email_technician' => $ta
                        ];
                    }
                }
            }
        }
        $groupedData = collect($storeData)
            ->groupBy(function ($item) {
                return $item['item_code'] . '_' . $item['site']; // Combine fields for grouping
            })
            ->map(function ($items, $key) {
                return [
                    'site' => $items[0]['site'],
                    'item_code' => $items[0]['item_code'],
                    'item_name' => $items[0]['item_name'],
                    'item_unit' => $items[0]['item_unit'],
                    'total_qty' => array_sum(array_column($items->toArray(), 'use_qty')), // Sum up 'use_qty'
                    'pay_by' => $items[0]['who_pay'],
                    'email' => $items[0]['technician'],
                    'email_technician' => $items[0]['email_technician'],
                ];
            })
            ->values(); // Reset keys
        $orderedData = $groupedData->sortByDesc('email_technician')->values();
        return response()->json($orderedData);
    }

    public function downloadDataMinimumStock(Request $request)
    {

        $data = Technical::select('site', 'quotation', 'technician')
            ->whereMonth('problem_date', date('m', strtotime($request->selectDate)))
            ->whereYear('problem_date', date('Y', strtotime($request->selectDate)))
            ->where('stock_type', 'minimum_stock')
            ->orderBy('problem_date', 'desc')
            ->get();
        $inputFileName = storage_path('app/templates/TechnicalDetailStock.xlsx');
        $storeData = array();
        $codes = ['113002', '112002', '212010', '208009', '208011', '208004', '208005', '208010', '208012', '209009'];
        foreach ($data as $item) {
            $t = $item->technician;
            $quotation = json_decode($item->quotation);
            foreach ($quotation as $q) {
                if (in_array($q->item_ref, $codes)) {

                    $storeData[] = [
                        'site' => $q->siteQuotation,
                        'item_code' => $q->item_ref,
                        'item_name' => $q->intervention_subcategory,
                        'item_unit' => $q->unit,
                        'use_qty' => $q->quantity,
                        'who_pay' => $q->who_pay,
                        'email' => $t
                    ];
                }
            }
        }
        $TBS = new \clsTinyButStrong;
        $ok = class_exists('clsOpenTBS', true);
        $TBS->OtbsMsExcelExplicitRef = false;
        $TBS->Plugin(\TBS_INSTALL, \OPENTBS_PLUGIN);
        $TBS->LoadTemplate($inputFileName, \OPENTBS_ALREADY_UTF8);
        $TBS->PlugIn(OPENTBS_SELECT_SHEET, 1);
        $TBS->SetOption("noerr", true);
        $TBS->MergeBlock('b', $storeData);

        $TBS->Show(OPENTBS_DOWNLOAD, "downloadMinimumStock.xlsx");
        return response()->json($storeData);
    }

    public function  downloadMinimumStock(Request $request)
    {
        $inputFileName = storage_path('app/templates/mini.xlsx');
        $dataAction = MinimumStock::whereMonth('month', date('m', strtotime($request->selectDate)))
            ->whereYear('month', date('Y', strtotime($request->selectDate)))
            ->where('email', $request->email)
            ->orderBy('month', 'desc')
            ->get();
        $dataActionExcel = array();
        foreach ($dataAction as $item) {
            $dataActionExcel[] = $item->toArray();
        }
        $data = MinimumStock::select('item_code', DB::raw('SUM(use_qty) as total_qty'))
            ->whereMonth('month', date('m', strtotime($request->selectDate)))
            ->whereYear('month', date('Y', strtotime($request->selectDate)))
            ->where('email', $request->email)
            ->orderBy('month', 'desc')
            ->groupBy('email', 'item_code', 'use_qty')
            ->get();

        $obj = array();

        $dataNewPrint = array();
        $codes = ['113002', '112002', '212010', '208009', '208011', '208004', '208005', '208010', '208012', '209009'];
        $groupedData = $data->groupBy('email'); // Group data by email

        foreach ($groupedData as $emailData) {
            $obj = [
                'today' => Carbon::now()->format('d-m-Y'),
                'email' => $request->email,
            ];
            if ($request->email == 'Neang Vuthy' || $request->email == 'Men Pisak' || $request->email == 'Morn Phanith') {
                $obj['title'] = 'ភ្នំពេញ';
                $obj['address'] = "#100,Str.95, Sangkat Beoung Trobek,Khan Chamkar Mon, Phnom Penh, Cambodia.";
                $obj['cashier'] = "Chorn Chankimsan";
                $obj['supervisor'] = "Lo Synada";
                $obj['phone'] = "023 215 427";
            }
            if ($request->email == 'Pech Odom' || $request->email == 'Ros Veasna') {
                $obj['title'] = 'បាត់ដំបង';
                $obj['address'] = "#676, Group 15.O-TaKom 1 village, Toul Ta eak commune, Battambang City, Cambodia";
                $obj['cashier'] = "Nou Chamroeun";
                $obj['supervisor'] = "Touch Bros";
                $obj['phone'] = "053 953 161";
            }
            if ($request->email == 'Pin Phalla' || $request->email == 'Sok Dara') {
                $obj['title'] = 'កំពង់ចាម';
                $obj['address'] = "Ti 2 village, Songkat Veal Vong, Kompong Cham city, Kompong Cham province, Cambodia.";
                $obj['cashier'] = "Hon Sreyrath";
                $obj['supervisor'] = "Lo Synada";
                $obj['phone'] = "042 210 898";
            }
            if ($request->email == 'Min Theary' || $request->email == 'Sen Sak' || $request->email == 'Sok Darith') {
                $obj['title'] = 'សៀមរាប';
                $obj['address'] = "Kasekam Village, Sangkat Sragne Krong Siem Reap , Siem Reap Province Siem Reap, 17252";
                $obj['cashier'] = "Heang Porleng";
                $obj['supervisor'] = "Touch Bros";
                $obj['phone'] = "042 210 898";
            }
            foreach ($codes as $code) {
                $obj['c' . $code] = 0; // Initialize all codes with 0
            }
            // Assign values to the corresponding codes
            foreach ($emailData as $item) {
                // if we write like this, it will show only item has codes
                // if (in_array($item->item_code, $codes)) {
                //     $obj['c' . $item->item_code] = $item->total_qty;
                // }
                // else {
                //     $obj['c' . $item->item_code] = 0;
                // }
                $obj['c' . $item->item_code] = intval($item->total_qty);
            }

            $dataNewPrint[] = $obj;
        }

        //dd($dataNewPrint);
        $TBS = new \clsTinyButStrong;
        $ok = class_exists('clsOpenTBS', true);
        $TBS->OtbsMsExcelExplicitRef = false;
        $TBS->Plugin(\TBS_INSTALL, \OPENTBS_PLUGIN);
        $TBS->LoadTemplate($inputFileName, \OPENTBS_ALREADY_UTF8);
        $TBS->PlugIn(OPENTBS_SELECT_SHEET, 1);
        $TBS->SetOption("noerr", true);
        $TBS->MergeBlock('a', [$obj]);
        $TBS->PlugIn(OPENTBS_SELECT_SHEET, 2);
        $TBS->MergeBlock('b', $dataActionExcel);
        $TBS->PlugIn(OPENTBS_SELECT_SHEET, 3);
        $TBS->MergeBlock('c', $dataNewPrint);
        $TBS->Show(OPENTBS_DOWNLOAD, "downloadMinimumStock.xlsx");
    }

    public function DownloadExcelMinimumStock(Request $request)
    {
        $obj = array();
        $inputFileName = storage_path('app/templates/minimumStock.xlsx');
        $obj['today'] = Carbon::now()->format('d-m-Y');
        $obj['email'] = $request->email;
        if ($request->email == 'vuthy.n@teuksaat1001.com' || $request->email == 'pisak.m@teuksaat1001.com' || $request->email == 'phanith.m@teuksaat1001.com') {
            $obj['title'] = 'ភ្នំពេញ';
            $obj['address'] = "#100,Str.95, Sangkat Beoung Trobek,Khan Chamkar Mon, Phnom Penh, Cambodia.";
            $obj['cashier'] = "Chorn Chankimsan";
            $obj['supervisor'] = "Lo Synada";
            $obj['phone'] = "023 215 427";
        } else if ($request->email == 'odom.p@teuksaat1001.com' || $request->email == 'veasna.r@teuksaat1001.com' || $request->email == 'darith.s@teuksaat1001.com') {
            $obj['title'] = 'បាត់ដំបង';
            $obj['address'] = "#676, Group 15.O-TaKom 1 village, Toul Ta eak commune, Battambang City, Cambodia";
            $obj['cashier'] = "Nou Chamroeun";
            $obj['supervisor'] = "Touch Bros";
            $obj['phone'] = "053 953 161";
        } else if ($request->email == 'phalla.p@teuksaat1001.com' || $request->email == 'dara.s@teuksaat1001.com') {
            $obj['title'] = 'កំពង់ចាម';
            $obj['address'] = "Ti 2 village, Songkat Veal Vong, Kompong Cham city, Kompong Cham province, Cambodia.";
            $obj['cashier'] = "Hon Sreyrath";
            $obj['supervisor'] = "Lo Synada";
            $obj['phone'] = "042 210 898";
        } else if ($request->email == 'theary.m@teuksaat1001.com' || $request->email == 'sak.s@teuksaat1001.com') {
            $obj['title'] = 'សៀមរាប';
            $obj['address'] = "Kasekam Village, Sangkat Sragne Krong Siem Reap , Siem Reap Province Siem Reap, 17252";
            $obj['cashier'] = "Heang Porleng";
            $obj['supervisor'] = "Touch Bros";
            $obj['phone'] = "042 210 898";
        } else {
            $obj['title'] = 'no data';
            $obj['address'] = "no data";
            $obj['cashier'] = "no data";
            $obj['supervisor'] = "no data";
            $obj['phone'] = "no data";
        }
        $TBS = new \clsTinyButStrong;
        $ok = class_exists('clsOpenTBS', true);
        $TBS->OtbsMsExcelExplicitRef = false;
        $TBS->Plugin(\TBS_INSTALL, \OPENTBS_PLUGIN);
        $TBS->LoadTemplate($inputFileName, \OPENTBS_ALREADY_UTF8);
        $TBS->PlugIn(OPENTBS_SELECT_SHEET, 1);
        $TBS->SetOption("noerr", true);
        $TBS->MergeBlock('c', [$obj]);

        $TBS->Show(OPENTBS_DOWNLOAD, "downloadMinimumStock.xlsx");
    }

    public function detailTechnical(string $site)
    {
        $technical= Technical::with('technicalProblem')
            ->where("site", "=", $site)->orderBy('problem_date', 'desc')->get();

        $data = array();

        foreach ($technical as $tech) {
            $techData = $tech->toArray();
            // Remove the technicalProblem array as we'll handle it separately
            unset($techData['technical_problem']);
            // Initialize variables to hold comma-separated values
            $problemCategories = [];
            $subProblems = [];
            $solution = [];
            $detailSolution = [];
            // Collect all problem categories and sub problems
            foreach ($tech->technicalProblem as $problem) {
                $problemCategories[] = $problem->problem_category;
                $subProblems[] = $problem->sub_problem;
                $solution[] = $problem->solution_list;
                $detailSolution[] = $problem->detail_solution;
            }
            // Join with commas and add to the main data
            $techData['problem_categories'] = implode(', ', $problemCategories);
            $techData['sub_problems'] = implode(', ', $subProblems);
            $techData['solutoin'] = implode(', ', $solution);
            $techData['detailSolution'] = implode(', ', $detailSolution);

            $data[] = $techData;
        }
        return $data;
    }
    /**
     * Show the form for creating a new resource.
     */
    public function getEmail()
    {
        return  auth()->user()->email;
    }
    public function create() {}

    public function downloadSite(string $site)
    {
        $inputFileName = storage_path('app/templates/downloadSiteDetail.xlsx');
        $technical = Technical::where("site", "=", $site)->orderBy('problem_date', 'desc')->get();
        $data = array();

        foreach ($technical as $tech) {
            $data = $tech->toArray();
        }

        //return $data;
        //dd($data);
        // $TBS = new \clsTinyButStrong;
        // $ok = class_exists('clsOpenTBS', true); 
        // $TBS->OtbsMsExcelExplicitRef = false;
        // $TBS->Plugin(\TBS_INSTALL, \OPENTBS_PLUGIN);
        // $TBS->LoadTemplate( $inputFileName,\OPENTBS_ALREADY_UTF8);
        // $TBS->PlugIn(OPENTBS_SELECT_SHEET, 1);
        // $TBS->SetOption("noerr", true);
        // $TBS->MergeBlock('t,a', $data);
        // $TBS->Show(OPENTBS_DOWNLOAD, "downloadSiteDetail.xlsx");
    }

    /**
     * Store a newly created resource in storage.
     */
    public function store(Request $request)
{
    $site = Site::find($request->site);

    $data = $request->all();
    $data['quotation'] = json_encode($data['quotation']);
    $data["report_by"] = auth()->user()->email;
    $data['site_platform'] = $site->Platform;
    $data['status'] = "Waiting Validation";

    // Convert to object for mail
    $technical = new Technical($data);

    try {
        // ✅ Send email FIRST
        $this->sendMailTechnical($technical);

        // ✅ Only save if email SUCCESS
        $technical->save();

        return response()->json([
            'success' => true,
            'data' => $technical
        ]);

    } catch (\Exception $e) {

        \Log::error('Mail sending failed: ' . $e->getMessage());

        return response()->json([
            'success' => false,
            'message' => 'Email sending failed. Data not saved.'
        ], 500);
    }
}

    private function sendMailTechnical($technical)
{
    $site = Site::where("Id_Site", $technical->site)->first();

    // ✅ Technician email
    $technician_email = !empty($site->technician_site)
        ? $site->technician_site
        : "chamnap.keo@teuksaat1001.com";

    // ✅ Supervisor mapping
    $group1 = [
        "leab.l@teuksaat1001.com",
        "odom.p@teuksaat1001.com",
        "veasna.r@teuksaat1001.com",
        "dara.s@teuksaat1001.com",
        "sak.s@teuksaat1001.com",
        "vichet.h@teuksaat1001.com",
    ];

    $group2 = [
        "vuthy.n@teuksaat1001.com",
        "pisak.m@teuksaat1001.com",
        "phanith.m@teuksaat1001.com",
        "phalla.p@teuksaat1001.com",
        "darith.s@teuksaat1001.com"
    ];

    $supervisor_email = null;

    if (in_array($site->technician_site, $group1)) {
        $supervisor_email = "bros.t@teuksaat1001.com";
    }

    if (in_array($site->technician_site, $group2)) {
        $supervisor_email = "chanthan.m@teuksaat1001.com";
    }

    // ✅ Platform emails
    $platformEmails = [
        'SR' => 'kimhong.p@teuksaat1001.com',
        'KC' => 'bun.ph@teuksaat1001.com',
        'PP' => 'lim.t@teuksaat1001.com',
        'BTB' => 'yet.y@teuksaat1001.com',
        'KSP' => 'rethy.m@teuksaat1001.com',
    ];

    // ✅ If no technician → fallback
    if (empty($site->technician_site)) {
        $recipients = ['chamnap.keo@teuksaat1001.com'];
    } else {
        $mainEmail = $platformEmails[$technical->site_platform] ?? null;

        $recipients = array_filter([
            $mainEmail,
            $supervisor_email,
            $technician_email,
            $technical->report_by
        ]);
    }

    // ✅ Send mail (will throw exception if fails)
    Mail::to($recipients)->send(new TechnicalAlertEmail($technical));
}
    private function sendMailRequestItem($technical)
    {
        $c = $technical->totalPriceAllItem;
        // $platformRecipients = [
        //     'BTB' => ['a@teuksaat1001.com', 'another@teuksaat1001.com'],
        //     'SR'  => ['b@teuksaat1001.com'],
        //     'KC'  => ['c@teuksaat1001.com'],
        //     'PP'  => ['d@teuksaat1001.com'],
        //     'KSP' => ['e@teuksaat1001.com'],
        // ];

        // $recipients = $platformRecipients[$technical->site_platform] ?? ['sokchann.c@teuksaat1001.com'];
        if ($c >= 200000) {
            if ($technical->site_platform == "BTB") {
                $recipients = ['yet.y@teuksaat1001.com', 'borin.t@teuksaat1001.com'];
            } elseif ($technical->site_platform == "SR") {
                $recipients = ['kimhong.p@teuksaat1001.com', 'borin.t@teuksaat1001.com'];
            } elseif ($technical->site_platform == "KC") {
                $recipients = ['bun.ph@teuksaat1001.com', 'borin.t@teuksaat1001.com'];
            } elseif ($technical->site_platform == "PP") {
                $recipients = ['lim.t@teuksaat1001.com', 'borin.t@teuksaat1001.com'];
            } elseif ($technical->site_platform == "KSP") {
                $recipients = ['rethy.m@teuksaat1001.com', 'borin.t@teuksaat1001.com'];
            } else {
                $recipients = ['chamnap.keo@teuksaat1001.com'];
            }

            // $recipients = ['chamnap.keo@teuksaat1001.com'];
        } else {
            $recipients = ['borin.t@teuksaat1001.com'];
        }
        // $recipients = ['borin.t@teuksaat1001.com'];
        // $recipients = ['chamnap.keo@teuksaat1001.com'];
        Mail::to($recipients)->send(new RequestTechnicalItem($technical));
    }
    private function sendMailValidateItem($technical)
    {
        if ($technical->item_platform == "SR") {
            //  $recipients = ['chamnap.keo@teuksaat1001.com'];
            $recipients = ['kimhong.p@teuksaat1001.com', 'bros.t@teuksaat1001.com', 'theary.m@teuksaat1001.com', "dara.s@teuksaat1001.com", "porleng.h@teuksaat1001.com", "dina.d@teuksaat1001.com", "geklorng.kh@teuksaat1001.com", "sreysrors.u@teuksaat1001.com"];
        } elseif ($technical->item_platform == "KC") {
            $recipients = ['bun.ph@teuksaat1001.com', "phalla.p@teuksaat1001.com", "bros.t@teuksaat1001.com", "darith.s@teuksaat1001.com", "sreyrath.h@teuksaat1001.com", "dina.d@teuksaat1001.com", "geklorng.kh@teuksaat1001.com", "sreysrors.u@teuksaat1001.com"];
        } elseif ($technical->item_platform == "PP") {
            $recipients = ['lim.t@teuksaat1001.com', "bros.t@teuksaat1001.com", "pisak.m@teuksaat1001.com", "vuthy.n@teuksaat1001.com", "sak.s@teuksaat1001.com", "sorvy.m@teuksaat1001.com", "dina.d@teuksaat1001.com", "geklorng.kh@teuksaat1001.com", "sreysrors.u@teuksaat1001.com"];
        } elseif ($technical->item_platform == "BTB") {
            $recipients = ['yet.y@teuksaat1001.com', "bros.t@teuksaat1001.com", "veasna.r@teuksaat1001.com", "odom.p@teuksaat1001.com", "sak.s@teuksaat1001.com", "chamroeun.no@teuksaat1001.com", "dina.d@teuksaat1001.com", "geklorng.kh@teuksaat1001.com", "sreysrors.u@teuksaat1001.com"];
        } elseif ($technical->item_platform == "KSP") {
            $recipients = ['rethy.m@teuksaat1001.com', "bros.t@teuksaat1001.com", "sak.s@teuksaat1001.com", "vuthy.n@teuksaat1001.com", "dina.d@teuksaat1001.com", "geklorng.kh@teuksaat1001.com", "sorvy.m@teuksaat1001.com", "sreysrors.u@teuksaat1001.com"];
        } else {
            $recipients = ['chamnap.keo@teuksaat1001.com'];
        }
        // if ($technical->site_platform != '')
        // $recipients = ['account@teuksaat1001.com','chamnap.keo@teuksaat1001.com'];
        $recipients1 = ['chamnap.keo@teuksaat1001.com'];

        Mail::to($recipients)->send(new ValidateTechnicalItem($technical));
    }

    /**
     * Display the specified resource.
     */
    public function show($id)
    {
        //dd($id);
        $technical = Technical::find($id);
        $technical['email'] = auth()->user()->email;
        return $technical;
    }

    /**
     * Show the form for editing the specified resource.
     */
    public function edit(Technical $technical)
    {
        //
    }

    /**
     * Update the specified resource in storage.
     */
    public function update(Request $request, int $id)
    {
        $technical = Technical::find($id);
        //$c =$request->totalPriceAllItem;

        $checkRequestRT = "";
        $validateRequestRT = "";
        $requestStock = '';
        $validateItem = '';
        $re = "";
        if (!$technical) {
            return response()->json(['message' => 'Technical record not found'], 404);
        }

        if ($technical) {
            $technical->fill($request->all());
            if ($request->Fixed == " " || $request->Fixed == "null" || $request->Fixed == null || $request->Fixed == NULL) {
                $technical->status = 'Validate_Ongoing';
            } else {
                $technical->status = 'Fixed';
            }
            // Request Stock
            if ($request->rt_request_stock == "stock_need" && $request->quotation != '' && $technical->rt_send_qoutation == '') {
                $requestItem = array();
                $requestItem = $request->quotation;
                foreach ($requestItem as $item) {
                    $requestStock .= "=>" . $item['intervention_subcategory'] . "\n";
                }
                $checkRequestRT = "yes";
                $technical->rt_send_qoutation = 1;
            }
            if ($request->Fixed == "Fixed") {
                $dataRTProblem = $request->allRTProblem;
                foreach ($dataRTProblem as $item) {
                    $technicalProblem = new TechnicalProblem();
                    $technicalProblem->technical_id = $technical->id;
                    $technicalProblem->problem_category = $item['rt_problem'];
                    $technicalProblem->sub_problem = $item['rt_sub_problem'];
                    $technicalProblem->solution_list = $item['rt_new_solution'];
                    $technicalProblem->detail_solution = $item['rt_comment'];
                    $technicalProblem->save();
                }
            }
            // manager validates
            if (($request->managerValidateItem == "validated_item" && $request->quotation != '') && ($technical->manager_validate_qoutation == '' || $technical->manager_validate_qoutation == 0)) {
                $t = $request->technician;
                if ($request->stock_type == 'minimum_stock') {
                    $list = [113002, 112002, 212010, 208009, 208011, 208004, 208005, 208010, 208012, 209009];
                    //$tech = Site::where('Id_Site', $technical->site)->first();
                    $sendItem1 = $request->quotation;
                    foreach ($sendItem1 as $item) {
                        if (in_array($item['item_ref'], $list)) {
                            $minimum = new MinimumStock();
                            $minimum->site = $item['siteQuotation'];
                            $minimum->month = $item['dateSend'];
                            $minimum->use_qty = $item['quantity'];
                            $minimum->item_code = $item['item_ref'];
                            $minimum->item_name = $item['intervention_subcategory'];
                            $minimum->item_unit = $item['unit'];
                            $minimum->email = $t;
                            $minimum->pay_by = $item['who_pay'];
                            $minimum->save();
                        }
                    }
                }
                $sendItem = $request->quotation;
                foreach ($sendItem as $item) {
                    $validateItem .= "=>" . $item['item_ref'] . '-' . $item['intervention_subcategory'] . "(" . $item['who_pay'] . ")" . "QTY :" . $item['quantity'] . "\n";
                    $consumable = new Consumable();
                    $consumable->Id_Site = $item['siteQuotation'];
                    //$consumable->Month = $item['send_month'] . "-01";
                    // this is another option
                    // $sendMonth = $item['send_month'];
                    // if ($today->isSameDay($dayBeforeEndOfMonth)) {
                    //     $sendMonth = Carbon::createFromFormat('Y-m', $item['send_month'])->addMonth()->format('Y-m');
                    // }   
                    $today = now();
                    $lastDayOfMonth = $today->copy()->endOfMonth();
                    $dayBeforeEndOfMonth = $lastDayOfMonth->copy()->subDay();
                    // If today is the day before the end of month, increment the month
                    //$sendMonth = $today->isSameDay($dayBeforeEndOfMonth) ? Carbon::createFromFormat('Y-m', $item['send_month'])->addMonth()->format('Y-m') : $item['send_month'];
                    if ($today->isSameDay($lastDayOfMonth) || $today->isSameDay($lastDayOfMonth->copy()->subDay())) {
                        $sendMonth = Carbon::createFromFormat('Y-m', $item['send_month'])->addMonth()->format('Y-m');
                    } else {
                        $sendMonth = $item['send_month'];
                    }
                    $consumable->Month = $sendMonth . "-01";
                    $consumable->Date_submission = $item['dateSend'];
                    $consumable->Category = 3;
                    $consumable->Number_Item = $item['quantity'];
                    $consumable->item = $item['item_ref'];
                    $consumable->Price_Item = $item['total'];
                    $consumable->English_name = $item['intervention_subcategory'];
                    $consumable->Khmer_name = $item['intervention_category'];
                    $consumable->Unit = $item['unit'];
                    if ($item['who_pay'] == "ts_pay") {
                        $consumable->Payment_method = "TS_Internal_Charge";
                    } else {
                        $consumable->Payment_method = "Invoice";
                    }
                    // $consumable->Payment_method = "Invoice";
                    $consumable->Validate = 1;
                    $consumable->save();
                    // dump($consumable);
                }
                // dd("end");
                $validateRequestRT = 'yes';
                $technical->manager_validate_qoutation = 1;
            }
            $technical->quotation = $request->quotation;
            $technical->send_quotation = collect([["user" => auth()->user()->email, "date" => date("Y-m-d H:i:s")]]);
        }
        $technical->save();
        $technical['requestStock'] = $requestStock;
        $technical['resultCheck'] = $re;
        $technical['validateItemSendEmail'] = $validateItem;
        if ($checkRequestRT == "yes") $this->sendMailRequestItem($technical);
        if ($validateRequestRT == "yes") {
            $technical['validate_sent'] = $this->sendMailValidateItem($technical);
        }

        return $technical;
    }

    /**
     * Remove the specified resource from storage.
     */
    public function destroy(Technical $technical)
    {
        //
    }
    public function downloadDN(Request $request)
    {
        $inputFileName = storage_path('app/templates/dnTechnical.xlsx');
        $inter = Technical::findOrFail($request->dnid);
        $data = array();
        $data_sheet2 = array();
        $obj = array();
        $obj = $inter->toArray();
        $tech = $inter->toArray();
        $obj['today'] = Carbon::now()->format('d-m-Y');

        if ($inter->site_platform == 'PP') {
            $obj['title'] = 'ភ្នំពេញ';
            $obj['address'] = "ផ្ទះលេខ 100 ផ្លូវ 95 សង្កាត់បឹងត្របែក ខណ្ឌចំការមន ភ្នំពេញ ";
            $obj['cashier'] = "ឆន ចាន់គឺមសាន";
        }
        if ($inter->site_platform == 'BTB') {
            $obj['title'] = 'បាត់ដំបង';
            $obj['address'] = "ផ្ទះលេខ៦៧៦ ភូមិអូរតាគាំ១​ សង្កាត់ទួលតាឯក ក្រុងបាត់ដំបង ខេត្តបាត់ដំបង ";
            $obj['cashier'] = "នូ ចំរើន";
        }
        if ($inter->site_platform == 'KC') {
            $obj['title'] = 'កំពង់ចាម';
            $obj['address'] = "ភូមិទី២ សង្កាត់វាងវង់ ក្រុងកំពង់ចាម ខេត្តកំពង់ចាម។";
            $obj['cashier'] = "ហ៊ន ស្រីរត្ន័";
        }
        if ($inter->site_platform == 'SR') {
            $obj['title'] = 'សៀមរាប';
            $obj['address'] = "ភូមិកសិកម្ម សង្កាត់ស្រងែ ក្រុងសៀមរាប ខេត្តសៀមរាប។";
            $obj['cashier'] = "ហ៊ាង ប៉ោឡេង";
        }
        $data_sheet2[] = $obj;
        $data[] = $obj;
        $interventions = json_decode($inter->quotation);
        if (sizeof($interventions) > 0) {
            foreach ($interventions as $item) {
                $obj['Khmer_name'] = $item->intervention_category;
                $obj['unit'] = isset($item->unit) ? $item->unit : "";
                $obj['total'] = $item->total;
                $obj['unit_price'] = $item->unit_price;
                $obj['quantity'] = $item->quantity;
                $obj['who_pay'] = $item->who_pay;
                $obj['item_ref'] = isset($item->item_ref) ? $item->item_ref : "";
                $data_sheet2[] = $obj;
                $data[] = $obj;
            }
        } else {
            $obj['Khmer_name'] = "-";
            $obj['unit'] = "-";
            $obj['item_ref'] = "";
            $obj['unit_price'] = 0;
            $obj['total'] == 0;
            $obj['quantity'] = 0;
            $obj['who_pay'] = '';
            $data_sheet2[] = $obj;
            $data[] = $obj;
        }


        //dd($data);
        $TBS = new \clsTinyButStrong;
        $ok = class_exists('clsOpenTBS', true);
        $TBS->OtbsMsExcelExplicitRef = false;
        $TBS->Plugin(\TBS_INSTALL, \OPENTBS_PLUGIN);
        $TBS->LoadTemplate($inputFileName, \OPENTBS_ALREADY_UTF8);
        $TBS->PlugIn(OPENTBS_SELECT_SHEET, 1);
        $TBS->SetOption("noerr", true);
        $TBS->MergeBlock('t,a', $data);
        $TBS->PlugIn(OPENTBS_SELECT_SHEET, 2);
        $TBS->MergeBlock('b,c', $data_sheet2);
        $TBS->Show(OPENTBS_DOWNLOAD, "dnTechnical.xlsx");
    }
    public function excelExport(Request $request)
    {
        $startDate = $request->startdate;
        $endDate = $request->enddate;
        $inputFileName = storage_path('app/templates/technical_report.xlsx');
        $technical = Technical::select("*")
            ->whereBetween('problem_date', [$startDate, $endDate])
            ->get();
        $data = array();
        $data_sheet2 = array();
        $obj = array();

        foreach ($technical as $inter) {

            $obj = $inter->toArray();

            if ($inter->end_intervention != '' || $inter->end_intervention != null) $obj['end_intervention'] = ($inter->end_intervention)->format('Y-m-d');
            if ($inter->start_intervention != '' || $inter->start_intervention != null) $obj['start_intervention'] = ($inter->start_intervention)->format('Y-m-d');
            if ($inter->stop != '' || $inter->stop != null) $obj['stop'] = ($inter->stop)->format('Y-m-d');

            // $obj['start_intervention'] = ($inter->start_intervention)->format('Y-m-d') ;
            // $obj['start_intervention']= $obj['start_intervention']->format('Y-m-d') ;
            //$obj['stop']= $obj['stop']->format('Y-m-d') ;
            if ($inter->end_intervention == "1970-01-01" || $inter->end_intervention == "01-01-1970") {
                $obj['end_intervention'] = "";
            }
            if ($inter->stop == "1970-01-01" || $inter->stop == "01-01-1970") {
                $obj['stop'] = "";
            }

            // $obj['id'] = $inter->getKeyId();
            $result = "";
            // $obj['ontime']=strtotime(($inter->problem_date)->format('Y-m-d'))- strtotime(($inter->end_intervention)->format('Y-m-d'));
            // $obj['diff'] = strtotime(($inter->end_intervention)->format('Y-m-d'))- strtotime(($inter->start_intervention)->format('Y-m-d'));
            // $obj['diff_interval'] = strtotime(($inter->start_intervention)->format('Y-m-d'))- strtotime(($inter->problem_date)->format('Y-m-d'));
            // $obj['differ_day']= abs(round($obj['diff']/86400))+1;
            // $obj['diff_interval1']= round($obj['diff_interval']/86400);
            // $obj['ontime']=1;
            // $obj['diff']=$obj['start_intervention']->format('Y-m-d') ;
            // $obj['diff_interval']=3;
            // if($obj['start_intervention']=='' || $obj['start_intervention']== null)
            // {
            //  $obj['differ_day']=$obj['start_intervention']->format('Y-m-d') ;
            // }
            // $obj['diff_interval1']=5;

            $data[] = $obj;

            $interventions = json_decode($inter->quotation);
            if (!is_null($interventions)) {
                if (sizeof($interventions) > 0) {
                    foreach ($interventions as $item) {
                        // $obj['category']= $item->intervention_category;
                        // $obj['item_name']= isset($item->item_name)?$item->item_name:"";
                        // $obj['qty_item']= isset($item->qty_item)?$item->qty_item:"";
                        // $obj['price_kh']= isset($item->price_kh)?$item->price_kh:"";
                        // $obj['price_dollar']= isset($item->price_dollar)? $item->price_dollar:"";
                        // $obj['total_item']= isset($item->total_item)?round($item->total_item,2):"";
                        // $obj['intervention']= $item->intervention;
                        // $obj['unit_price']= $item->unit_price;
                        // $obj['hours']= isset($item->hours)?$item->hours:"";
                        // $obj['line_total']= $item->total;
                        $obj['quantity'] = $item->quantity;
                        // $obj['item_ref111']= isset($item->item_ref)?$item->item_ref:"";
                        //$data[] = $obj;
                        $data_sheet2[] = $obj;
                    }
                } else {
                    // $obj['category']= "-";
                    // $obj['intervention']= "-";
                    // $obj['unit_price']= 0;
                    // $obj['hours']= 0;
                    // $obj['line_total']= 0;
                    $obj['quantity'] = 0;
                    // $obj['item_ref']= "";
                    // $obj['item_name']="";
                    // $obj['qty_item']= "";
                    // $obj['price_kh']= "";
                    // $obj['price_dollar']= "";
                    // $obj['total_item']= "";
                    //$data[] = $obj;
                    $data_sheet2[] = $obj;
                }
            }
        }
        // dd($obj);
        $TBS = new \clsTinyButStrong;
        $ok = class_exists('clsOpenTBS', true);
        $TBS->OtbsMsExcelExplicitRef = false;
        $TBS->Plugin(\TBS_INSTALL, \OPENTBS_PLUGIN);
        $TBS->LoadTemplate($inputFileName, \OPENTBS_ALREADY_UTF8);
        $TBS->PlugIn(OPENTBS_SELECT_SHEET, 1);
        $TBS->SetOption("noerr", true);
        $TBS->MergeBlock('a', $data);
        $TBS->PlugIn(OPENTBS_SELECT_SHEET, 2);
        $TBS->MergeBlock('b', $data_sheet2);
        $TBS->Show(OPENTBS_DOWNLOAD, "export_technical_intervention.xlsx");
    }

    public function excelExport2(Request $request)
    {
        $startDate = $request->startdate;
        $endDate = $request->enddate;
        $inputFileName = storage_path('app/templates/technical_report.xlsx');
        $technical = Technical::with("technicalProblem")
            ->whereBetween('problem_date', [$startDate, $endDate])
            ->get();
        $data = array();
        $data_sheet2 = array();
        $obj = array();

        foreach ($technical as $inter) {
            $obj = $inter->toArray();
            unset($obj['technical_problem']);
            for ($i = 1; $i <= 3; $i++) {
                $obj['problem_' . $i . '_category'] = null;
                $obj['problem_' . $i . '_sub_problem'] = null;
                $obj['problem_' . $i . '_solution'] = null;
                $obj['problem_' . $i . '_detail_solution'] = null;
            }
            foreach ($inter->technicalProblem as $index => $problem) {
                if ($index >= 3) break; // Limit to 3 problems

                $prefix = 'problem_' . ($index + 1) . '_';
                $obj[$prefix . 'category'] = $problem->problem_category;
                $obj[$prefix . 'sub_problem'] = $problem->sub_problem;
                $obj[$prefix . 'solution'] = $problem->solution_list;
                $obj[$prefix . 'detail_solution'] = $problem->detail_solution;
            }
            if ($inter->end_intervention != '' || $inter->end_intervention != null) $obj['end_intervention'] = ($inter->end_intervention)->format('Y-m-d');
            if ($inter->start_intervention != '' || $inter->start_intervention != null) $obj['start_intervention'] = ($inter->start_intervention)->format('Y-m-d');
            if ($inter->stop != '' || $inter->stop != null) $obj['stop'] = ($inter->stop)->format('Y-m-d');
            if ($inter->end_intervention == "1970-01-01" || $inter->end_intervention == "01-01-1970") {
                $obj['end_intervention'] = "";
            }
            if ($inter->stop == "1970-01-01" || $inter->stop == "01-01-1970") {
                $obj['stop'] = "";
            }
            $data[] = $obj;
            $interventions = json_decode($inter->quotation);
            if (!is_null($interventions)) {
                if (sizeof($interventions) > 0) {
                    foreach ($interventions as $item) {
                        $obj['quantity'] = $item->quantity;
                        $data_sheet2[] = $obj;
                    }
                } else {
                    $obj['quantity'] = 0;
                    $data_sheet2[] = $obj;
                }
            }
        }
        // dd($data);
        $TBS = new \clsTinyButStrong;
        $ok = class_exists('clsOpenTBS', true);
        $TBS->OtbsMsExcelExplicitRef = false;
        $TBS->Plugin(\TBS_INSTALL, \OPENTBS_PLUGIN);
        $TBS->LoadTemplate($inputFileName, \OPENTBS_ALREADY_UTF8);
        $TBS->PlugIn(OPENTBS_SELECT_SHEET, 1);
        $TBS->SetOption("noerr", true);
        $TBS->MergeBlock('a', $data);
        $TBS->PlugIn(OPENTBS_SELECT_SHEET, 2);
        $TBS->MergeBlock('b', $data_sheet2);
        $TBS->Show(OPENTBS_DOWNLOAD, "export_technical_intervention.xlsx");
    }




    public function getDistance(Request $request)
    {

        $startPoint = $request->startPoint;
        $endPoint = $request->endPoint;
        $latitudeFrom = 0;
        $longitudeFrom = 0;
        $latitudeTo = 0;
        $longitudeTo = 0;
        $unit = "K";
        $result = '';
        if ($startPoint == "PP_Office") {
            $latitudeFrom = 11.54062;
            $longitudeFrom = 104.92229;
        } else if ($startPoint == "BTB_Office") {
            $latitudeFrom = 13.08665;
            $longitudeFrom = 103.20881;
        } else if ($startPoint == "KC_Office") {
            $latitudeFrom = 11.98133;
            $longitudeFrom = 105.46255;
        } else if ($startPoint == "SR_Office") {
            $latitudeFrom = 13.38827;
            $longitudeFrom = 103.83292;
        } else {
            $firstSite = Site::query()->where('Id_Site', '=', $startPoint)->get();
            foreach ($firstSite as $first) {
                $latitudeFrom = $first->Latitude;
                $longitudeFrom = $first->Longitude;
            }
        }

        if ($endPoint == "PP_Office") {
            $latitudeTo = 11.54062;
            $longitudeTo = 104.92229;
        } else if ($endPoint == "BTB_Office") {
            $latitudeTo = 13.08665;
            $longitudeTo = 103.20881;
        } else if ($endPoint == "KC_Office") {
            $latitudeTo = 11.98133;
            $longitudeTo = 105.46255;
        } else if ($endPoint == "SR_Office") {
            $latitudeTo = 13.38827;
            $longitudeTo = 103.83292;
        } else {
            $secondSite = Site::query()->where('Id_Site', '=', $endPoint)->get();
            foreach ($secondSite as $second) {
                $latitudeTo = $second->Latitude;
                $longitudeTo = $second->Longitude;
            }
        }

        if (($latitudeFrom == $latitudeTo) && ($longitudeFrom == $longitudeTo)) {
            return 0;
        } else {
            $theta = $longitudeFrom - $longitudeTo;
            $dist = sin(deg2rad($latitudeFrom)) * sin(deg2rad($latitudeTo)) +  cos(deg2rad($latitudeFrom)) * cos(deg2rad($latitudeTo)) * cos(deg2rad($theta));
            $dist = acos($dist);
            $dist = rad2deg($dist);
            $miles = $dist * 60 * 1.1515;
            $unit = strtoupper($unit);

            if ($unit == "K") {
                return round($miles * 1.609344);
            } else if ($unit == "N") {
                return round($miles * 0.8684);
            } else {
                return round($miles);
            }
        }
    }

    public function uploadSiteTechnician(Request $request)
{
    $request->validate([
    'file' => 'required|file|mimetypes:text/csv,application/vnd.ms-excel,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
]);

    if (!$request->hasFile('file')) {
       // Log::error('No file found in request.');
        return response()->json(['message' => 'No file uploaded'], 400);
    }

    $file = $request->file('file');
    Log::info('Uploaded file:', [
        'original_name' => $file->getClientOriginalName(),
        'mime_type'     => $file->getMimeType(),
        'extension'     => $file->getClientOriginalExtension(),
        'path'          => $file->getRealPath(),
    ]);
    
    try {
        $import = new TechnicianSite();
        Excel::import($import, $file);
        return response()->json(['message' => 'Data uploaded successfully!']);
    } catch (\Exception $e) {
        //Log::error('Excel import failed: ' . $e->getMessage());
        return response()->json([
            'message' => 'Data upload failed!',
            'error'   => $e->getMessage()
        ], 500);
    }
}
}
