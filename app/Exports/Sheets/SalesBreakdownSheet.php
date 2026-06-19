<?php

namespace App\Exports\Sheets;

use Illuminate\Support\Collection;
use Maatwebsite\Excel\Concerns\FromCollection;
use Maatwebsite\Excel\Concerns\WithCharts;
use Maatwebsite\Excel\Concerns\WithColumnWidths;
use Maatwebsite\Excel\Concerns\WithHeadings;
use Maatwebsite\Excel\Concerns\WithStyles;
use Maatwebsite\Excel\Concerns\WithTitle;
use PhpOffice\PhpSpreadsheet\Chart\Chart;
use PhpOffice\PhpSpreadsheet\Chart\DataSeries;
use PhpOffice\PhpSpreadsheet\Chart\DataSeriesValues;
use PhpOffice\PhpSpreadsheet\Chart\Legend;
use PhpOffice\PhpSpreadsheet\Chart\PlotArea;
use PhpOffice\PhpSpreadsheet\Chart\Title;
use PhpOffice\PhpSpreadsheet\Style\Border;
use PhpOffice\PhpSpreadsheet\Style\Fill;
use PhpOffice\PhpSpreadsheet\Worksheet\Worksheet;

class SalesBreakdownSheet implements FromCollection, WithCharts, WithColumnWidths, WithHeadings, WithStyles, WithTitle
{
    public function __construct(private array $data) {}

    public function title(): string
    {
        return 'Sales Breakdown';
    }

    public function headings(): array
    {
        return ['Channel', 'Bottles'];
    }

    public function collection(): Collection
    {
        $rows = [];
        foreach ($this->data as $item) {
            $rows[] = [
                'channel' => $item['label'],
                'bottles' => $item['value'],
            ];
        }

        return collect($rows);
    }

    public function charts(): Chart|array
    {
        $dataCount = count($this->data);

        if ($dataCount === 0) {
            return [];
        }

        $chartRow = $dataCount + 3;

        $dataSeriesLabels = [
            new DataSeriesValues(
                DataSeriesValues::DATASERIES_TYPE_STRING,
                "'Sales Breakdown'!\$B\$1",
                null,
                1
            ),
        ];

        $xAxisTickValues = [
            new DataSeriesValues(
                DataSeriesValues::DATASERIES_TYPE_STRING,
                "'Sales Breakdown'!\$A\$2:\$A\$".($dataCount + 1),
                null,
                $dataCount
            ),
        ];

        $dataSeriesValues = [
            new DataSeriesValues(
                DataSeriesValues::DATASERIES_TYPE_NUMBER,
                "'Sales Breakdown'!\$B\$2:\$B\$".($dataCount + 1),
                null,
                $dataCount
            ),
        ];

        $plotSeries = new DataSeries(
            DataSeries::TYPE_PIECHART,
            DataSeries::GROUPING_STANDARD,
            [0],
            $dataSeriesLabels,
            $xAxisTickValues,
            $dataSeriesValues
        );

        $plotArea = new PlotArea(null, [$plotSeries]);
        $legend = new Legend(Legend::POSITION_RIGHT);
        $chart = new Chart(
            'sales_breakdown_chart',
            new Title('Monthly Sales Breakdown'),
            $legend,
            $plotArea
        );

        $chart->setTopLeftPosition("D{$chartRow}");
        $chart->setBottomRightPosition('J'.($chartRow + 18));

        return $chart;
    }

    public function columnWidths(): array
    {
        return [
            'A' => 20,
            'B' => 14,
            'C' => 4,
        ];
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
