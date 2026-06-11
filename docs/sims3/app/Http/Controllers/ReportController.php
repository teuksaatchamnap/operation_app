<?php

namespace App\Http\Controllers;

use App\Models\Assessment;
use App\Models\Beneficiaries;
use App\Models\Consumable;
use App\Models\DailySales;
use App\Models\Expense;
use App\Models\Indicator;
use App\Models\Rountine;
use App\Models\sales;
use App\Models\Sample;
use App\Models\Site;
use Illuminate\Http\Request;
use Illuminate\Support\Carbon;
use Illuminate\Support\Collection;
use Illuminate\Support\Facades\DB;

class ReportController extends Controller
{
    public function sites()
    {
        return Site::select('Id_Site', 'Platform')->get();
    }

    public function  incomeDetails($siteId)
    {
        $startDate = now()->subYears(2)->startOfYear();
        $endDate   = now()->endOfMonth();
        $sales = Sales::where('Id_Site', $siteId)
            ->whereBetween('Month', [$startDate, $endDate])
            ->select(
                DB::raw('YEAR(Month) as year'),
                DB::raw('MONTH(Month) as month'),
                DB::raw('CEILING(SUM(Total_Income)) as total_income')
            )
            ->groupBy('year', 'month')
            ->get();

        $expenses = Expense::where('Id_Site', $siteId)
            ->whereBetween('Month', [$startDate, $endDate])
            ->select(
                DB::raw('YEAR(Month) as year'),
                DB::raw('MONTH(Month) as month'),
                'Category_expenses',
                DB::raw('CEILING(SUM(Amount_expenses)) as amount'),
                DB::raw("CEILING(SUM(CASE 
            WHEN Ref_expenses IN ('fix_salary_entrepreneurs', 'variable_salary_entrepreneurs') 
            THEN Amount_expenses ELSE 0 END)) as entre_salary")
            )
            ->groupBy('year', 'month', 'Category_expenses')
            ->get();

        $salesMap = [];
        foreach ($sales as $row) {
            $salesMap[$row->year][$row->month] = $row->total_income;
        }

        // Build expense map with entrepreneur salary
        $expenseMap = [];
        foreach ($expenses as $row) {
            $year = $row->year;
            $month = $row->month;
            $category = $row->Category_expenses;

            if (!isset($expenseMap[$year])) {
                $expenseMap[$year] = [];
            }
            if (!isset($expenseMap[$year][$month])) {
                $expenseMap[$year][$month] = [];
            }

            $expenseMap[$year][$month][$category] = $row->amount;

            if ($category === 'salary') {
                $expenseMap[$year][$month]['entre_salary'] = $row->entre_salary;
            }
        }

        // Categories including entrepreneur salary
        $categories = [
            'contribution',
            'salary',
            'delivery',
            //'investment', // commented out as per your code
            'maintenance',
            'other',
            'production',
            'entre_salary',
        ];

        $result = [];

        for ($year = now()->year; $year >= now()->year - 2; $year--) {
            for ($month = 1; $month <= 12; $month++) {

                $income = $salesMap[$year][$month] ?? 0;
                $expenseByCategory = $expenseMap[$year][$month] ?? [];

                $expenseFinal = [];
                $totalExpense = 0;
                $entreSalary = 0;

                foreach ($categories as $cat) {
                    $value = $expenseByCategory[$cat] ?? 0;
                    $expenseFinal[$cat] = $value;

                    if ($cat === 'entre_salary') {
                        $entreSalary = $value; // store entrepreneur salary separately
                    } elseif ($cat !== 'entre_salary') {
                        $totalExpense += $value;
                    }
                }

                if ($income === 0 && $totalExpense === 0) {
                    continue;
                }

                $result[$year][$month] = [
                    'income'             => $income,
                    'expenses'           => $expenseFinal,
                    'total_expense'      => $totalExpense,
                    'pnl'                => $income - $totalExpense,
                    'pnl_plus_entre_salary' => ($income - $totalExpense) + $entreSalary,
                ];
            }
        }

        $finalResult = [];

        foreach ($result as $year => $months) {
            ksort($months); // sort months ascending

            $finalResult[$year] = [];

            foreach ($months as $monthNumber => $data) {
                $monthName = Carbon::create()->month($monthNumber)->format('M');
                $finalResult[$year][] = array_merge(['month' => $monthName], $data);
            }
        }

        return response()->json([
            'site_id' => $siteId,
            'currency' => 'USD',
            'data' => $finalResult,
        ]);
    }

    public function debtDetails(Request $request, $siteId)
    {
        $refExpensesList = [
            'debt',
            'consumable_teuk_saat_1001',
            'bottle_from_teuksaat_1001',
            'technical_intervention',
            'water_quality_intervention',
            'upload_electricity_bill',
            'delivery_program',
            'water quality alert',
            'technical intervention',
            'WinS_invoice',
            'delivery_program_fee',
            'bottle_invoice',
            'stock_ts',
            'entrepreneur_contribution'
        ];
        $currentDate = Carbon::now(); // 2025-12-23
        $currentYear = $currentDate->year;
        $previousYear = $currentYear - 1;

        // Get the last 2 years of data
        $startDate = Carbon::create($previousYear, 1, 1); // Start from Jan of previous year
        $endDate = $currentDate->endOfMonth(); // End at current month

        // Get data grouped by year and month
        $monthlyData = Expense::select(
            DB::raw('YEAR(Month) as year'),
            DB::raw('MONTH(Month) as month_number'),
            DB::raw('DATE_FORMAT(Month, "%b") as month_name'), // Jan, Feb, etc
            DB::raw('COALESCE(SUM(COALESCE(Amount_expenses, 0) - COALESCE(Paid, 0)), 0) AS total')
        )
            ->where('Id_Site', $siteId)
            ->whereIn('Ref_expenses', $refExpensesList)
            ->whereBetween('Month', [$startDate, $endDate])
            ->groupBy('year', 'month_number', 'month_name')
            ->orderBy('year', 'desc')
            ->orderBy('month_number') // Sort by month number
            ->get()
            ->groupBy('year')
            ->map(function ($yearData) {
                return $yearData->pluck('total', 'month_name');
            })
            ->toArray();
        return response()->json($monthlyData);
    }

    public function assessmentDetail(Request $request, $site)
    {
        $type = $request->query('type');

        return $type === 'assessment' ?
            Assessment::select('id', 'site', 'date_form', 'technician', 'first_site_assessment', 'which_part_do_you_want_to_modify', 'main_source_of_water', 'main_source_of_electricity')
            ->where('site', $site)->get() :
            Rountine::select(
                'id',
                'site',
                'date',
                'technician',
                'condition_of_raw_water_tank',
                'condition_of_ac_filter_tank',
                'condition_of_sand_filter_tank',
                'condition_of_resin_filter_tank',
                'condition_of_clear_water_tank',
                'frequency_of_the_cip_on_pipes'
            )
            ->where('site', $site)->get();
    }

    public function siteReport($siteId, Request $request)
    {
        $month = $request->query('month');
        $refExpensesList = [
            'debt',
            'consumable_teuk_saat_1001',
            'bottle_from_teuksaat_1001',
            'technical_intervention',
            'water_quality_intervention',
            'upload_electricity_bill',
            'delivery_program',
            'water quality alert',
            'technical intervention',
            'WinS_invoice',
            'delivery_program_fee',
            'bottle_invoice',
            'stock_ts',
            'entrepreneur_contribution'
        ];
        $currentDate = Carbon::parse($month . '-01');
        $currentEndMonth = Carbon::parse($month . '-01')->endOfMonth();
        $startDateYear   = $currentEndMonth->copy()->startOfYear();
        $startN1 = $currentDate->copy()->subYear()->startOfYear();
        $endN1   = $currentDate->copy()->subYear()->endOfMonth();
        $previousMonth = $currentDate->copy()->subMonth();
        /// check this . when ready, move up this comment back
        //$currentDate = now()->subMonths(now()->day >= 15 ? 1 : 2)->startOfMonth()->format('Y-m-d');
        $startDate = Carbon::now()->startOfYear(); // 2025-01-01 00:00:00
        $dateStartHistoric = Carbon::now()->subYears(4); // historic sales start date
        // --- Sites ---
        $siteDetails = Site::select(
            'Id_Site',
            'Platform',
            'Advisor',
            'Number_Population',
            'Number_Households',
            'Entrepreneur_English_Name',
            'Date_start_working',
            'Last_Tier'
        )
            ->where('Id_Site', $siteId)
            ->first();

        // --- Sales ---
        $sales = sales::select(
            'Id_Site',
            'Total_Income',
            DB::raw('CEILING(Total_sales - Bottle_Sales) as total_excluding_bottles'),
            'Hod_Sales',
            'Hod_Price',
            'Shopkeeper_Sales',
            'Shopkeeper_Price',
            'WiS_Sales',
            'WiS_Price',
            'Onsite_Sales',
            'Onsite_Price',
            'Free_Sales',
            'Number_open_days',
            'WiS_Income',
            DB::raw('CEILING((Total_Sales - Bottle_Sales)/Number_open_days) as monthly_avg_sales_per_day'),
            DB::raw('CEILING((Total_Sales - Bottle_Sales - WiS_Sales)/Number_open_days) as monthly_avg_non_wis_sales_per_day')
        )
            ->where('Month', $currentDate)
            ->where('Id_Site', $siteId)
            ->first();

        $salesM1 = sales::select('Total_Income', 'WiS_Income')
            ->where('Month', Carbon::parse($currentDate)->subMonth()->format('Y-m-01'))
            ->where('Id_Site', $siteId)
            ->first();

        $salesYtd = sales::select(
            DB::raw('CEILING(SUM(Total_Income)) as Total_Income'),
            DB::raw('CEILING(SUM(WiS_Income)) as WiS_Income'),
            DB::raw('CEILING(SUM(Total_sales - Bottle_Sales - WiS_Sales) / NULLIF(SUM(Number_open_days),0)) as avg_sales_per_day')
        )
            ->where('Id_Site', $siteId)
            ->whereBetween('Month', [$startDateYear, $currentEndMonth])
            ->groupBy('Id_Site')
            ->first();



        $salesYtdN1 = sales::select(
            DB::raw('CEILING(SUM(Total_Income)) as Total_Income'),
            DB::raw('CEILING(SUM(WiS_Income)) as WiS_Income')
        )
            ->where('Id_Site', $siteId)
            ->whereBetween('Month', [$startN1, $endN1])
            ->first();


        // --- Beneficiaries ---
        $beneficiaries = Beneficiaries::select('Beneficiaries')
            ->where('Month', $currentDate)
            ->where('Id_Site', $siteId)
            // ->get(); return as collection or array
            ->first(); // return as single record 
        // Finish this query
        // --- Indicators ---
        $indicatorsOp = Indicator::select('Number_of_Operator', 'Water_Consume')
            ->where('Month', $currentDate)
            ->where('Id_Site', $siteId)
            ->first();
        // --- WinS Average ---
        $winSAvg = DailySales::select(DB::raw('CEILING(AVG(WiS_Sales)) as avg_wis_sales'))
            ->whereBetween('Month', [$currentDate, Carbon::parse($currentDate)->addMonth()])
            ->where('Id_Site', $siteId)
            ->get();
        // Finish this query
        // --- Historic Sales ---
        $historicSales = sales::select(
            'Month',
            DB::raw('CEILING((Total_Sales - Bottle_Sales - WiS_Sales) / Number_open_days) as net_sales'),
            'Number_open_days'
        )
            ->whereBetween('Month', [$dateStartHistoric, $currentDate])
            ->where('Id_Site', $siteId)
            ->get();
        // --- Debt ---
        $lastMonth = Carbon::parse($currentDate->copy()->subMonth()->format('Y-m'));
        $debt = Expense::select(
            DB::raw('COALESCE(SUM(COALESCE(Amount_expenses, 0) - COALESCE(Paid, 0)), 0) AS Total_Net_Amount'),
        )
            ->whereYear('Month', $currentDate->year)
            ->whereMonth('Month', $currentDate->month)
            ->where('Id_Site', $siteId)
            ->whereIn('Ref_expenses', $refExpensesList)
            ->first();

        if (!$debt) {
            $debt = Expense::select(
                DB::raw('COALESCE(SUM(COALESCE(Amount_expenses, 0) - COALESCE(Paid, 0)), 0) AS Total_Net_Amount'),
                // DB::raw('COALESCE(SUM(COALESCE(Amount_expenses, 0) - COALESCE(Paid, 0)), 0) / 4070 AS Final_Result')
            )
                ->whereYear('Month', $lastMonth->year)
                ->whereMonth('Month', $lastMonth->month)
                ->where('Id_Site', $siteId)
                ->whereIn('Ref_expenses', $refExpensesList)
                ->first();
        }
        // --- Bottles ---
        $startDate = Carbon::now()->subYear()->startOfYear(); // Last year Jan 1
        $endDate = Carbon::now()->subYear()->endOfYear();     // Last year Dec 31
        $bottleCode = ['401001', '401002'];
        $bottlesYtd = Consumable::select(DB::raw('CEILING(SUM(Number_Item)) as total_bottles'))
            ->whereBetween('Month', [$startDate, $currentDate])
            ->whereIn('Item', $bottleCode)
            ->where('Id_Site', $siteId)
            ->groupBy('Id_Site')
            ->first();

        $bottlesN1 = Consumable::select(DB::raw('CEILING(SUM(Number_Item)) as total_bottles'))
            ->whereBetween('Month', [$startDate, $endDate])
            ->whereIn('Item', $bottleCode)
            ->where('Id_Site', $siteId)
            ->groupBy('Id_Site')
            ->first();

        $currentMonthExpenses = Expense::where('Id_Site', $siteId)
            ->where('Month', $currentDate)
            ->groupBy('Category_expenses')
            ->selectRaw('Category_expenses, CEILING(SUM(Amount_expenses)/4000) as total_expenses')
            ->get();
        $averageByCategory = Expense::where('Month', $currentDate)
            ->groupBy('Category_expenses')
            ->selectRaw('Category_expenses, CEILING(AVG(Amount_expenses)/4000) as average_expenses, COUNT(DISTINCT Id_Site) as site_count')
            ->get();

        // --- Expenses (Current Month) ---
        $expenses = Expense::where('Id_Site', $siteId)
            ->where('Month', $currentDate)
            ->select(
                DB::raw("
            CASE 
                WHEN Ref_expenses IN ('fix_salary_entrepreneurs','variable_salary_entrepreneurs') THEN 'salary_entrepreneur'
                WHEN Ref_expenses IN ('fix_salary_operators','variable_salary_operators') THEN 'salary_operator'
                ELSE Category_expenses
            END AS expense_category
        "),
                DB::raw('CEILING(SUM(Amount_expenses)) as total_expenses')
            )
            ->groupBy('expense_category')
            ->orderBy('expense_category')
            ->get();
        $salaryTotal = $expenses->whereIn('expense_category', ['salary_entrepreneur', 'salary_operator'])->sum('total_expenses');

        // Add as a new item
        $expenses->push((object)[
            'expense_category' => 'salary_total',
            'total_expenses' => $salaryTotal
        ]);
        // --- Expenses M-1 ---
        $expensesM1 = Expense::where('Id_Site', $siteId)
            ->where('Month', Carbon::parse($currentDate)->subMonth()->format('Y-m-01'))
            ->select(
                DB::raw("
            CASE 
                WHEN Ref_expenses IN ('fix_salary_entrepreneurs','variable_salary_entrepreneurs') THEN 'salary_entrepreneur'
                WHEN Ref_expenses IN ('fix_salary_operators','variable_salary_operators') THEN 'salary_operator'
                ELSE Category_expenses
            END AS expense_category
        "),
                DB::raw('CEILING(SUM(Amount_expenses)) as total_expenses')
            )
            ->groupBy('expense_category')
            ->orderBy('expense_category')
            ->get();
        $salaryTotalM1 = $expensesM1->whereIn('expense_category', ['salary_entrepreneur', 'salary_operator'])->sum('total_expenses');

        // Add as a new item
        $expensesM1->push((object)[
            'expense_category' => 'salary_total',
            'total_expenses' => $salaryTotalM1
        ]);
        // --- Expenses YTD ---
        $expensesYTD = Expense::where('Id_Site', $siteId)
            //->whereBetween('Month', [Carbon::create(now()->year, 1, 1), $currentDate])
            ->whereBetween('Month', [$startDateYear, $currentEndMonth])
            ->select(
                DB::raw("
            CASE 
                WHEN Ref_expenses IN ('fix_salary_entrepreneurs','variable_salary_entrepreneurs') THEN 'salary_entrepreneur'
                WHEN Ref_expenses IN ('fix_salary_operators','variable_salary_operators') THEN 'salary_operator'
                ELSE Category_expenses
            END AS expense_category
        "),
                DB::raw('CEILING(SUM(Amount_expenses)) as total_expenses')
            )
            ->groupBy('expense_category')
            ->orderBy('expense_category')
            ->get();
        $salaryTotalYTD = $expensesYTD->whereIn('expense_category', ['salary_entrepreneur', 'salary_operator'])->sum('total_expenses');

        // Add as a new item
        $expensesYTD->push((object)[
            'expense_category' => 'salary_total',
            'total_expenses' => $salaryTotalYTD
        ]);
        // --- Expenses YTD N-1 ---
        $expensesYTD_N1 = Expense::where('Id_Site', $siteId)
            ->whereBetween('Month', [$startN1, $endN1])
            //->whereBetween('Month', [Carbon::create(now()->year - 1, 1, 1), Carbon::parse($currentDate)->subYear()])
            ->select(
                DB::raw("
            CASE 
                WHEN Ref_expenses IN ('fix_salary_entrepreneurs','variable_salary_entrepreneurs') THEN 'salary_entrepreneur'
                WHEN Ref_expenses IN ('fix_salary_operators','variable_salary_operators') THEN 'salary_operator'
                ELSE Category_expenses
            END AS expense_category
        "),
                DB::raw('CEILING(SUM(Amount_expenses)) as total_expenses')
            )
            ->groupBy('expense_category')
            ->orderBy('expense_category')
            ->get();
        $salaryTotalYTD_N1 = $expensesYTD_N1->whereIn('expense_category', ['salary_entrepreneur', 'salary_operator'])->sum('total_expenses');

        // Add as a new item
        $expensesYTD_N1->push((object)[
            'expense_category' => 'salary_total',
            'total_expenses' => $salaryTotalYTD_N1
        ]);
        // --- Return JSON ---
        return response()->json([
            'month' => $currentDate,
            'siteDetails' => $siteDetails,
            'sales' => $sales,
            'salesM1' => $salesM1,
            'salesYtd' => $salesYtd,
            'salesYtdN1' => $salesYtdN1,
            'beneficiaries' => $beneficiaries,
            'indicatorsOp' => $indicatorsOp,
            'winSAvg' => $winSAvg,
            'historicSales' => $historicSales,
            'debt' => $debt,
            'bottlesYtd' => $bottlesYtd,
            'bottlesN1' => $bottlesN1,
            'expenses' => $expenses,
            'expensesM1' => $expensesM1,
            'expensesYTD' => $expensesYTD,
            'expensesYTD_N1' => $expensesYTD_N1,
            'currentMonthExpenses' => $currentMonthExpenses,
            'averageByCategory' => $averageByCategory,
        ]);
    }

    public function assessmentAnalysis($siteId, Request $request)
    {
        $processTemplate =
            [
                [
                    "process" => "ចម្រោះខ្សាច់/Sand filter",
                    "fields" => [
                        "Type"     => "type_of_sand_filter_tank",
                        "Volume"   => "sand_filter_tank_v_liter",
                        "Height"   => "sand_filter_tank_h_cm",
                        "Diameter" => "sand_filter_tank_d_cm",
                    ]
                ],
                [
                    "process" => "ចម្រោះធ្យូង/Activated Carbon filter",
                    "fields" => [
                        "Type"     => "type_of_ac_filter_tank",
                        "Volume"   => "ac_filter_tank_v_liter",
                        "Height"   => "ac_filter_tank_h_cm",
                        "Diameter" => "ac_filter_tank_d_cm",
                    ]
                ],
                [
                    "process" => "ចម្ររ៉េស៊ីន/Resin filter",
                    "fields" => [
                        "Type"     => "type_of_resin_filter_tank",
                        "Volume"   => "resin_filter_tank_v_liter",
                        "Height"   => "resin_filter_tank_h_cm",
                        "Diameter" => "resin_filter_tank_d_cm",
                    ]
                ],
                [
                    "process" => "ចម្រោះ R.O/Reverse Osmose",
                    "fields" => [
                        "Type"     => "reverse_osmose_pump",
                        "Volume"   => "reverse_osmose_pump_power",
                        "Height"   => "reverse_osmose_pump_height_hmax",
                        "Diameter" => "reverse_osmose_pump_flow_qmax",
                    ]
                ],
                [
                    "process" => "ចម្រោះ UF/Ultrafiltration",
                    "fields" => [
                        "Type"     => "ultrafiltration",
                        "Volume"   => "",
                        "Height"   => "",
                        "Diameter" => "",
                    ]
                ],
                [
                    "process" => "ចម្រោះសេរ៉ាម៉ិច/Ceramic filter",
                    "fields" => [
                        "Type"     => "",
                        "Volume"   => "",
                        "Height"   => "",
                        "Diameter" => "",
                    ]
                ],
                [
                    "process" => "ធុងទឹកថ្លា/Clear water tank",
                    "fields" => [
                        "Type"     => "type_of_clear_water_tank",
                        "Volume"   => "clear_water_tank_v_liter",
                        "Height"   => "clear_water_tank_h_cm",
                        "Diameter" => "clear_water_tank_d_cm",
                    ]
                ],
                [
                    "process" => "ធុងទឹកឆៅ/Raw water tank",
                    "fields" => [
                        "Type"     => "type_of_raw_water_tank",
                        "Volume"   => "raw_water_tank_v_liter",
                        "Height"   => "raw_water_tank_h_cm",
                        "Diameter" => "raw_water_tank_d_cm",
                    ]
                ],
                [
                    "process" => "AFM Filter",
                    "fields" => [
                        "Type"     => "type_of_afm",
                        "Volume"   => "afm_v_iter",
                        "Height"   => "afm_h_cm",
                        "Diameter" => "afm_d_cm",
                    ]
                ],
                [
                    "process" => "ZMag zeolite",
                    "fields" => [
                        "Type"     => "type_of_Zmag",
                        "Volume"   => "zmag_v_iter",
                        "Height"   => "zmag_h_cm",
                        "Diameter" => "zmag_d_cm",
                    ]
                ],
                [
                    "process" => "ប្រភេទនៃធុងចម្រោះខ្សាច់ & zmax/ type_of_sand_and_zmax",
                    "fields" => [
                        "Type"     => "type_of_sand_filter_and_Zmag_tank",
                        "Volume"   => "sand_filter_and_zmag_v_iter",
                        "Height"   => "sand_filter_and_zmag_h_cm",
                        "Diameter" => "sand_filter_and_zmag_d_cm",
                    ]
                ],
            ];

        $month = $request->query('month'); // e.g. "2025-09"
        if (!$month) {
            return response()->json([
                'dataThisMonth' => [],
                'dataYTD' => [],
            ]);
        }

        $year = date('Y', strtotime($month));
        $monthNum = date('m', strtotime($month));
        //$currentDate = Carbon::now()->startOfMonth();
        $currentDate = Carbon::now()->format('2025-07-01');
        $siteDetails = Site::select(
            'Id_Site',
            'Platform',
            'Entrepreneur_English_Name',
            'Date_start_working',
            'technician_site',
        )
            ->where('Id_Site', $siteId)
            ->first();
        $sales = sales::select(
            'Id_Site',
            DB::raw('(Total_Sales - Bottle_Sales - WiS_Sales)/Number_open_days as monthly_avg_non_wis_sales_per_day')
        )
            ->where('Month', $currentDate)
            ->where('Id_Site', $siteId)
            ->first();
        $salesYtd = sales::select(
            DB::raw('SUM(Total_sales - Bottle_Sales - WiS_Sales)/SUM(Number_open_days) as avg_sales_per_day')
        )
            ->whereBetween('Month', [Carbon::create(now()->year, 1, 1), $currentDate])
            ->where('Id_Site', $siteId)
            ->groupBy('Id_Site')
            ->first();
        $assessmentRecord = Assessment::where('site', $siteId)
            ->orderBy('date_form', 'desc')
            ->first();
        $attributes = $assessmentRecord->getAttributes();

        $processGroups = [];

        for ($i = 1; $i <= 7; $i++) {

            $processName = $attributes["pre_treatment_process_$i"] ?? null;
            if (!$processName) continue;

            // Find the template for this process
            $template = collect($processTemplate)->firstWhere('process', $processName);
            if (!$template) continue;

            $filled = [];

            // Replace each mapped field with its real value from DB
            foreach ($template['fields'] as $label => $dbFieldName) {
                $filled[$label] = $attributes[$dbFieldName] ?? null;
            }

            $processGroups[] = [
                'step'    => $i,
                'process' => $processName,
                'fields'  => $filled
            ];
        }

        $routine = Rountine::where('site', $siteId)
            ->orderBy('date', 'desc')
            ->first();

        $sample = Sample::join('Sites', 'samples.site', '=', 'Sites.Id_Site')
            ->whereYear('samples.sample_date', $year)
            ->whereMonth('samples.sample_date', $monthNum)
            ->where('samples.site', $siteId)
            ->whereIn('samples.type', ['Monthly Test', 'WQ Alert'])
            ->selectRaw('
                    COUNT(DISTINCT CASE WHEN samples.escherichia > 0 THEN samples.site END) as ecoli_alert,
                    COUNT(DISTINCT CASE WHEN samples.total_coliform > 0 THEN samples.site END) as coliform_alert
            ')
            ->first();

        $sampleYTD = Sample::whereYear('sample_date', $year)
            ->where('site', $siteId)
            ->whereIn('type', ['Monthly Test', 'WQ Alert'])
            ->selectRaw("
                COUNT(CASE WHEN escherichia > 0 THEN 1 END) AS ecoli_alert_ytd,
                COUNT(CASE WHEN total_coliform > 0 THEN 1 END) AS coliform_alert_ytd
            ")
            ->first();

        $alumiTubi = Sample::select('aluminium', 'turbidity')
            ->whereYear('sample_date', $year)
            ->where('site', $siteId)
            ->where('type', ['Monthly Test'])
            ->get()
            ->groupBy(function ($item) {
                return \Carbon\Carbon::parse($item->sample_date)->format('M'); // Returns Jan, Feb, etc.
            });

        $contamination = Sample::select(
            DB::raw("DATE_FORMAT(sample_date,'%b') AS month"),
            DB::raw("DATE_FORMAT(sample_date,'%m') AS month_num"),
            'contamination_level_machine',
            'contamination_level_bottle'
        )
            ->whereYear('sample_date', $year)
            ->where('site', $siteId)
            ->where('type', 'Monthly Test')
            ->orderBy('sample_date')
            ->get()
            ->groupBy('month')
            ->sortBy(function ($items, $month) {
                $monthNumbers = [
                    'Jan' => 1,
                    'Feb' => 2,
                    'Mar' => 3,
                    'Apr' => 4,
                    'May' => 5,
                    'Jun' => 6,
                    'Jul' => 7,
                    'Aug' => 8,
                    'Sep' => 9,
                    'Oct' => 10,
                    'Nov' => 11,
                    'Dec' => 12
                ];
                return $monthNumbers[$month] ?? 13;
            })
            ->map(function ($items) {
                // Because one test per month, get first item contamination levels
                $item = $items->first();
                return [
                    'machine' => (int) $item->contamination_level_machine,
                    'bottle' => (int) $item->contamination_level_bottle,
                ];
            });


        $assessmentYTD = Assessment::where('site', $siteId)
            ->select('id', 'site', 'date_form', 'technician', 'first_site_assessment', 'which_part_do_you_want_to_modify', 'main_source_of_water', 'main_source_of_electricity')
            ->get();
        $countYTD = $assessmentYTD->count();

        $routineYTD = Rountine::where('site', $siteId)
            ->select(
                'id',
                'site',
                'date',
                'technician',
                'condition_of_raw_water_tank',
                'condition_of_ac_filter_tank',
                'condition_of_sand_filter_tank',
                'condition_of_resin_filter_tank',
                'condition_of_clear_water_tank',
                'frequency_of_the_cip_on_pipes'
            )
            ->get();
        $routineCountYTD = $routineYTD->count();

        $list = [
            'ត្រួតពិនិត្យស្ថានីយ/Site Inspection',
            'បញ្ហាប្រភពអគ្គិសនី&ប្រភពទឹក/Electricity and Water Source',
            'បញ្ហាប្រព័ន្ធយូវី/UV System Problem',
            'ប្រព័ន្ធសូឡារ/Solar System',
            'បញ្ហាចម្រោះបឋម/Pre-treatment Problem',
            'ការសំអាត/Pre-treatment',
            'បញ្ហាម៉ូទ័រ/Motor',
            'បណ្តុះបណ្តាល/Training',
            'ប្រពន្ធ័ចំរោះ/Micro filter',
            'ប្រពន្ធភ្លើង/Grid'
        ];

        return response()->json([
            'month' => $currentDate,
            'siteDetails' => $siteDetails,
            'sales' => $sales,
            'salesYtd' => $salesYtd,
            'assessmentProcess' => $processGroups,
            'assessment' => $assessmentRecord,
            'routine' => $routine,
            'sample' => $sample,
            'sampleYTD' => $sampleYTD,
            'assessmentYTD' => $assessmentYTD,
            'assessmentCountYTD' => $countYTD,
            'routineYTD' => $routineYTD,
            'routineCountYTD' => $routineCountYTD,
            'alumiTubi' => $alumiTubi,
            'contamination' => $contamination,
        ]);
    }

    public function WQReport(Request $request)
    {
        $month = $request->query('month'); // e.g. "2025-09"
        if (!$month) {
            return response()->json([
                'dataThisMonth' => [],
                'dataYTD' => [],
            ]);
        }

        $year = date('Y', strtotime($month));
        $monthNum = date('m', strtotime($month));

        // data this month to show in Map
        $dataThisMonth = Sample::join('Sites', 'samples.site', '=', 'Sites.Id_Site')
            ->whereNotNull('samples.site')
            ->where('samples.type', 'Monthly Test')
            ->whereYear('samples.sample_date', $year)
            ->whereMonth('samples.sample_date', $monthNum)
            ->select([
                'Sites.Id_Site',
                'Sites.Latitude as latitude',
                'Sites.Longitude as longitude',
                'Sites.Platform as platform',
                'samples.contamination_level_machine as machine_contamination_level',
                'samples.contamination_level_bottle as bottle_contamination'
            ])
            ->get()
            ->toArray();
        // End of data this month for map

        // --- DATA YEAR-TO-DATE (grouped) ---
        $currentMonth = Carbon::now()->month;
        $ytdSamples = Sample::with('siteRelation')
            ->select('site', 'contamination_level_machine', 'contamination_level_bottle', 'sample_date', 'type')
            ->whereNotNull('site')
            ->where('type', 'Monthly Test')
            ->whereYear('sample_date', $year)
            ->whereMonth('sample_date', '<=', $monthNum)
            ->get()
            ->map(function ($sample) {
                $site = $sample->siteRelation;
                return [
                    'Id_Site' => $site?->Id_Site,
                    'platform' => $site?->Platform,
                    'machine_contamination_level' => $sample->contamination_level_machine,
                    'bottle_contamination' => $sample->contamination_level_bottle,
                ];
            })
            ->filter(fn($item) => $item['platform']) // make sure platform exists
            ->values();
        // ---- Identify high contamination sites (3 or more level 2 or 3) ----
        $highContaminationSites = [];

        foreach ($ytdSamples as $sample) {
            $siteId = $sample['Id_Site'] ?? null;
            $platform = $sample['platform'] ?? null;

            if (!$siteId) continue; // skip if no site

            if (!isset($highContaminationSites[$siteId])) {
                $highContaminationSites[$siteId] = [
                    'platform' => $platform,
                    'machine' => ['level2' => 0, 'level3' => 0],
                    'bottle' => ['level2' => 0, 'level3' => 0],
                ];
            }

            // increment machine levels
            $machineLevel = (int) $sample['machine_contamination_level'];
            if ($machineLevel == 2) $highContaminationSites[$siteId]['machine']['level2']++;
            if ($machineLevel == 3) $highContaminationSites[$siteId]['machine']['level3']++;

            // increment bottle levels
            $bottleLevel = (int) $sample['bottle_contamination'];
            if ($bottleLevel == 2) $highContaminationSites[$siteId]['bottle']['level2']++;
            if ($bottleLevel == 3) $highContaminationSites[$siteId]['bottle']['level3']++;
        }

        // Filter only sites where level2 or level3 for any type is >= 3
        $highContaminationSites = collect($highContaminationSites)
            ->map(function ($item, $siteId) {
                $keep = false;
                foreach (['machine', 'bottle'] as $type) {
                    foreach (['level2', 'level3'] as $lvl) {
                        if ($item[$type][$lvl] >= 3) {
                            $keep = true;
                        }
                    }
                }
                if ($keep) {
                    return array_merge(['Id_Site' => $siteId], $item);
                }
                return null;
            })
            ->filter()
            ->values();
        // End of high contamination sites
        // --- 1. Result resultMonthlyTest in month Where type = 'Monthly Test' ---
        $resultMonthlyTest = Sample::join('Sites', 'samples.site', '=', 'Sites.Id_Site')
            ->whereYear('samples.sample_date', $year)
            ->whereMonth('samples.sample_date', $monthNum)
            ->where('samples.type', 'Monthly Test')
            ->selectRaw('
            Sites.Platform,
            COUNT(DISTINCT samples.site) as sites,
            COUNT(DISTINCT CASE WHEN samples.contamination_level_machine = 1 THEN samples.site END) as ma_1,
            COUNT(DISTINCT CASE WHEN samples.contamination_level_machine = 2 THEN samples.site END) as ma_2,
            COUNT(DISTINCT CASE WHEN samples.contamination_level_machine = 3 THEN samples.site END) as ma_3,

            ROUND(((COUNT(DISTINCT samples.site) - COUNT(DISTINCT CASE WHEN samples.escherichia > 0 OR samples.escherichia = "TNTC" THEN samples.site END)) * 100.0 / 
                NULLIF(COUNT(DISTINCT samples.site), 0)), 1) as machine_percentage,

            ROUND(((COUNT(DISTINCT samples.site) - COUNT(DISTINCT CASE WHEN samples.escherichia_bottle > 0 OR samples.escherichia_bottle = "TNTC" THEN samples.site END)) * 100.0 / 
                NULLIF(COUNT(DISTINCT samples.site), 0)), 1) as bottle_percentage,

            ROUND(((COUNT(DISTINCT samples.site) - COUNT(DISTINCT CASE WHEN samples.contamination_level_machine > 0 THEN samples.site END)) * 100.0 / 
                NULLIF(COUNT(DISTINCT samples.site), 0)), 1) as machine_esch_ecoli,

            ROUND(((COUNT(DISTINCT samples.site) - COUNT(DISTINCT CASE WHEN samples.contamination_level_bottle > 0 THEN samples.site END)) * 100.0 / 
                NULLIF(COUNT(DISTINCT samples.site), 0)), 1) as bottle_esch_ecoli,

            ROUND(((COUNT(DISTINCT samples.site) - COUNT(CASE WHEN DATEDIFF(samples.analysis_date, samples.sample_date) > 1 THEN samples.site END)) * 100.0 / 
                NULLIF(COUNT(DISTINCT samples.site), 0)), 1) as delay
        ')
            ->groupBy('Sites.Platform')
            ->get();
        // End of resultMonthlyTest this month

        // --- 2. Result resultAfterIntervention in month Where type = 'WQ Alert' ---
        // $resultAfterIntervention = Sample::from('samples as s')
        //     ->join(DB::raw('(SELECT MAX(id) AS latest_id FROM samples WHERE type = "WQ Alert" GROUP BY site) as latest'), 's.id', '=', 'latest.latest_id')
        //     ->join('Sites', 's.site', '=', 'Sites.Id_Site')
        //     ->whereYear('s.sample_date', $year)
        //     ->whereMonth('s.sample_date', $monthNum)
        //     ->where('s.type', 'WQ Alert')
        //     ->selectRaw("
        //                 Sites.Platform,
        //                 COUNT(s.site) AS sites,

        //                 ROUND(((COUNT(s.site) - COUNT(CASE WHEN s.escherichia IS NOT NULL AND s.escherichia != '' AND (s.escherichia > 0 OR s.escherichia = 'TNTC') THEN 1 END)) * 100.0
        //                         / NULLIF(COUNT(s.site), 0)), 2) AS machine_percentage,

        //                 ROUND(((COUNT(s.site) - COUNT(CASE WHEN s.escherichia_bottle IS NOT NULL AND s.escherichia_bottle != '' AND (s.escherichia_bottle > 0 OR s.escherichia_bottle = 'TNTC') THEN 1 END)) * 100.0
        //                         / NULLIF(COUNT(s.site), 0)), 2) AS bottle_percentage,

        //                 ROUND(((COUNT(s.site) - COUNT(CASE WHEN s.contamination_level_machine IS NOT NULL AND s.contamination_level_machine != '' AND s.contamination_level_machine > 0 THEN 1 END)) * 100.0
        //                         / NULLIF(COUNT(s.site), 0)), 2) AS machine_esch_ecoli,

        //                 ROUND(((COUNT(s.site) - COUNT(CASE WHEN s.contamination_level_bottle IS NOT NULL AND s.contamination_level_bottle != '' AND s.contamination_level_bottle > 0 THEN 1 END)) * 100.0
        //                         / NULLIF(COUNT(s.site), 0)), 2) AS bottle_esch_ecoli
        //             ")
        //     ->groupBy('Sites.Platform')
        //     ->get();
        $platforms = ['PP', 'KSP', 'BTB', 'SR', 'KC'];

        $resultAfterIntervention = DB::table('Sites')
            ->whereIn('Sites.Platform', $platforms)
            ->leftJoin(DB::raw('(
        SELECT s.*
        FROM samples s
        INNER JOIN (
            SELECT MAX(id) AS latest_id
            FROM samples
            WHERE type = "WQ Alert"
              AND YEAR(sample_date) = ?
              AND MONTH(sample_date) = ?
            GROUP BY site
        ) latest ON s.id = latest.latest_id
    ) AS s'), function ($join) use ($year, $monthNum) {
                $join->on('Sites.Id_Site', '=', 's.site');
            })
            ->selectRaw("
        Sites.Platform,
        
        COALESCE(COUNT(s.site), 0) AS sites,
        
        CASE 
            WHEN COALESCE(COUNT(s.site), 0) = 0 THEN 100.00
            ELSE ROUND((
                (COALESCE(COUNT(s.site), 0) - COUNT(CASE 
                    WHEN s.escherichia IS NOT NULL 
                     AND s.escherichia != '' 
                     AND (s.escherichia > 0 OR s.escherichia = 'TNTC') 
                    THEN 1 END)
                ) * 100.0 / NULLIF(COALESCE(COUNT(s.site), 0), 0)
            ), 1)
        END AS machine_percentage,

        CASE 
            WHEN COALESCE(COUNT(s.site), 0) = 0 THEN 100.00
            ELSE ROUND((
                (COALESCE(COUNT(s.site), 0) - COUNT(CASE 
                    WHEN s.escherichia_bottle IS NOT NULL 
                     AND s.escherichia_bottle != '' 
                     AND (s.escherichia_bottle > 0 OR s.escherichia_bottle = 'TNTC') 
                    THEN 1 END)
                ) * 100.0 / NULLIF(COALESCE(COUNT(s.site), 0), 0)
            ), 1)
        END AS bottle_percentage,

        CASE 
            WHEN COALESCE(COUNT(s.site), 0) = 0 THEN 100.00
            ELSE ROUND((
                (COALESCE(COUNT(s.site), 0) - COUNT(CASE 
                    WHEN s.contamination_level_machine IS NOT NULL 
                     AND s.contamination_level_machine != '' 
                     AND s.contamination_level_machine > 0 
                    THEN 1 END)
                ) * 100.0 / NULLIF(COALESCE(COUNT(s.site), 0), 0)
            ), 1)
        END AS machine_esch_ecoli,

        CASE 
            WHEN COALESCE(COUNT(s.site), 0) = 0 THEN 100.00
            ELSE ROUND((
                (COALESCE(COUNT(s.site), 0) - COUNT(CASE 
                    WHEN s.contamination_level_bottle IS NOT NULL 
                     AND s.contamination_level_bottle != '' 
                     AND s.contamination_level_bottle > 0 
                    THEN 1 END)
                ) * 100.0 / NULLIF(COALESCE(COUNT(s.site), 0), 0)
            ), 1)
        END AS bottle_esch_ecoli
    ", [$year, $monthNum])  // Bind the two ? placeholders here
            ->groupBy('Sites.Platform')
            ->orderBy('Sites.Platform')
            ->get();

        // End of resultAfterIntervention in Month

        // --- 3. resultGlobalView: latest per site+platform, type in ['Monthly Test', 'WQ Alert'] ---

        $resultGlobalView = Sample::from('samples as s')
            ->join('Sites', 's.site', '=', 'Sites.Id_Site')
            ->whereIn('s.type', ['Monthly Test', 'WQ Alert'])
            ->whereYear('s.sample_date', $year)
            ->whereMonth('s.sample_date', $monthNum)
            ->whereIn('s.id', function ($query) use ($year, $monthNum) {
                $query->select(DB::raw('MAX(s2.id)'))
                    ->from('samples as s2')
                    ->join('Sites as st', 's2.site', '=', 'st.Id_Site')
                    ->whereIn('s2.type', ['Monthly Test', 'WQ Alert'])
                    ->whereYear('s2.sample_date', $year)
                    ->whereMonth('s2.sample_date', $monthNum)
                    ->groupBy('s2.site', 'st.Platform');
            })
            ->selectRaw("
                        Sites.Platform,
                        COUNT(s.site) AS sites,

                        ROUND(((COUNT(s.site) - COUNT(CASE WHEN s.escherichia IS NOT NULL AND s.escherichia != '' AND (s.escherichia > 0 OR s.escherichia = 'TNTC') THEN 1 END)) * 100.0
                                / NULLIF(COUNT(s.site), 0)), 1) AS machine_percentage,

                        ROUND(((COUNT(s.site) - COUNT(CASE WHEN s.escherichia_bottle IS NOT NULL AND s.escherichia_bottle != '' AND (s.escherichia_bottle > 0 OR s.escherichia_bottle = 'TNTC') THEN 1 END)) * 100.0
                                / NULLIF(COUNT(s.site), 0)), 1) AS bottle_percentage,

                        ROUND(((COUNT(s.site) - COUNT(CASE WHEN s.contamination_level_machine IS NOT NULL AND s.contamination_level_machine != '' AND s.contamination_level_machine > 0 THEN 1 END)) * 100.0
                                / NULLIF(COUNT(s.site), 0)), 1) AS machine_esch_ecoli,

                        ROUND(((COUNT(s.site) - COUNT(CASE WHEN s.contamination_level_bottle IS NOT NULL AND s.contamination_level_bottle != '' AND s.contamination_level_bottle > 0 THEN 1 END)) * 100.0
                                / NULLIF(COUNT(s.site), 0)), 1) AS bottle_esch_ecoli
                        ")
            ->groupBy('Sites.Platform')
            ->get();
        // End of resultGlobalView


        // --- 1. Result YTD ---
        $resultMonthlyYTD = Sample::join('Sites', 'samples.site', '=', 'Sites.Id_Site')
            ->whereYear('samples.sample_date', $year)
            ->whereMonth('samples.sample_date', '<=', $monthNum)
            ->where('samples.type', 'Monthly Test')
            ->selectRaw('
                        MONTH(samples.sample_date) as month,
                        COUNT(DISTINCT samples.site) as sites,
                        COUNT(DISTINCT CASE WHEN samples.contamination_level_machine = 1 THEN samples.site END) as ma_1,
                        COUNT(DISTINCT CASE WHEN samples.contamination_level_machine = 2 THEN samples.site END) as ma_2,
                        COUNT(DISTINCT CASE WHEN samples.contamination_level_machine = 3 THEN samples.site END) as ma_3,

                        ROUND(((COUNT(DISTINCT samples.site) - COUNT(DISTINCT CASE WHEN samples.escherichia > 0 OR samples.escherichia = "TNTC" THEN samples.site END)) * 100.0 / 
                            NULLIF(COUNT(DISTINCT samples.site), 0)), 1) as machine_percentage,

                        ROUND(((COUNT(DISTINCT samples.site) - COUNT(DISTINCT CASE WHEN samples.escherichia_bottle > 0 OR samples.escherichia_bottle = "TNTC" THEN samples.site END)) * 100.0 / 
                            NULLIF(COUNT(DISTINCT samples.site), 0)), 1) as bottle_percentage,

                        ROUND(((COUNT(DISTINCT samples.site) - COUNT(DISTINCT CASE WHEN samples.contamination_level_machine > 0 THEN samples.site END)) * 100.0 / 
                            NULLIF(COUNT(DISTINCT samples.site), 0)), 1) as machine_esch_ecoli,

                        ROUND(((COUNT(DISTINCT samples.site) - COUNT(DISTINCT CASE WHEN samples.contamination_level_bottle > 0 THEN samples.site END)) * 100.0 / 
                            NULLIF(COUNT(DISTINCT samples.site), 0)), 1) as bottle_esch_ecoli,

                        ROUND(((COUNT(DISTINCT samples.site) - COUNT(CASE WHEN DATEDIFF(samples.analysis_date, samples.sample_date) > 1 THEN samples.site END)) * 100.0 / 
                            NULLIF(COUNT(DISTINCT samples.site), 0)), 1) as delay
                       ')
            ->groupBy('month')
            ->orderBy('month')
            ->get();
        // End of resultMonthlyYTD

        // 2. queryResultAfterInterventionYTD
        //     $queryResultAfterInterventionYTD = Sample::where('type', 'WQ Alert')
        //         ->whereYear('sample_date', $year)
        //         ->whereIn('id', function ($query) use ($year) {
        //             $query->selectRaw('MAX(id)')
        //                 ->from('samples')
        //                 ->where('type', 'WQ Alert')
        //                 ->whereYear('sample_date', $year)
        //                 ->groupBy('site');
        //         });

        //     $resultsAfterInterventionYTD = DB::table(DB::raw("({$queryResultAfterInterventionYTD->toSql()}) as latest_samples"))
        //         ->mergeBindings($queryResultAfterInterventionYTD->getQuery())
        //         ->join('sites', 'latest_samples.site', '=', 'sites.Id_Site')
        //         ->selectRaw("
        //     MONTH(latest_samples.sample_date) as month,
        //     COUNT(DISTINCT latest_samples.site) as sites,
        //     COUNT(DISTINCT CASE WHEN latest_samples.contamination_level_machine = 1 THEN latest_samples.site END) as ma_1,
        //     COUNT(DISTINCT CASE WHEN latest_samples.contamination_level_machine = 2 THEN latest_samples.site END) as ma_2,
        //     COUNT(DISTINCT CASE WHEN latest_samples.contamination_level_machine = 3 THEN latest_samples.site END) as ma_3,

        //     ROUND(((COUNT(DISTINCT latest_samples.site) - COUNT(DISTINCT CASE WHEN latest_samples.escherichia > 0 OR latest_samples.escherichia = 'TNTC' THEN latest_samples.site END)) * 100.0 / 
        //         NULLIF(COUNT(DISTINCT latest_samples.site), 0)), 2) as machine_percentage,

        //     ROUND(((COUNT(DISTINCT latest_samples.site) - COUNT(DISTINCT CASE WHEN latest_samples.escherichia_bottle > 0 OR latest_samples.escherichia_bottle = 'TNTC' THEN latest_samples.site END)) * 100.0 / 
        //         NULLIF(COUNT(DISTINCT latest_samples.site), 0)), 2) as bottle_percentage,

        //     ROUND(((COUNT(DISTINCT latest_samples.site) - COUNT(DISTINCT CASE WHEN latest_samples.contamination_level_machine > 0 THEN latest_samples.site END)) * 100.0 / 
        //         NULLIF(COUNT(DISTINCT latest_samples.site), 0)), 2) as machine_esch_ecoli,

        //     ROUND(((COUNT(DISTINCT latest_samples.site) - COUNT(DISTINCT CASE WHEN latest_samples.contamination_level_bottle > 0 THEN latest_samples.site END)) * 100.0 / 
        //         NULLIF(COUNT(DISTINCT latest_samples.site), 0)), 2) as bottle_esch_ecoli,

        //     ROUND(((COUNT(DISTINCT latest_samples.site) - COUNT(CASE WHEN DATEDIFF(latest_samples.analysis_date, latest_samples.sample_date) > 1 THEN latest_samples.site END)) * 100.0 / 
        //         NULLIF(COUNT(DISTINCT latest_samples.site), 0)), 2) as delay
        // ")
        //         ->groupBy('month')
        //         ->orderBy('month')
        //         ->get();

        $resultsAfterInterventionYTD = Sample::from('samples as s')
            ->join('Sites', 's.site', '=', 'Sites.Id_Site')
            ->where('s.type', 'WQ Alert')
            ->whereYear('s.sample_date', $year)
            ->whereMonth('s.sample_date', '<=', $monthNum)
            ->selectRaw("
                        MONTH(s.sample_date) as month,
                        COUNT(DISTINCT s.site) as sites,
                        COUNT(DISTINCT CASE WHEN s.contamination_level_machine = 1 THEN s.site END) as ma_1,
                        COUNT(DISTINCT CASE WHEN s.contamination_level_machine = 2 THEN s.site END) as ma_2,
                        COUNT(DISTINCT CASE WHEN s.contamination_level_machine = 3 THEN s.site END) as ma_3,

                        ROUND(((COUNT(DISTINCT s.site) - COUNT(DISTINCT CASE WHEN s.escherichia > 0 OR s.escherichia = 'TNTC' THEN s.site END)) * 100.0 / 
                            NULLIF(COUNT(DISTINCT s.site), 0)), 1) as machine_percentage,

                        ROUND(((COUNT(DISTINCT s.site) - COUNT(DISTINCT CASE WHEN s.escherichia_bottle > 0 OR s.escherichia_bottle = 'TNTC' THEN s.site END)) * 100.0 / 
                            NULLIF(COUNT(DISTINCT s.site), 0)), 1) as bottle_percentage,
                        
                        ROUND(((COUNT(DISTINCT s.site) - COUNT(DISTINCT CASE WHEN s.contamination_level_machine > 0 THEN s.site END)) * 100.0 / 
                            NULLIF(COUNT(DISTINCT s.site), 0)), 1) as machine_esch_ecoli,
                                    
                        ROUND(((COUNT(DISTINCT s.site) - COUNT(DISTINCT CASE WHEN s.contamination_level_bottle > 0 THEN s.site END)) * 100.0 / 
                            NULLIF(COUNT(DISTINCT s.site), 0)), 1) as bottle_esch_ecoli,

                        ROUND(((COUNT(DISTINCT s.site) - COUNT(CASE WHEN DATEDIFF(s.analysis_date, s.sample_date) > 1 THEN s.site END)) * 100.0 / 
                            NULLIF(COUNT(DISTINCT s.site), 0)), 1) as delay
                    ")
            ->groupBy('month')
            ->orderBy('month')
            ->get();

        // end queryResultAfterInterventionYTD

        // 3. Global Result Vie YTD
        $globalresultYTD = DB::table('samples as s')
            ->selectRaw("
                            MONTH(s.sample_date) AS month,
                            COUNT(DISTINCT s.site) AS sites,

                            -- Percent machine (OK samples)
                            ROUND((COUNT(s.site)- COUNT(CASE WHEN s.escherichia IS NOT NULL AND s.escherichia != '' AND (s.escherichia > 0 OR s.escherichia = 'TNTC') THEN 1 END)) * 100.0 
                            / NULLIF(COUNT(s.site), 0), 1) AS machine_percentage,

                            -- Percent bottle (OK samples)
                            ROUND((COUNT(s.site)- COUNT(CASE WHEN s.escherichia_bottle IS NOT NULL AND s.escherichia_bottle != '' AND (s.escherichia_bottle > 0 OR s.escherichia_bottle = 'TNTC') 
                                THEN 1 END)) * 100.0 / NULLIF(COUNT(s.site), 0), 1) AS bottle_percentage,
                            -- machine contamination_level > 0 percentage
                            ROUND((COUNT(s.site)- COUNT(CASE WHEN s.contamination_level_machine IS NOT NULL AND s.contamination_level_machine != '' AND s.contamination_level_machine > 0
                                THEN 1 END)) * 100.0 / NULLIF(COUNT(s.site), 0), 1) AS machine_esch_ecoli,

                            -- bottle contamination_level > 0 percentage
                            ROUND((COUNT(s.site)- COUNT(CASE WHEN s.contamination_level_bottle IS NOT NULL AND s.contamination_level_bottle != '' AND s.contamination_level_bottle > 0
                                THEN 1 END)) * 100.0 / NULLIF(COUNT(s.site), 0), 1) AS bottle_esch_ecoli
                        ")
            ->whereYear('s.sample_date', $year)
            ->whereMonth('s.sample_date', '<=', $monthNum)
            ->whereIn('s.type', ['Monthly Test', 'WQ Alert'])
            ->groupBy(DB::raw("MONTH(s.sample_date)"))
            ->orderBy(DB::raw("MONTH(s.sample_date)"))
            ->get();
        // End of global result YTD


        $physicAndChimical = Sample::select([
            DB::raw('MONTH(sample_date) as month'),
            DB::raw('COUNT(*) as total_site_tests'),
            DB::raw('COUNT(turbidity) as turbidity_tests'),
            DB::raw('ROUND((COUNT(turbidity) * 100.0 / COUNT(*)), 1) as turbidity_percentage'),

            // Total coliform positive counts
            DB::raw("COUNT(CASE WHEN total_coliform > 0 OR total_coliform = 'TNTC' THEN 1 END) as total_coliform_positive"),
            DB::raw("COUNT(CASE WHEN total_coliform_bottle > 0 OR total_coliform_bottle = 'TNTC' THEN 1 END) as total_coliform_bottle_positive"),
            DB::raw("ROUND((COUNT(CASE WHEN total_coliform > 0 OR total_coliform = 'TNTC' THEN 1 END) * 100.0 / 
                NULLIF(COUNT(CASE WHEN total_coliform IS NOT NULL THEN 1 END), 0)), 1) 
                as total_coliform_positive_percentage"),

            // Escherichia positive counts
            DB::raw("COUNT(CASE WHEN escherichia > 0 OR escherichia = 'TNTC' THEN 1 END) as escherichia_positive"),
            DB::raw("COUNT(CASE WHEN escherichia_bottle > 0 OR escherichia_bottle = 'TNTC' THEN 1 END) as escherichia_bottle_positive"),
            DB::raw("ROUND((COUNT(CASE WHEN escherichia > 0 OR escherichia = 'TNTC' THEN 1 END) * 100.0 / 
                NULLIF(COUNT(CASE WHEN escherichia IS NOT NULL THEN 1 END), 0)), 1) 
                as escherichia_positive_percentage"),

            // Delayed analysis
            DB::raw("COUNT(CASE WHEN DATEDIFF(analysis_date, sample_date) > 1 THEN 1 END) as delayed_analysis"),
            DB::raw("ROUND((COUNT(CASE WHEN DATEDIFF(analysis_date, sample_date) > 1 THEN 1 END) * 100.0 / COUNT(*)), 1) 
                as delayed_analysis_percentage"),

            // Turbidity related
            DB::raw('COUNT(CASE WHEN turbidity > 2 THEN 1 END) as high_turbidity'),
            DB::raw('COUNT(CASE WHEN turbidity IS NOT NULL THEN 1 END) as turbidity_tested'),
            DB::raw('ROUND((COUNT(CASE WHEN turbidity <= 2 THEN 1 END) * 100.0 / 
        NULLIF(COUNT(CASE WHEN turbidity IS NOT NULL THEN 1 END), 0)), 1) 
        as normal_turbidity_percentage'),

            // TDS related
            DB::raw('COUNT(CASE WHEN tds > 250 THEN 1 END) as high_tds'),
            DB::raw('COUNT(CASE WHEN tds IS NOT NULL THEN 1 END) as tds_tested'),
            DB::raw('ROUND((COUNT(CASE WHEN tds <= 250 THEN 1 END) * 100.0 / 
                NULLIF(COUNT(CASE WHEN tds IS NOT NULL THEN 1 END), 0)), 1) 
                as normal_tds_percentage'),

            // Nitrate related
            DB::raw('COUNT(CASE WHEN nitrate > 50 THEN 1 END) as high_nitrate'),
            DB::raw('COUNT(CASE WHEN nitrate IS NOT NULL THEN 1 END) as nitrate_tested'),
            DB::raw('ROUND((COUNT(CASE WHEN nitrate <= 50 THEN 1 END) * 100.0 / 
                NULLIF(COUNT(CASE WHEN nitrate IS NOT NULL THEN 1 END), 0)), 1) 
                as normal_nitrate_percentage'),

            // Nitrite related
            DB::raw('COUNT(CASE WHEN nitrite > 50 THEN 1 END) as high_nitrite'),
            DB::raw('COUNT(CASE WHEN nitrite IS NOT NULL THEN 1 END) as nitrite_tested'),
            DB::raw('ROUND((COUNT(CASE WHEN nitrite <= 50 THEN 1 END) * 100.0 / 
                NULLIF(COUNT(CASE WHEN nitrite IS NOT NULL THEN 1 END), 0)), 1) 
                as normal_nitrite_percentage'),

            // Iron related
            DB::raw('COUNT(CASE WHEN iron > 0.05 THEN 1 END) as high_iron'),
            DB::raw('COUNT(CASE WHEN iron IS NOT NULL THEN 1 END) as iron_tested'),
            DB::raw('ROUND((COUNT(CASE WHEN iron <= 0.05 THEN 1 END) * 100.0 / 
                NULLIF(COUNT(CASE WHEN iron IS NOT NULL THEN 1 END), 0)), 1) 
                as normal_iron_percentage'),

            // Manganese related
            DB::raw('COUNT(CASE WHEN manganese > 0.05 THEN 1 END) as high_manganese'),
            DB::raw('COUNT(CASE WHEN manganese IS NOT NULL THEN 1 END) as manganese_tested'),
            DB::raw('ROUND((COUNT(CASE WHEN manganese <= 0.05 THEN 1 END) * 100.0 / 
                NULLIF(COUNT(CASE WHEN manganese IS NOT NULL THEN 1 END), 0)), 1) 
                as normal_manganese_percentage'),

            // Aluminium related
            DB::raw('COUNT(CASE WHEN aluminium > 0.2 THEN 1 END) as high_aluminium'),
            DB::raw('COUNT(CASE WHEN aluminium IS NOT NULL THEN 1 END) as aluminium_tested'),
            DB::raw('ROUND((COUNT(CASE WHEN aluminium <= 0.2 THEN 1 END) * 100.0 / 
                NULLIF(COUNT(CASE WHEN aluminium IS NOT NULL THEN 1 END), 0)), 1) 
                as normal_aluminium_percentage'),

            // pH related
            DB::raw('COUNT(CASE WHEN ph >= 6.5 AND ph <= 8.5 THEN 1 END) as normal_ph'),
            DB::raw('COUNT(CASE WHEN ph IS NOT NULL THEN 1 END) as ph_tested'),
            DB::raw('ROUND((COUNT(CASE WHEN ph >= 6.5 AND ph <= 8.5 THEN 1 END) * 100.0 / 
                NULLIF(COUNT(CASE WHEN ph IS NOT NULL THEN 1 END), 0)), 1) 
                as normal_ph_percentage'),

            // DB::raw('ROUND((COUNT(CASE WHEN ph >= 6.5 AND ph <= 8.5 THEN 1 END) * 100.0 / 
            // COUNT(*)), 2) as normal_ph_percentage_again'),

            // Contamination levels
            DB::raw('COUNT(CASE WHEN contamination_level_machine = 1 THEN 1 END) as contamination_level_1'),
            DB::raw('COUNT(CASE WHEN contamination_level_machine = 2 THEN 1 END) as contamination_level_2'),
            DB::raw('COUNT(CASE WHEN contamination_level_machine = 3 THEN 1 END) as contamination_level_3'),
            DB::raw('ROUND((COUNT(CASE WHEN contamination_level_machine = 1 THEN 1 END) * 100.0 / COUNT(*)), 1) 
                as contamination_level_1_percentage'),
        ])
            ->whereYear('sample_date', $year)
            ->whereMonth('sample_date', '<=', $monthNum)
            ->where('type', 'Monthly Test')
            ->groupBy('month')
            ->orderBy('month')
            ->get();

        return response()->json([
            'dataThisMonth' => $dataThisMonth, // show contamination data for this month
            'highContaminationSites' => $highContaminationSites, // show high contamination > 3 sites YTD 
            'resultMonthlyTest' => $resultMonthlyTest, // show result of Monthly Test this month
            'resultAfterIntervention' => $resultAfterIntervention, // show result resultAfterIntervention this month
            'resultGlobalView' => $resultGlobalView, // show result global view this month
            'resultYTD' => $resultMonthlyYTD, // show result monthly YTD
            'resultsAfterInterventionYTD' => $resultsAfterInterventionYTD, // show resultAfterIntervention YTD
            'resultGlobalViewYTD' => $globalresultYTD, // show result global view YTD
            'physicAndChimical' => $physicAndChimical, // show result global view YTD
        ]);
    }
    public function calculateResult(Request $request)
    {
        $selectedDate = '2025-10-15';
        [$year, $month] = explode('-', $selectedDate);


        $latestSamples = Sample::select('samples.*')
            ->join(
                DB::raw('(SELECT MAX(id) AS latest_id
                         FROM samples
                         WHERE type = "WQ Alert"
                         GROUP BY site) latest'),
                'samples.id',
                '=',
                'latest.latest_id'
            )
            ->whereYear('samples.sample_date', $year)
            ->whereMonth('samples.sample_date', $month)
            ->where('samples.type', 'WQ Alert');

        $results = DB::table(DB::raw("({$latestSamples->toSql()}) s"))
            ->mergeBindings($latestSamples->getQuery())
            ->join('Sites', 's.site', '=', 'Sites.Id_Site')
            ->selectRaw("
            Sites.Platform,
            COUNT(s.site) AS sites,
            
            ROUND(((COUNT(s.site) - COUNT(CASE WHEN s.escherichia IS NOT NULL AND s.escherichia != ''AND (s.escherichia > 0 OR s.escherichia = 'TNTC')THEN 1 END)) * 100.0 
                    / NULLIF(COUNT(s.site), 0)), 2) AS machine_percentage,

            ROUND(((COUNT(s.site) - COUNT(CASE WHEN s.escherichia_bottle IS NOT NULL AND s.escherichia_bottle != '' AND (s.escherichia_bottle > 0 OR s.escherichia_bottle = 'TNTC') THEN 1 END)) * 100.0 
                    / NULLIF(COUNT(s.site), 0)), 2) AS bottle_percentage,
            
            ROUND(((COUNT(s.site) - COUNT(CASE WHEN s.contamination_level_machine IS NOT NULL AND s.contamination_level_machine != '' AND s.contamination_level_machine > 0 THEN 1 END)) * 100.0 
                    / NULLIF(COUNT(s.site), 0)), 2) AS machine_esch_ecoli,
            ROUND(((COUNT(s.site) - COUNT(CASE WHEN s.contamination_level_bottle IS NOT NULL AND s.contamination_level_bottle != '' AND s.contamination_level_bottle > 0 THEN 1 END)) * 100.0 
                    / NULLIF(COUNT(s.site), 0)), 2) AS bottle_esch_ecoli
        ")
            ->groupBy('sites.Platform')
            ->get();

        return response()->json(['result' => $results]);
    }

    public function wq(Request $request)
    {
        $selectedDate = '2025-10-15';
        [$year, $month] = explode('-', $selectedDate);

        $results = Sample::join('Sites', 'samples.site', '=', 'Sites.Id_Site')
            ->whereYear('samples.sample_date', $year)
            ->whereMonth('samples.sample_date', $month)
            ->where('samples.type', 'Monthly Test')
            ->selectRaw('
                    Sites.Platform,
                    COUNT(DISTINCT samples.site) as sites,
                    COUNT(DISTINCT CASE WHEN samples.contamination_level_machine = 1 THEN samples.site END) as ma_1,
                    COUNT(DISTINCT CASE WHEN samples.contamination_level_machine = 2 THEN samples.site END) as ma_2,
                    COUNT(DISTINCT CASE WHEN samples.contamination_level_machine = 3 THEN samples.site END) as ma_3,

                    ROUND(((COUNT(DISTINCT samples.site) - COUNT(DISTINCT CASE WHEN samples.escherichia > 0 OR samples.escherichia = "TNTC" THEN samples.site END)) * 100.0 / 
                        NULLIF(COUNT(DISTINCT samples.site), 0)), 2) as machine_percentage,

                    ROUND(((COUNT(DISTINCT samples.site) - COUNT(DISTINCT CASE WHEN samples.escherichia_bottle > 0 OR samples.escherichia_bottle = "TNTC" THEN samples.site END)) * 100.0 / 
                        NULLIF(COUNT(DISTINCT samples.site), 0)), 2) as bottle_percentage,

                    ROUND(((COUNT(DISTINCT samples.site) - COUNT(DISTINCT CASE WHEN samples.contamination_level_machine > 0 THEN samples.site END)) * 100.0 / 
                        NULLIF(COUNT(DISTINCT samples.site), 0)), 2) as machine_esch_ecoli,

                    ROUND(((COUNT(DISTINCT samples.site) - COUNT(DISTINCT CASE WHEN samples.contamination_level_bottle > 0 THEN samples.site END)) * 100.0 / 
                        NULLIF(COUNT(DISTINCT samples.site), 0)), 2) as bottle_esch_ecoli,

                    ROUND(((COUNT(DISTINCT samples.site) - COUNT(CASE WHEN DATEDIFF(samples.analysis_date, samples.sample_date) > 1 THEN samples.site END)) * 100.0 / 
                        NULLIF(COUNT(DISTINCT samples.site), 0)), 2) as delay
                ')
            ->groupBy('Sites.Platform')
            ->get();

        return response()->json(['result' => $results]);
    }

    public function calculateResultMonthlyOrAlert(Request $request)
    {
        $selectedDate = '2025-10-15';
        [$year, $month] = explode('-', $selectedDate);

        // Step 1: Subquery to get latest sample per site + platform with type 'Monthly Test' or 'WQ Alert'
        // Join sites table to get platform in subquery, because you want latest per site+platform
        $latestSamples = Sample::select('samples.*', 'Sites.Platform')
            ->join('Sites', 'samples.site', '=', 'Sites.Id_Site')
            ->whereYear('samples.sample_date', $year)
            ->whereMonth('samples.sample_date', $month)
            ->whereIn('samples.type', ['Monthly Test', 'WQ Alert']);

        // Now get latest sample per site+platform based on max ID (you can switch to max date if preferred)
        $subquery = DB::table(DB::raw("({$latestSamples->toSql()}) as samples_with_platform"))
            ->mergeBindings($latestSamples->getQuery())
            ->selectRaw('site, Platform, MAX(id) as latest_id')
            ->groupBy('site', 'Platform');

        // Step 2: Join the subquery to get the full latest records
        $latestRecords = Sample::select('samples.*', 'Sites.Platform')
            ->join('Sites', 'samples.site', '=', 'Sites.Id_Site')
            ->joinSub($subquery, 'latest', function ($join) {
                $join->on('samples.id', '=', 'latest.latest_id');
                $join->on('Sites.Platform', '=', 'latest.Platform');
            });

        // Step 3: Calculate results grouping by Platform
        $results = DB::table(DB::raw("({$latestRecords->toSql()}) s"))
            ->mergeBindings($latestRecords->getQuery())
            ->selectRaw("
            s.Platform,
            COUNT(s.site) AS sites,
            
            ROUND(((COUNT(s.site) - COUNT(CASE WHEN s.escherichia IS NOT NULL AND s.escherichia != '' AND (s.escherichia > 0 OR s.escherichia = 'TNTC') THEN 1 END)) * 100.0
                    / NULLIF(COUNT(s.site), 0)), 2) AS machine_percentage,

            ROUND(((COUNT(s.site) - COUNT(CASE WHEN s.escherichia_bottle IS NOT NULL AND s.escherichia_bottle != '' AND (s.escherichia_bottle > 0 OR s.escherichia_bottle = 'TNTC') THEN 1 END)) * 100.0
                    / NULLIF(COUNT(s.site), 0)), 2) AS bottle_percentage,

            ROUND(((COUNT(s.site) - COUNT(CASE WHEN s.contamination_level_machine IS NOT NULL AND s.contamination_level_machine != '' AND s.contamination_level_machine > 0 THEN 1 END)) * 100.0
                    / NULLIF(COUNT(s.site), 0)), 2) AS machine_esch_ecoli,

            ROUND(((COUNT(s.site) - COUNT(CASE WHEN s.contamination_level_bottle IS NOT NULL AND s.contamination_level_bottle != '' AND s.contamination_level_bottle > 0 THEN 1 END)) * 100.0
                    / NULLIF(COUNT(s.site), 0)), 2) AS bottle_esch_ecoli
        ")
            ->groupBy('s.Platform')
            ->get();

        return response()->json(['result' => $results]);
    }

    public function calculateAllResults(Request $request)
    {
        $selectedDate = '2025-10-15';
        [$year, $month] = explode('-', $selectedDate);

        // --- 1. resultCalculate: latest per site, type = 'WQ Alert' ---
        $latestSamples = Sample::select('samples.*')
            ->join(
                DB::raw('(SELECT MAX(id) AS latest_id
                         FROM samples
                         WHERE type = "WQ Alert"
                         GROUP BY site) latest'),
                'samples.id',
                '=',
                'latest.latest_id'
            )
            ->whereYear('samples.sample_date', $year)
            ->whereMonth('samples.sample_date', $month)
            ->where('samples.type', 'WQ Alert');

        $resultsCalculate = DB::table(DB::raw("({$latestSamples->toSql()}) s"))
            ->mergeBindings($latestSamples->getQuery())
            ->join('Sites', 's.site', '=', 'Sites.Id_Site')
            ->selectRaw("
            Sites.Platform,
            COUNT(s.site) AS sites,
            
            ROUND(((COUNT(s.site) - COUNT(CASE WHEN s.escherichia IS NOT NULL AND s.escherichia != '' AND (s.escherichia > 0 OR s.escherichia = 'TNTC') THEN 1 END)) * 100.0
                    / NULLIF(COUNT(s.site), 0)), 2) AS machine_percentage,

            ROUND(((COUNT(s.site) - COUNT(CASE WHEN s.escherichia_bottle IS NOT NULL AND s.escherichia_bottle != '' AND (s.escherichia_bottle > 0 OR s.escherichia_bottle = 'TNTC') THEN 1 END)) * 100.0
                    / NULLIF(COUNT(s.site), 0)), 2) AS bottle_percentage,
            
            ROUND(((COUNT(s.site) - COUNT(CASE WHEN s.contamination_level_machine IS NOT NULL AND s.contamination_level_machine != '' AND s.contamination_level_machine > 0 THEN 1 END)) * 100.0
                    / NULLIF(COUNT(s.site), 0)), 2) AS machine_esch_ecoli,
                    
            ROUND(((COUNT(s.site) - COUNT(CASE WHEN s.contamination_level_bottle IS NOT NULL AND s.contamination_level_bottle != '' AND s.contamination_level_bottle > 0 THEN 1 END)) * 100.0
                    / NULLIF(COUNT(s.site), 0)), 2) AS bottle_esch_ecoli
        ")
            ->groupBy('sites.Platform')
            ->get();

        // --- 2. resultMonthlyOrAlert: latest per site+platform, type in ['Monthly Test', 'WQ Alert'] ---
        $baseSamples = Sample::select('samples.*', 'Sites.Platform')
            ->join('Sites', 'samples.site', '=', 'Sites.Id_Site')
            ->whereYear('samples.sample_date', $year)
            ->whereMonth('samples.sample_date', $month)
            ->whereIn('samples.type', ['Monthly Test', 'WQ Alert']);

        $subquery = DB::table(DB::raw("({$baseSamples->toSql()}) as base"))
            ->mergeBindings($baseSamples->getQuery())
            ->selectRaw('site, Platform, MAX(id) as latest_id')
            ->groupBy('site', 'Platform');

        $latestSamplesWithPlatform = Sample::select('samples.*', 'Sites.Platform')
            ->join('Sites', 'samples.site', '=', 'Sites.Id_Site')
            ->joinSub($subquery, 'latest', function ($join) {
                $join->on('samples.id', '=', 'latest.latest_id');
                $join->on('Sites.Platform', '=', 'latest.Platform');
            });

        $latestSamplesQB = DB::table(DB::raw("({$latestSamplesWithPlatform->toSql()}) s"))
            ->mergeBindings($latestSamplesWithPlatform->getQuery());

        $resultMonthlyOrAlert = (clone $latestSamplesQB)
            ->selectRaw("
            s.Platform,
            COUNT(s.site) AS sites,

            ROUND(((COUNT(s.site) - COUNT(CASE WHEN s.escherichia IS NOT NULL AND s.escherichia != '' AND (s.escherichia > 0 OR s.escherichia = 'TNTC') THEN 1 END)) * 100.0
                    / NULLIF(COUNT(s.site), 0)), 2) AS machine_percentage,

            ROUND(((COUNT(s.site) - COUNT(CASE WHEN s.escherichia_bottle IS NOT NULL AND s.escherichia_bottle != '' AND (s.escherichia_bottle > 0 OR s.escherichia_bottle = 'TNTC') THEN 1 END)) * 100.0
                    / NULLIF(COUNT(s.site), 0)), 2) AS bottle_percentage,

            ROUND(((COUNT(s.site) - COUNT(CASE WHEN s.contamination_level_machine IS NOT NULL AND s.contamination_level_machine != '' AND s.contamination_level_machine > 0 THEN 1 END)) * 100.0
                    / NULLIF(COUNT(s.site), 0)), 2) AS machine_esch_ecoli,

            ROUND(((COUNT(s.site) - COUNT(CASE WHEN s.contamination_level_bottle IS NOT NULL AND s.contamination_level_bottle != '' AND s.contamination_level_bottle > 0 THEN 1 END)) * 100.0
                    / NULLIF(COUNT(s.site), 0)), 2) AS bottle_esch_ecoli
        ")
            ->groupBy('s.Platform')
            ->get();

        // --- 3. resultMonthlyTest: your new Monthly Test query ---
        $resultMonthlyTest = Sample::join('Sites', 'samples.site', '=', 'Sites.Id_Site')
            ->whereYear('samples.sample_date', $year)
            ->whereMonth('samples.sample_date', $month)
            ->where('samples.type', 'Monthly Test')
            ->selectRaw('
            Sites.Platform,
            COUNT(DISTINCT samples.site) as sites,
            COUNT(DISTINCT CASE WHEN samples.contamination_level_machine = 1 THEN samples.site END) as ma_1,
            COUNT(DISTINCT CASE WHEN samples.contamination_level_machine = 2 THEN samples.site END) as ma_2,
            COUNT(DISTINCT CASE WHEN samples.contamination_level_machine = 3 THEN samples.site END) as ma_3,

            ROUND(((COUNT(DISTINCT samples.site) - COUNT(DISTINCT CASE WHEN samples.escherichia > 0 OR samples.escherichia = "TNTC" THEN samples.site END)) * 100.0 / 
                NULLIF(COUNT(DISTINCT samples.site), 0)), 2) as machine_percentage,

            ROUND(((COUNT(DISTINCT samples.site) - COUNT(DISTINCT CASE WHEN samples.escherichia_bottle > 0 OR samples.escherichia_bottle = "TNTC" THEN samples.site END)) * 100.0 / 
                NULLIF(COUNT(DISTINCT samples.site), 0)), 2) as bottle_percentage,

            ROUND(((COUNT(DISTINCT samples.site) - COUNT(DISTINCT CASE WHEN samples.contamination_level_machine > 0 THEN samples.site END)) * 100.0 / 
                NULLIF(COUNT(DISTINCT samples.site), 0)), 2) as machine_esch_ecoli,

            ROUND(((COUNT(DISTINCT samples.site) - COUNT(DISTINCT CASE WHEN samples.contamination_level_bottle > 0 THEN samples.site END)) * 100.0 / 
                NULLIF(COUNT(DISTINCT samples.site), 0)), 2) as bottle_esch_ecoli,

            ROUND(((COUNT(DISTINCT samples.site) - COUNT(CASE WHEN DATEDIFF(samples.analysis_date, samples.sample_date) > 1 THEN samples.site END)) * 100.0 / 
                NULLIF(COUNT(DISTINCT samples.site), 0)), 2) as delay
        ')
            ->groupBy('Sites.Platform')
            ->get();

        return response()->json([
            'resultMonthlyTest' => $resultMonthlyTest,
            'resultAfterIntervention' => $resultsCalculate,
            'resultGlobalView' => $resultMonthlyOrAlert
        ]);
    }

    public function testWQ(Request $request)
    {
        DB::enableQueryLog();
        $month = '2025-09';
        $year = date('Y', strtotime($month));
        $monthNum = date('m', strtotime($month));


        $results = Sample::select([
            DB::raw('MONTH(sample_date) as month'),
            DB::raw('COUNT(*) as total_site_tests'),
            DB::raw('COUNT(turbidity) as turbidity_tests'),
            DB::raw('ROUND((COUNT(turbidity) * 100.0 / COUNT(*)), 2) as turbidity_percentage'),

            // Total coliform positive counts
            DB::raw("COUNT(CASE WHEN total_coliform > 0 OR total_coliform = 'TNTC' THEN 1 END) as total_coliform_positive"),
            DB::raw("COUNT(CASE WHEN total_coliform_bottle > 0 OR total_coliform_bottle = 'TNTC' THEN 1 END) as total_coliform_bottle_positive"),
            DB::raw("ROUND((COUNT(CASE WHEN total_coliform > 0 OR total_coliform = 'TNTC' THEN 1 END) * 100.0 / 
                NULLIF(COUNT(CASE WHEN total_coliform IS NOT NULL THEN 1 END), 0)), 2) 
                as total_coliform_positive_percentage"),

            // Escherichia positive counts
            DB::raw("COUNT(CASE WHEN escherichia > 0 OR escherichia = 'TNTC' THEN 1 END) as escherichia_positive"),
            DB::raw("COUNT(CASE WHEN escherichia_bottle > 0 OR escherichia_bottle = 'TNTC' THEN 1 END) as escherichia_bottle_positive"),
            DB::raw("ROUND((COUNT(CASE WHEN escherichia > 0 OR escherichia = 'TNTC' THEN 1 END) * 100.0 / 
                NULLIF(COUNT(CASE WHEN escherichia IS NOT NULL THEN 1 END), 0)), 2) 
                as escherichia_positive_percentage"),

            // Delayed analysis
            DB::raw("COUNT(CASE WHEN DATEDIFF(analysis_date, sample_date) > 1 THEN 1 END) as delayed_analysis"),
            DB::raw("ROUND((COUNT(CASE WHEN DATEDIFF(analysis_date, sample_date) > 1 THEN 1 END) * 100.0 / COUNT(*)), 2) 
                as delayed_analysis_percentage"),

            // Turbidity related
            DB::raw('COUNT(CASE WHEN turbidity > 2 THEN 1 END) as high_turbidity'),
            DB::raw('COUNT(CASE WHEN turbidity IS NOT NULL THEN 1 END) as turbidity_tested'),
            DB::raw('ROUND((COUNT(CASE WHEN turbidity <= 2 THEN 1 END) * 100.0 / 
        NULLIF(COUNT(CASE WHEN turbidity IS NOT NULL THEN 1 END), 0)), 2) 
        as normal_turbidity_percentage'),

            // TDS related
            DB::raw('COUNT(CASE WHEN tds > 250 THEN 1 END) as high_tds'),
            DB::raw('COUNT(CASE WHEN tds IS NOT NULL THEN 1 END) as tds_tested'),
            DB::raw('ROUND((COUNT(CASE WHEN tds <= 250 THEN 1 END) * 100.0 / 
                NULLIF(COUNT(CASE WHEN tds IS NOT NULL THEN 1 END), 0)), 2) 
                as normal_tds_percentage'),

            // Nitrate related
            DB::raw('COUNT(CASE WHEN nitrate > 50 THEN 1 END) as high_nitrate'),
            DB::raw('COUNT(CASE WHEN nitrate IS NOT NULL THEN 1 END) as nitrate_tested'),
            DB::raw('ROUND((COUNT(CASE WHEN nitrate <= 50 THEN 1 END) * 100.0 / 
                NULLIF(COUNT(CASE WHEN nitrate IS NOT NULL THEN 1 END), 0)), 2) 
                as normal_nitrate_percentage'),

            // Nitrite related
            DB::raw('COUNT(CASE WHEN nitrite > 50 THEN 1 END) as high_nitrite'),
            DB::raw('COUNT(CASE WHEN nitrite IS NOT NULL THEN 1 END) as nitrite_tested'),
            DB::raw('ROUND((COUNT(CASE WHEN nitrite <= 50 THEN 1 END) * 100.0 / 
                NULLIF(COUNT(CASE WHEN nitrite IS NOT NULL THEN 1 END), 0)), 2) 
                as normal_nitrite_percentage'),

            // Iron related
            DB::raw('COUNT(CASE WHEN iron > 0.05 THEN 1 END) as high_iron'),
            DB::raw('COUNT(CASE WHEN iron IS NOT NULL THEN 1 END) as iron_tested'),
            DB::raw('ROUND((COUNT(CASE WHEN iron <= 0.05 THEN 1 END) * 100.0 / 
                NULLIF(COUNT(CASE WHEN iron IS NOT NULL THEN 1 END), 0)), 2) 
                as normal_iron_percentage'),

            // Manganese related
            DB::raw('COUNT(CASE WHEN manganese > 0.05 THEN 1 END) as high_manganese'),
            DB::raw('COUNT(CASE WHEN manganese IS NOT NULL THEN 1 END) as manganese_tested'),
            DB::raw('ROUND((COUNT(CASE WHEN manganese <= 0.05 THEN 1 END) * 100.0 / 
                NULLIF(COUNT(CASE WHEN manganese IS NOT NULL THEN 1 END), 0)), 2) 
                as normal_manganese_percentage'),

            // Aluminium related
            DB::raw('COUNT(CASE WHEN aluminium > 0.2 THEN 1 END) as high_aluminium'),
            DB::raw('COUNT(CASE WHEN aluminium IS NOT NULL THEN 1 END) as aluminium_tested'),
            DB::raw('ROUND((COUNT(CASE WHEN aluminium <= 0.2 THEN 1 END) * 100.0 / 
                NULLIF(COUNT(CASE WHEN aluminium IS NOT NULL THEN 1 END), 0)), 2) 
                as normal_aluminium_percentage'),

            // pH related
            DB::raw('COUNT(CASE WHEN ph >= 6.5 AND ph <= 8.5 THEN 1 END) as normal_ph'),
            DB::raw('COUNT(CASE WHEN ph IS NOT NULL THEN 1 END) as ph_tested'),
            DB::raw('ROUND((COUNT(CASE WHEN ph >= 6.5 AND ph <= 8.5 THEN 1 END) * 100.0 / 
                NULLIF(COUNT(CASE WHEN ph IS NOT NULL THEN 1 END), 0)), 2) 
                as normal_ph_percentage'),

            // DB::raw('ROUND((COUNT(CASE WHEN ph >= 6.5 AND ph <= 8.5 THEN 1 END) * 100.0 / 
            // COUNT(*)), 2) as normal_ph_percentage_again'),

            // Contamination levels
            DB::raw('COUNT(CASE WHEN contamination_level_machine = 1 THEN 1 END) as contamination_level_1'),
            DB::raw('COUNT(CASE WHEN contamination_level_machine = 2 THEN 1 END) as contamination_level_2'),
            DB::raw('COUNT(CASE WHEN contamination_level_machine = 3 THEN 1 END) as contamination_level_3'),
            DB::raw('ROUND((COUNT(CASE WHEN contamination_level_machine = 1 THEN 1 END) * 100.0 / COUNT(*)), 2) 
                as contamination_level_1_percentage'),
        ])
            ->whereYear('sample_date', $year)
            ->whereMonth('sample_date', '<=', $monthNum)
            ->where('type', 'Monthly Test')
            ->groupBy('month')
            ->orderBy('month')
            ->get();
        return response()->json(['result' => $results]);
    }
}
