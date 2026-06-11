<?php

namespace App\Jobs;

use App\Models\CashierNotification;
use App\Models\Expense;
use App\Models\Invoice;
use App\Models\InvoicesRecord;
use App\Models\Site;
use App\Models\SiteBalance;
use App\Models\TelegramGroup;
use Illuminate\Bus\Queueable;
use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Foundation\Bus\Dispatchable;
use Illuminate\Queue\InteractsWithQueue;
use Illuminate\Queue\SerializesModels;
use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Log;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Storage;
use Spatie\Browsershot\Browsershot;

class CheckAbaPaymentJob implements ShouldQueue
{
    use Dispatchable, InteractsWithQueue, Queueable, SerializesModels;

    /**
     * Create a new job instance.
     */
    protected $tran_id;

    public function __construct($tran_id)
    {
        $this->tran_id = $tran_id;
    }

    /**
     * Execute the job.
     */
    public function handle(): void
    {
        $tran_id = $this->tran_id;
        Log::info('Starting ABA Payment Check Job', ['tran_id' => $tran_id]);
        // 🔹 Extract values from tran_id (format: S12-2026-04-21233-SD)
        $parts = explode('-', $tran_id);
        $s = $parts[0];
        $y = $parts[1];
        $m = $parts[2];

        $merchant_id = config('payway.merchant_id');
        $api_key = config('payway.api_key');

        // ✅ SAME req_time for hash and request
        $req_time = now()->format('YmdHis');

        $b4hash = $req_time . $merchant_id . $tran_id;
        $hash = base64_encode(hash_hmac('sha512', $b4hash, $api_key, true));

        // 🔹 Call ABA API
        $response = Http::withHeaders([
            'Content-Type' => 'application/json'
        ])->post('https://checkout.payway.com.kh/api/payment-gateway/v1/payments/check-transaction-2', [
            "req_time" => $req_time,
            "merchant_id" => $merchant_id,
            "tran_id" => $tran_id,
            "hash" => $hash
        ]);

        $result = $response->json();
        if ($response->failed()) {
            Log::error('ABA API request failed', [
                'tran_id' => $tran_id,
                'status' => $response->status(),
                'body' => $response->body()
            ]);
            return;
        }

        // 🔹 Validate response
        if (!isset($result['data']['payment_status_code'])) {
            Log::error('Invalid ABA response', $result);
            return;
        }

        $code = $result['data']['payment_status_code'];

        // 🔁 Retry if still pending
        if ($code == 2) {
            Log::info('ABA still pending, retrying...', ['tran_id' => $tran_id]);

            self::dispatch($tran_id)->delay(now()->addSeconds(10));
            return;
        }

        // 🔹 YOUR ORIGINAL STATUS LOGIC (UNCHANGED)
        $aba_status_code = '';
        if ($code == 0 || $code == '0') {
            $aba_status_code = 'APPROVED';
        } else if ($code == 2 || $code == '2') {
            $aba_status_code = 'PENDING';
        } else if ($code == 3 || $code == '3') {
            $aba_status_code = 'DECLINDED';
        } else if ($code == 4 || $code == '4') {
            $aba_status_code = 'REFUNDED';
        } else {
            $aba_status_code = 'CANCELLED';
        }

        // 🔹 YOUR ORIGINAL DB LOGIC (UNCHANGED)
        $invoicesAll = Invoice::where('site', $s)
            ->whereYear('month', $y)
            ->whereMonth('month', $m)
            ->get();

        $schoolProgramSum = $invoicesAll->where('invoice_type', 'school-program')->sum('beginning_balance');
        $totalExceptSchoolProgram = $invoicesAll->whereNotIn('invoice_type', ['school-program', 'saving', 'withdraw'])->sum('beginning_balance');
        $totalRemain = $totalExceptSchoolProgram - $schoolProgramSum;

        $aba_amount = $result['data']['total_amount'];
        $aba_date = $result['data']['transaction_date'];
        $processType = substr(strrchr($tran_id, '-'), 1);
        // ✅ YOUR ORIGINAL COMPARISON (UNCHANGED)
        $expenseType = ['Consumable Bottle'=>['bottle_invoice','production'],'debts'=>['debt','debt'],'Delivery Program Fee'=>['delivery_program_fee','production']
        ,'Entrepreneur Contribution'=>['entrepreneur_contribution','contribution'],'school-program'=>['WinS_invoice',''],'Stock Invoice'=>['stock_ts','production']
        ,'Technical Intervention'=>['technical intervention','technical'],'Water Quality Alert'=>['water quality alert','technical']];
        if ($totalRemain == $aba_amount)
        {
            Invoice::where('site', $s)
                ->whereYear('month', $y)
                ->whereMonth('month', $m)
                ->whereNotIn('invoice_type', ['saving', 'withdraw'])
                ->update([
                    'aba_status_code' => $aba_status_code,
                    'aba_amount' => $aba_amount,
                    'aba_date' => $aba_date,
                    'aba_transaction_id' => $tran_id,
                    'transaction_amount' => DB::raw('beginning_balance'),
                    'status' => 'settle',
                    'remain_amount' => 0
                ]);
            // Insert expense records for invoices whose type maps to an expense category
            foreach ($invoicesAll as $invoice)
            {
                if (isset($expenseType[$invoice->invoice_type])) {
                    [$refExpense, $categoryExpense] = $expenseType[$invoice->invoice_type];
                    Expense::updateOrCreate(
                        [
                            'Id_Site'      => $invoice->site,
                            'Month'        => $invoice->month,
                            'Ref_expenses' => $refExpense,
                        ],
                        [
                            'Amount_expenses'   => $invoice->beginning_balance,
                            'Paid'              => $invoice->beginning_balance,
                            'Category_expenses' => $categoryExpense,
                        ]
                    );
                }
            }
        }
        else if ($aba_amount > $totalRemain)
        {
            foreach ($invoicesAll as $invoice)
            {
                if (isset($expenseType[$invoice->invoice_type])) {
                    [$refExpense, $categoryExpense] = $expenseType[$invoice->invoice_type];
                    Expense::updateOrCreate(
                        [
                            'Id_Site'      => $invoice->site,
                            'Month'        => $invoice->month,
                            'Ref_expenses' => $refExpense,
                        ],
                        [
                            'Amount_expenses'   => $invoice->beginning_balance,
                            'Paid'              => $invoice->beginning_balance,
                            'Category_expenses' => $categoryExpense,
                        ]
                    );
                }
            }
            if ($processType == 'ID')
            {
                $remainMoney = $aba_amount - $totalRemain;
                $currentBalance = SiteBalance::select('balance','beginning_balance')
                    ->where('site', $s)->first();
                $updateBalance = $currentBalance->balance + $remainMoney;
                SiteBalance::where('site', $s)->update(['beginning_balance' => $updateBalance]);
                Invoice::where('site', $s)
                ->whereYear('month', $y)
                ->whereMonth('month', $m)
                ->update([
                    'aba_status_code' => $aba_status_code,
                    'aba_amount' => $aba_amount,
                    'aba_date' => $aba_date,
                    'aba_transaction_id' => $tran_id,
                    'transaction_amount' => DB::raw('beginning_balance'),
                    'status' => 'settle',
                    'remain_amount' => 0
                ]);
                $invoice = new Invoice();
                $invoice->site = $s;
                $invoice->month = $y . '-' . $m . '-01';
                $invoice->beginning_balance = $currentBalance->balance;
                $invoice->transaction_amount = $remainMoney;
                $invoice->remain_amount = $updateBalance;
                $invoice->status = 'settle';
                $invoice->invoice_type_khmer_name = 'សន្សំ';
                $invoice->invoice_type = 'saving';
                $invoice->receipt_number = $tran_id;
                $invoice->invoice_ref = $tran_id;
                $invoice->aba_status_code = "APPROVED";
                $invoice->aba_amount = $remainMoney;
                $invoice->aba_date = $aba_date;
                $invoice->aba_transaction_id = $tran_id;
                $invoice->save();
            }
        }
        else if ($aba_amount < $totalRemain)
        {
            if ($processType == 'PI')
                {
                    Invoice::where('site', $s)
                        ->whereYear('month', $y)
                        ->whereMonth('month', $m)
                        ->update([
                            'aba_status_code' => $aba_status_code,
                            'aba_amount' => $aba_amount,
                            'aba_date' => $aba_date,
                            'aba_transaction_id' => $tran_id,
                        ]);
                }
        }

        if ($processType == 'SD')
                {
                    $currentBalance = SiteBalance::select('balance','beginning_balance')
                        ->where('site', $s)->first();
                    $updateBalance = $currentBalance->balance + $aba_amount;
                    SiteBalance::where('site', $s)->update(['beginning_balance' => $updateBalance]);
                    $invoice = new Invoice();
                    $invoice->site = $s;
                    $invoice->month = $y.'-'.$m.'-01';
                    $invoice->beginning_balance = $currentBalance->balance;
                    $invoice->transaction_amount = $aba_amount;
                    $invoice->remain_amount = $updateBalance;
                    $invoice->status = 'saving';
                    $invoice->invoice_type_khmer_name ='សន្សំ';
                    $invoice->invoice_type = 'saving';
                    $invoice->receipt_number = $tran_id;
                    $invoice->invoice_ref = $tran_id;
                    $invoice->save();
                }

        InvoicesRecord::where('transaction_id', $tran_id)
                ->update([
                    'payment_status' => "APPROVED",
                    'payment_date' => date('Y-m-d H:i:s', strtotime($aba_date))
                ]);
            Log::info('ABA Payment matched and settled', ['tran_id' => $tran_id]);
            // check data in site and site balance
            $sub = DB::table('invoices')->select('site','month',
                                DB::raw("SUM(CASE WHEN invoice_type IN ('school-program', 'withdraw')
                                        THEN beginning_balance
                                        ELSE 0
                                    END) as total_school_withdraw"),

                                DB::raw("SUM(CASE WHEN invoice_type NOT IN ('school-program', 'withdraw','saving')
                                        THEN beginning_balance
                                        ELSE 0
                                    END) as total_invoice
                                "),

                                DB::raw("SUM(CASE WHEN invoice_type NOT IN ('school-program', 'withdraw','saving')
                                        THEN transaction_amount
                                        ELSE 0
                                    END) as total_amount_paid
                                "),

                                DB::raw("SUM(CASE WHEN invoice_type = 'school-program'
                                        THEN beginning_balance
                                        ELSE 0
                                    END) as school
                                "),
                                DB::raw("SUM(CASE WHEN invoice_type = 'withdraw'
                                        THEN transaction_amount
                                        ELSE 0
                                    END) as withdraw
                                "),
                                DB::raw("SUM(CASE WHEN invoice_type = 'saving'
                                        THEN transaction_amount
                                        ELSE 0
                                    END) as saving
                                ")
                            )
                            ->where('site', $s)
                            ->whereYear('month', $y)
                            ->whereMonth('month', $m)
                            ->groupBy('site', 'month');

                        $result = DB::query()
                            ->fromSub($sub, 't')
                            ->selectRaw("site,month,total_school_withdraw,total_invoice,saving,withdraw,school,
                                (total_invoice - school) AS total_pay_by_entre,
                                (total_amount_paid - total_school_withdraw) AS cashReceived,
                                ((total_invoice - school) - (total_amount_paid - total_school_withdraw)) AS remain_amount
                            ")
                            ->first();

            $lastUpdateBalance = SiteBalance::select('balance', 'beginning_balance')
                ->where('site', $s)->first();

            $siteInfo = Site::select('Platform', 'Entrepreneur_Khmer_Name')
                ->where('Id_Site', $s)->first();

            $preparedByMap = [
                'PP'  => 'មន​ សោវី',
                'KSP' => 'មន​ សោវី',
                'BTB' => 'នូ ចំរើន',
                'KC'  => 'ហ៊ន ស្រីរត្ន័',
                'SR'  => 'ហ៊ាង ប៉ោឡេង',
            ];
            $platform    = $siteInfo->Platform ?? '';
            $preparedBy  = $preparedByMap[$platform] ?? '________________';
            $customerName = $siteInfo->Entrepreneur_Khmer_Name ?? '';

            $savingOrWithdrawInvoice = $invoicesAll->whereIn('invoice_type', ['saving', 'withdraw'])->first();
            $savingType   = $savingOrWithdrawInvoice ? $savingOrWithdrawInvoice->invoice_type : null;
            $savingAmount = $savingOrWithdrawInvoice ? $savingOrWithdrawInvoice->transaction_amount : 0;

            // Generate PNG invoice for settled payment
            if ($result) {
                $invoiceData = [
                    'invoiceNumber'             => $s.$y.'-'.$m,
                    'customerName'              => $customerName,
                    'site'                      => $s,
                    'transactionDate'           => now()->format('Y-m-d H:i:s'),
                    'amountEntrepreneurPayToTS' => $result?->total_pay_by_entre ?? 0,
                    'invoiceTotal'              => $result?->total_invoice ?? 0,
                    'schoolBalance'             => $result?->school ?? 0,
                    'cashReceived'              => $result?->cashReceived ?? 0,
                    'receiveMoney'              => $aba_amount,
                    'totalRemainingInvoice'     => $result?->remain_amount ?? 0,
                    'withdraw'                  => $result?->withdraw ?? 0,
                    'saving'                    => $result?->saving ?? 0,
                    'remaining'                 => ($result?->total_invoice ?? 0) - $aba_amount,
                    'beginningMonthBalance'     => $lastUpdateBalance->beginning_balance ?? 50,
                    'endingBalance'             => $lastUpdateBalance->balance ?? 0,
                    'preparedBy'                => $preparedBy,
                ];

                $dashCount = substr_count($tran_id, '-');
                if ($dashCount == 2 || $processType == 'ID') {
                    $invoicePath = $this->generateAndStoreInvoice($invoiceData, $tran_id, $s);
                    if ($invoicePath) {
                        Log::info('Invoice PNG generated successfully', [
                            'tran_id' => $tran_id,
                            'path'    => $invoicePath
                        ]);
                    }
                }
            } else {
                Log::warning('No invoice data found for site/month, skipping invoice generation', [
                    'tran_id' => $tran_id,
                    'site'    => $s,
                ]);
            }
    }

    /**
     * Generate PNG invoice from blade view and store it
     *
     * @param array $data Invoice data
     * @param string $tran_id Transaction ID for filename
     * @return string|null Path to stored invoice or null on failure
     */
    public function generateAndStoreInvoice1($data, $tran_id)
    {
        try {
            // Render the blade view to HTML
            $html = view('invoices.payment', $data)->render();

            // Generate filename
            $filename = 'invoice_' . $tran_id . '_' . time() . '.png';
            $storagePath = 'invoices/' . $filename;
            $fullPath = storage_path('app/public/' . $storagePath);

            // Ensure directory exists
            $directory = dirname($fullPath);
            if (!file_exists($directory)) {
                mkdir($directory, 0755, true);
            }

            // Use Browsershot to convert HTML to PNG
            Browsershot::html($html)
                ->noSandbox()
                ->windowSize(800, 1000)
                ->deviceScaleFactor(2)
                ->fullPage()
                ->save($fullPath);

            Log::info('Invoice generated successfully', [
                'tran_id' => $tran_id,
                'path' => $storagePath
            ]);

            return $storagePath;
        } catch (\Exception $e) {
            Log::error('Failed to generate invoice', [
                'tran_id' => $tran_id,
                'error' => $e->getMessage(),
                'trace' => $e->getTraceAsString()
            ]);

            return null;
        }
    }
    public function generateAndStoreInvoice($data, $tran_id,$s)
    {
        try {
            // 1. Render blade to HTML
            $html = view('invoices.payment', $data)->render();

            // 2. Generate image as binary (no file saved)
            $image = Browsershot::html($html)
                ->noSandbox()
                ->windowSize(800, 1000)
                ->deviceScaleFactor(2)
                ->fullPage()
                ->screenshot(); // 👈 THIS returns raw image data

            // 3. Send to Telegram
            //$botToken = config('services.telegram.bot_token');
            $botToken = env('TELEGRAM_BOT_TOKEN');
            $c = TelegramGroup::select('chat_id')->where('site',$s)->first();
            $chatId= $c->chat_id;
            $notification = CashierNotification::where("key", "cash-receipt")->first();
           // dd("Your chatID : ".$chatId);
            //$chatId = config('services.telegram.chat_id');
            //$chatId = -1003717360655;

            $response = Http::attach(
                'photo',
                $image,
                'invoice.png'
            )->post("https://api.telegram.org/bot{$botToken}/sendPhoto", [
                'chat_id' => $chatId,
                'caption' => $notification->message ?? "ជំរាបសួរ/សួរស្តីសហគ្រិន នេះគឺជាបង្កាន់ដៃបង់ប្រាក់របស់អ្នកជាមួយនិងឯកសារភ្ជាប់"
            ]);

            Log::info('Invoice sent to Telegram', [
                'tran_id' => $tran_id,
                'telegram_status' => 'invoice sent',
                //'telegram_response' => $response->json()
            ]);

            if (!empty($notification->audio)) {
                $audioPath = storage_path('app/public/' . $notification->audio);
                if (file_exists($audioPath)) {
                    Http::attach(
                        'audio',
                        file_get_contents($audioPath),
                        basename($audioPath)
                    )->post("https://api.telegram.org/bot{$botToken}/sendAudio", [
                        'chat_id' => $chatId,
                    ]);

                    Log::info('Audio sent to Telegram', [
                        'tran_id' => $tran_id,
                        'audio' => $notification->audio,
                    ]);
                } else {
                    Log::warning('Audio file not found', ['path' => $audioPath]);
                }
            }

            return true;
        } catch (\Exception $e) {
            Log::error('Failed to generate/send invoice', [
                'tran_id' => $tran_id,
                'error' => $e->getMessage(),
            ]);

            return false;
        }
    }
}
