<?php

namespace App\Http\Controllers;

use App\Models\File;
use App\Models\CashierSale;
use App\Models\Expense;
use App\Models\FlashReport;
use App\Models\Invoice;
use App\Models\sales;
use App\Models\SchoolProgram;
use App\Models\Site;
use App\Models\ValidatedData;
use App\Models\WaterMeter;
use Carbon\Carbon;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Storage;
use Intervention\Image\Laravel\Facades\Image;

class CashierAppController extends Controller
{
    public function index(Request $request)
    {
        $request->validate([
            'start' => 'date',
            'end' => 'date',
        ]);
        $start_date = $request->start ?? Carbon::now()->startOfWeek()->toDateString();
        $end_date = $request->end ?? Carbon::now()->endOfWeek()->toDateString();
        $sales = CashierSale::where('sale_date', '>=', $start_date)
            ->where('sale_date', '<=', $end_date);

        if ($request->has("site")) {
            // get the previous channels sales
            $types = CashierSale::select('type', 'unit_price', 'index')
                ->where('site', $request->site)
                ->where('sale_date', '>=', Carbon::parse($start_date)->addDays(-7))
                ->where('sale_date', '<=', $end_date)
                ->get()
                ->unique(function ($item) {
                    return $item->index . $item->type . $item->unit_price;
                })
                ->sortBy("index")
                ->values();

            if (sizeof($types) == 0) {
                // if no previous channels , use default
                $types = [
                    ["type" => "free", "unit_price" => 0, "index" => 0],
                    ["type" => "hod", "unit_price" => 2000, "index" => 1],
                    ["type" => "wis", "unit_price" => 0, "index" => 2],
                    ["type" => "onsite", "unit_price" => 1500, "index" => 3],
                    ["type" => "shop", "unit_price" => 1500, "index" => 4],
                    ["type" => "bottle", "unit_price" => 15000, "index" => 5]
                ];
            }
            return [
                "sales" => $sales->where('site', $request->site)
                    ->orderBy('index', 'asc')
                    ->orderBy('sale_date', 'asc')
                    ->get()
                    ->map(function ($sale) {
                        $sale->type_price = $sale->index . "-" . $sale->type . "-" . $sale->unit_price;
                        return $sale;
                    })
                    ->groupBy(['type_price', 'sale_date']),
                "types" => $types,
                "images" => File::where("site", $request->site)->where("type", "sales")->where("related_date", $end_date)->get(),
            ];
        }

        $sales = $sales->orderBy('site', 'asc')
            ->orderBy('sale_date', 'asc')
            ->get()
            ->groupBy('site');
        $water = WaterMeter::where('date', $end_date)
            ->get();
        $sites = Site::select('Id_Site', 'Advisor', 'Platform')
            ->where("is_pilot", true)
            ->where('Platform', '!=', 'Dead')
            ->orderBy('Id_Site')
            ->get();
        $sites->map(function ($site) use ($sales, $water) {
            $siteSales = $sales->get($site->Id_Site);
            if ($siteSales) {
                $site->distinct_sale_days = $siteSales->pluck('sale_date')->unique()->count();
            } else {
                $site->distinct_sale_days = 0;
            }
            $site->waterMeter = $water->where('site', $site->Id_Site)->first();
            return $site;
        });
        return [
            "sales" => $sales,
            "sites" => $sites->groupBy('Platform'),
            "start_date" => $start_date,
            "end_date" => $end_date
        ];
    }

    public function getEntrepreneurData($site)
    {
        $data = Site::select(["Entrepreneur_English_Name", "Entrepreneur_Khmer_Name", "Phone_Number", "Advisor"])->where("Id_Site", $site)->first();
        $telegramGroup = \App\Models\TelegramGroup::where("site", $site)->first();
        if ($data && $telegramGroup) {
            $data->telegram_invite_url = $telegramGroup->invite_url;
        }
        return $data;
    }

    public function store(Request $request)
    {
        $validated = $request->validate([
            'site' => 'required|string',
            'startDate' => 'required|date',
            'endDate' => 'required|date',
            'sales' => 'required|array',
            'types' => 'required|array',
        ]);

        // Delete all previous records for this site and date range before saving new ones.
        CashierSale::where('site', $validated['site'])
            ->whereBetween('sale_date', [$validated['startDate'], $validated['endDate']])
            ->delete();

        $salesToInsert = [];

        foreach ($validated['sales'] as $typeKey => $salesByDate) {
            // The key is expected to be in the format "index-type-unit_price"
            [$index, $type, $unit_price] = explode('-', $typeKey, 3);

            foreach ($salesByDate as $date => $saleData) {
                // The quantity is nested in an array [{ quantity: ... }]
                $quantity = $saleData[0]['quantity'] ?? null;

                if ($quantity !== null) {
                    $salesToInsert[] = [
                        'site' => $validated['site'],
                        'sale_date' => $date,
                        'index' => (int) $index,
                        'type' => $type,
                        'unit_price' => (float) $unit_price,
                        'quantity' => (int) $quantity,
                    ];
                }
            }
        }

        if (!empty($salesToInsert)) {
            CashierSale::insert($salesToInsert);
        }
        $this->recalculateSales($validated['site'], $validated['startDate'], $validated['endDate']);
        return response()->json(['message' => 'Sales data saved successfully.'], 201);
    }

    public function recalculateSales($site, $startDate, $endDate)
    {
        $monthStart = Carbon::parse($startDate)->firstOfMonth()->toDateString();
        $monthEnd = Carbon::parse($endDate)->firstOfMonth()->toDateString();
        $monthToRecalculate = collect([$monthStart, $monthEnd])->unique();
        foreach ($monthToRecalculate as $month) {
            $dailySales = CashierSale::where("site", $site)->where("sale_date", "like", substr($month, 0, 7) . "%")->get();
            $hodSales = 0;
            $hodIncome = 0;
            $shopkeeperSales = 0;
            $shopkeeperIncome = 0;
            $wisSales = 0;
            $wisIncome = 0;
            $onsiteSales = 0;
            $onsiteIncome = 0;
            $freeSales = 0;
            $bottleSales = 0;
            $bottleIncome = 0;
            $otherSales = 0;
            $otherIncome = 0;
            $emergencySales = 0;
            $emergencyIncome = 0;

            foreach ($dailySales as $dailySale) {
                $income = $dailySale->quantity * $dailySale->unit_price;
                switch ($dailySale->type) {
                    case 'hod':
                        $hodSales += $dailySale->quantity;
                        $hodIncome += $income;
                        break;
                    case 'shop':
                        $shopkeeperSales += $dailySale->quantity;
                        $shopkeeperIncome += $income;
                        break;
                    case 'wis':
                        $wisSales += $dailySale->quantity;
                        $wisIncome += $income;
                        break;
                    case 'onsite':
                        $onsiteSales += $dailySale->quantity;
                        $onsiteIncome += $income;
                        break;
                    case 'free':
                        $freeSales += $dailySale->quantity;
                        break;
                    case 'bottle':
                        $bottleSales += $dailySale->quantity;
                        $bottleIncome += $income;
                        break;
                    case 'other':
                        $otherSales += $dailySale->quantity;
                        $otherIncome += $income;
                        break;
                    case 'emergency':
                        $emergencySales += $dailySale->quantity;
                        $emergencyIncome += $income;
                        break;
                }
            }

            $totalSales = $hodSales + $shopkeeperSales + $wisSales + $onsiteSales + $freeSales + $bottleSales + $otherSales + $emergencySales;
            $totalIncome = $hodIncome + $shopkeeperIncome + $wisIncome + $onsiteIncome + $bottleIncome + $otherIncome + $emergencyIncome;

            $saleData = [
                'Total_Sales' => $totalSales,
                'Total_Income' => $totalIncome,
                'Total_Price_Average' => $totalSales > 0 ? $totalIncome / $totalSales : 0,
                'Hod_Sales' => $hodSales,
                'Hod_Income' => $hodIncome,
                'Hod_Price' => $hodSales > 0 ? $hodIncome / $hodSales : 0,
                'Shopkeeper_Sales' => $shopkeeperSales,
                'Shopkeeper_Income' => $shopkeeperIncome,
                'Shopkeeper_Price' => $shopkeeperSales > 0 ? $shopkeeperIncome / $shopkeeperSales : 0,
                'WiS_Sales' => $wisSales,
                'WiS_Income' => $wisIncome,
                'WiS_Price' => $wisSales > 0 ? $wisIncome / $wisSales : 0,
                'Onsite_Sales' => $onsiteSales,
                'Onsite_Income' => $onsiteIncome,
                'Onsite_Price' => $onsiteSales > 0 ? $onsiteIncome / $onsiteSales : 0,
                'Free_Sales' => $freeSales,
                'Bottle_Sales' => $bottleSales,
                'Bottle_Income' => $bottleIncome,
                'Bottle_Price' => $bottleSales > 0 ? $bottleIncome / $bottleSales : 0,
                'Other_Sales' => $otherSales,
                'Other_Income' => $otherIncome,
                'Other_Price' => $otherSales > 0 ? $otherIncome / $otherSales : 0,
                'Emergency_Sales' => $emergencySales,
                'Emergency_Income' => $emergencyIncome,
                'Emergency_Price' => $emergencySales > 0 ? $emergencyIncome / $emergencySales : 0,
                'Number_Open_Days' => $dailySales->where('quantity', '>', 0)->unique('sale_date')->count(),
            ];

            sales::updateOrCreate(
                ['Id_Site' => $site, 'Month' => $month],
                $saleData
            );

            // flashreport data
            $salesFrom1To15 = $dailySales
                ->where('sale_date', '>=', Carbon::parse($month)->firstOfMonth()->format('Y-m-d'))
                ->where('sale_date', '<', Carbon::parse($month)->firstOfMonth()->addDays(14)->format('Y-m-d'));

            FlashReport::updateOrCreate(
                ['Id_Site' => $site, 'Month' => $month, 'Period' => 'EndMonth'],
                [
                    'Period' => 'EndMonth',
                    'Month' => $month,
                    'Number_jugs_village' => $dailySales->where('type', '!=', 'wis')->where('type', '!=', 'emergency')->sum('quantity'),
                    'Number_jugs_school' => $dailySales->where('type', 'wis')->sum('quantity'),
                    'Number_bot_displace_people' => $dailySales->where('type', 'emergency')->sum('quantity'),
                    'Open_days' => $dailySales->where('quantity', '>', 0)->unique('sale_date')->count()
                ]
            );
            FlashReport::updateOrCreate(
                ['Id_Site' => $site, 'Month' => $month, 'Period' => 'MidMonth'],
                [
                    'Period' => 'MidMonth',
                    'Month' => $month,
                    'Number_jugs_village' => $salesFrom1To15->where('type', '!=', 'wis')->where('type', '!=', 'emergency')->sum('quantity'),
                    'Number_jugs_school' => $salesFrom1To15->where('type', 'wis')->sum('quantity'),
                    'Number_bot_displace_people' => $salesFrom1To15->where('type', 'emergency')->sum('quantity'),
                    'Open_days' => $salesFrom1To15->where('quantity', '>', 0)->unique('sale_date')->count()
                ]
            );
        }
    }

    public function getExpenses(Request $request)
    {
        $request->validate([
            'month' => 'date',
            'site' => 'string',
            'start' => 'date',
            'end' => 'date',
        ]);
        $month = $request->has('start') ? Carbon::parse($request->start) : ($request->has('month') ?  Carbon::parse($request->month) : Carbon::now()->firstOfMonth());
        if ($request->has('site')) {
            $expenses = Expense::where('Id_Site', $request->site)
                ->where('Month', '>=', $request->start)
                ->where('Month', '<=', $request->end)
                ->where("Ref_expenses", "<>", "debt")
                ->get();
            return [
                "expenses" => $expenses->groupBy("Ref_expenses"),
                "invoices" => Invoice::select(["beginning_balance", "invoice_ref", "invoice_type"])
                    ->where("site", $request->site)
                    ->whereIn("invoice_type", ["Consumable Bottle", "Stock Invoice", "Delivery Program Fee"])
                    ->where("month", $month)
                    ->get(),
                "expenses_count" => $expenses->count(),
                "images" => File::where("site", $request->site)->where("type", "expenses")->where("related_date", $request->end)->get(),
                "categories" => [
                    "production" => ["consumable_production", "stock_ts", "bottle_invoice", "electricity", "gasoline_waterpump", "raw_water"],
                    "salary" => ["fix_salary_entrepreneurs", "variable_salary_entrepreneurs", "fix_salary_operators", "variable_salary_operators"],
                    "delivery" => ["maintenance_delivery", "gasoline_delivery"],
                    "contribution" => ["commune_contribution", "entrepreneur_contribution"],
                    "technical" => ["technical intervention", "water quality alert"],
                    "investment" => ["investment", "delivery_program_fee"]
                ]
            ];
        }
        $sites = Site::select('Id_Site')
            ->where("is_pilot", true)
            ->get()->pluck("Id_Site")->values();
        $expenses = Expense::where('Month', 'like', $month . '%');
        return [
            "expenses" => $expenses->whereIn("Id_Site", $sites)
                ->where("Ref_expenses", "<>", "debt")
                ->where("Ref_expenses", "<>", "entrepreneur_contribution")
                ->where("Ref_expenses", "<>", "WinS_invoice")
                ->where("Ref_expenses", "<>", "stock_ts")
                ->orderBy('Id_Site')->get()->groupBy('Id_Site'),
            "month" => $month->toDateString()
        ];
    }

    public function storeExpenses(Request $request)
    {
        $request->validate([
            'expenses' => 'required|array',
            'expenses.*.Id_Site' => 'required|string',
            'expenses.*.Month' => 'required|date',
            'expenses.*.Ref_expenses' => 'required|string',
            'expenses.*.Amount_expenses' => 'nullable|numeric',
        ]);
        foreach ($request->expenses as $expenseData) {
            if ($expenseData['Amount_expenses'] === null) {
                Expense::where('Id_Site', $expenseData['Id_Site'])
                    ->where('Month', $expenseData['Month'])
                    ->where('Ref_expenses', $expenseData['Ref_expenses'])
                    ->delete();
            } else {
                Expense::updateOrCreate(
                    [
                        'Id_Site' => $expenseData['Id_Site'],
                        'Month' => $expenseData['Month'],
                        'Ref_expenses' => $expenseData['Ref_expenses'],
                    ],
                    [
                        'Amount_expenses' => $expenseData['Amount_expenses'],
                        'Category_expenses' => $expenseData['Category_expenses'] ?? null,
                    ]
                );
            }
        }
        return response()->json(['message' => 'Expenses data saved successfully.'], 201);
    }

    public function getWiS(Request $request)
    {
        $request->validate([
            'month' => 'date',
            'site' => 'string',
            'start' => 'date',
            'end' => 'date',
        ]);
        $month = $request->has('month') ? Carbon::parse($request->month) : Carbon::parse($request->start)->firstOfMonth();
        if ($request->has('site')) {
            $wisSales = CashierSale::where('site', $request->site)
                ->where('sale_date', '>=', $request->start)
                ->where('sale_date', '<=', $request->end)
                ->where('type', 'wis')
                ->orderBy('sale_date', 'asc')
                ->get();
            return [
                "wis" => $wisSales->groupBy('sale_date'),
                "wis_count" => $wisSales->count(),
                "images" => File::where("site", $request->site)->where("type", "wis")->where("related_date", $request->end)->get(),
                "unit_price" => $wisSales->max("unit_price") ?? null,
                "is_validated" => ValidatedData::where("site", $request->site)->where("validated_date", $request->end)->where("type", "wis")->exists(),
                "school" => SchoolProgram::select("school_code", "school_name_english", "school_director_name_english", "bottle_approved", "academy_year")
                    ->where("academy_year", ">=", $month->year - 2)
                    ->where("Id_Site", $request->site)
                    ->where("status", "validation")
                    ->get()
                    ->groupBy(["school_code", "academy_year"]),
            ];
        }
        $sites = Site::select('Id_Site')
            ->where("is_pilot", true)
            ->get()->pluck("Id_Site")->values();
        $wisSales = CashierSale::where('sale_date', '>=', $month->toDateString())
            ->where('sale_date', '<=', $month->lastOfMonth()->toDateString())
            ->where("type", "wis");
        return [
            "wis" => $wisSales->whereIn("site", $sites)
                ->orderBy('site')->get()->groupBy('site'),
            "month" => $month->toDateString(),
            "validated" => ValidatedData::where("validated_date", $month->lastOfMonth()->toDateString())->where("type", "wis")->get()->pluck("site")->values(),
        ];
    }

    public function storeWiS(Request $request)
    {
        $request->validate([
            'unit_price' => 'required|numeric',
            'month' => 'required|date',
            'site' => 'required|string',
            'wis' => 'required|array',
            'wis.*.site' => 'required|string',
            'wis.*.sale_date' => 'required|date',
            'wis.*.quantity' => 'nullable|numeric',
            'wis.*.type' => 'required|in:wis',
        ]);

        $toUpsert = [];
        $toDelete = [];

        foreach ($request->wis as $item) {
            unset($item['created_at'], $item['updated_at']);
            if ($item['quantity'] === null) {
                $toDelete[] = [
                    'site' => $item['site'],
                    'sale_date' => $item['sale_date'],
                    'type' => $item['type'],
                ];
            } else {
                $toUpsert[] = array_merge($item, [
                    'unit_price' => $request->unit_price,
                    'index' => 999,
                ]);
            }
        }

        if (!empty($toDelete)) {
            foreach ($toDelete as $record) {
                CashierSale::where('site', $record['site'])
                    ->where('sale_date', $record['sale_date'])
                    ->where('type', $record['type'])
                    ->delete();
            }
        }

        if (!empty($toUpsert)) {
            CashierSale::upsert($toUpsert, ['site', 'sale_date', 'type'], ['quantity', 'unit_price', 'index']);
            ValidatedData::upsert([
                "site" => $request->site,
                "validated_date" => $request->month,
                "type" => "wis",
            ], ['site', 'validated_date', 'type']);
        }
        $this->recalculateSales($request->site, Carbon::parse($request->month)->firstOfMonth()->toDateString(), Carbon::parse($request->month)->lastOfMonth()->toDateString());
        return response()->json(['message' => 'WiS data saved successfully.'], 201);
    }
    public function getLatestWater(Request $request)
    {
        $request->validate([
            'end_date' => 'required|date',
            'start_date' => 'required|date',
            'site' => 'required|string',
        ]);
        $previous = 0;
        $water = WaterMeter::where('site', $request->site)
            ->where('date', '<=', $request->start_date)
            ->latest('date')
            ->first();
        if (!$water) {
            $firstOfMonth = Carbon::parse($request->end_date)->firstOfMonth()->toDateString();
            $water = DB::table("Indicators")
                ->where("Id_Site", $request->site)
                ->where('Month', '<', $firstOfMonth)
                ->latest('Month')
                ->first();
            $previous = $water->Water_end ?? 0;
        } else {
            $previous = $water->value;
        }
        $water = WaterMeter::where('site', $request->site)
            ->where('date', $request->end_date)
            ->first();
        return [
            'previous' => $previous,
            'current' => $water->value ?? null,
            'images' => File::where("site", $request->site)->where("type", "water_meter")->where("related_date", $request->end_date)->get(),
            'consumption' => intval(CashierSale::where("site", $request->site)->whereBetween('sale_date', [$request->start_date, $request->end_date])->sum('quantity'))
        ];
    }
    public function storeWater(Request $request)
    {
        $request->validate([
            'end_date' => 'required|date',
            'site' => 'required|string',
            'value' => 'required|integer',
            'file' => 'nullable|file|mimes:jpg,jpeg,png,pdf',
        ]);
        WaterMeter::updateOrCreate(
            [
                'site' => $request->site,
                'date' => $request->end_date,
            ],
            [
                'value' => $request->value,
            ]
        );

        // update the commcare table : problem is week and month do not match
        /* $month = Carbon::parse($request->end_date)->firstOfMonth()->toDateString();
        $waterBegin = WaterMeter::where("site", $request->site)
                        ->where('date', 'like', substr($month, 0, 7)."%")->min("value");
        $waterEnd = WaterMeter::where("site", $request->site)
                        ->where('date', 'like', substr($month, 0, 7)."%")->max("value");
        DB::table("Indicators")->updateOrInsert(
                ['Id_Site' => $request->site, 'Month' => $month],
                [
                    'Water_begining' => $waterBegin,
                    'Water_end' => $waterEnd,
                    'Water_consume' => $waterEnd - $waterBegin,
                ]
            ); */
        return response()->json(['message' => 'Water meter data saved successfully.'], 201);
    }

    public function uploadFile(Request $request)
    {
        $validated = $request->validate([
            'site' => 'required|string',
            'type' => 'required|string',
            'related_date' => 'required|date',
            'files' => 'required|array',
            'files.*' => 'file|mimes:jpg,jpeg,png,pdf',
        ]);

        foreach ($request->file('files') as $file) {
            $extension = strtolower($file->getClientOriginalExtension());
            $uniqueId = now()->toDateString() . "-" . uniqid();

            if (in_array($extension, ['jpg', 'jpeg', 'png'])) {
                // compression
                $image = Image::read($file)->scaleDown(3000, 3000);
                $path = 'attached_files/' . $uniqueId . "." . $extension;
                Storage::disk('public')->put($path, $image->encodeByExtension($file->getClientOriginalExtension(), quality: 85));

                // miniature
                $image->scaleDown(200, 200);
                $miniaturePath = 'attached_files/' . $uniqueId . "_miniature." . $extension;
                Storage::disk('public')->put($miniaturePath, $image->encodeByExtension($file->getClientOriginalExtension(), quality: 70));
            } else {
                $path = $file->store('public/attached_files');
                $miniaturePath = null;
            }

            File::create([
                'name' => $request->site . "-" . $request->related_date . "-" . $file->getClientOriginalName(),
                'path' => "public/" . $path,
                'miniature_path' => "public/" . $miniaturePath,
                'type' => $request->type,
                'related_date' => $request->related_date,
                'site' => $request->site
            ]);
        }

        return response()->json(['message' => 'Files uploaded successfully.'], 201);
    }
}
