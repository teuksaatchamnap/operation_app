<?php

namespace App\Http\Controllers;

use App\Imports\Test1Import;
use App\Mail\FA;
use App\Models\sales;
use App\Models\Site;
use App\Models\Technical;
use App\Models\Test2;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Mail;
use Illuminate\Support\Facades\Storage;
use Maatwebsite\Excel\Facades\Excel;
use Carbon\Carbon;
use Carbon\CarbonPeriod;
use Dotenv\Util\Str;

class Test1Controller extends Controller
{
    function import(Request $request)
    {
        if ($request->file('file')) {
            $import =  Excel::import(new Test1Import, request()->file('file'));
            // return collect(head($import))
            //         ->each(function ($row, $key) {
            //             DB::table('test2')
            //                 ->where('site', $row['site'])
            //                 ->update(Arr::except($row, ['site']));
            //         });

            $msg_success = "Data Uploaded Succesfully! ";
            $msg_danger = "Data Uploaded failed! ";
            if ($import) {
                return  $msg_success;
            } else {
                return $msg_danger;
            }
        }
    }

    // public function getEmailAlert(String $permissionName)
    // {
    //     $emails = User::all()
    //         ->filter(function ($user) {
    //             $permissions = json_decode($user->permission, true);
    //             return in_array($permissionName, $permissions ?? []);
    //         })
    //         ->pluck('email')
    //         ->values(); // reindex the collection
    //         foreach ($emails as $email) {
    //            $recipients[] = $email;
    //         }
    //             Mail::to($recipients)->send(new FA($result));
    // }


    public function email()
    {
        $inputFileName = storage_path('app/templates/test.xlsx');
        $inter = Technical::select('*')
            ->limit(100)
            ->get()->toarray();
        $TBS = new \clsTinyButStrong;
        $ok = class_exists('clsOpenTBS', true);
        $TBS->OtbsMsExcelExplicitRef = false;
        $TBS->Plugin(\TBS_INSTALL, \OPENTBS_PLUGIN);
        $TBS->LoadTemplate($inputFileName, \OPENTBS_ALREADY_UTF8);
        $TBS->PlugIn(OPENTBS_SELECT_SHEET, 1);
        $TBS->SetOption("noerr", true);
        $TBS->MergeBlock('a', $inter);
        $TBS->Show(OPENTBS_STRING); // terminate the merging without leaving the script nor to display the result
        $result = $TBS->Source;

        // Save the file to storage
        //Storage::put('public/1.xlsx', $result);

        $recipients = ['chamnap.keo@teuksaat1001.com'];
        Mail::to($recipients)->send(new FA($result));
    }

    public function getData()
    {
        $startYear = '2021-01-01';
        $endYear = '2023-12-31';

        // $data = Test2::select('Id_Site', 'Month')
        // ->whereBetween('Month', [
        //     Carbon::parse('2021-01-01'),
        //     Carbon::parse('2023-12-31'),
        // ])
        //     ->groupBy('Id_Site', 'month')
        //     ->get();
        // return $data; 
        $data = Test2::whereBetween('Month', [$startYear, $endYear])
            ->select('Id_Site', 'Month', 'Total_Sales')
            ->groupBy('Id_Site', 'Month', 'Total_Sales')
            ->get();
        $formattedData = [];
        foreach ($data as $row) {
            $formattedData[$row->Id_Site][$row->Month] = $row->Total_Sales;
        }
        $s = CarbonPeriod::create($startYear, '1 month', $endYear);
        return response()->json([
            "data" => $formattedData,
            "timestamps" => CarbonPeriod::create($startYear, '1 month', $endYear)
        ]);
    }
    public function salesChart1(Request $request)
    {

        $now = now()->format('Y-m-d H:i:s');

        // Fetch data starting from 2025 until now
        $salesData = sales::where('Month', '>=', '2023-01-01 00:00:00') // Start from 2025
            ->where('Month', '<=', $now) // Until now
            ->orderBy('Month', 'asc')
            ->get();

        $groupedData = [];
        foreach ($salesData as $sale) {
            $year = \Carbon\Carbon::parse($sale->Month)->format('Y'); // Extract year
            $month = \Carbon\Carbon::parse($sale->Month)->format('m'); // Extract month

            if (!isset($groupedData[$year])) {
                $groupedData[$year] = [];
            }

            $groupedData[$year][] = [
                'month' => $month,
                'sale_amount' => $sale->Total_Sales
            ];
        }
       
        // Format data for the frontend
        $formattedData = [];
        foreach ($groupedData as $year => $data) {
            $formattedData[] = [
                'year' => $year,
                'data' => $data
            ];
        }

        return response()->json($formattedData);
    }
    public function salesChart($siteId = null)
{
    $allSites = Site::select('Id_Site')
            ->whereNotIn('Platform', ['Dead', 'Stop'])
            ->whereNotIn('Id_Site',['A1','A3','A4','AA1'])
            ->get();
    $query = sales::selectRaw('YEAR(Month) as year, MONTH(Month) as month, SUM(Total_Sales) as total_sales')
    ->where('Month', '>=', '2023-01-01 00:00:00')
    ->groupBy('year', 'month')
    ->orderBy('year', 'asc')
    ->orderBy('month', 'asc');

            // Filter by site if siteId is provided
            if (!empty($siteId)) {
                $query->where('Id_Site', $siteId);
            }

            $salesData = $query->get();

            // Group data by year
            $groupedData = [];
            foreach ($salesData as $sale) {
                $year = $sale->year;  // Use selected year
                $month = $sale->month; // Use selected month

                if (!isset($groupedData[$year])) {
                    $groupedData[$year] = [];
                }

                $groupedData[$year][] = [
                    'month' => $month,
                    'sale_amount' => $sale->total_sales // Use correct alias
                ];
            }
            //dd($groupedData);
            // Format data for the frontend
            $formattedData = [];
            foreach ($groupedData as $year => $data) {
                $formattedData[] = [
                    'year' => $year,
                    'data' => $data
                ];
            }

            return response()->json([
                'data' => $formattedData,
                'sites' => $allSites->pluck('Id_Site')
            ]);

            } 
}
