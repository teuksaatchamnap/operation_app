<?php

namespace App\Exports\Sheets;

use Illuminate\Support\Collection;
use Maatwebsite\Excel\Concerns\FromCollection;
use Maatwebsite\Excel\Concerns\WithHeadings;
use Maatwebsite\Excel\Concerns\WithStyles;
use Maatwebsite\Excel\Concerns\WithTitle;
use PhpOffice\PhpSpreadsheet\Style\Border;
use PhpOffice\PhpSpreadsheet\Style\Fill;
use PhpOffice\PhpSpreadsheet\Worksheet\Worksheet;

class BottlePurchasesSheet implements FromCollection, WithHeadings, WithStyles, WithTitle
{
    public function __construct(private array $data) {}

    public function title(): string
    {
        return 'Bottle Purchases';
    }

    public function headings(): array
    {
        return ['Period', 'Bottles'];
    }

    public function collection(): Collection
    {
        $ytd = $this->data['ytd'] ?? 0;
        $lastYear = $this->data['last_year'] ?? 0;
        $diff = $ytd - $lastYear;
        $pct = $lastYear > 0 ? round(($diff / $lastYear) * 100, 1) : 0;

        return collect([
            ['period' => 'YTD', 'bottles' => $ytd],
            ['period' => 'Previous Year', 'bottles' => $lastYear],
            ['period' => 'YTD vs Previous Year', 'bottles' => ($diff >= 0 ? '+' : '').$diff.' ('.$pct.'%)'],
        ]);
    }

    public function styles(Worksheet $sheet): array
    {
        return [
            1 => [
                'font' => ['bold' => true, 'size' => 11, 'color' => ['rgb' => 'FFFFFF']],
                'fill' => ['fillType' => Fill::FILL_SOLID, 'startColor' => ['rgb' => '1976D2']],
                'borders' => [
                    'bottom' => ['borderStyle' => Border::BORDER_MEDIUM, 'color' => ['rgb' => '0D47A1']],
                ],
            ],
        ];
    }
}
