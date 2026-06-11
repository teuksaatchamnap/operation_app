<?php

namespace App\Console\Commands;

use App\Models\Technical;
use Illuminate\Console\Command;
use Illuminate\Support\Facades\Mail;
use App\Mail\FA;
use App\Models\SaleTeam;
use App\Models\User;
use Carbon\Carbon;
use Illuminate\Support\Facades\DB;

class SendEmailsWithAttachment extends Command
{
    /**
     * The name and signature of the console command.
     *
     * @var string
     */
    protected $signature = 'app:send-emails-with-attachment';

    /**
     * The console command description.
     *
     * @var string
     */
    protected $description = 'Command description';

    /**
     * Execute the console command.
     */
    public function handle()
    {
        // command to run task: php artisan schedule:work. this work in local
        $today = Carbon::now();  // Get current date and time
        $previousMonth = $today->subMonth();  // Subtract one month
        $inputFileName = storage_path('app/templates/saleTeamConsolidate.xlsx');
        // $inter = SaleTeam::select('site','sale_type', DB::raw('SUM(free) as free,SUM(refill) as refill,SUM(new_bottle) as new_bottle,SUM(lending_bottle)
        //                      as lending_bottle, SUM(free)+SUM(refill)+SUM(new_bottle)+SUM(lending_bottle) as total_bottle'),DB::raw('count(customer) as customer'))
        //     ->whereMonth('sale_date', date('m', strtotime($previousMonth)))
        //     ->whereYear('sale_date', date('Y', strtotime($previousMonth)))
        //     ->where ('site','!=','')
        //     ->orderBy('sale_date','desc')
        //     ->groupBy('site','sale_type')
        //     ->get();
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
            ->whereMonth('st.sale_date', date('m', strtotime($previousMonth)))
            ->whereYear('st.sale_date', date('Y', strtotime($previousMonth)))
            ->where('st.site', '!=', '')
            ->groupBy('st.site', 'st.sale_type', 's.Platform')
            ->orderBy('st.sale_date', 'desc')
            ->get();
        $data = array();

        foreach ( $inter as $sale )
        {
            $sale['month'] = $previousMonth->format('Y-m');
            if ($sale->sale_type=="opening_site")
            {
                $sale['target']= 500;
                $sale['rate'] = ($sale->customer/500) ;
            }
            else{
                $sale['target']= 150;
                $sale['rate'] = ($sale->customer/150) ;
            }
            $data[] = $sale->toArray();

        }

        // $inter1= SaleTeam::whereMonth('sale_date', date('m', strtotime($previousMonth)))
        // ->whereYear('sale_date', date('Y', strtotime($previousMonth)))
        // ->orderBy('sale_date','desc')
        // ->get();
        $inter1 = SaleTeam::from('sale_team as st')
            ->select('st.*', 's.Platform')
            ->join('Sites as s', 'st.site', '=', 's.Id_Site')
            ->whereMonth('st.sale_date', date('m', strtotime($previousMonth)))
            ->whereYear('st.sale_date', date('Y', strtotime($previousMonth)))
            ->orderBy('st.sale_date', 'desc')
            ->get();
        $data2= array();
        foreach($inter1 as $sale)
        {
            $data2[]= $sale->toArray();
        }
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
        $TBS->Show(OPENTBS_STRING); // terminate the merging without leaving the script nor to display the result
        $result = $TBS->Source;

        $recipients = User::whereJsonContains('permissions', 'Sale:receive_sale_monthly_report')
                        ->pluck('email') // Assuming the email field is named 'email'
                        ->toArray();
        $additionalRecipients = ['info@teuksaat1001.com'];
        $allRecipients = array_unique(array_merge($recipients, $additionalRecipients));
        //\Log::info('Recipients: ' . json_encode($allRecipients));
        $recipients1 = ['chamnap.keo@teuksaat1001.com'];
        $recipients2 = ['chamnap.keo@teuksaat1001.com','rithy.m@teuksaat1001.com',
        'amandine.chaussinand@teuksaat1001.com','yet.y@teuksaat1001.com','bun.ph@teuksaat1001.com','kimhong.p@teuksaat1001.com'
        ,'lim.t@teuksaat1001.com','mongkul.s@teuksaat1001.com','sousdey.y@teuksaat1001.com','reaksmey.p@teuksaat1001.com'];
        Mail::to($recipients2)->send(new FA($result));
    }
}
