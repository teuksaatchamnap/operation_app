<?php

namespace App\Http\Controllers;

use App\Exports\InvoicesExport;
use App\Exports\InvoicesMultiSheetExport;
use App\Exports\SchoolExport;
use App\Imports\InvoiceImport;
use App\Imports\MainExcelImport;
use App\Jobs\CheckAbaPaymentJob;
use App\Models\Assessment;
use App\Models\CashierNotification;
use App\Models\Expense;
use App\Models\Invoice;
use App\Models\InvoicesRecord;
use App\Models\sales;
use App\Models\Site;
use App\Models\SiteBalance;
use App\Models\TelegramGroup;
use App\Models\CashierSale;
use App\Models\DailySales;
use DateTime;
use Illuminate\Support\Facades\Log;
use Illuminate\Support\Facades\Http;
use Illuminate\Http\Request;
use Carbon\Carbon;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Storage;
use Maatwebsite\Excel\Facades\Excel;

class InvoiceController extends Controller
{
    public function importInvoice(Request $request)
    {
        // $request->validate([
        //     'file' => 'required|file|mimes:xlsx,xls',
        // ]);

        Excel::import(new MainExcelImport, $request->file('file'));

        return response()->json(['message' => 'Excel imported successfully']);
    }
    public function invoicesRecordHistory(Request $request)
    {
        $site = $request->query('site');
        $monthInput = $request->query('month'); // e.g. 2026-01-31 or 2026-01-31T...

        // ✅ Extract only YYYY-MM safely
        $year = substr($monthInput, 0, 4);   // 2026
        $month = substr($monthInput, 5, 2);  // 01

        $records = InvoicesRecord::where('site', $site)
            ->whereYear('month', $year)
            ->whereMonth('month', $month)
            ->orderBy('issue_date', 'desc')
            ->get();

        return response()->json([
            'success' => true,
            'data' => $records
        ]);
    }
    public function invoicesDetail(Request $request)
    {
        $site  = $request->site;
        $monthReceive = $request->month; // "2025-12"
        $date1 = DateTime::createFromFormat('Y-m', $monthReceive);
        // Subtract one month
        $date1->modify('-1 month');

        // Get the new year and month
        $year1 = $date1->format('Y');
        $month1 = $date1->format('m');

        [$year, $month] = explode('-', $monthReceive);
        if (!$site || !$month) {
            return response()->json([], 400);
        }
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

        $siteInfo = Site::select('Platform', 'Advisor', 'Entrepreneur_Khmer_Name')
            ->where('Id_Site', $site)
            ->first();
        // Fetch invoices for the site and month
        $balance = SiteBalance::select('balance', 'beginning_balance')
            ->where('site', $site)
            ->first();

        $saleIncome = sales::select('Total_Income')
            ->whereYear('Month', $year1)
            ->whereMonth('Month', $month1)
            ->where('Id_Site', $site)
            ->first();
        $expense = Expense::where('Id_Site', $site)
            ->whereYear('month', $year1)
            ->whereMonth('month', $month1)
            ->whereNotIn('Ref_expenses', $refExpensesList)
            ->sum('Amount_expenses');
        $expensesByCategory = Expense::where('Id_Site', $site)
            ->whereYear('month', $year1)
            ->whereMonth('month', $month1)
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
        $salaryTotal = $expensesByCategory->whereIn('expense_category', ['salary_entrepreneur', 'salary_operator'])->sum('total_expenses');

        // Add as a new item
        $expensesByCategory->push((object)[
            'expense_category' => 'salary_total',
            'total_expenses' => $salaryTotal
        ]);
        // Convert "2025-12" → first day of month
        //$monthStart = $month . '-01';

        $invoices = Invoice::where('site', $site)
            ->whereNotIn('invoice_type', ['saving', 'withdraw'])
            ->whereYear('month', $year)
            ->whereMonth('month', $month)
            ->get();
        $invoicesCashReceipt = Invoice::where('site', $site)
            //->where('invoice_type', '!=', ['saving','withdraw'])
            ->whereYear('month', $year)
            ->whereMonth('month', $month)
            ->get();
        $invoicesRecord = InvoicesRecord::where('site', $site)
            // ->whereMonth('month', date('m', strtotime($monthStart)))
            // ->whereYear('month', date('Y', strtotime($monthStart)))
            ->whereYear('month', $year)
            ->whereMonth('month', $month)
            ->get();
        return response()->json([
            'success' => true,
            'data' => [
                'balance' => $balance,
                'sale_income' => $saleIncome,
                'expense' => $expense,
                'invoices' => $invoices,
                'expenses_by_category' => $expensesByCategory,
                'site_info' => $siteInfo,
                'invoices_record' => $invoicesRecord,
                'invoicesCashReceipt' => $invoicesCashReceipt,
            ]
        ]);
    }

    public function sql()
    {
        $sub = DB::table('invoices')
            ->select(
                'site',
                'month',

                DB::raw("
            SUM(CASE
                WHEN invoice_type IN ('school-program', 'withdraw')
                THEN beginning_balance
                ELSE 0
            END) as total_school_withdraw
        "),

                DB::raw("
            SUM(CASE
                WHEN invoice_type NOT IN ('school-program', 'withdraw')
                THEN beginning_balance
                ELSE 0
            END) as total_invoice
        "),

                DB::raw("
            SUM(CASE
                WHEN invoice_type NOT IN ('school-program', 'withdraw')
                THEN transaction_amount
                ELSE 0
            END) as total_amount_paid
        "),

                DB::raw("
            SUM(CASE
                WHEN invoice_type = 'school-program'
                THEN beginning_balance
                ELSE 0
            END) as school
        ")
            )
            ->where('site', 'T6')
            ->where('month', '2026-03-01')
            ->groupBy('site', 'month');

        $result = DB::query()
            ->fromSub($sub, 't')
            ->selectRaw("
        site,
        month,
        total_school_withdraw,
        total_invoice,
        school,
        (total_invoice - school) AS total_pay_by_entre,
        (total_amount_paid - total_school_withdraw) AS cashReceived,
        ((total_invoice - school) - (total_amount_paid - total_school_withdraw)) AS remain_amount
    ")
            ->first();
        $lastUpdateBalance = SiteBalance::where('site', 'T6')->first();
        $dataNow = [
            'result' => $result,
            'lastBalance' => $lastUpdateBalance
        ];
        return response()->json($dataNow);
    }

    public function updatePayments(Request $request)
    {
        try {
            $payments = $request->input('payments', []);
            $deductSaving = $request->input('deductSaving', false);
            $originalBalance = $request->input('originalBalance', false);
            $remainingBalance = (floatval($originalBalance) - floatval($deductSaving));
            $totalRemainingInvoice = $request->input('totalNormalRemaining', false);
            $schoolOverInvoice = $request->input('netAmount', false);
            $invoiceAndDeposit = $request->input('invoiceAndDeposit', false);
            $paymentDate = $request->input('paymentDate', null);
            $transactionID = $request->input('transactionID', null);
            //  dd("school over invoice: " . $schoolOverInvoice . " | deduct saving: " . $deductSaving . " | original balance: "
            //  . $originalBalance . " | remaining balance: " . $remainingBalance . " | total remaining invoice: " . $totalRemainingInvoice . " | invoice and deposit: " . $invoiceAndDeposit);
            $siteId = null;
            $month = null;
            $firstInvoice = null;

            $qrPath = null;
            if ($request->has('qr_code') && $request->input('qr_code')) {
                $qrBase64 = $request->input('qr_code');
                $qrFileType = $request->input('qr_filetype', 'image/png');

                // Clean base64 string and decode
                $qrData = base64_decode(preg_replace('#^data:[^;]+;base64,#i', '', $qrBase64));

                // Generate unique filename
                $qrFileName = 'qr_' . time() . '_' . uniqid() . '.' . $this->getExtensionFromMime($qrFileType);

                // Save to public storage
                Storage::disk('public')->put('QR_codes/' . $qrFileName, $qrData);

                $qrPath = 'QR_codes/' . $qrFileName;
            }
            $randomNumber = mt_rand(1000, 9999); // or use any random logic you like
            $receiptNumber = "receipt" . $siteId . $randomNumber;
            $expenseType = ['Consumable Bottle'=>['bottle_invoice','production'],'debts'=>['debt','debt'],'Delivery Program Fee'=>['delivery_program_fee','production']
        ,'Entrepreneur Contribution' =>['entrepreneur_contribution','contribution'],'school-program'=>['WinS_invoice',''],'Stock Invoice'=>['stock_ts','production']
        ,'Technical Intervention'=>['technical intervention','technical'],'Water Quality Alert'=>['water quality alert','technical']];
            foreach ($payments as $payment) {
                //update here
                $invoice = Invoice::find($payment['id']);
                if (!$invoice) {
                    // Invoice not found: fail early or skip
                    return response()->json([
                        'success' => false,
                        'message' => "Invoice with ID {$payment['id']} not found.",
                    ], 404);
                }

                if ($firstInvoice === null) {
                    $firstInvoice = $invoice;
                    $siteId = $invoice->site;
                    $month = $invoice->month;
                    $receiptNumber = mt_rand(100000, 9999999);
                }

                $invoice->transaction_amount = $payment['amount_receive'];
                $invoice->remain_amount = $payment['remain_amount'];
                $invoice->status = 'settle';

                if ($qrPath) {
                    $invoice->pictureQR = $qrPath;
                }
                $invoice->receipt_number = $receiptNumber;
                $invoice->aba_date = $paymentDate;
                $invoice->aba_transaction_id = $transactionID;
                $invoice->save();

                Log::info('[Expense] invoice_type=' . $invoice->invoice_type . ' exists_in_map=' . (isset($expenseType[$invoice->invoice_type]) ? 'yes' : 'no'));
                if (isset($expenseType[$invoice->invoice_type])) {
                    [$refExpense, $categoryExpense] = $expenseType[$invoice->invoice_type];
                    Log::info('[Expense] attempting updateOrCreate', [
                        'Id_Site'          => $invoice->site,
                        'Month'            => $invoice->month,
                        'Ref_expenses'     => $refExpense,
                        'Amount_expenses'  => $invoice->beginning_balance,
                        'Paid'             => $payment['amount_receive'],
                        'Category_expenses'=> $categoryExpense,
                    ]);
                    try {
                        $expense = Expense::updateOrCreate(
                            [
                                'Id_Site'      => $invoice->site,
                                'Month'        => $invoice->month,
                                'Ref_expenses' => $refExpense,
                            ],
                            [
                                'Amount_expenses'   => $invoice->beginning_balance,
                                'Paid'              => $payment['amount_receive'],
                                'Category_expenses' => $categoryExpense,
                            ]
                        );
                        Log::info('[Expense] saved id=' . $expense->Code_expenses . ' wasRecentlyCreated=' . ($expense->wasRecentlyCreated ? 'true' : 'false'));
                    } catch (\Exception $e) {
                        Log::error('[Expense] failed: ' . $e->getMessage());
                    }
                }
            }
            if ($schoolOverInvoice < 0) { // if school amount < 0, it is school program. else it is amount to pay
                $reverseAmountSchool = -1 * floatval($schoolOverInvoice);
                $r = 0;
                $remainingInvoice = SiteBalance::where('site', $siteId)->first();
                if ($remainingInvoice) {
                    if ($remainingInvoice->beginning_balance < 0) {
                        $remainingInvoice->beginning_balance = $reverseAmountSchool;  // take amount of school remain to sum with existing beginning_balance
                        $r = $reverseAmountSchool;
                        $remainingInvoice->save();
                    } else {
                        $r = $remainingInvoice->beginning_balance + $reverseAmountSchool; // sum more amount remaining from school to existing beginning_balance
                        $remainingInvoice->beginning_balance = $r;
                        $remainingInvoice->save();
                    }
                }
                $savingInvoice = new Invoice();
                $savingInvoice->site = $siteId;
                $savingInvoice->month = $month;
                $savingInvoice->beginning_balance = $reverseAmountSchool;
                $savingInvoice->transaction_amount = $reverseAmountSchool;
                $savingInvoice->remain_amount = $r;
                $savingInvoice->status = 'settle';
                $savingInvoice->invoice_type = 'saving';
                $savingInvoice->receipt_number = 'saving';
                $savingInvoice->invoice_ref = 'saving';
                $savingInvoice->save();
            } else {
                if ($deductSaving > 0 && $siteId && $month) {
                    $savingInvoice = new Invoice();
                    $savingInvoice->site = $siteId;
                    $savingInvoice->month = $month;
                    $savingInvoice->beginning_balance = $originalBalance;
                    $savingInvoice->transaction_amount = $deductSaving;
                    $savingInvoice->remain_amount = $remainingBalance;
                    $savingInvoice->status = 'settle';
                    $savingInvoice->invoice_type = 'withdraw';
                    $savingInvoice->receipt_number = 'withdraw';
                    $savingInvoice->invoice_ref = 'withdraw';
                    $savingInvoice->save();

                    $savingBalance = SiteBalance::where('site', $siteId)->first();
                    if ($savingBalance) {
                        if ($totalRemainingInvoice > 0) {
                            $savingBalance->beginning_balance = -1 * $totalRemainingInvoice;
                        } else {
                            $savingBalance->beginning_balance = $remainingBalance;
                        }
                        $savingBalance->save();
                    }
                } else {
                    $reverseAmount = -1 * floatval($totalRemainingInvoice);
                    $remainingInvoice = SiteBalance::where('site', $siteId)->first();
                    if ($remainingInvoice) {
                        $remainingInvoice->beginning_balance = $remainingInvoice->beginning_balance + $reverseAmount;
                        $remainingInvoice->save();
                    }
                }
            }

            if($invoiceAndDeposit >0)
                // update this.
                {
                    $remainingInvoice = SiteBalance::where('site', $siteId)->first();
                        if ($remainingInvoice) {
                            $remainingInvoice->beginning_balance = $remainingInvoice->beginning_balance + $invoiceAndDeposit;
                            $remainingInvoice->save();
                        }
                    $depositInvoice = new Invoice();
                    $depositInvoice->site = $siteId;
                    $depositInvoice->month = $month;
                    $depositInvoice->beginning_balance = $remainingInvoice ? $remainingInvoice->beginning_balance : 0;
                    $depositInvoice->transaction_amount = $invoiceAndDeposit;
                    $depositInvoice->remain_amount =  $remainingInvoice->beginning_balance + $invoiceAndDeposit;;
                    $depositInvoice->status = 'settle';
                    $depositInvoice->invoice_type = 'saving';
                    $depositInvoice->invoice_type_khmer_name = 'សន្សំ';
                    $depositInvoice->receipt_number = $siteId."-".$month;
                    $depositInvoice->invoice_ref = $siteId."-".$month;
                    $depositInvoice->save();

                }

            return response()->json([
                'success' => true,
                'message' => 'All payments updated successfully.',
                'data' => [
                    'saving_deduction_added' => $deductSaving > 0,
                    'saving_deduction_amount' => $deductSaving,
                    'updated_invoices_count' => count($payments),
                ],
            ]);
        } catch (\Exception $e) {
            Log::error('Failed to update payments: ' . $e->getMessage());
            Log::error($e->getTraceAsString());

            return response()->json([
                'success' => false,
                'message' => 'Failed to update payments: ' . $e->getMessage(),
                'stack' => $e->getTraceAsString()
            ], 500);
        }
    }

    private function getExtensionFromMime($mimeType)
    {
        $extensions = [
            'image/jpeg' => 'jpg',
            'image/jpg' => 'jpg',
            'image/png' => 'png',
            'image/gif' => 'gif',
            'application/pdf' => 'pdf',
            'application/zip' => 'zip',
            'application/x-zip-compressed' => 'zip',
        ];

        return $extensions[$mimeType] ?? 'bin';
    }
    public function getSitesWithInvoices(Request $request)
    {
        $monthFilter = $request->query('month'); // e.g. '2025-12'
        $sitesQuery = Site::query();
        if ($monthFilter) {
            [$year, $month] = explode('-', $monthFilter);

            // Only include sites that have invoices in this month
            $sitesQuery->whereHas('invoices', function ($query) use ($year, $month) {
                $query->whereYear('month', $year)
                    ->whereMonth('month', $month);
            });
        } else {
            // if no filter, only sites with any invoices
            $sitesQuery->has('invoices');
        }

        $sites = $sitesQuery->with(['invoices' => function ($query) use ($monthFilter, $year, $month) {
            $query->orderBy('month', 'desc');
            if ($monthFilter) {
                $query->whereYear('month', $year)
                    ->whereMonth('month', $month);
            }
        }])
            ->select('Id_Site', 'Platform', 'Advisor', 'Entrepreneur_Khmer_Name')
            ->get()
            ->map(function ($site) {
                return [
                    'Id_Site' => $site->Id_Site,
                    'Platform' => $site->Platform,
                    'Advisor' => $site->Advisor,
                    'Entrepreneur' => $site->Entrepreneur_Khmer_Name,
                    'invoices' => $site->invoices->map(function ($invoice) {
                        return [
                            'id' => $invoice->id,
                            'month' => $invoice->month->format('Y-m-d'),
                            'beginning_balance' => $invoice->beginning_balance,
                            'transaction_amount' => $invoice->transaction_amount,
                            'invoice_type' => $invoice->invoice_type,
                            'invoice_type_khmer_name' => $invoice->invoice_type_khmer_name,
                            'status' => $invoice->status,
                            'remain_amount' => $invoice->remain_amount,
                            'invoice_ref' => $invoice->invoice_ref,
                            'receipt_number' => $invoice->receipt_number,
                            'pictureQR' => $invoice->pictureQR,
                            'aba_status_code' => $invoice->aba_status_code,
                            'aba_amount' => $invoice->aba_amount,
                            'aba_date' => $invoice->formatted_aba_date,
                            'aba_transaction_id' => $invoice->aba_transaction_id,
                        ];
                    }),
                    'total_invoices' => $site->invoices->count(),
                    'latest_invoice' => $site->invoices->first() ? [
                        'month' => $site->invoices->first()->month->format('F Y'),
                        'status' => $site->invoices->first()->status,
                    ] : null,
                ];
            });

        return response()->json([
            'success' => true,
            'data' => $sites
        ]);
    }

    public function sendCashReceipt(Request $request)
    {
        $request->validate([
            'chat_id' => 'required|string',
            'file' => 'required|file|mimes:png,jpg,jpeg'
        ]);

        $botToken = env('TELEGRAM_BOT_TOKEN');
        $chatId = $request->input('chat_id');
        $file = $request->file('file');

        $response = Http::attach(
            'photo',
            file_get_contents($file->getRealPath()),
            $file->getClientOriginalName()
        )->post("https://api.telegram.org/bot{$botToken}/sendPhoto", [
            'chat_id' => $chatId,
            'caption' => 'ជំរាបសួរ/សួរស្តីសហគ្រិន នេះគឺជាបង្កាន់ដៃបង់ប្រាក់របស់អ្នកជាមួយនិងឯកសារភ្ជាប់'
        ]);

        if ($response->failed()) {
            return response()->json([
                'success' => false,
                'telegram_error' => $response->json(),
            ], 500);
        }

        return response()->json([
            'success' => true,
            'message' => 'Photo sent successfully',
            'telegram_response' => $response->json()
        ], 200);
    }

    public function receivePaymentABA(Request $request)
    {
        $tran_id = $request->tran_id;

        Log::info('ABA Webhook received', $request->all());

        // ✅ Replace sleep with queue delay
        CheckAbaPaymentJob::dispatch($tran_id)
            ->delay(now()->addSeconds(10));

        // ✅ Respond immediately (important)
        return response()->json([
            'success' => true,
            'message' => 'Webhook received'
        ]);
    }

    public function getTransactionDetail()
    {
        $transaction_id = request()->query('transaction_id');
        $merchant_id = config('payway.merchant_id');
        $api_key = config('payway.api_key');
        $tran_id = $transaction_id;
        $req_time = now()->format('YmdHis');
        $b4hash = $req_time . $merchant_id . $tran_id;
        $hash = base64_encode(hash_hmac('sha512', $b4hash, $api_key, true));

        try {
            $response = Http::timeout(30)
                ->retry(3, 100) // Retry 3 times with 100ms delay
                ->withHeaders([
                    'Content-Type' => 'application/json',
                ])
                // during production we need to put this url
                ->post('https://checkout.payway.com.kh/api/payment-gateway/v1/payments/transaction-detail', [
                    'req_time' => $req_time,
                    'merchant_id' => $merchant_id,
                    'tran_id' => $tran_id,
                    'hash' => $hash,
                ]);

            $data1 = $response->json();
            $transaction = $data1['data'] ?? null;
            $status = $data1['payment_status_code'] ?? null;
            $result = $transaction['payment_status'] ?? null;
            if ($result == 'APPROVED' || $result == 'REFUNDED' || $result == 'DECLINED' || $result == 'CANCELLED' || $result == 'PENDING') {
                InvoicesRecord::where('transaction_id', $tran_id)->update(['payment_status' => $result]);
            }
            $returnData = InvoicesRecord::where('transaction_id', $tran_id)->first();
            return response()->json([
                'data' => $returnData
            ]);
            // if ($response->successful()) {
            //     return response()->json([
            //         'success' => true,
            //         'message' => 'Check detail invoice is successfully',
            //         'transaction' => $transaction,
            //         'status' => $status,
            //         'result' => $result,
            //         'object' => "testing",
            //         'returnData' => $returnData
            //     ]);
            //     }



        } catch (\Exception $e) {
            \Log::error('PayWay API Exception', [
                'message' => $e->getMessage(),
                'status' => "Exception occurred while fetching transaction details",
            ]);

            return [
                'error' => true,
                'message' => $e->getMessage(),
            ];
        }
    }

    public function sendInvoiceTelegram(Request $request)
    {
        $request->validate([
            'chat_id' => 'required|string',
            'file' => 'required|image'
        ]);

        $botToken = env('TELEGRAM_BOT_TOKEN');
        $chatId   = $request->chat_id;
        $amount   = $request->amount;
        $site     = $request->site;
        $month    = $request->month;
        InvoicesRecord::create([
            'site' => $site,
            'month' => Carbon::parse($month)->startOfMonth(),
            'transaction_id' => $site. "-" . $month,
            'amount' => $amount,
            'issue_date' => Carbon::now(),
            'payment_status' => 'pending',
        ]);

        // 1️⃣ Generate QR from ABA
        $url = config('payway.api_url');
        $merchant_id = config('payway.merchant_id');
        $api_key = config('payway.api_key');
        $callback_url = base64_encode(config('payway.callback_url'));
        //$callback_url = config('payway.callback_url');

        $request_time = now('UTC')->format('YmdHis');
        $tran_id = $site. "-" . $month;
        $amount = $amount;
        $lifetime = 43200; // 12 hours in seconds
        $currency = "KHR"; // KHR works fine
        $payment_option = "abapay_khqr";
        $purchase_type = "purchase";
        $qr_image_template = "template3_color";
        $hash = base64_encode(hash_hmac(
            'sha512',
            $request_time . $merchant_id . $tran_id . $amount . $purchase_type . $payment_option . $callback_url . $currency . $lifetime . $qr_image_template,
            $api_key,
            true
        ));

        $params = [
            "req_time" => $request_time,
            "merchant_id" => $merchant_id,
            "tran_id" => $tran_id,
            "amount" => $amount,
            "payment_option" => $payment_option,
            "currency" => $currency,
            "lifetime" => $lifetime,
            "qr_image_template" => $qr_image_template,
            "purchase_type" => $purchase_type,
            "callback_url" => $callback_url,
            "hash" => $hash
        ];

        // Send as JSON explicitly
        if (app()->isProduction() || $merchant_id != null) {
            $responseQR = Http::withHeaders([
                'Content-Type' => 'application/json'
            ])->withBody(json_encode($params), 'application/json')
                ->post($url)
                ->json();
            if (!isset($responseQR['qrImage'])) {
                return response()->json([
                    'success' => false,
                    'message' => 'Failed to generate QR',
                    'data' => $responseQR
                ], 500);
            }
        } else {
            $responseQR = ['qrImage' => base64_encode(file_get_contents(base_path("public/img/qrts1001.png")))];
        }

        // Decode QR from base64 (no need to store to disk)
        $qrImageContent = base64_decode(str_replace('data:image/png;base64,', '', $responseQR['qrImage']));

        // 2️⃣ Get the uploaded invoice image
        $canvasPath = $request->file('file')->store('temp');
        $invoiceImageContent = Storage::get($canvasPath);

        // 3️⃣ Prepare logo
        $logoFullPath = public_path('img/qrts1001.jpg');
        if (!file_exists($logoFullPath)) {
            return response()->json([
                'success' => false,
                'message' => 'Logo file not found'
            ], 404);
        }

        // 4️⃣ Send all images to Telegram
        $caption = 'ជូនចំពោះសហគ្រិននេះគឺជាវិក្កយបត្ររបស់អ្នកសម្រាប់ខែនេះ។ សូមប្រើប្រាស់ QR code សម្រាប់ការទូទាត់។';
        $notification = CashierNotification::where("key", "send-invoice")->first();
        if ($notification) {
            $caption = $notification->message;
        }
        $responseTelegram = Http::attach(
            'photo1',
            $invoiceImageContent,
            'invoice.png'
            // )->attach(
            //     'photo2',
            //     file_get_contents($logoFullPath),
            //     'logo.png'
        )->attach(
            'photo3',
            $qrImageContent,
            'qr.png'
        )->post("https://api.telegram.org/bot{$botToken}/sendMediaGroup", [
            'chat_id' => $chatId,
            'media' => json_encode([
                [
                    'type' => 'photo',
                    'media' => 'attach://photo1',
                    'caption' => $caption,
                ],
                // [
                //     'type' => 'photo',
                //     'media' => 'attach://photo2'
                // ],
                [
                    'type' => 'photo',
                    'media' => 'attach://photo3'
                ]
            ])
        ]);
        if ($notification && $notification->audio) {
            app(TelegramController::class)->sendAudioToSite($request->site, Storage::disk("public")->path($notification->audio));
        }

        // 5️⃣ Cleanup
        Storage::delete($canvasPath);

        if ($responseTelegram->failed()) {
            return response()->json([
                'success' => false,
                'telegram_error' => $responseTelegram->json()
            ], 500);
        }

        return response()->json([
            'success' => true,
            'message' => 'Images sent successfully',
            'telegram_response' => $responseTelegram->json()
        ]);
    }

    public function generateQRFromCashier(Request $request)
    {
        $request->validate([
            'chat_id' => 'required|string',
            'file' => 'required|image'
        ]);

        $botToken = env('TELEGRAM_BOT_TOKEN');
        $chatId   = $request->chat_id;
        $amount   = $request->amount;
        $site     = $request->site;
        $month    = $request->month;
        $processType = $request->process_type;
        $randomDigits = str_pad(mt_rand(0, 9999), 4, '0', STR_PAD_LEFT);
        InvoicesRecord::create([
            'site' => $site,
            'month' => Carbon::parse($month)->startOfMonth(),
            'transaction_id' => $site. "-" . $month . "-" . $randomDigits ."-".$processType,
            'amount' => $amount,
            'issue_date' => Carbon::now(),
            'payment_status' => 'pending',
        ]);

        // 1️⃣ Generate QR from ABA
        $url = config('payway.api_url');
        $merchant_id = config('payway.merchant_id');
        $api_key = config('payway.api_key');
        $callback_url = base64_encode(config('payway.callback_url'));

        $request_time = now('UTC')->format('YmdHis');
        $tran_id = $site. "-" . $month . "-" . $randomDigits ."-".$processType;
        $amount = $amount;
        $lifetime = 43200; // 12 hours in seconds
        $currency = "KHR";
        $payment_option = "abapay_khqr";
        $purchase_type = "purchase";
        $qr_image_template = "template3_color";

        $hash = base64_encode(hash_hmac(
            'sha512',
            $request_time . $merchant_id . $tran_id . $amount . $purchase_type . $payment_option . $callback_url . $currency . $lifetime . $qr_image_template,
            $api_key,
            true
        ));

        $params = [
            "req_time" => $request_time,
            "merchant_id" => $merchant_id,
            "tran_id" => $tran_id,
            "amount" => $amount,
            "payment_option" => $payment_option,
            "currency" => $currency,
            "lifetime" => $lifetime,
            "qr_image_template" => $qr_image_template,
            "purchase_type" => $purchase_type,
            "callback_url" => $callback_url,
            "hash" => $hash
        ];

        // Send as JSON explicitly
        $responseQR = Http::withHeaders([
            'Content-Type' => 'application/json'
        ])->withBody(json_encode($params), 'application/json')
            ->post($url)
            ->json();

        if (!isset($responseQR['qrImage'])) {
            return response()->json([
                'success' => false,
                'message' => 'Failed to generate QR',
                'data' => $responseQR
            ], 500);
        } else {
            Log::info('QR generated successfully', [
                'tran_id' => $tran_id,
                "message" => "QR generated by cashier",
            ]);
        }

        // Decode QR from base64
        $qrImageContent = base64_decode(str_replace('data:image/png;base64,', '', $responseQR['qrImage']));

        // 2️⃣ Get the uploaded invoice image (if you still need it)
        $canvasPath = $request->file('file')->store('temp');
        $invoiceImageContent = Storage::get($canvasPath);

        // 3️⃣ Prepare logo (if needed)
        $logoFullPath = public_path('img/qrts1001.jpg');
        if (!file_exists($logoFullPath)) {
            return response()->json([
                'success' => false,
                'message' => 'Logo file not found'
            ], 404);
        }

        // 4️⃣ Send ONLY QR code as a single photo
        $responseTelegram = Http::attach(
            'photo',
            $qrImageContent,
            'qr_code.png'
        )->post("https://api.telegram.org/bot{$botToken}/sendPhoto", [
            'chat_id' => $chatId,
            'caption' => 'ជូនចំពោះសហគ្រិននេះគឺជា QR code សម្រាប់ការទូទាត់។'
        ]);

        // 5️⃣ Cleanup
        Storage::delete($canvasPath);

        if ($responseTelegram->failed()) {
            return response()->json([
                'success' => false,
                'telegram_error' => $responseTelegram->json()
            ], 500);
        }

        return response()->json([
            'success' => true,
            'message' => 'QR code sent successfully',
            'telegram_response' => $responseTelegram->json()
        ]);
    }

    public function updateStatusBySiteAndMonth(Request $request)
    {
        $siteId = $request->input('Id_Site');
        $monthFilter = $request->input('month'); // expected 'YYYY-MM'


        if (!$siteId || !$monthFilter) {
            return response()->json([
                'success' => false,
                'message' => 'Missing Id_Site or month'
            ], 400);
        }

        [$year, $month] = explode('-', $monthFilter);

        // Fetch all invoices for site and month
        $invoices = Invoice::where('site', $siteId)
            ->whereYear('month', $year)
            ->whereMonth('month', $month)
            ->get();

        if ($invoices->isEmpty()) {
            return response()->json([
                'success' => false,
                'message' => 'No invoices found for site and month'
            ], 404);
        }

        foreach ($invoices as $invoice) {
            // Apply your status transition logic
            if ($invoice->status === 'pending') {
                $invoice->status = 'sending';
            } elseif ($invoice->status === 'sending') {
                $invoice->status = 'settle';
            }
            // If already settled or other status, no change
            $invoice->save();
        }

        return response()->json([
            'success' => true,
            'message' => 'Invoice statuses updated successfully'
        ]);
    }

    public function getSiteBalance(Request $request)
    {

        $siteId = $request->input('Id_Site');
        $monthFilter = $request->input('month'); // expected 'YYYY-MM'

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

        if (!$siteId || !$monthFilter) {
            return response()->json([
                'success' => false,
                'message' => 'Missing Id_Site or month'
            ], 400);
        }

        [$year, $month] = explode('-', $monthFilter);

        // Fetch invoices for the site and month
        $balance = SiteBalance::select('balance')
            ->where('site', $siteId)
            ->first();

        $saleIncome = sales::select('Total_Income')
            ->whereYear('Month', $year)
            ->whereMonth('Month', $month)
            ->where('Id_Site', $siteId)
            ->first();
        $expense = Expense::where('Id_Site', $siteId)
            ->whereYear('month', $year)
            ->whereMonth('month', $month)
            ->whereNotIn('Ref_expenses', $refExpensesList)
            ->sum('Amount_expenses');
        $expensesByCategory = Expense::where('Id_Site', $siteId)
            ->whereYear('month', $year)
            ->whereMonth('month', $month)
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
        $salaryTotal = $expensesByCategory->whereIn('expense_category', ['salary_entrepreneur', 'salary_operator'])->sum('total_expenses');

        // Add as a new item
        $expensesByCategory->push((object)[
            'expense_category' => 'salary_total',
            'total_expenses' => $salaryTotal
        ]);


        return response()->json([
            'success' => true,
            'data' => [
                'balance' => $balance,
                'sale_income' => $saleIncome,
                'month' => $monthFilter,
                'expense' => $expense
            ]
        ]);
    }

    public function savingAnddebt(Request $request)
    {
        $site = $request->input('site');
        $siteBalance = SiteBalance::where('site', $site)->first();
        $IdSite = Site::where('Platform', '!=', 'Dead')
            ->whereNotIn('Id_Site', ['A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'A7', 'A8'])
            ->get();
        if (!$siteBalance) {
            return response()->json([
                'success' => false,
                'message' => 'Site balance not found'
            ], 404);
        }

        return response()->json([
            'success' => true,
            'data' => [
                'balance' => $siteBalance->balance,
                'Id_Site' => $IdSite->Id_Site
            ]
        ]);
    }
    public function getSite()
    {
        $sites = Site::select('Id_Site')
            ->where('Platform', '!=', 'Dead')
            ->whereNotIn('Id_Site', ['A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'A7', 'A8'])
            ->get();
        return response()->json(['sites' => $sites]);
    }
    public function getSiteBalanceById($siteId)
    {

        $siteBalance = SiteBalance::where('site', $siteId)->first();

        if (!$siteBalance) {
            return response()->json([
                'success' => false,
                'message' => 'Site balance not found'
            ], 404);
        }

        return response()->json([
            'success' => true,
            'data' => [
                'balance' => $siteBalance->balance
            ]
        ]);
    }

    public function updateBalance(Request $request)
    {

        $siteId = $request->input('site');
        $amount = str_replace(',', '', $request->input('amount'));
        $invoice_type = $request->input('invoice_type');
        $month = $request->input('month');
        $fullDate = $month . '-01';
        $status = '';

        if (!$siteId || !is_numeric($amount)) {
            return response()->json([
                'success' => false,
                'message' => 'Invalid siteId or amount'
            ], 400);
        }

        $siteBalance = SiteBalance::where('site', $siteId)->first();

        $currentBalance = $siteBalance ? $siteBalance->balance : 0;

        if ($invoice_type == 'Withdrawal') {
            $updateBalance = $currentBalance - $amount;
            $status = 'withdraw';
        } else {
            $updateBalance = $currentBalance + $amount;
            $status = 'saving';
        }

        if ($siteBalance) {
            $siteBalance->beginning_balance = $updateBalance;
            $siteBalance->save();
        }

        if (!empty($invoice_type)) {
            $invoice = new Invoice();
            $invoice->site = $siteId;
            $invoice->month = $fullDate;
            $invoice->beginning_balance = $currentBalance;
            $invoice->transaction_amount = $amount;
            $invoice->remain_amount = $updateBalance;
            $invoice->status = 'settle';
            $invoice->invoice_type_khmer_name = $status == 'withdraw' ? 'ដកប្រាក់' : 'ដាក់ប្រាក់';
            $invoice->invoice_type = $status;
            $invoice->receipt_number = $status;
            $invoice->invoice_ref = $status;
            $invoice->save();
        }

        return response()->json([
            'success' => true,
            'message' => 'Balance updated successfully',
            'data' => [
                'balance' => $updateBalance
            ]
        ]);
    }

    public function getChatID($site)
    {
        $siteCode = $site; // This is Id_Site value

        if (!$siteCode) {
            return response()->json([
                'success' => false,
                'message' => 'Missing site code'
            ], 400);
        }

        // Option 1: Direct query if telegram_groups.site stores Id_Site
        $telegramGroup = TelegramGroup::where('site', $siteCode) // Assuming 'site' column stores Id_Site
            ->first(); // Use first() not get() for single record

        if (!$telegramGroup) {
            return response()->json([
                'success' => true,
                'data' => [
                    'chat_id' => '7359315398', // Default
                    'found' => false,
                    'message' => 'Using default chat ID - no Telegram group configured'
                ]
            ]);
        }

        return response()->json([
            'success' => true,
            'data' => [
                'chat_id' => $telegramGroup->chat_id,
                'found' => true,
            ]
        ]);
    }

    public function newCashier(Request $request)
    {
        // 1️⃣ Get month input (YYYY-MM), default to current month
        $monthInput = $request->month ?? date('Y-m');
        [$year, $month] = explode('-', $monthInput);

        // 2️⃣ Load invoices with site relationship - CORRECT SYNTAX
        $invoices = Invoice::with(['siteObject' => function ($query) {
            $query->select('Id_Site', 'Platform', 'Advisor');
        }])
            ->whereYear('month', $year)
            ->whereMonth('month', $month)
            ->orderBy('site')
            ->get();

        // 3️⃣ Map invoices to structured array
        $invoicesData = $invoices->map(function ($inv) {
            $siteModel = $inv->siteObject;
            return [
                'id' => $inv->id,
                'site' => $siteModel ? $siteModel->Id_Site : null,
                'platform' => $siteModel ? $siteModel->Platform : null,
                'advisor' => $siteModel ? $siteModel->Advisor : null,
                'month' => $inv->month ? $inv->month->format('Y-m') : null,
                'beginning_balance' => ($inv->invoice_type == 'school-program' || $inv->invoice_type == 'withdraw')
                    ? 1 * $inv->beginning_balance
                    : $inv->beginning_balance,
                'transaction_amount' => ($inv->invoice_type == 'school-program' || $inv->invoice_type == 'withdraw')
                    ? -1 * $inv->transaction_amount
                    : $inv->transaction_amount,
                'remain_amount' => $inv->remain_amount,
                'invoice_ref' => $inv->invoice_ref,
                'invoice_type' => $inv->invoice_type,
                'invoice_type_khmer_name' => $inv->invoice_type_khmer_name,
                'status' => $inv->status,
                'pictureQR' => $inv->pictureQR
                    ? asset('storage/' . $inv->pictureQR)
                    : null,
                'receipt_number' => $inv->receipt_number,
                'aba_status_code' => $inv->aba_status_code,
                'aba_amount' => $inv->aba_amount,
                'aba_date' => $inv->formatted_aba_date,
                'aba_transaction_id' => $inv->aba_transaction_id,
            ];
        });
        return response()->json($invoicesData);

    }
    public function exportInvoice(Request $request)
    {
        $monthInput = $request->month ?? date('Y-m');
        return Excel::download(new InvoicesMultiSheetExport($monthInput), "Invoices_$monthInput.xlsx");
    }
    public function exportInvoice1(Request $request)
    {
        $monthInput = $request->month ?? date('Y-m');
        [$year, $month] = explode('-', $monthInput);

        $invoices = Invoice::with(['siteObject' => function ($query) {
                $query->select('Id_Site', 'Platform', 'Advisor');
            }])
            ->whereYear('month', $year)
            ->whereMonth('month', $month)
            ->orderBy('site')
            ->get();

        $data = $invoices->map(function ($inv) {
            $siteModel = $inv->siteObject;
            return [
                'month'                  => $inv->month ? Carbon::parse($inv->month)->format('Y-m') : null,
                'cash_transaction_id'    => $inv->invoice_ref,
                'platform'               => $siteModel?->Platform,
                'site'                   => $siteModel?->Id_Site,
                'advisor'                => $siteModel?->Advisor,
                'date_transaction'       => $inv->month ? Carbon::parse($inv->month)->format('Y-m-d') : null,
                'beginning_balance'      => $inv->beginning_balance,
                'transaction_amount'     => ($inv->invoice_type == 'school-program')
                                                ? -1 * $inv->transaction_amount
                                                : $inv->transaction_amount,
                'invoice_ref'            => $inv->invoice_ref,
                'invoice_type'           => $inv->invoice_type,
                'remain_amount'          => $inv->remain_amount,
                'invoice_type_khmer_name'=> $inv->invoice_type_khmer_name,
                'status'                 => $inv->status,
                'payment_method'         => 'qr',
                'aba_status_code'        => $inv->aba_status_code,
                'aba_amount'             => $inv->aba_amount,
                'aba_date'               => $inv->formatted_aba_date,
                'aba_transaction_id'     => $inv->aba_transaction_id,
            ];
        })->values()->toArray();

        $inputFileName = storage_path('app/templates/excelTemplate.xlsx');

        $TBS = new \clsTinyButStrong;
        $ok = class_exists('clsOpenTBS', true);
        $TBS->OtbsMsExcelExplicitRef = false;
        $TBS->Plugin(\TBS_INSTALL, \OPENTBS_PLUGIN);
        $TBS->LoadTemplate($inputFileName, \OPENTBS_ALREADY_UTF8);
        $TBS->PlugIn(OPENTBS_SELECT_SHEET, 1);
        $TBS->SetOption("noerr", true);
        $TBS->MergeBlock('a', $data);
        $TBS->Show(OPENTBS_DOWNLOAD, "Invoices_{$monthInput}.xlsx");
    }
    public function exportSchool(Request $request)
    {
        $monthInput = $request->month ?? date('Y-m');
        return Excel::download(new InvoicesExport($monthInput), "Invoices_$monthInput.xlsx");
    }

    public function getInvoices()
    {
        $invoice = Invoice::with('site')->first();
        return response()->json($invoice->site);
    }
    public function generateQR()
    {
        $url = config('payway.api_url');
        $merchant_id = config('payway.merchant_id');
        $api_key = config('payway.api_key');
        $callback_url = config('payway.callback_url');

        $request_time = now('UTC')->format('YmdHis');
        $tran_id = "kriya" . time();
        $lifetime = 43200; // 12 hours in seconds
        $amount = 400;
        $currency = "KHR"; // ✅ KHR is supported
        $payment_option = "abapay_khqr";
        $purchase_type = "purchase";
        $qr_image_template = "template3_color";

        $hash = base64_encode(hash_hmac(
            'sha512',
            $request_time . $merchant_id . $tran_id . $amount . $purchase_type . $payment_option . $callback_url . $currency . $lifetime . $qr_image_template,
            $api_key,
            true
        ));

        $params = [
            "req_time" => $request_time,
            "merchant_id" => $merchant_id,
            "tran_id" => $tran_id,
            "amount" => $amount,
            "payment_option" => $payment_option,
            "currency" => $currency,
            "lifetime" => $lifetime,
            "qr_image_template" => $qr_image_template,
            "purchase_type" => $purchase_type,
            "callback_url" => $callback_url,
            "hash" => $hash
        ];

        // Send JSON properly
        $responseQR = Http::withHeaders([
            "Content-Type" => "application/json"
        ])->withBody(json_encode($params), 'application/json')
            ->post($url)
            ->json(); // already decoded JSON

        return response()->json($responseQR);
    }
    public function test123()
    {
        return response()->json([
            'success' => true,
            'message' => 'Test endpoint working'
        ]);
    }
    public function school(Request $request)
    {
        $monthInput = $request->month ?? date('Y-m');
        $isExcel = $request->has('excel');
        $monthArray = [
            '2025-11' => 22,
            '2025-12' => 26,
            '2026-01' => 25,
            '2026-02' => 24,
            '2026-03' => 26,
            '2026-04' => 14,
            '2026-05' => 23,
            '2026-06' => 25,
            '2026-07' => 27,
            '2026-08' => 26,
            '2026-09' => 0,
            '2026-10' => 0,
            '2026-11' => 0,
            '2026-12' => 0,
        ];
        $bottleNumber = $monthArray[$monthInput] ?? 0;
        [$year, $month1] = explode('-', $monthInput);
        $inputFileName = storage_path('app/templates/schoolProgramReport.xlsx');

        $sites = Site::select('Id_Site', 'Platform', 'school_program')
            ->whereNotIn('Id_Site', ['A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'A7', 'A8'])
            ->whereNotIn('Platform', ['Dead', 'Stop'])
            ->get();

        $siteIds = $sites->pluck('Id_Site')->toArray();

        $cashierSalesData = CashierSale::select(
            'site',
            DB::raw('COUNT(DISTINCT CASE WHEN quantity > 0 THEN sale_date END) as open_days_count'),
            DB::raw('SUM(quantity) as total_sales')
        )
            ->whereYear('sale_date', $year)
            ->whereMonth('sale_date', $month1)
            ->whereIn('site', $siteIds)
            ->where('type', 'wis')
            ->groupBy('site')
            ->get()
            ->keyBy('site');

        $dailySalesData = DailySales::select(
            'Id_Site',
            DB::raw('COUNT(*) as open_days_count'),
            DB::raw('SUM(WiS_Sales) as total_sales')
        )
            ->whereYear('Month', $year)
            ->whereMonth('Month', $month1)
            ->where('WiS_Sales', '>', 0)
            ->whereIn('Id_Site', $siteIds)
            ->groupBy('Id_Site')
            ->get()
            ->keyBy('Id_Site');

        $data = $sites->map(function ($site) use ($monthInput, $cashierSalesData, $dailySalesData, $bottleNumber) {
            $openDaysCount = 0;
            $totalSales = 0;
            $dataSource = '';

            if ($cashierSalesData->has($site->Id_Site)) {
                $cashierData = $cashierSalesData->get($site->Id_Site);
                $openDaysCount = $cashierData->open_days_count ?? 0;
                $totalSales = $cashierData->total_sales ?? 0;
                $dataSource = 'cashier_sales';
            } elseif ($dailySalesData->has($site->Id_Site)) {
                $dailyData = $dailySalesData->get($site->Id_Site);
                $openDaysCount = $dailyData->open_days_count ?? 0;
                $totalSales = $dailyData->total_sales ?? 0;
                $dataSource = 'DailySales';
            }

            $totalSchoolBudget = $site->school_program * $bottleNumber;
            $difference = $totalSchoolBudget - $totalSales;
            return [
                'site' => $site->Id_Site,
                'month' => $monthInput,
                'platform' => $site->Platform,
                'budget' => $site->school_program,
                'open_days_count' => $openDaysCount,
                'total_school_budget' => $totalSchoolBudget,
                'total_advisor_put_system' => $totalSales,
                'difference' => $difference,
                'data_source' => $dataSource,
            ];
        });

        // 👇 EXPORT LOGIC
        if ($isExcel) {
            $TBS = new \clsTinyButStrong();
            $ok = class_exists('clsOpenTBS', true); // hack to force class loading of TBS
            $TBS->Plugin(\TBS_INSTALL, \OPENTBS_PLUGIN);
            $TBS->OtbsMsExcelExplicitRef = false;
            $TBS->LoadTemplate($inputFileName, \OPENTBS_ALREADY_UTF8);
            $TBS->SetOption("noerr", true);
            $TBS->MergeBlock('a', $data);
            //$TBS->PlugIn(OPENTBS_DEBUG_XML_CURRENT);
            $filename = "SchoolProgram" . $request->month . ".xlsx";
            $TBS->Show(OPENTBS_DOWNLOAD, $filename);
        }

        // 👇 DEFAULT JSON RESPONSE
        return response()->json($data);
    }
    public function recordAssess(Request $request)
    {
        $s = $request->input('site');
        $data = Assessment::where('site', $s)
            ->orderBy('created_at', 'desc')->first();
        return response()->json($data);
    }
    public function testFinance(Request $request)
    {
        $month = $request->input('month'); // e.g. "2024-03"

        $invoices = Invoice::where('month', 'like', $month . '%')
            ->orderBy('site')
            ->get(['site', 'invoice_type', 'beginning_balance', 'remain_amount']);

        // Group by site
        $grouped = $invoices->groupBy('site')->map(function ($rows, $site) {
            return [
                'site'  => $site,
                'rows'  => $rows,
                'total' => $rows->sum('beginning_balance'),
            ];
        })->values();

        return response()->json($grouped);
    }
}
