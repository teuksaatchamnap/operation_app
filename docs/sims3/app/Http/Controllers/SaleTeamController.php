<?php

namespace App\Http\Controllers;

use App\Models\SaleSurvey;
use App\Models\SaleTeam;
use Illuminate\Contracts\Validation\Validator;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;

class SaleTeamController extends Controller
{
    /**
     * Display a listing of the resource.
     */
    public function index(Request $request)
    {
        // $validator = Validator::make(['monthYear' => $monthYear], [
        //     'monthYear' => 'required|date_format:Y-m', // Ensure valid format
        // ]);
        $request->validate([
            'selectDate' => 'required|date_format:Y-m'
        ]);
        return SaleTeam::select(
            'sale_team.site',
            'sale_team.sale_type',
            'Sites.Platform',
            DB::raw('SUM(free) as free'),
            DB::raw('SUM(refill) as refill'),
            DB::raw('SUM(new_bottle) as new_bottle'),
            DB::raw('SUM(lending_bottle) as lending_bottle'),
            DB::raw('SUM(free)+SUM(refill)+SUM(new_bottle)+SUM(lending_bottle) as total_bottle'),
            DB::raw('COUNT(customer) as customer')
        )
            ->join('Sites', 'sale_team.site', '=', 'Sites.Id_Site')
            ->whereMonth('sale_team.sale_date', date('m', strtotime($request->selectDate)))
            ->whereYear('sale_team.sale_date', date('Y', strtotime($request->selectDate)))
            ->where('sale_team.site', '!=', '')
            ->groupBy('sale_team.site', 'sale_team.sale_type', 'Sites.Platform')
            ->orderBy('sale_team.sale_date', 'desc')
            ->get();

        // return SaleTeam::selectRaw('sale_teams.*,SUM(CASE WHEN new_bottle THEN 1 ELSE 0 END) + SUM(CASE WHEN lending_bottle THEN 1 ELSE 0 END) as')
        // ->groupBy('site')
        // ->orderBy('sale_date','desc')
        // ->limit(300)
        // ->get();

    }
    public function show(Request $request)
    {

        $query = SaleTeam::query();
        $limit = 500;
        if ($request->has('excel')) {
            $limit = 999999;
        }
        if ($request->has("detail_sale")) {
            return SaleTeam::whereMonth('sale_date', date('m', strtotime($request->selectDate)))
                ->whereYear('sale_date', date('Y', strtotime($request->selectDate)))
                ->where('site', $request->site)
                ->orderBy('sale_date', 'desc')
                ->skip(($request->page - 1) * 100)
                ->take($limit)
                ->get();
        } else {
            return SaleTeam::select('site', 'sale_date', DB::raw('SUM(free) as free,SUM(refill) as refill,SUM(new_bottle) as new_bottle,SUM(lending_bottle) as lending_bottle, SUM(free)+SUM(refill)+SUM(new_bottle)+SUM(lending_bottle) as total_bottle'), DB::raw('count(customer) as customer'))
                ->whereMonth('sale_date', date('m', strtotime($request->selectDate)))
                ->whereYear('sale_date', date('Y', strtotime($request->selectDate)))
                ->where('site', $request->site)
                ->orderBy('sale_date', 'desc')
                ->groupBy('site', 'sale_date')
                ->skip(($request->page - 1) * 15)
                ->take($limit)
                ->get();
        }
        //dd($request->selectDate);

    }

    public function saleDownloadReport(Request $request)
    {

        if ($request->select_report == "Monthly Report") {
            $inter = SaleTeam::from('sale_team as st')
                ->select(
                    'st.site',
                    'st.sale_type',
                    's.Platform',
                    DB::raw('SUM(st.free) as free'),
                    DB::raw('SUM(st.refill) as refill'),
                    DB::raw('SUM(st.new_bottle) as new_bottle'),
                    DB::raw('SUM(st.lending_bottle) as lending_bottle'),
                    DB::raw('SUM(st.free)+SUM(st.refill)+SUM(st.new_bottle)+SUM(st.lending_bottle) as total_bottle'),
                    DB::raw('COUNT(st.customer) as customer')
                )
                ->join('Sites as s', 'st.site', '=', 's.Id_Site')
                ->whereMonth('st.sale_date', date('m', strtotime($request->selectDate)))
                ->whereYear('st.sale_date', date('Y', strtotime($request->selectDate)))
                ->groupBy('st.site', 'st.sale_type', 's.Platform') // ⚠️ must include Platform
                ->orderBy('st.sale_date', 'desc')
                ->get();
            $inter1 = SaleTeam::from('sale_team as st')
                ->select('st.*', 's.Platform')
                ->join('Sites as s', 'st.site', '=', 's.Id_Site')
                ->whereMonth('st.sale_date', date('m', strtotime($request->selectDate)))
                ->whereYear('st.sale_date', date('Y', strtotime($request->selectDate)))
                ->orderBy('st.sale_date', 'desc')
                ->get();
        } else {
            $inter = SaleTeam::from('sale_team as st')
                ->select(
                    'st.site',
                    'st.sale_type',
                    's.Platform',
                    DB::raw('SUM(st.free) as free'),
                    DB::raw('SUM(st.refill) as refill'),
                    DB::raw('SUM(st.new_bottle) as new_bottle'),
                    DB::raw('SUM(st.lending_bottle) as lending_bottle'),
                    DB::raw('SUM(st.free + st.refill + st.new_bottle + st.lending_bottle) as total_bottle'),
                    DB::raw('COUNT(st.customer) as customer')
                )
                ->join('Sites as s', 'st.site', '=', 's.Id_Site')
                ->whereDate('st.sale_date', '>=', $request->start_date)
                ->whereDate('st.sale_date', '<=', $request->end_date)
                ->groupBy('st.site', 'st.sale_type', 's.Platform')
                ->orderBy('st.sale_date', 'desc')
                ->get();
            $inter1 = SaleTeam::from('sale_team as st')
                ->select('st.*', 's.Platform')
                ->join('Sites as s', 'st.site', '=', 's.Id_Site')
                ->whereDate('st.sale_date', '>=', $request->start_date)
                ->whereDate('st.sale_date', '<=', $request->end_date)
                ->orderBy('st.sale_date', 'desc')
                ->get();
        }



        $data = array();

        foreach ($inter as $sale) {
            $sale['month'] = $request->selectDate;
            if ($request->select_report == "Monthly Report") {
                $inputFileName = storage_path('app/templates/saleTeamConsolidate.xlsx');
            } else {
                $inputFileName = storage_path('app/templates/saleTeamConsolidateRangeDate.xlsx');
            }
            if ($sale->sale_type == "opening_site") {
                $sale['target'] = 500;
                $sale['rate'] = ($sale->customer / 500);
            } else {
                $sale['target'] = 150;
                $sale['rate'] = ($sale->customer / 150);
            }
            $data[] = $sale->toArray();
        }


        $data2 = array();
        foreach ($inter1 as $sale) {
            $data2[] = $sale->toArray();
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
        $TBS->SetOption("noerr", true);
        $TBS->MergeBlock('b', $data2);
        $TBS->Show(OPENTBS_DOWNLOAD, "saleTeam.xlsx");
    }

    public function searchRecord($id)
    {
        return SaleTeam::find($id);
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


    /**
     * Update the specified resource in storage.
     */
    public function update(Request $request, int $id)
    {
        $saleTeam = SaleTeam::find($id);
        $saleTeam->fill($request->all());
        $updates = $saleTeam->last_updates;

        if ($updates == null) {
            $saleTeam->last_updated = collect([["user" => auth()->user()->email, "date" => date("Y-m-d H:i:s")]]);
        } else {
            $updates->push(["user" => auth()->user()->email, "date" => date("Y-m-d H:i:s")]);
            $saleTeam->last_updated = $updates;
        }
        //dd($a);
        $saleTeam->save();
        return $saleTeam;
    }

    /**
     * Remove the specified resource from storage.
     */
    public function destroy($id)
    {
        $saleTeam = SaleTeam::find($id);
        $saleTeam->delete($id);
        return "Data is deleted";
    }
    public function salSurveyDownloadReport(Request $request)
    {
        $s= $request->start_date;
        $e= $request->end_date;

        $query = SaleSurvey::query()
            ->leftJoin('Sites', 'sale_survey.site', '=', 'Sites.Id_Site')
            ->select('sale_survey.*', 'Sites.Platform');

        if ($request->has('start_date') && $request->has('end_date')) {
            $query->whereDate('submitted_date', '>=', $request->start_date)
                ->whereDate('submitted_date', '<=', $request->end_date);
        }
        $data = $query->get();

        $dataArray = [];
        foreach ($data as $item) {
            $dataArray[] = $item->toArray();
        }
       // dd($dataArray);
        // Load the template
        $inputFileName = storage_path('app/templates/saleSurvey.xlsx');
        $TBS = new \clsTinyButStrong;
        $ok = class_exists('clsOpenTBS', true);
        $TBS->OtbsMsExcelExplicitRef = false;
        $TBS->Plugin(\TBS_INSTALL, \OPENTBS_PLUGIN);
        $TBS->LoadTemplate($inputFileName, \OPENTBS_ALREADY_UTF8);

        // Merge data into the template
        $TBS->MergeBlock('a', $dataArray);

        // Output the file for download
        $TBS->Show(OPENTBS_DOWNLOAD, "sale_survey.xlsx");
    }
}
