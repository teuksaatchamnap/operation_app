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

class GeneralDetailsSheet implements FromCollection, WithHeadings, WithStyles, WithTitle
{
    public function __construct(private array $data) {}

    public function title(): string
    {
        return 'General Details';
    }

    public function headings(): array
    {
        return ['Field', 'Value'];
    }

    public function collection(): Collection
    {
        return collect([
            ['Platform', $this->data['platform']],
            ['Entrepreneur Name', $this->data['entrepreneur_name']],
            ['Start Working Date', $this->data['start_working_date']],
            ['Advisor Name', $this->data['advisor_name']],
            ['ROM Name', $this->data['rom_name']],
            ['Commune Name', $this->data['commune_name']],
            ['Population Commune', $this->data['population_commune']],
            ['Households', $this->data['households']],
            ['Delivery Program', $this->data['delivery_program']],
            ['Treatment Process', $this->data['treatment_process']],
        ]);
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
            'A' => [
                'font' => ['bold' => true],
            ],
        ];
    }
}
