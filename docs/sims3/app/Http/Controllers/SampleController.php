<?php

namespace App\Http\Controllers;

use App\Mail\Judgement;
use App\Mail\LabEmailBack;
use App\Mail\QualityAlertEmail;
use App\Mail\SiteOpenOrSelection;
use App\Models\Configuration;
use Illuminate\Support\Facades\Log;
use App\Models\Sample;
use App\Models\SampleExternal;
use App\Models\Site;
use App\Models\Technical;
use App\Models\UploadPicture;
use Illuminate\Http\Request;
use Illuminate\Support\Carbon;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Mail;
use Illuminate\Support\Facades\Storage;
use Illuminate\Support\Str;
use ZipArchive;

class SampleController extends Controller
{
    /**
     * Display a listing of the resource.
     */
    public function pr(Request $request)
    {
        $labOfficerNameEng = "";
        $labOfficerNameKh = "";
        $labOfficerPh = "";
        $ROMEng = "";
        $ROMKh = "";
        $ROMPh = "";
        $plat = $request->platform;
        $labName = $request->labName;
        if ($labName == "chakriya.v@teuksaat1001.com") {
            $labOfficerNameEng = "Mrs. Va Chakriya";
            $labOfficerNameKh = "អ្នកស្រី វ៉ា ចរិយា";
            $labOfficerPh = "071 555 3547";
        } else if ($labName == "sreymao.b@teuksaat1001.com") {
            $labOfficerNameEng = "Miss. Bunthoeurn Sreymao";
            $labOfficerNameKh = "កញ្ញា ប៊ុនធឿន ស្រីម៉ៅ";
            $labOfficerPh = "071 555 6966";
        } else if ($labName == "chanmonida.h@teuksaat1001.com") {
            $labOfficerNameEng = "Heng Chanmonida";
            $labOfficerNameKh = "កញ្ញា ហេង ច័ន្ទមុនីដា";
            $labOfficerPh = "071 555 3484";
        } else if ($labName == "champey.p@teuksaat1001.com") {
            $labOfficerNameEng = "Phan Champey";
            $labOfficerNameKh = "កញ្ញា ផាន ចំបុី";
            $labOfficerPh = "071 555 3474";
        }

        else {
            $labOfficerNameEng = "not found";
            $labOfficerNameKh = "អត់មាន";
            $labOfficerPh = "";
        }
        if ($request->platform) {

            if ($plat == "PP") {

                $ROMEng = "Mr. Touch Lim";
                $ROMKh = "លោក ទូច លឹម";
                $ROMPh = "071 555 3681";
            } else if ($plat == "KSP") {

                $ROMEng = "Mr. Mao Rethy";
                $ROMKh = "លោក ម៉ៅ ឫទ្ធី";
                $ROMPh = "071 555 6718";
            } else if ($plat == "BTB") {

                $ROMEng = "Mr. Yiev Yet";
                $ROMKh = "លោក យៀវ​ យ៉េត";
                $ROMPh = "071 555 3504";
            } else if ($plat == "SR") {

                $ROMEng = "Mr. Breng Koem Hong";
                $ROMKh = "លោក ប្រេង គឹមហុង";
                $ROMPh = "071 555 6701";
            } else if ($plat == "KC") {

                $ROMEng = "Mr. Phoeung Bun";
                $ROMKh = "លោក ភឿង ប៊ុន";
                $ROMPh = "071 555 3492";
            } else {

                $ROMEng = "chamnap";
                $ROMKh = "chamnap";
                $ROMPh = "071 555 3492";
            }
            $d = $request->d;
            [$year, $month] = explode('-', $d);
            $reportType = $request->re;

            if ($reportType == "Monthly Test") {
                $t = "first";
            } else {
                $t = $request->tn;
            }
            $data = Sample::with('siteRelation')
                ->whereMonth('sample_date', $month)
                ->whereYear('sample_date', $year)
                ->where('type', '!=', 'Site_Selection')
                ->where('type', '!=', 'Site_Opening')
                ->where('type', '!=', 'Site_Intervention')
                ->where('created_by', '=', $labName)
                ->where('type', '=', $reportType)
                ->where('test_number', '=', $t)
                ->when($plat && $plat !== 'All', function ($query) use ($plat) {
                    $query->whereHas('siteRelation', function ($q) use ($plat) {
                        $q->where('Platform', $plat);
                    });
                })
                ->orderBy('sample_date', 'desc')
                //->limit(10)
                ->get()
                ->map(function ($sample)  use ($labOfficerNameEng, $labOfficerNameKh, $labOfficerPh, $ROMEng, $ROMKh, $ROMPh) {
                    if ($sample->siteRelation->Water_Source == "lake") {
                        $source = "ទឹកបឹង";
                    } else if ($sample->siteRelation->Water_Source == "Piped Water") {
                        $source = "ទឹករដ្ធាករ";
                    } else if ($sample->siteRelation->Water_Source == "Pond") {
                        $source = "ទឹកស្រះ";
                    } else if ($sample->siteRelation->Water_Source == "River") {
                        $source = "ទឹកទន្លេ";
                    } else if ($sample->siteRelation->Water_Source == "Well") {
                        $source = "ទឹកអណ្តូង";
                    } else if ($sample->siteRelation->Water_Source == "Drinking Water") {
                        $source = "ទឹកពិសារ";
                    } else {
                        $source = "no water source";
                    }
                    return [
                        'site' => $sample->site,
                        'platform' => $sample->siteRelation->Platform ?? null,
                        'advisor' => $sample->siteRelation->Advisor ?? null,
                        'kh_advisor' => $sample->siteRelation->Khmer_advisor ?? null,
                        'water_source' => $sample->siteRelation->Water_Source ?? null,
                        'kh_water_source' => $source ?? "ទឹកទន្លេ",
                        'commune_khmer' => $sample->siteRelation->Commune_khmer ?? null,
                        'District_khmer' => $sample->siteRelation->District_khmer ?? null,
                        'Province_khmer' => $sample->siteRelation->Province_khmer ?? null,
                        'chlorine' => $sample->chlorine,
                        'hardness' => $sample->hardness,
                        'manganese' => $sample->manganese,
                        'calcium' => $sample->calcium,
                        'nitrate' => $sample->nitrate,
                        'nitrite' => $sample->nitrite,
                        'sulfates' => $sample->sulfates,
                        'alkalinity' => $sample->alkalinity,
                        'chloride' => $sample->chloride,
                        'amonia' => $sample->amonia,
                        'iron' => $sample->iron,
                        'fluoride' => $sample->fluoride,
                        'total_chlore' => $sample->total_chlore,
                        'arsenic' => $sample->arsenic,
                        'ph' => $sample->ph,
                        'tds' => $sample->tds,
                        'turbidity' => $sample->turbidity,
                        'conductivity' => $sample->conductivity,
                        'aluminium' => $sample->aluminium,
                        'coli_machine' => $sample->total_coliform,
                        'el_machine' => $sample->escherichia,
                        'coli_bottle' => $sample->total_coliform_bottle,
                        'el_bottle' => $sample->escherichia_bottle,
                        'comment' => $sample->comment,
                        'sample_date' => $sample->sample_date->format('d-m-Y'),
                        'received_date' => $sample->received_date->format('d-m-Y'),
                        'analysis_date' => $sample->analysis_date->format('d-m-Y'),
                        'labOfficerNameEng' => $labOfficerNameEng,
                        'labOfficerNameKh' => $labOfficerNameKh,
                        'labOfficerPh' => $labOfficerPh,
                        'ROMEng' => $ROMEng,
                        'ROMKh' => $ROMKh,
                        'ROMPh' => $ROMPh
                    ];
                });
        } else {
            // Retrieve the sample record by ID with its related site data
            $source = "";
            $id = $request->id;
            $record = Sample::with(['siteRelation' => function ($query) {
                $query->select('Id_Site', 'Platform', 'Advisor', 'Khmer_advisor', 'Water_Source', 'Commune_khmer', 'District_khmer', 'Province_khmer'); // Only retrieve these fields from the Site table
            }])
                ->find($id); // Fetch the record by ID

            // Check if the record exists
            if (!$record) {
                return response()->json(['message' => 'Record not found'], 404);
            }
            if ($record->siteRelation->Water_Source == "lake") {
                $source = "ទឹកបឹង";
            } else if ($record->siteRelation->Water_Source == "Piped Water") {
                $source = "ទឹករដ្ធាករ";
            } else if ($record->siteRelation->Water_Source == "Pond") {
                $source = "ទឹកស្រះ";
            } else if ($record->siteRelation->Water_Source == "River") {
                $source = "ទឹកទន្លេ";
            } else if ($record->siteRelation->Water_Source == "Well") {
                $source = "ទឹកអណ្តូង";
            } else if ($record->siteRelation->Water_Source == "") {
                $source = "";
            }
            $plat = $record->siteRelation->Platform;
            if ($plat == "PP") {
                $labOfficerNameEng = "Mrs. Va Chakriya";
                $labOfficerNameKh = "អ្នកស្រី វ៉ា ចរិយា";
                $labOfficerPh = "071 555 3547";
                $ROMEng = "Mr. Touch Lim";
                $ROMKh = "លោក ទូច លឹម";
                $ROMPh = "071 555 3681";
            } else if ($plat == "KSP") {
                $labOfficerNameEng = "Mrs. Va Chakriya";
                $labOfficerNameKh = "អ្នកស្រី វ៉ា ចរិយា";
                $labOfficerPh = "071 555 3547";
                $ROMEng = "Mr. Mao Rethy";
                $ROMKh = "លោក ម៉ៅ ឫទ្ធី";
                $ROMPh = "071 555 2178";
            } else if ($plat == "BTB") {
                $labOfficerNameEng = "Miss. Bunthoeurn Sreymao ";
                $labOfficerNameKh = "កញ្ញា ប៊ុនធឿន ស្រីម៉ៅ";
                $labOfficerPh = "071 555 6966";
                $ROMEng = "Mr. Yiev Yet";
                $ROMKh = "លោក យៀវ​ យ៉េត";
                $ROMPh = "071 555 3504";
            } else if ($plat == "SR") {
                $labOfficerNameEng = "Mrs. Phan Champey";
                $labOfficerNameKh = "អ្នកស្រី ផាន ចំបុី";
                $labOfficerPh = "071 555 3474";
                $ROMEng = "Mr. Breng Koem Hong";
                $ROMKh = "លោក ប្រេង គឹមហុង";
                $ROMPh = "071 555 6701";
            } else if ($plat == "KC") {
                $labOfficerNameEng = "Mrs. Va Chakriya";
                $labOfficerNameKh = "អ្នកស្រី វ៉ា ចរិយា";
                $labOfficerPh = "071 555 3484";
                $ROMEng = "Mr. Phoeung Bun";
                $ROMKh = "លោក ភឿង ប៊ុន";
                $ROMPh = "071 555 3492";
            } else {
                $labOfficerNameEng = "chamnap";
                $labOfficerNameKh = "chamnap";
                $labOfficerPh = "071 555 3484";
                $ROMEng = "chamnap";
                $ROMKh = "chamnap";
                $ROMPh = "071 555 3492";
            }
            // Prepare the data to return
            $data = [
                'site' => $record->site,
                'platform' => $record->siteRelation->Platform ?? null,
                'advisor' => $record->siteRelation->Advisor ?? null,
                'kh_advisor' => $record->siteRelation->Khmer_advisor ?? null,
                'water_source' => $record->siteRelation->Water_Source ?? null,
                'kh_water_source' => $source ?? "ទឹកទន្លេ",
                'commune_khmer' => $record->siteRelation->Commune_khmer ?? null,
                'District_khmer' => $record->siteRelation->District_khmer ?? null,
                'Province_khmer' => $record->siteRelation->Province_khmer ?? null,
                'chlorine' => $record->chlorine,
                'hardness' => $record->hardness,
                'manganese' => $record->manganese,
                'calcium' => $record->calcium,
                'nitrate' => $record->nitrate,
                'nitrite' => $record->nitrite,
                'sulfates' => $record->sulfates,
                'alkalinity' => $record->alkalinity,
                'chloride' => $record->chloride,
                'amonia' => $record->amonia,
                'iron' => $record->iron,
                'fluoride' => $record->fluoride,
                'total_chlore' => $record->total_chlore,
                'arsenic' => $record->arsenic,
                'ph' => $record->ph,
                'tds' => $record->tds,
                'turbidity' => $record->turbidity,
                'conductivity' => $record->conductivity,
                'aluminium' => $record->aluminium,
                'coli_machine' => $record->total_coliform,
                'el_machine' => $record->escherichia,
                'coli_bottle' => $record->total_coliform_bottle,
                'el_bottle' => $record->escherichia_bottle,
                'comment' => $record->comment,
                'sample_date' => $record->sample_date->format('d-m-Y'),
                'received_date' => $record->received_date->format('d-m-Y'),
                'analysis_date' => $record->analysis_date->format('d-m-Y'),
                'labOfficerNameEng' => $labOfficerNameEng,
                'labOfficerNameKh' => $labOfficerNameKh,
                'labOfficerPh' => $labOfficerPh,
                'ROMEng' => $ROMEng,
                'ROMKh' => $ROMKh,
                'ROMPh' => $ROMPh
            ];
        }
        //dd($data);
        return response()->json($data);
    }

    public function sampleExcelRangDate(Request $request)
    {
        $startDate = $request->start;
        $endDate = $request->end;
        $samples = Sample::select("*")
            ->whereBetween('sample_date', [$startDate, $endDate])
            ->where('type', '!=', 'Site_Opening')
            ->where('type', '!=', 'Site_Selection')
            ->where('type', '!=', 'Site_Intervention')
            ->orderBy('sample_date', 'desc')
            ->get();
        $inputFileName = storage_path('app/templates/new_certificate.xlsx');
        $sites = Site::orderBy("Id_Site")->get();
        $data = array();
        $obj1 = array();
        $register_array = array();
        $site_platform = array();
        foreach ($sites as $site) {
            $site_platform[$site->Id_Site] = $site->Platform;
            $obj1[$site->Id_Site]['pro'] = $site->Village_khmer . " " . $site->Commune_khmer . " " . $site->District_khmer . " " . $site->Province_khmer;
            $obj1[$site->Id_Site]['water_source'] = $site->Water_Source;
            $obj1[$site->Id_Site]['advisor'] = $site->Advisor;
        }

        foreach ($samples as $sample) {
            $sd = $sample->sample_date->format('Y-m-d');
            $ad = $sample->analysis_date->format('Y-m-d');
            if (isset($sample->recieved_date)) {
                $rd = $sample->recieved_date->format('Y-m-d');
            } else {
                $rd = "";
            }
            $obj = $sample->toArray();
            $obj['platform'] = isset($site_platform[$obj['site']]) ? $site_platform[$obj['site']] : "";
            $obj['kh_location'] = isset($obj1[$obj['site']]) ? $obj1[$obj['site']]['pro'] : "";
            $obj['source'] = isset($obj1[$obj['site']]) ? $obj1[$obj['site']]['water_source'] : "";
            // $obj['advisor'] = isset($register_array[$obj['site']]) ? $register_array[$obj['site']]['advisor'] : "";
            $obj['advisor'] = isset($obj1[$obj['site']]) ? $obj1[$obj['site']]['advisor'] : "";
            $obj['sampleDate'] = date("Y-m-d", strtotime("$sd +1 day"));
            $obj['analysisDate'] = date("Y-m-d", strtotime("$ad +1 day"));
            $obj['recievedDate'] = isset($obj['recievedDate']) ? date("Y-m-d", strtotime("$rd +1 day")) : "";
            $data[] = $obj;
        }

        $TBS = new \clsTinyButStrong();
        $ok = class_exists('clsOpenTBS', true); // hack to force class loading of TBS
        $TBS->Plugin(\TBS_INSTALL, \OPENTBS_PLUGIN);
        $TBS->OtbsMsExcelExplicitRef = false;
        $TBS->LoadTemplate($inputFileName, \OPENTBS_ALREADY_UTF8);
        $TBS->SetOption("noerr", true);
        $TBS->MergeBlock('a', $data);
        //$TBS->PlugIn(OPENTBS_DEBUG_XML_CURRENT);
        $filename = "quality_monthly_report_" . $request->month . ".xlsx";
        $TBS->Show(OPENTBS_DOWNLOAD, $filename);
    }

    public function index(Request $request)
    {
        $request->validate([
            'month' => 'required|numeric',
            'year' => 'required|numeric',
        ]);
        return [
            "samples" => Sample::whereMonth("sample_date", "=", $request->month)
                ->whereNotIn("type", ["Site_Selection", "Site_Opening", "Site_Intervention", "Raw_Water"])
                ->whereYear("sample_date", "=", $request->year)
                ->orderBy("site")
                ->orderBy("sample_date", "desc")
                ->get()
                ->groupBy("site"),
            "sites" => Site::select("Id_Site", "Platform")
                ->where("Platform", "!=", "Dead")
                ->orderBy("Id_Site")
                ->get()
                ->groupBy("Platform")->sortKeys(),
        ];
    }
    public function show($id)
    {
        return [
            "samples" =>  Sample::find($id),
            "email" => auth()->user()->email
        ];
    }
    public function requestEmail()
    {
        return auth()->user()->email;
    }
    public function getSampleCode()
    {
        return Sample::select(DB::raw('max(sample_code) as sample_code'))->where('type', 'Site_Selection')->get();
    }

    public function siteOpening(Request $request)
    {
        $query = Sample::query();
        $data = Sample::with(['site:Id_Site,Platform']);
        $limit = 500;
        if ($request->has('excel')) {
            $limit = 999999;
        }
        if ($request->has("external_test")) {
            return SampleExternal::orderBy("test_date", "desc")
                ->skip(($request->page - 1) * 15)
                ->take($limit)
                ->get();
        } else {
            if ($request->has("site_opening")) {
                $query->where('type', '=', 'Site_Opening');
                return $query->orderBy("sample_date", "desc")
                ->skip(($request->page - 1) * 15)
                ->take($limit)
                ->get();
            } else if ($request->has("site_selection")) {
                $query->where('type', '=', 'Site_Selection');
                return $query->orderBy("sample_code", "desc")
                    ->skip(($request->page - 1) * 15)
                    ->take($limit)
                    ->get();
            } else if ($request->has("site_intervention")) {
                $query->where('type', '=', 'Site_Intervention');
                return $query->orderBy("sample_date", "desc")
                ->skip(($request->page - 1) * 15)
                ->take($limit)
                ->get();
            } else if ($request->has("raw_water")) {
                $data->where('type', '=', 'Raw_Water');
                return $data->orderBy("created_at", "desc")
                ->skip(($request->page - 1) * 15)
                ->take($limit)
                ->get();
            }


        }
    }
    public function getSamplesForSite(Request $request, string $site)
    {
        return Sample::where("site", "=", $site)
            ->where("type", "!=", "Site_Selection")
            ->where("type", "!=", "Site_Opening")
            ->where("type", "!=", "Site_Intervention")
            ->orderBy('sample_date', 'desc')->get();
    }

    public function checkColiform()
    {
        // Step 1: Extract sites for current month (June 2025)
        $currentMonthStart = Carbon::create(2025, 6, 1)->startOfMonth();
        $currentMonthEnd = Carbon::create(2025, 6, 30)->endOfMonth();

        $currentMonthSites = Sample::select('site')
            ->whereBetween('sample_date', [$currentMonthStart, $currentMonthEnd])
            ->where(function ($query) {
                $query->whereRaw('CAST(total_coliform AS DECIMAL) > 20')
                    ->orWhereRaw('CAST(total_coliform_bottle AS DECIMAL) > 20');
            })
            ->distinct()
            ->get()
            ->pluck('site')
            ->toArray();

        // Debug: Log current month sites and their data
        $currentMonthData = Sample::select('site', 'total_coliform', 'total_coliform_bottle', 'sample_date')
            ->whereBetween('sample_date', [$currentMonthStart, $currentMonthEnd])
            ->where(function ($query) {
                $query->whereRaw('CAST(total_coliform AS DECIMAL) > 20')
                    ->orWhereRaw('CAST(total_coliform_bottle AS DECIMAL) > 20');
            })
            ->get()
            ->toArray();
        \Log::info('Current month (June 2025) sites with high coliform: ', $currentMonthSites);
        \Log::info('Current month (June 2025) raw data: ', $currentMonthData);

        // Step 2: Count sites per month from Jan 1, 2025 to May 30, 2025
        $yearStart = Carbon::create(2025, 1, 1);
        $yearEnd = Carbon::create(2025, 5, 30);

        $yearSites = Sample::select('site', DB::raw('YEAR(sample_date) as year'), DB::raw('MONTH(sample_date) as month'))
            ->whereBetween('sample_date', [$yearStart, $yearEnd])
            ->where(function ($query) {
                $query->whereRaw('CAST(total_coliform AS DECIMAL) > 20')
                    ->orWhereRaw('CAST(total_coliform_bottle AS DECIMAL) > 20');
            })
            ->groupBy('site', 'year', 'month')
            ->get()
            ->groupBy('site')
            ->map(function ($group) {
                return $group->count();
            })
            ->toArray();

        // Debug: Log year-to-date site counts and their data
        $yearData = Sample::select('site', 'total_coliform', 'total_coliform_bottle', 'sample_date')
            ->whereBetween('sample_date', [$yearStart, $yearEnd])
            ->where(function ($query) {
                $query->whereRaw('CAST(total_coliform AS DECIMAL) > 20')
                    ->orWhereRaw('CAST(total_coliform_bottle AS DECIMAL) > 20');
            })
            ->get()
            ->toArray();
        \Log::info('Year-to-date (Jan-May 2025) site counts by month: ', $yearSites);
        \Log::info('Year-to-date (Jan-May 2025) raw data: ', $yearData);

        // Step 3: Merge and count total months per site
        $siteCounts = [];

        // Include current month sites (count as 1 month if present)
        foreach ($currentMonthSites as $site) {
            $siteCounts[$site] = ($siteCounts[$site] ?? 0) + 1;
        }

        // Add year-to-date counts
        foreach ($yearSites as $site => $monthCount) {
            $siteCounts[$site] = ($siteCounts[$site] ?? 0) + $monthCount;
        }

        // Filter sites with more than 2 months
        $siteCounts = array_filter($siteCounts, function ($count) {
            return $count > 2;
        });

        // Count total number of sites
        $totalSites = count($siteCounts);

        // Debug: Log final site counts
        \Log::info('Sites with high coliform in more than 2 months: ', $siteCounts);
        \Log::info('Total number of sites with high coliform in more than 2 months: ' . $totalSites);

        // Step 4: Return response
        if (empty($siteCounts)) {
            return response()->json([
                'message' => 'No sites found with high coliform in more than 2 months.',
                'total_sites' => 0,
                'current_month_sites' => $currentMonthSites,
                'current_month_data' => $currentMonthData,
                'year_to_date_site_counts' => $yearSites,
                'year_to_date_data' => $yearData,
                'sites_with_high_coliform' => []
            ], 200);
        }

        return response()->json([
            'total_sites' => $totalSites,
            'sites_with_high_coliform' => $siteCounts,
            'current_month_sites' => $currentMonthSites,
            'current_month_data' => $currentMonthData,
            'year_to_date_site_counts' => $yearSites,
            'year_to_date_data' => $yearData
        ]);
    }

    public function panaltySite(Request $request)
    {

        //     $results = DB::table('samples')
        // ->select('site', DB::raw('COUNT(*) AS occurrence_count'))
        // ->where(function ($query) {
        //     $query->where('total_coliform', '>', 20)
        //           ->orWhere('total_coliform_bottle', '>', 20)
        //           ->orWhere('total_coliform', '=', 'TNTC')
        //           ->orWhere('total_coliform_bottle', '=', 'TNTC');
        // })
        // ->whereNotIn('type', ['Site_Selection', 'Site_Opening', 'Site_Intervention'])
        // ->whereBetween('sample_date', ['2025-01-01 00:00:00', now()])
        // ->groupBy('site')
        // ->orderByDesc('occurrence_count')
        // ->get();

        $m = $request->month;
        $inputFileName = storage_path('app/templates/panaltySite.xlsx');
        [$year, $month] = explode("-", $request->month);
        $samples = Sample::select('samples.site', 'samples.escherichia', 'samples.escherichia_bottle', 'samples.sample_date', 'Sites.Platform', 'Sites.Advisor')
            ->join('Sites', 'samples.site', '=', 'Sites.Id_Site')
            ->where(function ($query) {
                $query->where('escherichia', '>', 0)
                    ->orWhere('escherichia', 'TNTC')
                    ->orWhere('escherichia_bottle', '>', 0)
                    ->orWhere('escherichia_bottle', 'TNTC');
            })
            ->where('type', '!=', 'Site_Selection')
            ->where('type', '!=', 'Site_Opening')
            ->where('type', '!=', 'Site_Intervention')
            ->whereMonth('sample_date', $month)
            ->whereYear("sample_date", "=", $year)
            ->orderBy('sample_date', 'desc')
            ->get();
        $data = array();
        $shortYear = substr($year, -2);
        $cashier = "";
        $in = "WQ";
        // if ($samples->isEmpty()) {
        //     return response()->json(['message' => 'No record found'], 404);
        // }
        // else
        // {
        $counter = 1;
        foreach ($samples as $sample) {
            if ($sample->Platform == "SR") {
                $cashier = "Heang_Porleng";
            } else if ($sample->Platform == "BTB") {
                $cashier = "Nou_Chamroeun";
            } else if ($sample->Platform == "PP" || $sample->Platform == "KSP") {
                $cashier = "Mon_Sorvy";
            } else if ($sample->Platform == "KC") {
                $cashier = "Hon_Sreyrath";
            } else {
                $cashier = "";
            }
            $invoiceNumber = $in . $sample->Platform . $shortYear . $month . "-" . str_pad($counter, 4, '0', STR_PAD_LEFT);
            $data[] = [
                'site' => $sample->site,
                'platform' => $sample->Platform,
                'advisor' => $sample->Advisor,
                'invoice' => $invoiceNumber,
                'escherichia' => $sample->escherichia,
                'escherichia_bottle' => $sample->escherichia_bottle,
                'sample_date' => $sample->sample_date->format('Y/m/d'),
                'cashier' => $cashier
            ];
            $counter++;
        }
        $TBS = new \clsTinyButStrong();
        $ok = class_exists('clsOpenTBS', true); // hack to force class loading of TBS
        $TBS->Plugin(\TBS_INSTALL, \OPENTBS_PLUGIN);
        $TBS->OtbsMsExcelExplicitRef = false;
        $TBS->LoadTemplate($inputFileName, \OPENTBS_ALREADY_UTF8);
        $TBS->SetOption("noerr", true);
        $TBS->MergeBlock('a', $data);
        //$TBS->PlugIn(OPENTBS_DEBUG_XML_CURRENT);
        $filename = "panaltySite_" . $request->month . ".xlsx";
        $TBS->Show(OPENTBS_DOWNLOAD, $filename);
    }

    private function sendMail($sample)
    {
        $site = Site::where("Id_Site", $sample->site)->first();
        $sample['en_name'] = $site->Entrepreneur_English_Name ?? null;
        $sample['en_phone'] = $site->Phone_Number ?? null;
        $recipients = '';
        $technician_email = '';
        $advisor_email = '';
        $supervisor_email = '';
        $resultMachine = "";
        $resultBottle = "";
        if ($site->technician_site != Null || $site->technician_site != '') {
            $technician_email = $site->technician_site;
            $advisor_email = $site->Advisor_email;
        } else {
            $technician_email = "chamnap.keo@teuksaat1001.com";
        }
        if ($site->technician_site == "phalla.p@teuksaat1001.com" || $site->technician_site == "odom.p@teuksaat1001.com" || $site->technician_site == "veasna.r@teuksaat1001.com" || $site->technician_site == "dara.s@teuksaat1001.com" || $site->technician_site == "vichet.h@teuksaat1001.com" || $site->technician_site == "theary.m@teuksaat1001.com") {
            $supervisor_email = "bros.t@teuksaat1001.com";
        } else if ($site->technician_site == "vuthy.n@teuksaat1001.com" || $site->technician_site == "pisak.m@teuksaat1001.com" || $site->technician_site == "phanith.m@teuksaat1001.com" || $site->technician_site == "phalla.p@teuksaat1001.com" || $site->technician_site == "darith.s@teuksaat1001.com" || $site->technician_site == "leab.l@teuksaat1001.com") {
            $supervisor_email = "chanthan.m@teuksaat1001.com";
        } else {
            $supervisor_email = "chamnap.keo@teuksaat1001.com";
        }
        if (intval($sample->contamination_level_machine) == intval($sample->contamination_level_bottle)) {
            $resultMachine = intval($sample->contamination_level_machine);
        } else if (intval($sample->contamination_level_machine) > intval($sample->contamination_level_bottle)) {
            $resultMachine = intval($sample->contamination_level_machine);
        } else if (intval($sample->contamination_level_machine) < intval($sample->contamination_level_bottle)) {
            $resultBottle = intval($sample->contamination_level_bottle);
        }
        $sample['resultMachine'] = $resultMachine ?? "";
        $sample['resultBottle'] = $resultBottle ?? "";
        if ($resultMachine) {
            if ($resultMachine == 1) {
                if ($site->Platform == "SR") {
                    $recipients = ['samnang.p@teuksaat1001.com', $technician_email, $advisor_email];
                }
                if ($site->Platform == "KC") {
                    $recipients = ['chakriya.v@teuksaat1001.com', $advisor_email, $technician_email];
                }
                if ($site->Platform == "PP") {
                    $recipients = ['chakriya.v@teuksaat1001.com', $advisor_email, $technician_email];
                }
                if ($site->Platform == "BTB") {
                    $recipients = ['sreymao.b@teuksaat1001.com', $advisor_email, $technician_email];
                }
                if ($site->Platform == "KSP") {
                    $recipients = ['chakriya.v@teuksaat1001.com', $advisor_email, $technician_email];
                }
                if ($site->technician_site == Null || $site->technician_site == '') {
                    $recipients = ['chamnap.keo@teuksaat1001.com'];
                }
            }
            if ($resultMachine == 2) {
                if ($site->Platform == "SR") {
                    $recipients = ['samnang.p@teuksaat1001.com','samnang.p@teuksaat1001.com', $technician_email, $advisor_email, $supervisor_email];
                }
                if ($site->Platform == "KC") {
                    $recipients = ['samnang.p@teuksaat1001.com','chakriya.v@teuksaat1001.com', $supervisor_email, $technician_email, $advisor_email];
                }
                if ($site->Platform == "PP") {
                    $recipients = ['samnang.p@teuksaat1001.com','chakriya.v@teuksaat1001.com', $supervisor_email, $technician_email, $advisor_email];
                }
                if ($site->Platform == "BTB") {
                    $recipients = ['samnang.p@teuksaat1001.com','sreymao.b@teuksaat1001.com', $supervisor_email, $technician_email, $advisor_email];
                }
                if ($site->Platform == "KSP") {
                    $recipients = ['samnang.p@teuksaat1001.com','chakriya.v@teuksaat1001.com', $supervisor_email, $technician_email, $advisor_email];
                }
                if ($site->technician_site == Null || $site->technician_site == '') {
                    $recipients = ['chamnap.keo@teuksaat1001.com'];
                }
            }
            if ($resultMachine == 3) {
                if ($site->Platform == "SR") {
                    $recipients = ['samnang.p@teuksaat1001.com','kimhong.p@teuksaat1001.com','samnang.p@teuksaat1001.com', 'borin.t@teuksaat1001.com', 'louth.t@teuksaat1001.com', $technician_email, $advisor_email, $supervisor_email];
                }
                if ($site->Platform == "KC") {
                    $recipients = ['samnang.p@teuksaat1001.com','bun.ph@teuksaat1001.com', 'borin.t@teuksaat1001.com', 'chakriya.v@teuksaat1001.com', $supervisor_email, $technician_email, $advisor_email];
                }
                if ($site->Platform == "PP") {
                    $recipients = ['samnang.p@teuksaat1001.com','lim.t@teuksaat1001.com', 'borin.t@teuksaat1001.com', 'chakriya.v@teuksaat1001.com', $supervisor_email, $technician_email, $advisor_email];
                }
                if ($site->Platform == "BTB") {
                    $recipients = ['samnang.p@teuksaat1001.com','yet.y@teuksaat1001.com', 'borin.t@teuksaat1001.com', 'sreymao.b@teuksaat1001.com', $supervisor_email, $technician_email, $advisor_email];
                }
                if ($site->Platform == "KSP") {
                    $recipients = ['samnang.p@teuksaat1001.com','rethy.m@teuksaat1001.com', 'borin.t@teuksaat1001.com', 'chakriya.v@teuksaat1001.com', $supervisor_email, $technician_email, $advisor_email];
                }
                if ($site->technician_site == Null || $site->technician_site == '') {
                    $recipients = ['chamnap.keo@teuksaat1001.com'];
                }
            }
        }
        if ($resultBottle) {
            if ($resultBottle == 1) {
                if ($site->Platform == "SR") {
                    $recipients = ['samnang.p@teuksaat1001.com', $technician_email, $advisor_email];
                }
                if ($site->Platform == "KC") {
                    $recipients = ['chakriya.v@teuksaat1001.com', $advisor_email, $technician_email];
                }
                if ($site->Platform == "PP") {
                    $recipients = ['chakriya.v@teuksaat1001.com', $advisor_email, $technician_email];
                }
                if ($site->Platform == "BTB") {
                    $recipients = ['sreymao.b@teuksaat1001.com', $advisor_email, $technician_email];
                }
                if ($site->Platform == "KSP") {
                    $recipients = ['chakriya.v@teuksaat1001.com', $advisor_email, $technician_email];
                }
                if ($site->technician_site == Null || $site->technician_site == '') {
                    $recipients = ['chamnap.keo@teuksaat1001.com'];
                }
            }
            if ($resultBottle == 2) {
                if ($site->Platform == "SR") {
                    $recipients = ['samnang.p@teuksaat1001.com','samnang.p@teuksaat1001.com', $technician_email, $advisor_email, $supervisor_email];
                }
                if ($site->Platform == "KC") {
                    $recipients = ['samnang.p@teuksaat1001.com','chakriya.v@teuksaat1001.com', $supervisor_email, $technician_email, $advisor_email];
                }
                if ($site->Platform == "PP") {
                    $recipients = ['samnang.p@teuksaat1001.com','chakriya.v@teuksaat1001.com', $supervisor_email, $technician_email, $advisor_email];
                }
                if ($site->Platform == "BTB") {
                    $recipients = ['samnang.p@teuksaat1001.com','sreymao.b@teuksaat1001.com', $supervisor_email, $technician_email, $advisor_email];
                }
                if ($site->Platform == "KSP") {
                    $recipients = ['samnang.p@teuksaat1001.com','chakriya.v@teuksaat1001.com', $supervisor_email, $technician_email, $advisor_email];
                }
                if ($site->technician_site == Null || $site->technician_site == '') {
                    $recipients = ['chamnap.keo@teuksaat1001.com'];
                }
            }
            if ($resultBottle == 3) {
                if ($site->Platform == "SR") {
                    $recipients = ['samnang.p@teuksaat1001.com','kimhong.p@teuksaat1001.com','samnang.p@teuksaat1001.com', 'borin.t@teuksaat1001.com', $technician_email, $advisor_email, $supervisor_email];
                }
                if ($site->Platform == "KC") {
                    $recipients = ['samnang.p@teuksaat1001.com','bun.ph@teuksaat1001.com', 'borin.t@teuksaat1001.com', 'chakriya.v@teuksaat1001.com', $supervisor_email, $technician_email, $advisor_email];
                }
                if ($site->Platform == "PP") {
                    $recipients = ['samnang.p@teuksaat1001.com','lim.t@teuksaat1001.com', 'borin.t@teuksaat1001.com', 'chakriya.v@teuksaat1001.com', $supervisor_email, $technician_email, $advisor_email];
                }
                if ($site->Platform == "BTB") {
                    $recipients = ['samnang.p@teuksaat1001.com','yet.y@teuksaat1001.com', 'borin.t@teuksaat1001.com', 'sreymao.b@teuksaat1001.com', $supervisor_email, $technician_email, $advisor_email];
                }
                if ($site->Platform == "KSP") {
                    $recipients = ['samnang.p@teuksaat1001.com','rethy.m@teuksaat1001.com', 'borin.t@teuksaat1001.com', 'chakriya.v@teuksaat1001.com', $supervisor_email, $technician_email, $advisor_email];
                }
                if ($site->technician_site == Null || $site->technician_site == '') {
                    $recipients = ['chamnap.keo@teuksaat1001.com'];
                }
            }
        }

        // Filter out any empty strings before sending
        $recipients = is_array($recipients) ? array_values(array_filter($recipients)) : [];

        Log::info('sendMail resolved values', [
            'sample_id'             => $sample->id,
            'site'                  => $sample->site,
            'platform'              => $site->Platform ?? 'null',
            'contamination_machine' => $sample->contamination_level_machine,
            'contamination_bottle'  => $sample->contamination_level_bottle,
            'resultMachine'         => $resultMachine,
            'resultBottle'          => $resultBottle,
            'technician_email'      => $technician_email,
            'advisor_email'         => $advisor_email,
            'supervisor_email'      => $supervisor_email,
            'recipients'            => $recipients,
        ]);

        if (empty($recipients)) {
            Log::error('sendMail aborted: recipients list is empty', [
                'sample_id' => $sample->id,
                'site'      => $sample->site,
                'platform'  => $site->Platform ?? 'null',
            ]);
            return false;
        }

        try {
            Mail::to($recipients)->send(new QualityAlertEmail($sample));
            Log::info('sendMail sent successfully', ['sample_id' => $sample->id, 'recipients' => $recipients]);
            return true;
        } catch (\Exception $e) {
            Log::error('sendMail exception', [
                'sample_id' => $sample->id,
                'error'     => $e->getMessage(),
                'trace'     => $e->getTraceAsString(),
            ]);
            return false;
        }
    }

    private function sendMail1($sample)
    {
        $site = Site::where("Id_Site", $sample->site)->first();

        // $conf = Configuration::where("app", "quality")->where("name", "alert")->first();
        // $recipients_conf = json_decode($conf->value);
        // if (property_exists($recipients_conf, $site->Platform)) {
        //     $recipients = [$recipients_conf->{$site->Platform}];
        //     $e= [$recipients,$site->technician_site];
        //     //$recipients = ['chamnap.keo@teuksaat1001.com'];
        // } else { // platform doesnt exist in configuration of quality alert so we send to admins
        //     $e = ['chamnap.keo@teuksaat1001.com'];
        // }
        $sample['en_name'] = $site->Entrepreneur_English_Name ?? null;
        $sample['en_phone'] = $site->Phone_Number ?? null;
        $recipients = '';
        $technician_email = '';
        $supervisor_email = '';
        if ($site->technician_site != Null || $site->technician_site != '') {
            $technician_email = $site->technician_site;
        } else {
            $technician_email = "chamnap.keo@teuksaat1001.com";
        }
        if ($site->technician_site == "phalla.p@teuksaat1001.com" || $site->technician_site == "odom.p@teuksaat1001.com" || $site->technician_site == "veasna.r@teuksaat1001.com" || $site->technician_site == "dara.s@teuksaat1001.com" || $site->technician_site == "sak.s@teuksaat1001.com") {
            $supervisor_email = "bros.t@teuksaat1001.com";
        } else if ($site->technician_site == "vuthy.n@teuksaat1001.com" || $site->technician_site == "pisak.m@teuksaat1001.com" || $site->technician_site == "phanith.m@teuksaat1001.com" || $site->technician_site == "phalla.p@teuksaat1001.com" || $site->technician_site == "darith.s@teuksaat1001.com") {
            $supervisor_email = "chanthan.m@teuksaat1001.com";
        } else {
            $supervisor_email = "chamnap.keo@teuksaat1001.com";
        }
        if ($site->Platform == "SR") {
            $recipients = ['kimhong.p@teuksaat1001.com','samnang.p@teuksaat1001.com', $supervisor_email, $technician_email];
        }
        if ($site->Platform == "KC") {
            $recipients = ['bun.ph@teuksaat1001.com', 'chakriya.v@teuksaat1001.com', $supervisor_email, $technician_email];
        }
        if ($site->Platform == "PP") {
            $recipients = ['lim.t@teuksaat1001.com', 'chakriya.v@teuksaat1001.com', $supervisor_email, $technician_email];
        }
        if ($site->Platform == "BTB") {
            $recipients = ['yet.y@teuksaat1001.com', 'sreymao.b@teuksaat1001.com', $supervisor_email, $technician_email];
        }
        if ($site->Platform == "KSP") {
            $recipients = ['rethy.m@teuksaat1001.com', 'chakriya.v@teuksaat1001.com', $supervisor_email, $technician_email];
        }
        if ($site->technician_site == Null || $site->technician_site == '') {
            $recipients = ['chamnap.keo@teuksaat1001.com'];
        }
        // dd($recipients);
        Mail::to($recipients)->send(new QualityAlertEmail($sample));
    }
    // send email via site selection and open
    private function sendMailSiteOpenOrSelection($sample)
    {
        $recipients = '';
        // $site = Site::where("Id_Site", $sample->site)->first();
        if ($sample->type == "Site_Opening") {

            if ($sample->laboratory == "SR") {

                $recipients = ['kimhong.p@teuksaat1001.com','samnang.p@teuksaat1001.com', 'amandine.chaussinand@teuksaat1001.com', "mongkul.s@teuksaat1001.com", "saly.s@teuksaat1001.com", auth()->user()->email];
            }
            if ($sample->laboratory == "KC") {

                $recipients = ['bun.ph@teuksaat1001.com', 'amandine.chaussinand@teuksaat1001.com', "mongkul.s@teuksaat1001.com", "saly.s@teuksaat1001.com", "chakriya.v@teuksaat1001.com", auth()->user()->email];
            }
            if ($sample->laboratory == "PP") {

                $recipients = ['lim.t@teuksaat1001.com', 'amandine.chaussinand@teuksaat1001.com', "mongkul.s@teuksaat1001.com", "saly.s@teuksaat1001.com", "chakriya.v@teuksaat1001.com", auth()->user()->email];
            }
            if ($sample->laboratory == "BTB") {

                $recipients = ['yet.y@teuksaat1001.com', 'amandine.chaussinand@teuksaat1001.com', "mongkul.s@teuksaat1001.com", "saly.s@teuksaat1001.com", "sreymao.b@teuksaat1001.com", auth()->user()->email];
            }
            if ($sample->laboratory == "KSP") {

                $recipients = ['rethy.m@teuksaat1001.com', 'amandine.chaussinand@teuksaat1001.com', "mongkul.s@teuksaat1001.com", "saly.s@teuksaat1001.com", "chakriya.v@teuksaat1001.com", auth()->user()->email];
            }
        }
        if ($sample->type == "Site_Selection") {

            if ($sample->laboratory == "SR") {

                $recipients = ['amandine.chaussinand@teuksaat1001.com','samnang.p@teuksaat1001.com', "mongkul.s@teuksaat1001.com", "saly.s@teuksaat1001.com", auth()->user()->email];
            }
            if ($sample->laboratory == "KC") {

                $recipients = ['amandine.chaussinand@teuksaat1001.com', "mongkul.s@teuksaat1001.com", "saly.s@teuksaat1001.com", "chakriya.v@teuksaat1001.com", auth()->user()->email];
            }
            if ($sample->laboratory == "PP") {

                $recipients = ['amandine.chaussinand@teuksaat1001.com', "mongkul.s@teuksaat1001.com", "saly.s@teuksaat1001.com", "chakriya.v@teuksaat1001.com", auth()->user()->email];
            }
            if ($sample->laboratory == "BTB") {

                $recipients = ['amandine.chaussinand@teuksaat1001.com', "mongkul.s@teuksaat1001.com", "saly.s@teuksaat1001.com", "sreymao.b@teuksaat1001.com", auth()->user()->email];
            }
            if ($sample->laboratory == "KSP") {

                $recipients = ['amandine.chaussinand@teuksaat1001.com', "mongkul.s@teuksaat1001.com", "saly.s@teuksaat1001.com", "chakriya.v@teuksaat1001.com", auth()->user()->email];
            }
        }
        // site intervention
        if ($sample->type == "Site_Intervention") {

            if ($sample->laboratory == "SR") {

                $recipients = ['kimhong.p@teuksaat1001.com', auth()->user()->email,'samnang.p@teuksaat1001.com'];
            }
            if ($sample->laboratory == "KC") {

                $recipients = ['bun.ph@teuksaat1001.com', "chakriya.v@teuksaat1001.com", auth()->user()->email];
            }
            if ($sample->laboratory == "PP") {

                $recipients = ['lim.t@teuksaat1001.com', "chakriya.v@teuksaat1001.com", auth()->user()->email];
            }
            if ($sample->laboratory == "BTB") {

                $recipients = ['yet.y@teuksaat1001.com', "sreymao.b@teuksaat1001.com", auth()->user()->email];
            }
            if ($sample->laboratory == "KSP") {

                $recipients = ['rethy.m@teuksaat1001.com', "chakriya.v@teuksaat1001.com", auth()->user()->email];
            }
        }

        // $recipients = ['chamnap.keo@teuksaat1001.com'];


        Mail::to($recipients)->send(new SiteOpenOrSelection($sample));
    }
    // lab alert email
    private function labAlertEmail($sample)
    {
        $s = $sample->site;
        $site = Site::select('Platform')->where("Id_Site", $s)->first();
        $rom = "";
        if (!$site) {
            $rom = 'chamnap.keo@teuksaat1001.com';
        }
        else if ($site->Platform == null || $site->Platform == '') {
             $rom = 'chamnap.keo@teuksaat1001.com';
        } elseif ($site->Platform == "SR") {
            $rom = 'kimhong.p@teuksaat1001.com';
        } elseif ($site->Platform == "BTB") {
            $rom = 'yet.y@teuksaat1001.com';
        } elseif ($site->Platform == "PP") {
            $rom = 'lim.t@teuksaat1001.com';
        } elseif ($site->Platform == "KSP") {
            $rom = 'rethy.m@teuksaat1001.com';
        } elseif ($site->Platform == "KC") {
            $rom = 'bun.ph@teuksaat1001.com';
        } else {
            $rom = 'chamnap.keo@teuksaat1001.com';
        }
        if ($sample->type == "Site_Opening" || $sample->type == "Site_Selection" || $sample->type == "Site_Intervention") {

            $recipients = [
                'amandine.chaussinand@teuksaat1001.com',
                'andrea.delsoldato@teuksaat1001.com',
                'saly.s@teuksaat1001.com',
                'borin.t@teuksaat1001.com',
                'mongkul.s@teuksaat1001.com',
                $rom
            ];
        } else {
            $recipients = ['chamnap.keo@teuksaat1001.com'];
        }

        // $recipients = ['chamnap.keo@teuksaat1001.com'];

        Mail::to($recipients)->send(new LabEmailBack($sample));
    }
    // final judgement email alert
    private function finalJudgement($sample, $platform)
    {
        $recipients = '';
        if ($sample->type == "Site_Opening") {
            if ($platform == "SR") {

                $recipients = [
                    'samnang.p@teuksaat1001.com',
                    'kimhong.p@teuksaat1001.com',
                    "amandine.chaussinand@teuksaat1001.com",
                    "mongkul.s@teuksaat1001.com",
                    "saly.s@teuksaat1001.com",
                    'andrea.delsoldato@teuksaat1001.com',
                    'borin.t@teuksaat1001.com',
                    'rethy.m@teuksaat1001.com',
                    'samnang.p@teuksaat1001.com'
                ];
            }
            if ($platform == "KC") {

                $recipients = [
                    'samnang.p@teuksaat1001.com',
                    'bun.ph@teuksaat1001.com',
                    "amandine.chaussinand@teuksaat1001.com",
                    "mongkul.s@teuksaat1001.com",
                    "saly.s@teuksaat1001.com",
                    "chakriya.v@teuksaat1001.com",
                    'andrea.delsoldato@teuksaat1001.com',
                    'borin.t@teuksaat1001.com',
                    'rethy.m@teuksaat1001.com',

                ];
            }
            if ($platform == "PP") {

                $recipients = [
                    'samnang.p@teuksaat1001.com',
                    'lim.t@teuksaat1001.com',
                    "amandine.chaussinand@teuksaat1001.com",
                    "mongkul.s@teuksaat1001.com",
                    "saly.s@teuksaat1001.com",
                    "chakriya.v@teuksaat1001.com",
                    'andrea.delsoldato@teuksaat1001.com',
                    'borin.t@teuksaat1001.com',
                    'rethy.m@teuksaat1001.com',

                ];
            }
            if ($platform == "BTB") {

                $recipients = [
                    'samnang.p@teuksaat1001.com',
                    'yet.y@teuksaat1001.com',
                    "amandine.chaussinand@teuksaat1001.com",
                    "mongkul.s@teuksaat1001.com",
                    "saly.s@teuksaat1001.com",
                    "sreymao.b@teuksaat1001.com",
                    'andrea.delsoldato@teuksaat1001.com',
                    'borin.t@teuksaat1001.com',
                    'rethy.m@teuksaat1001.com',

                ];
            }
            if ($platform == "KSP") {

                $recipients = [
                    'samnang.p@teuksaat1001.com',
                    'rethy.m@teuksaat1001.com',
                    "amandine.chaussinand@teuksaat1001.com",
                    "mongkul.s@teuksaat1001.com",
                    "saly.s@teuksaat1001.com",
                    "chakriya.v@teuksaat1001.com",
                    'andrea.delsoldato@teuksaat1001.com',
                    'borin.t@teuksaat1001.com',
                    'rethy.m@teuksaat1001.com',

                ];
            }
        }
        if ($sample->type == "Site_Selection") {
            if ($sample->laboratory == "SR") {

                $recipients = [
                    'samnang.p@teuksaat1001.com',
                    "amandine.chaussinand@teuksaat1001.com",
                    "mongkul.s@teuksaat1001.com",
                    "saly.s@teuksaat1001.com",
                    'andrea.delsoldato@teuksaat1001.com',
                    'borin.t@teuksaat1001.com',

                ];
            }
            if ($sample->laboratory == "KC") {

                $recipients = [
                    'samnang.p@teuksaat1001.com',
                    "amandine.chaussinand@teuksaat1001.com",
                    "mongkul.s@teuksaat1001.com",
                    "saly.s@teuksaat1001.com",
                    "chakriya.v@teuksaat1001.com",
                    'andrea.delsoldato@teuksaat1001.com',
                    'borin.t@teuksaat1001.com',

                ];
            }
            if ($sample->laboratory == "PP") {

                $recipients = [
                    'samnang.p@teuksaat1001.com',
                    "amandine.chaussinand@teuksaat1001.com",
                    "mongkul.s@teuksaat1001.com",
                    "saly.s@teuksaat1001.com",
                    "chakriya.v@teuksaat1001.com",
                    'andrea.delsoldato@teuksaat1001.com',
                    'borin.t@teuksaat1001.com',
                    'rethy.m@teuksaat1001.com',

                ];
            }
            if ($sample->laboratory == "BTB") {

                $recipients = [
                    'samnang.p@teuksaat1001.com',
                    "amandine.chaussinand@teuksaat1001.com",
                    "mongkul.s@teuksaat1001.com",
                    "saly.s@teuksaat1001.com",
                    "sreymao.b@teuksaat1001.com",
                    'andrea.delsoldato@teuksaat1001.com',
                    'borin.t@teuksaat1001.com',

                ];
            }
        }
        if ($sample->type == "Site_Intervention") {

            if ($platform == "SR") {

                $recipients = ["amandine.chaussinand@teuksaat1001.com", 'kimhong.p@teuksaat1001.com', 'andrea.delsoldato@teuksaat1001.com','samnang.p@teuksaat1001.com'];
            }
            if ($platform == "KC") {

                $recipients = ["amandine.chaussinand@teuksaat1001.com", 'bun.ph@teuksaat1001.com', "chakriya.v@teuksaat1001.com", 'andrea.delsoldato@teuksaat1001.com'];
            }
            if ($platform == "PP") {

                $recipients = ["amandine.chaussinand@teuksaat1001.com", 'lim.t@teuksaat1001.com', "chakriya.v@teuksaat1001.com", 'andrea.delsoldato@teuksaat1001.com'];
            }
            if ($platform == "BTB") {

                $recipients = ["amandine.chaussinand@teuksaat1001.com", 'yet.y@teuksaat1001.com', "sreymao.b@teuksaat1001.com", 'andrea.delsoldato@teuksaat1001.com'];
            }
            if ($platform == "KSP") {

                $recipients = ["amandine.chaussinand@teuksaat1001.com", 'rethy.m@teuksaat1001.com', "chakriya.v@teuksaat1001.com", 'andrea.delsoldato@teuksaat1001.com'];
            }
        }
        // $recipients = ['chamnap.keo@teuksaat1001.com'];

        Mail::to($recipients)->send(new Judgement($sample));
    }
    /**
     * Store a newly created resource in storage.
     */

    public function store(Request $request)
    {

        //$sample = $request->all();
        $sampleData = json_decode($request->sample, true);
        //dd($sampleData);
        $site1 = $sitefield = $site = $phone = '';
        if (isset($sampleData['site'])) {
            if ($sampleData['site'] != '' || $sampleData['site'] != null) {
                $site1 = Site::find($sampleData['site']);
                $sitefield = $site1->Platform;
                $site = $sampleData['site'];
                $phone = $site1->Phone_Number;
            }
        } else {
            $sampleData['site'] = "";
        }

        $sampleData["created_by"] = auth()->user()->email;
        $sampleData["last_updates"] = collect([["user" => auth()->user()->email, "date" => date("Y-m-d H:i:s")]]);
        $sampleData["phone_tech"] = $phone;
        $sample = Sample::create($sampleData);
        if ($request->hasFile('images')) {
            foreach ($request->file('images') as $image) {
                $imageName = time() . '_' . Str::random(20) . '.' . $image->extension();
                $imagePath = $image->storeAs('public/samples/' . $sample->id, $imageName);
                UploadPicture::create(['path' => $imagePath, 'sample_id' => $sample->id]);
            }
        }

        if ($sampleData['type'] == "Monthly Test" || $sampleData['type'] == "WQ Alert") {
            if ($sample->contamination_level_machine > 0 || $sample->contamination_level_bottle > 0) {
                //if ($sample->contamination_level_machine > 1) {
               $check= $this->sendMail($sample);
               if($check){
                Log::info("email sent successfully for sample id: ".$sample->id);
               }
               else{
                Log::error("email sending failed for sample id: ".$sample->id);
               }
            }
        }
        if ($sampleData['type'] == "Site_Opening" || $sampleData['type'] == "Site_Selection" || $sampleData['type'] == "Site_Intervention") {
            $this->sendMailSiteOpenOrSelection($sample);
        }
        // Add to technical if contamination is level 2 ,3
        if ($sampleData['type'] == "Monthly Test" || $sampleData['type'] == "WQ Alert") {
            if ($sample->contamination_level_machine > 1) {
                $technical = new Technical();
                $technical->site = $site;
                $technical->problem_date = Carbon::now();
                $technical->site_problem_description = "Alert_WQ";
                $technical->sub_problem_description = "Alert_WQ";
                $technical->comment_problem = "Alert from WQ app";
                $technical->report_by = auth()->user()->email;
                $technical->phone_number = $phone;
                if ($sample->contamination_level_machine == 3) {
                    $technical->problem_status = "Can Not Produce";
                    $technical->stop_work = 1;
                } else {
                    $technical->problem_status = "Can Produce";
                    $technical->stop_work = 0;
                }

                $technical->site_platform = $sitefield;
                $technical->status = "Waiting Validation";
                $technical->save();
            }
        }
        return $sample;
    }
    public function external()
    {
        return sampleExternal::get();
    }
    /**
     * Update the specified resource in storage.
     */
    public function update(Request $request, Sample $sample)
    {

        $returnSite = Site::find($request->site);
        $platform = $returnSite ? $returnSite->Platform : 'Test';
        $original_risk =  max([$sample->contamination_level_bottle, $sample->contamination_level_machine]);
        $sample->fill($request->all());
        $updates = $sample->last_updates;

        $updates->push(["user" => auth()->user()->email, "date" => date("Y-m-d H:i:s")]);
        $sample->last_updates = $updates;

        if ($request->type == "Monthly Test" || $request->type == "WQ Alert") {
            if ($original_risk == 0 && ($sample->contamination_level_machine > 0 || $sample->contamination_level_bottle > 0)) {
                // original_risk is used to send email only if the update is about a sample that was previous not contaminated
                // if sample was already contaminated before updating it no need to send email as one email has already been sent
                //$this->sendMail($sample);
            }
        }
        if ($request->type == "Site_Opening"  || $request->type == "Site_Intervention") {
            if ($sample->contamination_level_machine != '' || $sample->contamination_level_bottle != '') {
                $this->labAlertEmail($sample);
            }
        }
        if ($request->type == "Site_Selection") {
            if ($sample->ph != "" && $sample->email_status == "") {
                $this->labAlertEmail($sample);
                 $sample->email_status = 1;
            }
        }
        if ($request->type == "Site_Opening" || $request->type == "Site_Selection" || $request->type == "Site_Intervention") {
            if ($sample->site_open_final_judgement != "" || $sample->site_open_final_judgement != null) {
                $this->finalJudgement($sample, $platform);
            }
        }

        $sample->save();
        return $sample;
    }

    /**
     * Remove the specified resource from storage.
     */
    public function destroy(Sample $sample, Request $request)
    {
        $data = Sample::findOrFail($request->id);
        $data->delete();
        return "data is deleted";
    }

    public function print(Request $request)
    {
        $request->validate(['id' => 'required']);

        $sample = Sample::findOrFail($request->id);
        $site = Site::where("Id_site", "=", $sample->site)->firstOrFail();
        $template = storage_path('app/templates/result-printer-teuksaat-PP.xlsx');
        switch ($site->Platform) {
            case 'KPC':
            case 'SR':
            case 'KSP':
                $template = storage_path('app/templates/result-printer-teuksaat-KPC.xlsx');
                break;
            case 'PP':
                $template = storage_path('app/templates/result-printer-teuksaat-PP.xlsx');
                break;
            case 'BTB':
                $template = storage_path('app/templates/result-printer-teuksaat-BTB.xlsx');
                break;
        }

        $sample = $sample->toArray();
        $sample["sample_date"] = substr($sample["sample_date"], 0, 7);
        $sample["analysis_date"] = substr($sample["sample_date"], 0, 7);

        if (isset($sample["safe"]) && $sample["safe"] == "yes") {
            $sample["safe_box"] = "☑";
            $sample["unsafe_box"] = "☐";
        } else {
            $sample["safe_box"] = "☐";
            $sample["unsafe_box"] = "☑";
        }

        $TBS = new \clsTinyButStrong();
        $ok = class_exists('clsOpenTBS', true); // hack to force class loading of TBS
        $TBS->Plugin(TBS_INSTALL, OPENTBS_PLUGIN);
        $TBS->OtbsMsExcelExplicitRef = false;
        $TBS->LoadTemplate($template, OPENTBS_ALREADY_UTF8);
        $TBS->SetOption("noerr", true);
        $TBS->MergeField('sample', $sample);
        //$TBS->PlugIn(OPENTBS_DEBUG_XML_CURRENT);
        $filename = "quality_" . $site . "_" . $sample["sample_date"] . ".xlsx";
        $TBS->Show(OPENTBS_DOWNLOAD, $filename);
    }

    public function donwloadPicture(Request $request)
    {
        $id = $request->sample_id;
        $sample = Sample::findOrFail($id);
        $pictures = $sample->uploadPicture;

        $zip = new ZipArchive;
        $zipFileName = 'sample_' . $sample->id . '.zip';
        $zipPath = storage_path('app/public/samples/' . $zipFileName);
        if ($zip->open($zipPath, ZipArchive::CREATE) !== true) {
            return response()->json(['error' => 'Error creating zip file'], 500);
        }
        foreach ($pictures as $picture) {
            $filePath = storage_path('app/' . $picture->path);
            //dump($filePath, file_exists($filePath));
            if (!file_exists($filePath)) {
                continue;
            }
            $relativePath = 'images/' . $sample->id . '/' . basename($picture->path);
            if ($zip->addFile($filePath, $relativePath) !== true) {
                $zip->close();
                Storage::delete($zipPath);
                return response()->json(['error' => 'Error adding file to zip'], 500);
            }
        }
        $zip->close();
        return response()->download($zipPath)
            ->deleteFileAfterSend(true);
        // ->header('Content-Type', 'application/zip');;

    }
    public function exportExcel(Request $request)
    {
        $request->validate(['month' => 'required']);
        $inputFileName = storage_path('app/templates/new_certificate.xlsx');

        if ($request->month == "all") {
            $query = Sample::orderBy('sample_date', 'desc');
        } else {
            [$year, $month] = explode("-", $request->month);
            $query = Sample::whereMonth("sample_date", "=", $month)
                ->whereYear("sample_date", "=", $year)
                // ->where("test_number", "first")
                ->orderBy('sample_date', 'desc');
        }
        $samples = $query->get();
        $sites = Site::orderBy("Id_Site")->get();

        $data = array();
        $obj1 = array();
        $register_array = array();
        $site_platform = array();

        foreach ($sites as $site) {
            $site_platform[$site->Id_Site] = $site->Platform;
            $obj1[$site->Id_Site]['pro'] = $site->Village_khmer . " " . $site->Commune_khmer . " " . $site->District_khmer . " " . $site->Province_khmer;
            $obj1[$site->Id_Site]['water_source'] = $site->Water_Source;
            $obj1[$site->Id_Site]['advisor'] = $site->Advisor;
        }

        foreach ($samples as $sample) {
            $sd = $sample->sample_date->format('Y-m-d');
            $ad = $sample->analysis_date->format('Y-m-d');
            if (isset($sample->recieved_date)) {
                $rd = $sample->recieved_date->format('Y-m-d');
            } else {
                $rd = "";
            }
            $obj = $sample->toArray();
            $obj['platform'] = isset($site_platform[$obj['site']]) ? $site_platform[$obj['site']] : "";
            $obj['kh_location'] = isset($obj1[$obj['site']]) ? $obj1[$obj['site']]['pro'] : "";
            $obj['source'] = isset($obj1[$obj['site']]) ? $obj1[$obj['site']]['water_source'] : "";
            // $obj['advisor'] = isset($register_array[$obj['site']]) ? $register_array[$obj['site']]['advisor'] : "";
            $obj['advisor'] = isset($obj1[$obj['site']]) ? $obj1[$obj['site']]['advisor'] : "";
            $obj['sampleDate'] = date("Y-m-d", strtotime("$sd +1 day"));
            $obj['analysisDate'] = date("Y-m-d", strtotime("$ad +1 day"));
            $obj['recievedDate'] = isset($obj['recievedDate']) ? date("Y-m-d", strtotime("$rd +1 day")) : "";
            $data[] = $obj;
        }

        $TBS = new \clsTinyButStrong();
        $ok = class_exists('clsOpenTBS', true); // hack to force class loading of TBS
        $TBS->Plugin(\TBS_INSTALL, \OPENTBS_PLUGIN);
        $TBS->OtbsMsExcelExplicitRef = false;
        $TBS->LoadTemplate($inputFileName, \OPENTBS_ALREADY_UTF8);
        $TBS->SetOption("noerr", true);
        $TBS->MergeBlock('a', $data);
        //$TBS->PlugIn(OPENTBS_DEBUG_XML_CURRENT);
        $filename = "quality_monthly_report_" . $request->month . ".xlsx";
        $TBS->Show(OPENTBS_DOWNLOAD, $filename);
    }

    public function sampleExcelSiteOpenOrSiteSelection(Request $request)
    {
        $type = $request->type;
        $inputFileName = "";

        if ($type == "Site_Selection") {
            $inputFileName = storage_path('app/templates/site_selection.xlsx');
        }
        else if ($type == "Raw_Water") {
            $inputFileName = storage_path('app/templates/raw_water.xlsx');
        }
        else {
            $inputFileName = storage_path('app/templates/site_opening.xlsx');
        }
        if ($type == "Raw_Water") {
             $query = Sample::where("type", $type)
                ->orderBy('created_at', 'desc');
        }
        else {
             $query = Sample::where("type", $type)
            ->orderBy('sample_date', 'desc');
        }
        $samples = $query->get();
        $sites = Site::orderBy("Id_Site")->get();

        $data = array();
        $obj1 = array();
        $register_array = array();
        $site_platform = array();

        foreach ($sites as $site) {
            $site_platform[$site->Id_Site] = $site->Platform;
            $obj1[$site->Id_Site]['pro'] = $site->Village_khmer . " " . $site->Commune_khmer . " " . $site->District_khmer . " " . $site->Province_khmer;
            $obj1[$site->Id_Site]['water_source'] = $site->Water_Source;
            $obj1[$site->Id_Site]['advisor'] = $site->Advisor;
        }

        foreach ($samples as $sample) {
            $sd = $sample->site_open_sample_date->format('Y-m-d');
            $ad = $sample->analysis_date->format('Y-m-d');
            if (isset($sample->recieved_date)) {
                $rd = $sample->recieved_date->format('Y-m-d');
            } else {
                $rd = "";
            }
            $obj = $sample->toArray();
            $obj['platform'] = isset($site_platform[$obj['site']]) ? $site_platform[$obj['site']] : "";
            $obj['kh_location'] = isset($obj1[$obj['site']]) ? $obj1[$obj['site']]['pro'] : "";
            $obj['source'] = isset($obj1[$obj['site']]) ? $obj1[$obj['site']]['water_source'] : "";
            // $obj['advisor'] = isset($register_array[$obj['site']]) ? $register_array[$obj['site']]['advisor'] : "";
            $obj['advisor'] = isset($obj1[$obj['site']]) ? $obj1[$obj['site']]['advisor'] : "";
            $obj['sampleDate'] = date("Y-m-d", strtotime("$sd +1 day"));
            $obj['analysisDate'] = date("Y-m-d", strtotime("$ad +1 day"));
            $obj['recievedDate'] = isset($obj['recievedDate']) ? date("Y-m-d", strtotime("$rd +1 day")) : "";
            $obj['created_sample_date'] = date("Y-m-d", strtotime($sample->created_at));
            $data[] = $obj;
        }

        //dd($data);
        $TBS = new \clsTinyButStrong();
        $ok = class_exists('clsOpenTBS', true); // hack to force class loading of TBS
        $TBS->Plugin(\TBS_INSTALL, \OPENTBS_PLUGIN);
        $TBS->OtbsMsExcelExplicitRef = false;
        $TBS->LoadTemplate($inputFileName, \OPENTBS_ALREADY_UTF8);
        $TBS->SetOption("noerr", true);
        $TBS->MergeBlock('a', $data);
        //$TBS->PlugIn(OPENTBS_DEBUG_XML_CURRENT);
        $filename = "quality_monthly_report_" . "specific_SITE" . ".xlsx";
        $TBS->Show(OPENTBS_DOWNLOAD, $filename);
    }


    public function sampleExcelSite(Request $request)
    {
        $site = $request->site;

        $inputFileName = storage_path('app/templates/new_certificate.xlsx');
        $query = Sample::where("site", $site)
            ->orderBy('sample_date', 'desc');

        $samples = $query->get();
        $sites = Site::orderBy("Id_Site")->get();

        $data = array();
        $obj1 = array();
        $register_array = array();
        $site_platform = array();

        foreach ($sites as $site) {
            $site_platform[$site->Id_Site] = $site->Platform;
            $obj1[$site->Id_Site]['pro'] = $site->Village_khmer . " " . $site->Commune_khmer . " " . $site->District_khmer . " " . $site->Province_khmer;
            $obj1[$site->Id_Site]['water_source'] = $site->Water_Source;
            $obj1[$site->Id_Site]['advisor'] = $site->Advisor;
        }

        foreach ($samples as $sample) {
            $sd = $sample->sample_date->format('Y-m-d');
            $ad = $sample->analysis_date->format('Y-m-d');
            if (isset($sample->recieved_date)) {
                $rd = $sample->recieved_date->format('Y-m-d');
            } else {
                $rd = "";
            }
            $obj = $sample->toArray();
            $obj['platform'] = isset($site_platform[$obj['site']]) ? $site_platform[$obj['site']] : "";
            $obj['kh_location'] = isset($obj1[$obj['site']]) ? $obj1[$obj['site']]['pro'] : "";
            $obj['source'] = isset($obj1[$obj['site']]) ? $obj1[$obj['site']]['water_source'] : "";
            // $obj['advisor'] = isset($register_array[$obj['site']]) ? $register_array[$obj['site']]['advisor'] : "";
            $obj['advisor'] = isset($obj1[$obj['site']]) ? $obj1[$obj['site']]['advisor'] : "";
            $obj['sampleDate'] = date("Y-m-d", strtotime("$sd +1 day"));
            $obj['analysisDate'] = date("Y-m-d", strtotime("$ad +1 day"));
            $obj['recievedDate'] = isset($obj['recievedDate']) ? date("Y-m-d", strtotime("$rd +1 day")) : "";
            $data[] = $obj;
        }

        $TBS = new \clsTinyButStrong();
        $ok = class_exists('clsOpenTBS', true); // hack to force class loading of TBS
        $TBS->Plugin(\TBS_INSTALL, \OPENTBS_PLUGIN);
        $TBS->OtbsMsExcelExplicitRef = false;
        $TBS->LoadTemplate($inputFileName, \OPENTBS_ALREADY_UTF8);
        $TBS->SetOption("noerr", true);
        $TBS->MergeBlock('a', $data);
        //$TBS->PlugIn(OPENTBS_DEBUG_XML_CURRENT);
        $filename = "quality_monthly_report_" . "specific_SITE" . ".xlsx";
        $TBS->Show(OPENTBS_DOWNLOAD, $filename);
    }

    // extract data for map




}
