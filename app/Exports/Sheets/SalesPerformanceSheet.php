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

class SalesPerformanceSheet implements FromCollection, WithCharts, WithColumnWidths, WithHeadings, WithStyles, WithTitle
{
    public function __construct(private array $data) {}

    public function title(): string
    {
        return 'Sales Performance';
    }

    public function headings(): array
    {
        $headings = ['Month'];
        foreach ($this->data['series'] as $series) {
            $headings[] = $series['name'];
        }

        return $headings;
    }

    public function collection(): Collection
    {
        $categories = $this->data['categories'];
        $series = $this->data['series'];
        $numSeries = count($series);

        $rows = [];
        for ($i = 0; $i < 12; $i++) {
            $row = ['month' => $categories[$i] ?? ''];
            for ($j = 0; $j < $numSeries; $j++) {
                $row['s'.$j] = $series[$j]['data'][$i] ?? null;
            }
            $rows[] = $row;
        }

        return collect($rows);
    }

    public function charts(): Chart
    {
        $series = $this->data['series'];
        $numSeries = count($series);
        $dataRowCount = 12;
        $chartRow = $dataRowCount + 3;
        $lastCol = chr(65 + $numSeries);

        $dataSeriesLabels = [];
        $dataSeriesValues = [];
        for ($j = 0; $j < $numSeries; $j++) {
            $col = chr(66 + $j);
            $dataSeriesLabels[] = new DataSeriesValues(
                DataSeriesValues::DATASERIES_TYPE_STRING,
                "'Sales Performance'!\$$col\$1",
                null,
                1
            );
            $dataSeriesValues[] = new DataSeriesValues(
                DataSeriesValues::DATASERIES_TYPE_NUMBER,
                "'Sales Performance'!\$$col\$2:\$$col\$".($dataRowCount + 1),
                null,
                $dataRowCount
            );
        }

        $xAxisTickValues = [
            new DataSeriesValues(
                DataSeriesValues::DATASERIES_TYPE_STRING,
                "'Sales Performance'!\$A\$2:\$A\$".($dataRowCount + 1),
                null,
                $dataRowCount
            ),
        ];

        $plotSeries = new DataSeries(
            DataSeries::TYPE_LINECHART,
            DataSeries::GROUPING_STANDARD,
            range(0, $numSeries - 1),
            $dataSeriesLabels,
            $xAxisTickValues,
            $dataSeriesValues
        );

        $plotArea = new PlotArea(null, [$plotSeries]);
        $legend = new Legend(Legend::POSITION_BOTTOM);
        $chart = new Chart(
            'sales_performance_chart',
            new Title('Monthly Sales Performance (bottles/day)'),
            $legend,
            $plotArea
        );

        $chart->setTopLeftPosition("A{$chartRow}");
        $chart->setBottomRightPosition("{$lastCol}".($chartRow + 18));

        return $chart;
    }

    public function columnWidths(): array
    {
        $widths = ['A' => 8];
        $numSeries = count($this->data['series']);
        for ($j = 0; $j < $numSeries; $j++) {
            $col = chr(66 + $j);
            $widths[$col] = 12;
        }

        return $widths;
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
