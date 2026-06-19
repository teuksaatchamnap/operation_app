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

class ExpenseComparisonSheet implements FromCollection, WithCharts, WithColumnWidths, WithHeadings, WithStyles, WithTitle
{
    public function __construct(private array $data) {}

    public function title(): string
    {
        return 'Expense Comparison';
    }

    public function headings(): array
    {
        return ['Category', 'Site Amount (KHR)', 'Network Avg (KHR)'];
    }

    public function collection(): Collection
    {
        $rows = [];
        foreach ($this->data as $item) {
            $rows[] = [
                'category' => $item['category'],
                'site_amount' => $item['site_amount'],
                'avg_amount' => $item['avg_amount'],
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
                "'Expense Comparison'!\$B\$1",
                null,
                1
            ),
            new DataSeriesValues(
                DataSeriesValues::DATASERIES_TYPE_STRING,
                "'Expense Comparison'!\$C\$1",
                null,
                2
            ),
        ];

        $xAxisTickValues = [
            new DataSeriesValues(
                DataSeriesValues::DATASERIES_TYPE_STRING,
                "'Expense Comparison'!\$A\$2:\$A\$".($dataCount + 1),
                null,
                $dataCount
            ),
        ];

        $dataSeriesValues = [
            new DataSeriesValues(
                DataSeriesValues::DATASERIES_TYPE_NUMBER,
                "'Expense Comparison'!\$B\$2:\$B\$".($dataCount + 1),
                null,
                $dataCount
            ),
            new DataSeriesValues(
                DataSeriesValues::DATASERIES_TYPE_NUMBER,
                "'Expense Comparison'!\$C\$2:\$C\$".($dataCount + 1),
                null,
                $dataCount
            ),
        ];

        $plotSeries = new DataSeries(
            DataSeries::TYPE_BARCHART,
            DataSeries::GROUPING_CLUSTERED,
            [0, 1],
            $dataSeriesLabels,
            $xAxisTickValues,
            $dataSeriesValues
        );

        $plotArea = new PlotArea(null, [$plotSeries]);
        $legend = new Legend(Legend::POSITION_BOTTOM);
        $chart = new Chart(
            'expense_comparison_chart',
            new Title('Monthly Expenses Comparison'),
            $legend,
            $plotArea
        );

        $chart->setTopLeftPosition("A{$chartRow}");
        $chart->setBottomRightPosition('H'.($chartRow + 18));

        return $chart;
    }

    public function columnWidths(): array
    {
        return [
            'A' => 22,
            'B' => 18,
            'C' => 18,
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
