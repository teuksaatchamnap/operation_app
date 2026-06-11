<?php

namespace App\Exports;

use App\Models\Invoice;
use Carbon\Carbon;
use Illuminate\Support\Collection;
use Maatwebsite\Excel\Concerns\FromCollection;
use Maatwebsite\Excel\Concerns\WithHeadings;
use Maatwebsite\Excel\Concerns\WithTitle;
use Maatwebsite\Excel\Concerns\WithEvents;
use Maatwebsite\Excel\Concerns\WithMultipleSheets;
use Maatwebsite\Excel\Events\AfterSheet;
use PhpOffice\PhpSpreadsheet\Style\Fill;
use PhpOffice\PhpSpreadsheet\Style\Alignment;

class InvoicesExport implements WithMultipleSheets
{
    protected $monthInput;

    public function __construct($monthInput)
    {
        $this->monthInput = $monthInput;
    }

    public function sheets(): array
    {
        [$year, $month] = explode('-', $this->monthInput);

        // Single query — pass pre-grouped collections to each sheet
        $invoices = Invoice::with(['siteObject' => function ($q) {
                $q->select('Id_Site', 'Platform', 'Advisor');
            }])
            ->whereYear('month', $year)
            ->whereMonth('month', $month)
            ->orderBy('site')
            ->orderBy('aba_transaction_id')
            ->get();

        $grouped = $invoices->groupBy(function ($inv) {
            return $inv->siteObject?->Advisor ?? 'Unknown';
        });

        $sheets = [];

        // Main sheet with all data combined
        $sheets[] = new InvoicesAdvisorSheet('All Data', $invoices);

        foreach ($grouped->sortKeys() as $advisor => $advisorInvoices) {
            $sheets[] = new InvoicesAdvisorSheet($advisor, $advisorInvoices);
        }

        return $sheets;
    }
}

class InvoicesAdvisorSheet implements FromCollection, WithHeadings, WithTitle, WithEvents
{
    protected $advisor;
    protected $invoices;
    protected $totalRowNumbers = [];
    protected $grandTotalRow   = null;

    public function __construct(string $advisor, Collection $invoices)
    {
        $this->advisor  = $advisor;
        $this->invoices = $invoices;
    }

    public function title(): string
    {
        return mb_substr(preg_replace('/[\/\\\?\*\[\]:]/', '', $this->advisor), 0, 31);
    }

    public function collection()
    {
        $rows          = [];
        $rowIndex      = 2;
        $grandTxnTotal = 0;
        $grandAbaTotal = 0;

        $bySite = $this->invoices->groupBy(fn ($inv) =>
            $inv->siteObject?->Id_Site ?? '__unknown__'
        );

        foreach ($bySite as $siteInvoices) {
            $siteTxnTotal = 0;
            $siteAbaTotal = 0;
            $siteModel    = $siteInvoices->first()->siteObject;

            $byTxn = $siteInvoices->groupBy('aba_transaction_id');

            foreach ($byTxn as $txnId => $txnInvoices) {
                $txnTotal  = 0;
                $abaAmount = null;
                $isFirst   = true;

                foreach ($txnInvoices as $inv) {
                    $txnAmount = ($inv->invoice_type == 'school-program' || $inv->invoice_type == 'withdraw')
                        ? -1 * $inv->transaction_amount
                        : $inv->transaction_amount;

                    $txnTotal += $txnAmount;

                    if ($isFirst) {
                        $abaAmount = $inv->aba_amount;
                        $isFirst   = false;
                    }

                    $firstInTxn = $txnInvoices->first()->id === $inv->id;

                    $rows[] = [
                        'month'                   => $inv->month ? Carbon::parse($inv->month)->format('Y-m') : null,
                        'cash_transaction_id'     => $inv->aba_transaction_id,
                        'platform'                => $siteModel?->Platform,
                        'site'                    => $siteModel?->Id_Site,
                        'advisor'                 => $siteModel?->Advisor,
                        'date_transaction'        => $inv->aba_date ? Carbon::parse($inv->aba_date)->format('Y-m-d') : null,
                        'beginning_balance'       => ($inv->invoice_type == 'school-program' || $inv->invoice_type == 'withdraw')
                                                        ? 1 * $inv->beginning_balance
                                                        : $inv->beginning_balance,
                        'transaction_amount'      => $txnAmount,
                        'invoice_ref'             => $inv->invoice_ref,
                        'invoice_type'            => $inv->invoice_type,
                        'remain_amount'           => $inv->remain_amount,
                        'invoice_type_khmer_name' => $inv->invoice_type_khmer_name,
                        'status'                  => $inv->status,
                        'payment_method'          => 'qr',
                        'aba_status_code'         => $firstInTxn ? $inv->aba_status_code : null,
                        'aba_amount'              => $firstInTxn ? $inv->aba_amount : null,
                        'aba_date'                => $firstInTxn ? $inv->formatted_aba_date : null,
                        'aba_transaction_id'      => $firstInTxn ? $txnId : null,
                    ];
                    $rowIndex++;
                }

                $siteTxnTotal += $txnTotal;
                $siteAbaTotal += (float) ($abaAmount ?? 0);
            }

            // Site total row
            $this->totalRowNumbers[] = $rowIndex;
            $rows[] = [
                'month'                   => null,
                'cash_transaction_id'     => null,
                'platform'                => null,
                'site'                    => $siteModel?->Id_Site,
                'advisor'                 => null,
                'date_transaction'        => null,
                'beginning_balance'       => 'Total :',
                'transaction_amount'      => number_format($siteTxnTotal),
                'invoice_ref'             => null,
                'invoice_type'            => null,
                'remain_amount'           => null,
                'invoice_type_khmer_name' => null,
                'status'                  => null,
                'payment_method'          => null,
                'aba_status_code'         => null,
                'aba_amount'              => number_format($siteAbaTotal),
                'aba_date'                => null,
                'aba_transaction_id'      => null,
            ];
            $rowIndex++;

            $grandTxnTotal += $siteTxnTotal;
            $grandAbaTotal += $siteAbaTotal;
        }

        // Grand total row
        $this->grandTotalRow = $rowIndex;
        $rows[] = [
            'month'                   => null,
            'cash_transaction_id'     => null,
            'platform'                => null,
            'site'                    => null,
            'advisor'                 => null,
            'date_transaction'        => null,
            'beginning_balance'       => 'Grand Total :',
            'transaction_amount'      => number_format($grandTxnTotal),
            'invoice_ref'             => null,
            'invoice_type'            => null,
            'remain_amount'           => null,
            'invoice_type_khmer_name' => null,
            'status'                  => null,
            'payment_method'          => null,
            'aba_status_code'         => 'Grand Total :',
            'aba_amount'              => number_format($grandAbaTotal),
            'aba_date'                => null,
            'aba_transaction_id'      => null,
        ];

        return collect($rows);
    }

    public function headings(): array
    {
        return [
            'Month', 'Cash Transaction ID', 'Platform', 'Site', 'Advisor',
            'Date Transaction', 'Beginning Balance', 'Transaction Amount',
            'Invoice Ref', 'Invoice Type', 'Remain Amount', 'Invoice Type Khmer Name',
            'Status', 'Payment Method', 'ABA Status Code', 'ABA Amount',
            'ABA Date', 'ABA Transaction ID',
        ];
    }

    public function registerEvents(): array
    {
        return [
            AfterSheet::class => function (AfterSheet $event) {
                $sheet   = $event->sheet->getDelegate();
                $lastCol = 'R';

                // Header row — green
                $sheet->getStyle('A1:' . $lastCol . '1')->applyFromArray([
                    'font'      => ['bold' => true, 'size' => 12, 'color' => ['rgb' => 'FFFFFF']],
                    'fill'      => ['fillType' => Fill::FILL_SOLID, 'startColor' => ['rgb' => '4CAF50']],
                    'alignment' => ['horizontal' => Alignment::HORIZONTAL_CENTER, 'vertical' => Alignment::VERTICAL_CENTER],
                ]);

                // Site total rows — dark blue
                foreach ($this->totalRowNumbers as $row) {
                    $sheet->getStyle('A' . $row . ':' . $lastCol . $row)->applyFromArray([
                        'font' => ['bold' => true, 'size' => 11, 'color' => ['rgb' => 'FFFFFF']],
                        'fill' => ['fillType' => Fill::FILL_SOLID, 'startColor' => ['rgb' => '1565C0']],
                    ]);
                }

                // Grand total row — dark green
                if ($this->grandTotalRow) {
                    $row = $this->grandTotalRow;
                    $sheet->getStyle('A' . $row . ':' . $lastCol . $row)->applyFromArray([
                        'font' => ['bold' => true, 'size' => 12, 'color' => ['rgb' => 'FFFFFF']],
                        'fill' => ['fillType' => Fill::FILL_SOLID, 'startColor' => ['rgb' => '1B5E20']],
                    ]);
                }
            },
        ];
    }
}
