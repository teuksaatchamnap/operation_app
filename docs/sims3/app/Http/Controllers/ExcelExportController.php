<?php

namespace App\Http\Controllers;

use App\Exports\ActivityIndicatorExport;
use App\Exports\ClosureExport;
use App\Exports\ConsumablesExport;
use App\Exports\F2FExport;
use App\Exports\FinanceReportExport;
use App\Exports\FlashReportExport;
use App\Exports\ManagementDashboardExport;
use App\Exports\OFDExport;
use App\Exports\QualityExport;
use App\Exports\SalesTeamPerformanceExport;
use App\Exports\SiteAlertExport;
use App\Exports\SiteAnalysisExport;
use App\Exports\SiteAnalysisTechnicalExport;
use App\Exports\SiteProfileExport;
use App\Exports\TechnicalInterventionExport;
use App\Exports\VehicleDeliveryImpactExport;
use Carbon\Carbon;
use Illuminate\Http\Request;

/**
 * Controller for downloading the monthly Excel reports.
 *
 * Each action validates an optional `month` (YYYY-MM) query parameter,
 * instantiates the matching Export class, and streams the .xlsx file.
 */
class ExcelExportController extends Controller
{
    /**
     * F2F (Face-to-Face) report.
     * GET /api/f2f/export?month=YYYY-MM
     */
    public function exportF2F(Request $request)
    {
        $month = $this->resolveMonth($request);
        $export = new F2FExport($month);
        return $export->download();
    }

    /**
     * OFD (Operational & Financial Dashboard).
     * GET /api/ofd/export?month=YYYY-MM
     */
    public function exportOFD(Request $request)
    {
        $month = $this->resolveMonth($request);
        $export = new OFDExport($month);
        return $export->download();
    }

    /**
     * Activity Indicators.
     * GET /api/activity-indicator/export?month=YYYY-MM
     */
    public function exportActivityIndicator(Request $request)
    {
        $month = $this->resolveMonth($request);
        $export = new ActivityIndicatorExport($month);
        return $export->download();
    }

    /**
     * Standalone Site Analysis.
     * GET /api/site-analysis/export?month=YYYY-MM
     */
    public function exportSiteAnalysis(Request $request)
    {
        $month = $this->resolveMonth($request);
        $export = new SiteAnalysisExport($month);
        return $export->download();
    }

    /**
     * Closure report (fermetures de sites).
     * GET /api/closure/export?month=YYYY-MM
     */
    public function exportClosure(Request $request)
    {
        $month = $this->resolveMonth($request);
        return (new ClosureExport($month))->download();
    }

    /**
     * Flash Report (indicateurs commerciaux rapides).
     * GET /api/flash-report/export?month=YYYY-MM
     */
    public function exportFlashReport(Request $request)
    {
        $month = $this->resolveMonth($request);
        return (new FlashReportExport($month))->download();
    }

    /**
     * Consumables (consommables et factures).
     * GET /api/consumables/export?month=YYYY-MM
     */
    public function exportConsumables(Request $request)
    {
        $month = $this->resolveMonth($request);
        return (new ConsumablesExport($month))->download();
    }

    /**
     * Finance Report (P&L, dettes, KPI).
     * GET /api/finance-report/export?month=YYYY-MM
     */
    public function exportFinanceReport(Request $request)
    {
        $month = $this->resolveMonth($request);
        return (new FinanceReportExport($month))->download();
    }

    /**
     * Quality Report (qualité de l'eau).
     * GET /api/quality/export?month=YYYY-MM
     */
    public function exportQuality(Request $request)
    {
        $month = $this->resolveMonth($request);
        return (new QualityExport($month))->download();
    }

    /**
     * Technical Intervention Report.
     * GET /api/technical-intervention/export?month=YYYY-MM
     */
    public function exportTechnicalIntervention(Request $request)
    {
        $month = $this->resolveMonth($request);
        return (new TechnicalInterventionExport($month))->download();
    }

    /**
     * Sales Team Performance Report.
     * GET /api/sales-team-performance/export?month=YYYY-MM
     */
    public function exportSalesTeamPerformance(Request $request)
    {
        $month = $this->resolveMonth($request);
        return (new SalesTeamPerformanceExport($month))->download();
    }

    /**
     * Site Alert (sites en alerte/déclin).
     * GET /api/site-alert/export?month=YYYY-MM
     */
    public function exportSiteAlert(Request $request)
    {
        $month = $this->resolveMonth($request);
        return (new SiteAlertExport($month))->download();
    }

    /**
     * Site Profile Database.
     * GET /api/site-profile/export?month=YYYY-MM
     */
    public function exportSiteProfile(Request $request)
    {
        $month = $this->resolveMonth($request);
        return (new SiteProfileExport($month))->download();
    }

    /**
     * Vehicle Delivery Impact Analysis.
     * GET /api/vehicle-delivery-impact/export?month=YYYY-MM
     * Accepte aussi vehicleDates en JSON : {"B3":"2024-05","C2":"2024-08",...}
     */
    public function exportVehicleDeliveryImpact(Request $request)
    {
        $month = $this->resolveMonth($request);
        $vehicleDates = $request->input('vehicleDates')
            ? json_decode($request->input('vehicleDates'), true) ?? []
            : [];
        return (new VehicleDeliveryImpactExport($month, $vehicleDates))->download();
    }

    /**
     * Management Dashboard (6 tabs).
     * GET /api/management-dashboard/export?month=YYYY-MM
     */
    public function exportManagementDashboard(Request $request)
    {
        $month = $this->resolveMonth($request);
        return (new ManagementDashboardExport($month))->download();
    }

    /**
     * Site Analysis Technical (analyse technique par site avec dropdown).
     * GET /api/site-analysis-technical/export?month=YYYY-MM
     */
    public function exportSiteAnalysisTechnical(Request $request)
    {
        $month = $this->resolveMonth($request);
        return (new SiteAnalysisTechnicalExport($month))->download();
    }

    // ─── Helpers ──────────────────────────────────────────────────

    private function resolveMonth(Request $request): Carbon
    {
        $request->validate([
            'month' => 'nullable|date_format:Y-m',
        ]);

        return $request->input('month')
            ? Carbon::createFromFormat('Y-m', $request->input('month'))->startOfMonth()
            : Carbon::now()->startOfMonth()->subMonth();
    }
}
