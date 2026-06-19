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

class ProfitLossSheet implements FromCollection, WithHeadings, WithStyles, WithTitle
{
    public function __construct(private array $data) {}

    public function title(): string
    {
        return 'Profit & Loss';
    }

    public function headings(): array
    {
        $labels = $this->data['labels'];

        return [
            'Category',
            $labels['current'],
            $labels['previous'],
            $labels['ytd'],
            $labels['last_year'],
        ];
    }

    public function collection(): Collection
    {
        $data = $this->data;
        $rows = [];

        $rows[] = ['category' => 'REVENUE', 'current' => '', 'previous' => '', 'ytd' => '', 'last_year' => ''];
        $rows[] = [
            'category' => '  Revenue from sales',
            'current' => $data['revenue']['sales']['current'],
            'previous' => $data['revenue']['sales']['previous'],
            'ytd' => $data['revenue']['sales']['ytd'],
            'last_year' => $data['revenue']['sales']['last_year'],
        ];
        $rows[] = [
            'category' => '  Revenue from water in school',
            'current' => $data['revenue']['water_in_school']['current'],
            'previous' => $data['revenue']['water_in_school']['previous'],
            'ytd' => $data['revenue']['water_in_school']['ytd'],
            'last_year' => $data['revenue']['water_in_school']['last_year'],
        ];
        $rows[] = [
            'category' => 'Subtotal Revenue',
            'current' => $data['revenue']['sub_total']['current'],
            'previous' => $data['revenue']['sub_total']['previous'],
            'ytd' => $data['revenue']['sub_total']['ytd'],
            'last_year' => $data['revenue']['sub_total']['last_year'],
        ];

        $rows[] = ['category' => 'EXPENSES', 'current' => '', 'previous' => '', 'ytd' => '', 'last_year' => ''];
        foreach ($data['expenses']['categories'] as $cat) {
            $rows[] = [
                'category' => '  '.$cat['category'],
                'current' => $cat['current'],
                'previous' => $cat['previous'],
                'ytd' => $cat['ytd'],
                'last_year' => $cat['last_year'],
            ];
        }
        $rows[] = [
            'category' => 'Subtotal Expenses',
            'current' => $data['expenses']['sub_total']['current'],
            'previous' => $data['expenses']['sub_total']['previous'],
            'ytd' => $data['expenses']['sub_total']['ytd'],
            'last_year' => $data['expenses']['sub_total']['last_year'],
        ];

        $rows[] = [
            'category' => 'Result (Revenue - Expenses)',
            'current' => $data['result']['current'],
            'previous' => $data['result']['previous'],
            'ytd' => $data['result']['ytd'],
            'last_year' => $data['result']['last_year'],
        ];
        $rows[] = [
            'category' => 'Entrepreneur Income (Salary + Profit)',
            'current' => $data['result']['current'] + $data['entrepreneur_salary']['current'],
            'previous' => $data['result']['previous'] + $data['entrepreneur_salary']['previous'],
            'ytd' => $data['result']['ytd'] + $data['entrepreneur_salary']['ytd'],
            'last_year' => $data['result']['last_year'] + $data['entrepreneur_salary']['last_year'],
        ];

        return collect($rows);
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
