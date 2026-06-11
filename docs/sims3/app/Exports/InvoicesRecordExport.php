<?php

namespace App\Exports;

use App\Models\InvoicesRecord;
use Carbon\Carbon;
use Maatwebsite\Excel\Concerns\FromCollection;
use Maatwebsite\Excel\Concerns\WithHeadings;
use Maatwebsite\Excel\Concerns\WithTitle;
use Maatwebsite\Excel\Concerns\WithStyles;
use PhpOffice\PhpSpreadsheet\Worksheet\Worksheet;

class InvoicesRecordExport implements FromCollection, WithHeadings, WithTitle, WithStyles
{
    protected $year;
    protected $month;

    public function __construct($monthInput)
    {
        [$this->year, $this->month] = explode('-', $monthInput);
    }

    public function collection()
    {
        return InvoicesRecord::whereYear('month', $this->year)
            ->whereMonth('month', $this->month)
            ->orderBy('site')
            ->get()
            ->map(function ($record) {
                return [
                    'site'           => $record->site,
                    'month'          => $record->month ? Carbon::parse($record->month)->format('Y-m') : null,
                    'transaction_id' => $record->transaction_id,
                    'amount'         => $record->amount,
                    'issue_date'     => $record->issue_date,
                    'payment_status' => $record->payment_status,
                    'payment_date'   => $record->payment_date,
                ];
            });
    }

    public function headings(): array
    {
        return [
            'Site',
            'Month',
            'Transaction ID',
            'Amount',
            'Issue Date',
            'Payment Status',
            'Payment Date',
        ];
    }

    public function title(): string
    {
        return 'Invoice Records';
    }

    public function styles(Worksheet $sheet)
    {
        return [
            1 => [
                'font' => [
                    'bold' => true,
                    'size' => 14,
                    'color' => ['rgb' => 'FFFFFF'],
                ],
                'fill' => [
                    'fillType' => \PhpOffice\PhpSpreadsheet\Style\Fill::FILL_SOLID,
                    'startColor' => ['rgb' => '1976D2'],
                ],
                'alignment' => [
                    'horizontal' => \PhpOffice\PhpSpreadsheet\Style\Alignment::HORIZONTAL_CENTER,
                    'vertical'   => \PhpOffice\PhpSpreadsheet\Style\Alignment::VERTICAL_CENTER,
                ],
            ],
        ];
    }
}
