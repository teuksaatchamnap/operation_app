<?php

namespace App\Http\Controllers;

use App\Models\FlashReport;
use App\Models\Sample;
use App\Models\Site;
use App\Models\Technical;
use App\Models\WeeklyFlashReport;
use Illuminate\Http\Request;

class FlashReportController extends Controller
{
    /**
     * Display a listing of the resource.
     */
    public function index(Request $request)
    {
        $request->validate([
            'month' => 'required|numeric',
            'year' => 'required|numeric',
            'report_type'=> 'required|string'
        ]);
        if($request->report_type =='Weekly_Flash_report')
        {

            return [
                "samples" => WeeklyFlashReport::whereMonth("Month", "=", $request->month)
                    ->whereYear("Month", "=", $request->year)
                    ->where("Week","=",$request->week)
                    ->orderBy("Id_Site")
                    ->orderBy("Month", "desc")
                    ->get()
                    ->groupBy("Id_Site"),
                "sites" => Site::select("Id_Site", "Platform")
                    ->where("Platform", "!=", "Dead")
                    ->orderBy("Id_Site")
                    ->get()
                    ->groupBy("Platform")->sortKeys(),
            ];
        }
        else if ($request->report_type =='Mid_Flash_Report') 
        {
            return [
                "samples" => FlashReport::whereMonth("Month", "=", $request->month)
                    ->whereYear("Month", "=", $request->year)
                    ->where("Period","=","MidMonth")
                    ->orderBy("Id_Site")
                    ->orderBy("Month", "desc")
                    ->get()
                    ->groupBy("Id_Site"),
                "sites" => Site::select("Id_Site", "Platform")
                    ->where("Platform", "!=", "Dead")
                    ->orderBy("Id_Site")
                    ->get()
                    ->groupBy("Platform")->sortKeys(),
            ];
        }
        else{
            return [
                "samples" => FlashReport::whereMonth("Month", "=", $request->month)
                    ->whereYear("Month", "=", $request->year)
                    ->where("Period","=","EndMonth")
                    ->orderBy("Id_Site")
                    ->orderBy("Month", "desc")
                    ->get()
                    ->groupBy("Id_Site"),
                "sites" => Site::select("Id_Site", "Platform")
                    ->where("Platform", "!=", "Dead")
                    ->orderBy("Id_Site")
                    ->get()
                    ->groupBy("Platform")->sortKeys(),
            ];
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
    public function detail( Request $request)
    {
        return FlashReport::where("Code_Flash_report", "=", $request->id)->first();
    
    }
    public function show(Request $request,FlashReport $flashReport)
    {
        // $request->validate([
        //     'receiveDate' => 'required|date_format:Y-m',
        //     'report_type'=> 'required|string'
        // ]);
        if($request->report_type =='Weekly_Flash_report')
        {
            return WeeklyFlashReport::whereMonth('Month', date('m', strtotime($request->receiveDate)))
            ->whereYear('Month', date('Y', strtotime($request->receiveDate)))
            ->get();
        }
        else if ($request->report_type =='Mid_Flash_Report') 
        {
            $result = FlashReport::with("site:Id_Site,Platform,Advisor")
                ->whereHas("site")
                ->where("Period","=","MidMonth")
                ->whereMonth('Month', date('m', strtotime($request->receiveDate)))
                ->whereYear('Month', date('Y', strtotime($request->receiveDate)))
                ->orderBy('Month', 'desc')
                ->get();
            return $result;
        }
        else{
            $result = FlashReport::with("site:Id_Site,Platform,Advisor")
            ->whereHas("site")
            // ->where("Platform", "!=", "Stop")
            // ->where("Platform", "!=", "Dead")
            ->where("Period","=","EndMonth")
            ->whereMonth('Month', date('m', strtotime($request->receiveDate)))
            ->whereYear('Month', date('Y', strtotime($request->receiveDate)))
            ->orderBy('Month', 'desc')
            ->get();
                return $result;
        }
    }

    /**
     * Update the specified resource in storage.
     */
    public function update(Request $request, int $Code_Flash_report)
    {
      // dd($request->Code_Flash_report);
        $record = FlashReport::findOrFail($request->Code_Flash_report);

            // Update only the provided fields
            $record->update($request->only(['Code_Flash_report', 'Id_Site','Month','Number_jugs_village','Number_jugs_school']));
            // $record->update([
            //     'Code_Flash_report' => $request->Code_Flash_report,
            //     'Id_Site' => $request->Id_Site,
            //     'Month' => $request->Month,
            //     'Number_jugs_village'=>$request->Number_jugs_village,
            //     'Number_jugs_school' => $request->Number_jugs_school
            // ]);

            return response()->json(['message' => 'Record updated successfully.'], 200);

    
    }

    /**
     * Remove the specified resource from storage.
     */
    public function destroy(FlashReport $flashReport)
    {
        //
    }
}
