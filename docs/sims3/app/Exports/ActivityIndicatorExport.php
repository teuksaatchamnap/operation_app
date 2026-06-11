<?php

namespace App\Exports;

use App\Services\KpiSheetService;
use App\Services\TierService;
use Carbon\Carbon;
use Illuminate\Support\Facades\DB;
use PhpOffice\PhpSpreadsheet\Cell\Coordinate;
use PhpOffice\PhpSpreadsheet\Spreadsheet;
use PhpOffice\PhpSpreadsheet\Style\Alignment;
use PhpOffice\PhpSpreadsheet\Style\Border;
use PhpOffice\PhpSpreadsheet\Style\Conditional;
use PhpOffice\PhpSpreadsheet\Style\Fill;
use PhpOffice\PhpSpreadsheet\Style\NumberFormat;
use PhpOffice\PhpSpreadsheet\Worksheet\Worksheet;
use PhpOffice\PhpSpreadsheet\Writer\Xlsx;
use Symfony\Component\HttpFoundation\StreamedResponse;

/**
 * Activity Indicators — PHP conversion of ExcelActivityIndicator.py.
 *
 * Sheets:
 *   1. Data — all sites × all months since 2017, metric selected by dropdown
 *   2. Summary — 4-year comparison (Month / YTD / Last 12 Months)
 *   3. KPI (one or more tabs) — 16 KPI blocks via KpiSheetService
 */
class ActivityIndicatorExport
{
    private Carbon $currentDate;
    private int    $exchangeRate;
    private array  $platforms;
    private array  $listTier;
    private array  $tierMap;
    private array  $tierData;

    // Dropdown metric options (must match Python CHOOSE order)
    private const METRICS = [
        'L/day inc. WinS',
        'Bot/day inc. WinS',
        'Bot/day exc. WinS',
        'Sales Bot inc. WinS',
        'Sales Bot exc. WinS',
        'Sales $ inc. WinS',
        'Sales $ exc. WinS',
        'Open Days',
        'WinS Sales',
        'Beneficiaries',
        'Operators',
        'School Beneficiaries',
    ];

    public function __construct(Carbon $currentDate)
    {
        $this->currentDate  = $currentDate->copy()->startOfMonth();
        $this->exchangeRate = TierService::exchangeRate($currentDate);
        $this->platforms    = TierService::platformList();

        $tierService = new TierService();
        $this->tierData = $tierService->calculateTiers($this->currentDate);
        $this->listTier = $this->tierData['allSiteTier'];
        // Pre-build O(1) tier lookup map
        $this->tierMap = array_column($this->listTier, 'tier', 'site_id');
    }

    public function download(?string $filename = null): StreamedResponse
    {
        $filename ??= 'Activity_Indicators_' . $this->currentDate->format('Y-m') . '.xlsx';
        $spreadsheet = $this->build();

        return new StreamedResponse(function () use ($spreadsheet) {
            $writer = new Xlsx($spreadsheet);
            $writer->setPreCalculateFormulas(false);
            $writer->save('php://output');
            $spreadsheet->disconnectWorksheets();
        }, 200, [
            'Content-Type'        => 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'Content-Disposition' => 'attachment; filename="' . $filename . '"',
            'Cache-Control'       => 'max-age=0',
        ]);
    }

    public function build(): Spreadsheet
    {
        $spreadsheet = new Spreadsheet();
        $spreadsheet->removeSheetByIndex(0);
        // 1. Data sheet
        $wsData = new Worksheet($spreadsheet, 'Data');
        $spreadsheet->addSheet($wsData);
        $this->writeRawData($wsData);

        // 2. Summary sheet
        $wsSummary = new Worksheet($spreadsheet, 'Summary');
        $spreadsheet->addSheet($wsSummary);
        $this->writeSummary($wsSummary);

        // 3. KPI sheets — up to 3 periods
        $this->kpiService = new KpiSheetService();
        $dateJanv1 = Carbon::create($this->currentDate->year - 1, 12, 1);
        $dateN1    = $this->currentDate->copy()->subMonths(12);
        $dateM1    = $this->currentDate->copy()->subMonth();

        // Pre-compute tiers once for all KPI sheets (avoids redundant DB queries)
        $precomputedTiers = $this->kpiService->precomputeTiers($this->currentDate, 2018);

        // Pre-warm Expenses + Sales caches for all active KPI periods in one pass.
        // Builds the date1Values list dynamically to match only the periods that will be
        // actually written below (Monthly is skipped in January; LTM is skipped when it
        // equals YTD — i.e., in December).
        $date1ForPrewarm = [];
        if ($this->currentDate->month !== 1) $date1ForPrewarm[] = $dateM1;
        $date1ForPrewarm[] = $dateJanv1;
        if (!$dateJanv1->equalTo($dateN1)) $date1ForPrewarm[] = $dateN1;
        $this->kpiService->prewarmMultiPeriod($this->currentDate, $date1ForPrewarm, KpiSheetService::KPI_YEARS_SHOWN);

        // Single month KPI (if not January)
        if ($this->currentDate->month !== 1) {
            $label1 = 'KPI ' . $this->currentDate->format('M') . ' ' . $this->currentDate->format('y');
            $wsKPI1 = new Worksheet($spreadsheet, $label1);
            $spreadsheet->addSheet($wsKPI1);
            $this->kpiService->writeFullKpiSheet(
                $wsKPI1, $this->currentDate, $dateM1,
                $this->platforms, $this->exchangeRate, 2018, true, $precomputedTiers
            );
        }

        // YTD KPI
        $labelYTD = 'KPI YTD ' . $this->currentDate->format('y');
        $wsKPIYTD = new Worksheet($spreadsheet, $labelYTD);
        $spreadsheet->addSheet($wsKPIYTD);
        $this->kpiService->writeFullKpiSheet(
            $wsKPIYTD, $this->currentDate, $dateJanv1,
            $this->platforms, $this->exchangeRate, 2018, true, $precomputedTiers
        );

        // Last 12 Months KPI (if dateJanv1 != dateN1)
        if (!$dateJanv1->equalTo($dateN1)) {
            $labelLTM = 'KPI LTM ' . $this->currentDate->format('y');
            $wsKPILTM = new Worksheet($spreadsheet, $labelLTM);
            $spreadsheet->addSheet($wsKPILTM);
            $this->kpiService->writeFullKpiSheet(
                $wsKPILTM, $this->currentDate, $dateN1,
                $this->platforms, $this->exchangeRate, 2018, true, $precomputedTiers
            );
        }

        $spreadsheet->setActiveSheetIndex(0);
        return $spreadsheet;
    }

    // ─── DATA SHEET ──────────────────────────────────────────────

    private function writeRawData(Worksheet $ws): void
    {
        $ws->getSheetView()->setZoomScale(70);
        $ws->getColumnDimension('A')->setWidth(17);
        $ws->getColumnDimension('B')->setWidth(17);
        $ws->getColumnDimension('C')->setWidth(17);
        $ws->getColumnDimension('D')->setWidth(17);
        $ws->getColumnDimension('E')->setWidth(17);
        $er = $this->exchangeRate;

        // Metric selector in A1
        $ws->setCellValue('A1', self::METRICS[0]);
        $ws->getStyle('A1')->applyFromArray([
            'fill' => ['fillType' => Fill::FILL_SOLID, 'startColor' => ['rgb' => 'FFFF00']],
            'font' => ['bold' => true, 'size' => 12],
        ]);

        // Build comma-separated list for data validation dropdown
        $metricList = implode(',', self::METRICS);
        $validation = $ws->getCell('A1')->getDataValidation();
        $validation->setType(\PhpOffice\PhpSpreadsheet\Cell\DataValidation::TYPE_LIST);
        $validation->setFormula1('"' . $metricList . '"');
        $validation->setShowDropDown(true);

        // Site info headers (row 3 in Python = row 4 here since we start from 1)
        $infoHeaders = ['Site', 'Platform', 'Province', 'Advisor', 'Tier'];
        $headerRow = 4;
        foreach ($infoHeaders as $ci => $h) {
            $cell = Coordinate::stringFromColumnIndex($ci + 1) . $headerRow;
            $ws->setCellValue($cell, $h);
            $ws->getStyle($cell)->applyFromArray([
                'font' => ['bold' => true, 'color' => ['rgb' => 'FFFFFF']],
                'fill' => ['fillType' => Fill::FILL_SOLID, 'startColor' => ['rgb' => '4472C4']],
                'alignment' => ['horizontal' => Alignment::HORIZONTAL_LEFT],
            ]);
        }

        // Month columns: from 2017-01 to current date
        $startDate = Carbon::create(2017, 1, 1);
        $current   = $startDate->copy();
        $monthCols = [];
        $col = 6; // 1-based, starting after Site/Platform/Province/Advisor/Tier
        while ($current->lte($this->currentDate)) {
            $monthCols[] = ['date' => $current->copy(), 'col' => $col];
            $cell = Coordinate::stringFromColumnIndex($col) . $headerRow;
            $ws->setCellValue($cell, $current->year . '-' . $current->month);
            $ws->getColumnDimensionByColumn($col)->setWidth(11);

            // Hide columns > 3 years old
            if ($current->diffInYears($this->currentDate) >= 3) {
                $ws->getColumnDimensionByColumn($col)->setOutlineLevel(1);
                $ws->getColumnDimensionByColumn($col)->setCollapsed(true);
                $ws->getColumnDimensionByColumn($col)->setVisible(false);
            }
            $col++;
            $current->addMonth();
        }

        // Batch style for all month column headers at once
        if (count($monthCols) > 0) {
            $firstMonthCol = Coordinate::stringFromColumnIndex(6);
            $lastMonthCol  = Coordinate::stringFromColumnIndex(count($monthCols) + 5);
            $ws->getStyle("{$firstMonthCol}{$headerRow}:{$lastMonthCol}{$headerRow}")->applyFromArray([
                'font' => ['bold' => true],
                'alignment' => ['horizontal' => Alignment::HORIZONTAL_CENTER],
                'fill' => ['fillType' => Fill::FILL_SOLID, 'startColor' => ['rgb' => 'BDD7EE']], // Light Blue
            ]);
        }

        // Fetch all sales data
        $allSales = DB::table('Sales')
            ->where('Month', '>=', $startDate)
            ->where('Month', '<=', $this->currentDate)
            ->groupBy('Id_Site', 'Month')
            ->selectRaw("Id_Site, Month,
                SUM(Total_Income)/{$er} as inc_all,
                SUM(Total_Income-WiS_Income)/{$er} as inc_exc,
                SUM(Total_Sales-Bottle_Sales) as bot_inc,
                SUM(Total_Sales-Bottle_Sales-WiS_Sales) as bot_exc,
                CASE WHEN SUM(Number_Open_Days)>0 THEN SUM(Total_Sales-Bottle_Sales)/SUM(Number_Open_Days) ELSE 0 END as bd_inc,
                CASE WHEN SUM(Number_Open_Days)>0 THEN SUM(Total_Sales-Bottle_Sales-WiS_Sales)/SUM(Number_Open_Days) ELSE 0 END as bd_exc,
                CASE WHEN SUM(Number_Open_Days)>0 THEN SUM(Total_Sales-Bottle_Sales)/SUM(Number_Open_Days)*20 ELSE 0 END as ld_inc,
                SUM(Number_Open_Days) as open_days,
                SUM(WiS_Sales) as wins")
            ->get();

        // Organize by site+month
        $salesMap = [];
        foreach ($allSales as $s) {
            $monthKey = Carbon::parse($s->Month)->format('Y-m');
            $salesMap[$s->Id_Site][$monthKey] = $s;
        }

        // Operators
        $allOperators = DB::table('Indicators')
            ->where('Month', '>=', $startDate)->where('Month', '<=', $this->currentDate)
            ->select('Id_Site', 'Month', 'Number_of_Operator')
            ->get();
        $opMap = [];
        foreach ($allOperators as $o) {
            $opMap[$o->Id_Site][Carbon::parse($o->Month)->format('Y-m')] = (int) $o->Number_of_Operator;
        }

        // Beneficiaries
        $allBenef = DB::table('Beneficiaries')
            ->where('Month', '>=', $startDate)->where('Month', '<=', $this->currentDate)
            ->select('Id_Site', 'Month', 'Beneficiaries')
            ->get();
        $benefMap = [];
        foreach ($allBenef as $b) {
            $benefMap[$b->Id_Site][Carbon::parse($b->Month)->format('Y-m')] = (int) $b->Beneficiaries;
        }

        // School Beneficiaries (by academy year)
        $allSchoolBenef = DB::table('school_programs')
            ->groupBy('Id_Site', 'academy_year')
            ->selectRaw('SUM(number_of_children) as total, Id_Site, academy_year')
            ->get();
        $schoolBenefMap = [];
        foreach ($allSchoolBenef as $sb) {
            $schoolBenefMap[$sb->Id_Site][$sb->academy_year] = (int) $sb->total;
        }
        // Academy months: Jan-Oct use previous year as academy_year
        $academyMonths = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];

        // Sites info
        $sitesInfo = DB::table('Sales')
            ->join('Sites', 'Sales.Id_Site', '=', 'Sites.Id_Site')
            ->select('Sales.Id_Site', 'Sites.Platform', 'Sites.Province', 'Sites.Advisor')
            ->distinct()
            ->orderByRaw("LEFT(Sales.Id_Site, 1), LENGTH(Sales.Id_Site), Sales.Id_Site")
            ->get();

        // Write data rows
        $dataRow = 5; // first data row
        // Pre-build the METRICS match string (same for every cell)
        $metricsMatchStr = '{"' . implode('","', self::METRICS) . '"}';

        foreach ($sitesInfo as $site) {
            $siteId = $site->Id_Site;

            // Tier — O(1) lookup
            $tier = $this->tierMap[$siteId] ?? '';

            // Site info
            $ws->setCellValue("A{$dataRow}", $siteId);
            $ws->setCellValue("B{$dataRow}", $site->Platform);
            $ws->setCellValue("C{$dataRow}", $site->Province ?? '');
            $ws->setCellValue("D{$dataRow}", $site->Advisor);
            $ws->setCellValue("E{$dataRow}", $tier);

            // Monthly data with CHOOSE formula
            foreach ($monthCols as $mc) {
                $mKey    = $mc['date']->format('Y-m');
                $colNum  = $mc['col'];
                $sd      = $salesMap[$siteId][$mKey] ?? null;
                $op      = $opMap[$siteId][$mKey] ?? '';
                $ben     = $benefMap[$siteId][$mKey] ?? '';

                // School beneficiaries: in academy months (Jan-Oct), use previous year as academy_year
                $mcMonth = $mc['date']->month;
                $mcYear  = $mc['date']->year;
                $schoolYear = in_array($mcMonth, $academyMonths) ? $mcYear - 1 : $mcYear;
                $schoolBen = $schoolBenefMap[$siteId][$schoolYear] ?? '';

                // Build values array matching METRICS order
                $vals = [
                    $sd ? round((float) $sd->ld_inc, 2) : '',
                    $sd ? round((float) $sd->bd_inc, 2) : '',
                    $sd ? round((float) $sd->bd_exc, 2) : '',
                    $sd ? (int) $sd->bot_inc : '',
                    $sd ? (int) $sd->bot_exc : '',
                    $sd ? round((float) $sd->inc_all, 2) : '',
                    $sd ? round((float) $sd->inc_exc, 2) : '',
                    $sd ? (int) $sd->open_days : '',
                    $sd ? (int) $sd->wins : '',
                    $ben,
                    $op,
                    $schoolBen, // School beneficiaries
                ];

                // Skip cells where all values are empty (no data at all)
                $hasData = false;
                foreach ($vals as $v) {
                    if ($v !== '' && $v !== 0) { $hasData = true; break; }
                }
                if (!$hasData) { continue; }

                // Write CHOOSE formula
                $valsStr = implode(',', array_map(fn($v) => $v === '' ? '""' : $v, $vals));
                $cell = Coordinate::stringFromColumnIndex($colNum) . $dataRow;
                $ws->setCellValue($cell, "=IFERROR(CHOOSE(MATCH(\$A\$1,{$metricsMatchStr},0),{$valsStr}),\"\")");
            }

            $dataRow++;
        }

        // Batch apply number format to entire data range at once (instead of per-cell)
        $lastDataRow = $dataRow - 1;
        if ($lastDataRow >= 5) {
            $firstDataCol = Coordinate::stringFromColumnIndex(6);
            $lastDataCol  = Coordinate::stringFromColumnIndex(count($monthCols) + 5);
            $ws->getStyle("{$firstDataCol}5:{$lastDataCol}{$lastDataRow}")
               ->getNumberFormat()->setFormatCode('#,##0');
        }
        $firstCol = Coordinate::stringFromColumnIndex(6);
        $lastCol  = Coordinate::stringFromColumnIndex(count($monthCols) + 5);

        // Total rows — Python: row 0 = Average, row 1 = Sum, row 2 = Nb Active Sites (in col E)
        $ws->setCellValue('E1', 'Average');
        $ws->getStyle('E1')->getFont()->setBold(true);
        $ws->setCellValue('E2', 'Sum');
        $ws->getStyle('E2')->getFont()->setBold(true);
        $ws->setCellValue('E3', 'Nb Active Sites');
        $ws->getStyle('E3')->getFont()->setBold(true);

        for ($mc = 0; $mc < count($monthCols); $mc++) {
            $cl = Coordinate::stringFromColumnIndex($monthCols[$mc]['col']);
            $ws->setCellValue("{$cl}1", "=SUBTOTAL(1,{$cl}5:{$cl}{$lastDataRow})");
            $ws->setCellValue("{$cl}2", "=SUBTOTAL(9,{$cl}5:{$cl}{$lastDataRow})");
            $ws->setCellValue("{$cl}3", "=SUBTOTAL(2,{$cl}5:{$cl}{$lastDataRow})");
            $ws->getStyle("{$cl}1:{$cl}3")->getNumberFormat()->setFormatCode('#,##0');
        }

        // Bold total rows
        $ws->getStyle("{$firstCol}1:{$lastCol}3")->getFont()->setBold(true);

        // Conditional formatting — grey background on blank cells
        $condRange = "{$firstCol}5:{$lastCol}{$lastDataRow}";
        $ws->getStyle($condRange)->applyFromArray([]);
        $conditional = new \PhpOffice\PhpSpreadsheet\Style\Conditional();
        $conditional->setConditionType(\PhpOffice\PhpSpreadsheet\Style\Conditional::CONDITION_EXPRESSION);
        $conditional->addCondition("{$firstCol}5=\"\"");
        $conditional->getStyle()->getFill()
            ->setFillType(Fill::FILL_SOLID)
            ->getStartColor()->setRGB('C0C0C0');
        $ws->getStyle($condRange)->setConditionalStyles([$conditional]);

        // Autofilter on data range — filter out Dead platform rows by default
        $ws->setAutoFilter("A4:{$lastCol}{$lastDataRow}");
        $bFilter = $ws->getAutoFilter()->getColumn('B');
        $bFilter->setFilterType(\PhpOffice\PhpSpreadsheet\Worksheet\AutoFilter\Column::AUTOFILTER_FILTERTYPE_CUSTOMFILTER);
        $bFilter->createRule()
            ->setRule(\PhpOffice\PhpSpreadsheet\Worksheet\AutoFilter\Column\Rule::AUTOFILTER_COLUMN_RULE_NOTEQUAL, 'Dead')
            ->setRuleType(\PhpOffice\PhpSpreadsheet\Worksheet\AutoFilter\Column\Rule::AUTOFILTER_RULETYPE_CUSTOMFILTER);
        $ws->getAutoFilter()->showHideRows();

        $ws->freezePane('F5');
    }

    // ─── SUMMARY SHEET ───────────────────────────────────────────

    private function writeSummary(Worksheet $ws): void
    {
        $ws->getSheetView()->setZoomScale(80);
        $ws->getColumnDimension('A')->setWidth(17);
        $ws->getColumnDimension('B')->setWidth(17);
        $ws->getColumnDimension('C')->setWidth(17);
        $ws->getColumnDimension('D')->setWidth(17);
        $ws->getColumnDimension('E')->setWidth(17);
        $er = $this->exchangeRate;

        // Selectors
        $ws->setCellValue('A1', 'Month');
        $ws->getStyle('A1')->applyFromArray([
            'fill' => ['fillType' => Fill::FILL_SOLID, 'startColor' => ['rgb' => 'FFFF00']],
            'font' => ['bold' => true, 'size' => 12],
        ]);

        $periodValidation = $ws->getCell('A1')->getDataValidation();
        $periodValidation->setType(\PhpOffice\PhpSpreadsheet\Cell\DataValidation::TYPE_LIST);
        $periodValidation->setFormula1('"Month,YTD,Last 12 Months"');
        $periodValidation->setShowDropDown(true);

        $ws->setCellValue('C1', 'Bot/day');
        $ws->getStyle('C1')->applyFromArray([
            'fill' => ['fillType' => Fill::FILL_SOLID, 'startColor' => ['rgb' => 'FFFF00']],
            'font' => ['bold' => true, 'size' => 12],
        ]);

        $metricValidation = $ws->getCell('C1')->getDataValidation();
        $metricValidation->setType(\PhpOffice\PhpSpreadsheet\Cell\DataValidation::TYPE_LIST);
        $metricValidation->setFormula1('"Bot/day,Sales Bot,Sales $,Beneficiaries,Open Days"');
        $metricValidation->setShowDropDown(true);

        // Headers
        $sitesInfo = DB::table('Sales')
            ->join('Sites', 'Sales.Id_Site', '=', 'Sites.Id_Site')
            ->where('Sales.Month', '<=', $this->currentDate)
            ->where('Sales.Month', '>', $this->currentDate->copy()->subMonths(12))
            ->select('Sales.Id_Site', 'Sites.Old_Platform', 'Sites.Province', 'Sites.Advisor')
            ->distinct()
            ->orderByRaw("LEFT(Sales.Id_Site, 1), LENGTH(Sales.Id_Site), Sales.Id_Site")
            ->get();

        $headerRow = 3;
        $siteHeaders = ['Site', 'Platform', 'Province', 'Advisor', 'Tier'];
        $headerStyle = [
            'font' => ['bold' => true, 'color' => ['rgb' => 'FFFFFF']],
            'fill' => ['fillType' => Fill::FILL_SOLID, 'startColor' => ['rgb' => '4472C4']],
            'alignment' => ['horizontal' => Alignment::HORIZONTAL_LEFT],
        ];

        foreach ($siteHeaders as $ci => $h) {
            $cell = Coordinate::stringFromColumnIndex($ci + 1) . $headerRow;
            $ws->setCellValue($cell, $h);
            $ws->getStyle($cell)->applyFromArray($headerStyle);
        }

        // Year columns: 4 years × 3 (inc. WinS, exc. WinS, WinS)
        $yearColors = ['DA9694', '92D050', '8DB4E2', '00B0F0'];
        $baseCol = 6;

        for ($y = 0; $y < 4; $y++) {
            $year = $this->currentDate->year - $y;
            for ($sub = 0; $sub < 3; $sub++) {
                $col = $baseCol + $y * 3 + $sub;
                $subLabel = ['inc. WinS', 'exc. WinS', 'WinS'][$sub];
                $cell = Coordinate::stringFromColumnIndex($col) . $headerRow;
                $ws->setCellValue($cell, "{$year} {$subLabel}");
                $ws->getStyle($cell)->applyFromArray([
                    'font' => ['bold' => true, 'color' => ['rgb' => 'FFFFFF']],
                    'fill' => ['fillType' => Fill::FILL_SOLID, 'startColor' => ['rgb' => $yearColors[$y]]],
                    'alignment' => ['horizontal' => Alignment::HORIZONTAL_CENTER],
                ]);
                $ws->getColumnDimensionByColumn($col)->setWidth(15);
            }
        }

        // Fetch data for all 4 years — consolidated into 2 queries instead of 16
        $er = $this->exchangeRate;
        $earliestDate = $this->currentDate->copy()->subMonths(60); // covers LTM for year-3

        // Single query: all monthly sales data
        $allMonthlySales = DB::table('Sales')
            ->where('Month', '>=', $earliestDate)
            ->where('Month', '<=', $this->currentDate)
            ->selectRaw("Id_Site, Month,
                Total_Sales - Bottle_Sales as bot_inc,
                Total_Sales - Bottle_Sales - WiS_Sales as bot_exc,
                WiS_Sales as wins,
                Number_Open_Days as open_days,
                Total_Income as total_income,
                Total_Income - WiS_Income as income_exc")
            ->get();

        // Organize by site -> month integer key (e.g. 202601)
        $rawBySite = [];
        foreach ($allMonthlySales as $s) {
            $mInt = (int) Carbon::parse($s->Month)->format('Ym');
            $rawBySite[$s->Id_Site][] = [
                'm' => $mInt,
                'bi' => (float) $s->bot_inc,
                'be' => (float) $s->bot_exc,
                'w'  => (float) $s->wins,
                'od' => (float) $s->open_days,
                'ti' => (float) $s->total_income,
                'ie' => (float) $s->income_exc,
            ];
        }

        // Single query: all reference-month beneficiaries in one go
        $refDates = [];
        for ($y = 0; $y < 4; $y++) {
            $refDates[] = $this->currentDate->copy()->subMonths(12 * $y);
        }
        $allBenef = DB::table('Beneficiaries')
            ->whereIn('Month', $refDates)
            ->select('Id_Site', 'Month', 'Beneficiaries')
            ->get();
        $benefByYearSite = [];
        foreach ($allBenef as $b) {
            $mInt = (int) Carbon::parse($b->Month)->format('Ym');
            $benefByYearSite[$mInt][$b->Id_Site] = (int) $b->Beneficiaries;
        }

        // Aggregate in PHP for each year/period
        $yearData = [];
        for ($y = 0; $y < 4; $y++) {
            $refDate = $this->currentDate->copy()->subMonths(12 * $y);
            $refMInt = (int) $refDate->format('Ym');
            $ytdStartMInt = (int) Carbon::create($refDate->year, 1, 1)->format('Ym');
            $ltmStartMInt = (int) $refDate->copy()->subMonths(11)->format('Ym');

            $periods = [
                'month' => [$refMInt, $refMInt],
                'ytd'   => [$ytdStartMInt, $refMInt],
                'ltm'   => [$ltmStartMInt, $refMInt],
            ];

            foreach ($periods as $pKey => [$pStartMInt, $pEndMInt]) {
                $aggregated = [];
                foreach ($rawBySite as $siteId => $rows) {
                    $botInc = $botExc = $wins = $openDays = $totInc = $incExc = 0;
                    foreach ($rows as $r) {
                        if ($r['m'] >= $pStartMInt && $r['m'] <= $pEndMInt) {
                            $botInc  += $r['bi'];
                            $botExc  += $r['be'];
                            $wins    += $r['w'];
                            $openDays += $r['od'];
                            $totInc  += $r['ti'];
                            $incExc  += $r['ie'];
                        }
                    }
                    if ($botInc || $botExc || $wins || $openDays || $totInc) {
                        $aggregated[$siteId] = (object) [
                            'bot_inc'   => $botInc,
                            'bot_exc'   => $botExc,
                            'wins'      => $wins,
                            'bd_inc'    => $openDays > 0 ? $botInc / $openDays : 0,
                            'bd_exc'    => $openDays > 0 ? $botExc / $openDays : 0,
                            'inc_all'   => $totInc / $er,
                            'inc_exc'   => $incExc / $er,
                            'open_days' => $openDays,
                        ];
                    }
                }
                $yearData[$y][$pKey] = $aggregated;
            }

            $yearData[$y]['benef'] = $benefByYearSite[$refMInt] ?? [];
        }

        // Data rows
        $dataRow = 4;
        // Pre-build the CHOOSE match string for summary
        $summaryMetricsStr = '{"Bot/day","Sales Bot","Sales $","Beneficiaries","Open Days"}';

        foreach ($sitesInfo as $site) {
            $siteId = $site->Id_Site;
            $tier = $this->tierMap[$siteId] ?? '';

            $ws->setCellValue("A{$dataRow}", $siteId);
            $ws->setCellValue("B{$dataRow}", $site->Old_Platform);
            $ws->setCellValue("C{$dataRow}", $site->Province ?? '');
            $ws->setCellValue("D{$dataRow}", $site->Advisor);
            $ws->setCellValue("E{$dataRow}", $tier);

            for ($y = 0; $y < 4; $y++) {
                $col = $baseCol + $y * 3;

                foreach (['month', 'ytd', 'ltm'] as $pi => $period) {
                    $data = $yearData[$y][$period][$siteId] ?? null;
                    $benef = $yearData[$y]['benef'][$siteId] ?? 0;

                    $bdInc   = (float) ($data->bd_inc ?? 0);
                    $bdExc   = (float) ($data->bd_exc ?? 0);
                    $botInc  = (int) ($data->bot_inc ?? 0);
                    $botExc  = (int) ($data->bot_exc ?? 0);
                    $incAll  = round((float) ($data->inc_all ?? 0));
                    $incExc  = round((float) ($data->inc_exc ?? 0));
                    $openD   = (int) ($data->open_days ?? 0);

                    $periodValues[$period] = [
                        'inc' => [$bdInc, $botInc, $incAll, $benef, $openD],
                        'exc' => [$bdExc, $botExc, $incExc, 0, $openD],
                        'wins' => [$bdInc - $bdExc, $botInc - $botExc, $incAll - $incExc, 0, 0],
                    ];
                }

                foreach ([0, 1, 2] as $sub) {
                    $subKey  = ['inc', 'exc', 'wins'][$sub];
                    $cellCol = $col + $sub;
                    $cellRef = Coordinate::stringFromColumnIndex($cellCol) . $dataRow;

                    $monthVals = $periodValues['month'][$subKey];
                    $ytdVals   = $periodValues['ytd'][$subKey];
                    $ltmVals   = $periodValues['ltm'][$subKey];

                    $chooseMonth = "CHOOSE(MATCH(\$C\$1,{$summaryMetricsStr},0)," . implode(',', $monthVals) . ")";
                    $chooseYTD   = "CHOOSE(MATCH(\$C\$1,{$summaryMetricsStr},0)," . implode(',', $ytdVals) . ")";
                    $chooseLTM   = "CHOOSE(MATCH(\$C\$1,{$summaryMetricsStr},0)," . implode(',', $ltmVals) . ")";

                    $formula = "=IFERROR(IF(\$A\$1=\"Month\",{$chooseMonth},IF(\$A\$1=\"YTD\",{$chooseYTD},{$chooseLTM})),\"\")";
                    $ws->setCellValue($cellRef, $formula);
                }
            }

            $dataRow++;
        }

        // Batch apply number format to all summary data cells
        $lastSummaryRow = $dataRow - 1;
        if ($lastSummaryRow >= 4) {
            $firstSumCol = Coordinate::stringFromColumnIndex($baseCol);
            $lastSumCol  = Coordinate::stringFromColumnIndex($baseCol + 4 * 3 - 1);
            $ws->getStyle("{$firstSumCol}4:{$lastSumCol}{$lastSummaryRow}")
               ->getNumberFormat()->setFormatCode('#,##0');

            // Conditional formatting — grey background on blank cells
            $condRange = "F4:Q{$lastSummaryRow}";
            $conditional = new \PhpOffice\PhpSpreadsheet\Style\Conditional();
            $conditional->setConditionType(\PhpOffice\PhpSpreadsheet\Style\Conditional::CONDITION_EXPRESSION);
            $conditional->addCondition('F4=""');
            $conditional->getStyle()->getFill()
                ->setFillType(Fill::FILL_SOLID)
                ->getStartColor()->setRGB('C0C0C0');
            $ws->getStyle($condRange)->setConditionalStyles([$conditional]);
        }

        // Summary total labels (Python: row 0 = Total, row 1 = Average at col E)
        $ws->setCellValue('E1', 'Total');
        $ws->getStyle('E1')->getFont()->setBold(true);
        $ws->setCellValue('E2', 'Average');
        $ws->getStyle('E2')->getFont()->setBold(true);

        // Total/Average formulas for summary columns
        for ($c = $baseCol; $c < $baseCol + 4 * 3; $c++) {
            $cl = Coordinate::stringFromColumnIndex($c);
            $ws->setCellValue("{$cl}1", "=SUBTOTAL(9,{$cl}4:{$cl}{$lastSummaryRow})");
            $ws->setCellValue("{$cl}2", "=SUBTOTAL(1,{$cl}4:{$cl}{$lastSummaryRow})");
            $ws->getStyle("{$cl}1:{$cl}2")->getNumberFormat()->setFormatCode('#,##0');
        }

        // Bold total rows
        $firstSumColStr = Coordinate::stringFromColumnIndex($baseCol);
        $lastSumColStr  = Coordinate::stringFromColumnIndex($baseCol + 4 * 3 - 1);
        $ws->getStyle("{$firstSumColStr}1:{$lastSumColStr}2")->getFont()->setBold(true);

        // Autofilter on header row — filter out Dead platform rows by default
        $ws->setAutoFilter("A3:{$lastSumColStr}{$lastSummaryRow}");
        $bFilter = $ws->getAutoFilter()->getColumn('B');
        $bFilter->setFilterType(\PhpOffice\PhpSpreadsheet\Worksheet\AutoFilter\Column::AUTOFILTER_FILTERTYPE_CUSTOMFILTER);
        $bFilter->createRule()
            ->setRule(\PhpOffice\PhpSpreadsheet\Worksheet\AutoFilter\Column\Rule::AUTOFILTER_COLUMN_RULE_NOTEQUAL, 'Dead')
            ->setRuleType(\PhpOffice\PhpSpreadsheet\Worksheet\AutoFilter\Column\Rule::AUTOFILTER_RULETYPE_CUSTOMFILTER);
        $ws->getAutoFilter()->showHideRows();

        $ws->freezePane('F4');
    }
}
