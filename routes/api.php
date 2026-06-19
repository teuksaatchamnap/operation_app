<?php

use App\Http\Controllers\AuthController;
use App\Http\Controllers\DimensionsController;
use App\Http\Controllers\FactMonthlyController;
use App\Http\Controllers\KpiController;
use App\Http\Controllers\ObjectiveController;
use App\Http\Controllers\SiteAnalysisController;
use App\Http\Controllers\SiteHoverController;
use Illuminate\Support\Facades\Route;

Route::post('/login', [AuthController::class, 'login']);

Route::middleware('auth:sanctum')->group(function () {
    Route::apiResource('kpis', KpiController::class);
    Route::apiResource('kpis.objectives', ObjectiveController::class)->only(['store', 'update', 'destroy']);
    Route::get('/objectives', [ObjectiveController::class, 'index']);
    Route::get('/fact-monthly', [FactMonthlyController::class, 'index']);
    Route::get('/getAuth', [AuthController::class, 'getAuth']);
    Route::post('/logout', [AuthController::class, 'logout']);
    Route::get('/advisors', [DimensionsController::class, 'getAdvisors']);
    Route::get('/platforms', [DimensionsController::class, 'getPlatforms']);
    Route::get('/sites', [DimensionsController::class, 'getSites']);
    Route::get('/sites/hover-data', [SiteHoverController::class, 'index']);
    Route::get('/sites/{site}/analysis', [SiteAnalysisController::class, 'show']);
    Route::get('/sites/{site}/analysis/export', [SiteAnalysisController::class, 'exportExcel']);
    Route::get('/sites/{site}/monthly-performance', [SiteAnalysisController::class, 'monthlyPerformance']);
    Route::get('/sites/{site}/sales-comparison', [SiteAnalysisController::class, 'salesComparison']);
    Route::get('/sites/{site}/monthly-sales-breakdown', [SiteAnalysisController::class, 'monthlySalesBreakdown']);
    Route::get('/sites/{site}/expense-breakdown', [SiteAnalysisController::class, 'expenseBreakdown']);
    Route::get('/sites/{site}/profit-loss', [SiteAnalysisController::class, 'profitLoss']);
    Route::get('/sites/{site}/pnl-expenses', [SiteAnalysisController::class, 'pnlExpenses']);
    Route::get('/sites/{site}/monthly-expense-by-category', [SiteAnalysisController::class, 'monthlyExpenseByCategory']);
    Route::get('/sites/{site}/monthly-profit-loss', [SiteAnalysisController::class, 'monthlyProfitLoss']);
    Route::get('/sites/{site}/profile', [SiteAnalysisController::class, 'siteProfile']);
    Route::get('/sites/{site}/channel-prices', [SiteAnalysisController::class, 'channelPrices']);
    Route::get('/sites/{site}/bottle-purchases', [SiteAnalysisController::class, 'bottlePurchases']);
    Route::get('/sites/{site}/daily-sales', [SiteAnalysisController::class, 'dailySales']);
    Route::get('/sites/{site}/water-loss-by-week', [SiteAnalysisController::class, 'waterLossByWeek']);
    Route::get('/sites/{site}/download-commune-contract', [SiteAnalysisController::class, 'downloadCommuneContract']);
    Route::get('/sites/{site}/entrepreneur-history', [SiteAnalysisController::class, 'entrepreneurHistory']);
    Route::get('/download-entrepreneur-contract/{filename}', [SiteAnalysisController::class, 'downloadEntrepreneurContract']);
});
