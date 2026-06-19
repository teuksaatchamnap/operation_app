<?php

namespace App\Exports;

use App\Exports\Sheets\BottlePurchasesSheet;
use App\Exports\Sheets\ChannelPricesSheet;
use App\Exports\Sheets\ExpenseComparisonSheet;
use App\Exports\Sheets\GeneralDetailsSheet;
use App\Exports\Sheets\ProfitLossSheet;
use App\Exports\Sheets\SalesBreakdownSheet;
use App\Exports\Sheets\SalesPerformanceSheet;
use App\Exports\Sheets\SiteKpisSheet;
use Maatwebsite\Excel\Concerns\WithMultipleSheets;

class SiteAnalysisExport implements WithMultipleSheets
{
    public function __construct(private array $data) {}

    public function sheets(): array
    {
        return [
            new GeneralDetailsSheet($this->data['general']),
            new SiteKpisSheet($this->data['kpis']),
            new SalesPerformanceSheet($this->data['sales_performance']),
            new SalesBreakdownSheet($this->data['sales_breakdown']),
            new ExpenseComparisonSheet($this->data['expense_comparison']),
            new ProfitLossSheet($this->data['profit_loss']),
            new ChannelPricesSheet($this->data['channel_prices']),
            new BottlePurchasesSheet($this->data['bottle_purchases']),
        ];
    }
}
