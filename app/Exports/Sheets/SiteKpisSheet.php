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

class SiteKpisSheet implements FromCollection, WithHeadings, WithStyles, WithTitle
{
    public function __construct(private array $data) {}

    public function title(): string
    {
        return 'Site KPIs';
    }

    public function headings(): array
    {
        return ['KPI', 'Value', 'Objective', 'Status'];
    }

    public function collection(): Collection
    {
        $rows = [];
        foreach ($this->data as $def) {
            $val = $def['value'];
            $obj = $def['objective'];

            $status = '-';
            if (is_numeric($val) && is_numeric($obj) && $obj > 0) {
                $status = (float) $val >= (float) $obj ? 'Met' : 'Unmet';
            }

            $rows[] = [
                'kpi' => $def['label'],
                'value' => $val,
                'objective' => $obj,
                'status' => $status,
            ];
        }

        return collect($rows);
    }

    public function styles(Worksheet $sheet): array
    {
        return [
            1 => [
                'font' => ['bold' => true, 'size' => 12, 'color' => ['rgb' => 'FFFFFF']],
                'fill' => ['fillType' => Fill::FILL_SOLID, 'startColor' => ['rgb' => '1976D2']],
                'borders' => [
                    'bottom' => ['borderStyle' => Border::BORDER_MEDIUM, 'color' => ['rgb' => '0D47A1']],
                ],
            ],
        ];
    }
}
