<?php

use App\Http\Controllers\AdvisorBonusController;
use App\Http\Controllers\ExcelExportController;
use App\Http\Controllers\AssessmentController;
use App\Http\Controllers\AuthController;
use App\Http\Controllers\CashierAppController;
use App\Http\Controllers\CommcareController;
use App\Http\Controllers\ConfigurationController;
use App\Http\Controllers\ConsumableController;
use App\Http\Controllers\EntrepreneurProfileController;
use App\Http\Controllers\FlashController;
use App\Http\Controllers\FlashReportController;
use App\Http\Controllers\InvoiceController;
use App\Http\Controllers\KolController;
use App\Http\Controllers\KpiController;
use App\Http\Controllers\MissionController;
use App\Http\Controllers\NewEntrepreneurController;
use App\Http\Controllers\PerformanceApprailsalController;
use App\Http\Controllers\ProvinceReportController;
use App\Http\Controllers\ReportController;
use App\Http\Controllers\RountineController;
use App\Http\Controllers\SaleObjectionController;
use App\Http\Controllers\SaleRecordController;
use App\Http\Controllers\SaleTeamController;
use App\Http\Controllers\SampleController;
use App\Http\Controllers\SampleExternalController;
use App\Http\Controllers\SchoolProgramController;
use App\Http\Controllers\SensorController;
use App\Http\Controllers\SiteController;
use App\Http\Controllers\TechnicalController;
use App\Http\Controllers\TelegramController;
use App\Http\Controllers\Test1Controller;
use App\Http\Controllers\TrainingController;
use App\Http\Controllers\UserController;
use App\Http\Controllers\ReminderController;
use App\Http\Controllers\CashierNotificationController;
use Illuminate\Support\Facades\Route;
use Illuminate\Support\Facades\Storage;


Route::middleware(['auth:sanctum'])->group(function () {
    Route::get('/getAuth', [AuthController::class, 'getAuth']);    Route::apiResource('missions', MissionController::class);
    Route::get('/missions/{mission}/print', [MissionController::class, 'print']);
    Route::get('/missionsExport', [MissionController::class, 'export']);
    Route::get('/datastore/settleForms', [CommcareController::class, 'getSettleInvoiceForms']);
    Route::apiResource('/sites', SiteController::class)->only(["index"]);
    Route::post('/sites/importExcel', [SiteController::class, 'importExcel']);
    Route::apiResource('sites', SiteController::class)->only(["store", "update"]);
});

Route::middleware(['auth:sanctum', 'permission:quality_view'])->group(function () {
    Route::apiResource('samples', SampleController::class);
    Route::get('/sampleExcelSite', [SampleController::class, 'sampleExcelSite']);
    Route::get('/sampleExcelSiteOpenOrSiteSelection', [SampleController::class, 'sampleExcelSiteOpenOrSiteSelection']); // get excel of site opening and selection
    Route::get('/technical/downloadSite/{site}', [TechnicalController::class, 'downloadSite']);
    Route::get('/samplesForSite/{site}', [SampleController::class, 'getSamplesForSite']);
    Route::get('/samplesExport', [SampleController::class, 'exportExcel']);
    Route::get('/samplePrint', [SampleController::class, 'print']);
    Route::get('/technical/{id}', [TechnicalController::class, 'show']);
    Route::get('/technical/detail/{id}', [TechnicalController::class, 'detailTechnical']);
    //Route::get('/technical/downloadSite/{site}',[TechnicalController::class,'downloadSite']);
    Route::post('/technical/store', [TechnicalController::class, 'store']);
    Route::get('/technical', [TechnicalController::class, 'index']);
    Route::put('/technical/update/{id}', [TechnicalController::class, 'update']);
    Route::get('/getMail', [TechnicalController::class, 'getEmail']);
    Route::get('/downloadReport', [TechnicalController::class, 'excelExport']);
    Route::get('/downloadDN', [TechnicalController::class, 'downloadDN']);
    Route::get('/getDistance', [TechnicalController::class, 'getDistance']);
    Route::get('/siteOpening', [SampleController::class, 'siteOpening']);
    Route::get('/getSampleCode', [SampleController::class, 'getSampleCode']);
    Route::delete('/sample/{id}', [SampleController::class, 'destroy']);
});
// Route for PA
Route::middleware(['auth:sanctum', 'permission:pa_view'])->group(function () {
    Route::get('/newCashier', [InvoiceController::class, 'newCashier']);
    Route::get('/invoices/export', [InvoiceController::class, 'exportInvoice']);
    Route::get('/school/export', [InvoiceController::class, 'exportSchool']);
    Route::get('/getInvoices', [InvoiceController::class, 'getInvoices']);
    Route::get('/payway/qr', [InvoiceController::class, 'generateQR']);
    Route::get('/school', [InvoiceController::class, 'school']);
    Route::get('/recordAssess', [InvoiceController::class, 'recordAssess']);
    Route::get('/newEntrepreneur', [NewEntrepreneurController::class, 'show']);

    Route::get('/pr', [SampleController::class, 'pr']);
    Route::get('/minimumStock', [TechnicalController::class, 'minimumStock']);
    Route::get('/downloadMinimumStock', [TechnicalController::class, 'downloadMinimumStock']);
    Route::get('/DownloadExcelMinimumStock', [TechnicalController::class, 'DownloadExcelMinimumStock']);
    Route::get('/getDataMinimumStock', [TechnicalController::class, 'getDataMinimumStock']);
    Route::get('/downloadDataMinimumStock', [TechnicalController::class, 'downloadDataMinimumStock']);
    Route::get('/sampleExcelRangDate', [SampleController::class, 'sampleExcelRangDate']);
    Route::get('/getEntrepreneur', [NewEntrepreneurController::class, 'show']);
    Route::get('/getAllEntrepreneur', [EntrepreneurProfileController::class, 'show']);
    Route::get('/panaltySite', [SampleController::class, 'panaltySite']);
    Route::post('/uploadExcel', [ConsumableController::class, 'uploadExcel']);
    Route::get('/getRequestConsumable', [ConsumableController::class, 'index']);
    Route::put('/validateRequestConsumable', [ConsumableController::class, 'update']);
    Route::delete('/rejectValidation', [ConsumableController::class, 'destroy']);
    Route::get('/salesChart/{siteId?}', [Test1Controller::class, 'salesChart']);
    Route::get('/checkLocation', [MissionController::class, 'checkLocation']);
    // Route::get('/takeRecordFromGoogle', [EntrepreneurProfileController::class, 'create']);
    // Route::get('/insertRecordFromGoogle', [EntrepreneurProfileController::class, 'index']);
    Route::get('/checkColiform', [SampleController::class, 'checkColiform']);
    Route::post('/editTechnicianSite', [SiteController::class, 'editTechnicianSite']);
    Route::post('/uploadEntrepreneurContract', [EntrepreneurProfileController::class, 'uploadEntrepreneurContract']);
    Route::get('/getSites', [SiteController::class, 'getSites']);
    Route::post('/site-contract', [SiteController::class, 'storeOrUpdateCommuneOrTrainingContract']);
    Route::delete('/entrepreneur/delete/{id}', [EntrepreneurProfileController::class, 'destroy']);
    Route::get('/downloadPictures', [CommcareController::class, 'downloadPictures']);
    Route::get('/getPermission', [Test1Controller::class, 'getPermission']);
    Route::post('/uploadSiteTechnician', [TechnicalController::class, 'uploadSiteTechnician']);
    Route::get('/getAllYears', [SchoolProgramController::class, 'getAllYears']);
    Route::get('/entrepreneurForm/{id}', [EntrepreneurProfileController::class, 'edit']);
    Route::put('/entrepreneur/update/{id}', [EntrepreneurProfileController::class, 'update']);
    Route::get('/reports/{siteId}', [ReportController::class, 'siteReport']);
    Route::get('/WQReport', [ReportController::class, 'WQReport']);
    Route::get('/calculateResult', [ReportController::class, 'calculateResult']);
    Route::get('/wq', [ReportController::class, 'wq']);
    Route::get('/calculateResultMonthlyOrAlert', [ReportController::class, 'calculateResultMonthlyOrAlert']);
    Route::get('/calculateAllResults', [ReportController::class, 'calculateAllResults']);
    Route::get('/assessmentAnalysis/{siteId}', [ReportController::class, 'assessmentAnalysis']);
    Route::get('/assessmentDetail/detail/{site}', [ReportController::class, 'assessmentDetail']);
    Route::get('/testWQ', [ReportController::class, 'testWQ']);
    Route::get('/advisorsEmail', [SiteController::class, 'advisorsEmail']);
    Route::get('/debt-details/{siteId}', [ReportController::class, 'debtDetails']);
    Route::get('/income-details/{siteId}', [ReportController::class, 'incomeDetails']);
    Route::get('/allInvoices', [InvoiceController::class, 'getSitesWithInvoices']);
    Route::post('/send-invoice-telegram', [InvoiceController::class, 'sendInvoiceTelegram']);
    Route::post('/generateQRFromCashier', [InvoiceController::class, 'generateQRFromCashier']);
    Route::post('/invoices/update-status-by-site-month', [InvoiceController::class, 'updateStatusBySiteAndMonth']);
    Route::get('/invoicesDetail', [InvoiceController::class, 'invoicesDetail']);
    Route::post('/invoices/update-payments', [InvoiceController::class, 'updatePayments']);
    Route::post('/getSiteBalance', [InvoiceController::class, 'getSiteBalance']);
    Route::get('/savingAnddebt', [InvoiceController::class, 'savingAnddebt']);
    Route::get('/getSite', [InvoiceController::class, 'getSite']);
    Route::get('/getChatID/{siteId}', [InvoiceController::class, 'getChatID']);
    Route::get('/getSiteBalance/{siteId}', [InvoiceController::class, 'getSiteBalanceById']);
    Route::post('/updateBalance', [InvoiceController::class, 'updateBalance']);

    Route::post('/saleobjection', [SaleObjectionController::class, 'import']);
    Route::apiResource('flashReport', FlashReportController::class);
    Route::get('/pa', [PerformanceApprailsalController::class, 'index']);
    Route::get('/pa/{id}', [PerformanceApprailsalController::class, 'show']);
    Route::get('/staffInfo', [PerformanceApprailsalController::class, 'staffInfo']);
    Route::get('/getTraining/{email}', [PerformanceApprailsalController::class, 'getTraining']);
    Route::get('/getPreviousPA/{email}', [PerformanceApprailsalController::class, 'getPreviousPA']);
    Route::get('/detailStaffInfo/{email}', [PerformanceApprailsalController::class, 'detailStaffInfo']);
    Route::get('/getKPI/{email}', [PerformanceApprailsalController::class, 'getKPI']);
    Route::post('/pa/store', [PerformanceApprailsalController::class, 'store']);
    Route::put('/pa/update/{id}', [PerformanceApprailsalController::class, 'update']);
    Route::put('/pa/staffAgree/{id}', [PerformanceApprailsalController::class, 'staffAgree']);
    Route::get('/pa/print/{id}', [PerformanceApprailsalController::class, 'printExcel']);
    Route::get('/pa/newprint/{id}', [PerformanceApprailsalController::class, 'newPrintExcel']);

    Route::post('/objective', [Test1Controller::class, 'import']);
    Route::post('/kpi', [KpiController::class, 'importData']);
    Route::post('/trainingImport', [KpiController::class, 'importDataTraining']);
    Route::post('/paImport', [KpiController::class, 'importDataPA']);
    Route::get('/training', [TrainingController::class, 'index']);
    Route::get('/training/{id}', [TrainingController::class, 'show']);
    Route::get('/saleobjection', [SaleObjectionController::class, 'index']);
    Route::get('email', [Test1Controller::class, 'email']);
    Route::get('/staffInfo', [PerformanceApprailsalController::class, 'staffInfo']);
    Route::apiResource('kol', KolController::class);

    Route::apiResource('/saleRecord', SaleTeamController::class);
    Route::get('/saleRecord/detail', [SaleTeamController::class, 'show']);
    Route::put('/saleRecord/update/{id}', [SaleTeamController::class, 'update']);
    Route::delete('/saleRecord/delete/{id}', [SaleTeamController::class, 'destroy']);
    Route::get('/saleRecord/search/{id}', [SaleTeamController::class, 'searchRecord']);
    Route::get('/saleDownloadReport', [SaleTeamController::class, 'saleDownloadReport']);
    Route::get('/padownloadExcel', [PerformanceApprailsalController::class, 'exportExcel1']);
    Route::get('/test1', [PerformanceApprailsalController::class, 'test']);
    Route::get('/siteSelection/donwloadPicture', [SampleController::class, 'donwloadPicture']);
    Route::post('/importSiteAssessment', [AssessmentController::class, 'importData']);
    Route::post('/importSiteRountine', [RountineController::class, 'importData']);
    // Route::post('/importInvoice', [InvoiceController::class, 'importInvoice1']);
    Route::post('/upload-excel', [InvoiceController::class, 'importInvoice']);
    Route::get('/invoicesRecordHistory', [InvoiceController::class, 'invoicesRecordHistory']);
    Route::get('/assessment', [AssessmentController::class, 'index']);
    Route::get('/assessmentDownload', [AssessmentController::class, 'excelDownload']);
    Route::get('/assessmentDownloadAll', [AssessmentController::class, 'assessmentDownloadAll']);
    Route::put('/sites/update/{id}', [SiteController::class, 'updateSite']);
    Route::delete('/pa/delete/{id}', [PerformanceApprailsalController::class, 'deleteRecord']);

    Route::get('/newEntrepreneurDetail/detail/{id}', [EntrepreneurProfileController::class, 'detailEntrepreneur']);
    Route::get('/newEntrepreneur/detail/{id}', [NewEntrepreneurController::class, 'detailEntrepreneur']);
    Route::get('/schoolProgram', [SchoolProgramController::class, 'index']);
    Route::get('/schoolProgram/search/{id}', [SchoolProgramController::class, 'searchRecord']);
    Route::get('/schoolProgramDownload', [SchoolProgramController::class, 'schoolProgramDownload1']);
    Route::get('/ass/{site}', [AssessmentController::class, 'record']);
    Route::get('/getData', [Test1Controller::class, 'getData']);
    Route::put('/schoolProgram/update/{id}', [SchoolProgramController::class, 'update']);
    Route::get('/schoolsContractPrint/{platform}', [SchoolProgramController::class, 'schoolsContractPrint']);
    Route::get('/schoolProgramDownloadExcel', [SchoolProgramController::class, 'schoolProgramDownloadExcel']);
    Route::delete('/deleteSchoolProgram/{id}', [SchoolProgramController::class, 'deleteSchoolProgram']);
    Route::get('/schoolQuery', [SchoolProgramController::class, 'schoolQuery']);
    Route::put('/validateSchool', [SchoolProgramController::class, 'validateSchool']);
    Route::get('/formAssessment/{id}', [AssessmentController::class, 'showformAssessment']);
    Route::put('/formAssessment/update/{id}', [AssessmentController::class, 'update']);
    Route::get('/formRoutine/{id}', [RountineController::class, 'show']);
    Route::put('/formRoutine/update/{id}', [RountineController::class, 'update']);
    Route::get('/external', [SampleController::class, 'external']);
    Route::post('/samplesExternal', [SampleExternalController::class, 'saveSamplesExternal']);
    Route::delete('/deleteExternalSample/{id}', [SampleExternalController::class, 'destroy']);
    Route::get('/downloadFile/{path}', [SampleExternalController::class, 'downloadFile']);
    Route::get('/transportation', [AssessmentController::class, 'transportation']);
    Route::get('/flashReportDashboard', [FlashReportController::class, 'show']);
    Route::get('/flashReport/form/{id}', [FlashReportController::class, 'detail']);
    Route::put('/flashReport/update/{id}', [FlashReportController::class, 'update']);
    Route::get('/downloadCommuneContract/{path}', [SiteController::class, 'downloadCommuneContract']);

    Route::get('/downloadTrainingContract/{path}', [SiteController::class, 'downloadTrainingContract']);
    Route::get('/downloadEntrepreneurContract/{path}', [EntrepreneurProfileController::class, 'downloadEntrepreneurContract']);
    Route::get('/datastore/settleForms', [CommcareController::class, 'getSettleInvoiceForms']);
    Route::get('/getSiteStatus', [CommcareController::class, 'getSiteStatus']);
    Route::get('/showPicture', [CommcareController::class, 'showPicture']);
    Route::get('/datastore/schoolPictures', [CommcareController::class, 'getSchoolPictures']);
    Route::get('/kolDownloadReport', [KolController::class, 'kolDownloadReport']);
    Route::get('/salSurveyDownloadReport', [SaleTeamController::class, 'salSurveyDownloadReport']);
    Route::get('/saleSurvey', [KolController::class, 'saleSurvey']);
});

Route::middleware(['auth:sanctum', 'permission:sale_view'])->group(function () {
    // Route::apiResource('/saleRecord',SaleTeamController::class);

});

Route::middleware(['auth:sanctum', 'permission:finance_check'])->group(function () {
    Route::get('/provinceReport/provinces', [ProvinceReportController::class, 'provinces']);
    Route::get('/provinceReport/download',  [ProvinceReportController::class, 'download']);
});

Route::middleware(['auth:sanctum', 'permission:edit_permissions'])->group(function () {
    Route::apiResource('users', UserController::class);
    Route::get('/permissions', [UserController::class, 'getPermissions']);
    Route::get('/allPermissions', [UserController::class, 'getAllPermissions']);
    Route::apiResource('configurations', ConfigurationController::class);
    Route::apiResource('telegram-groups', TelegramController::class);
    Route::post('/telegram/send-test-message', [TelegramController::class, 'sendTestMessage']);
});

Route::middleware(['auth:sanctum', 'permission:site_edit'])->group(function () {
    //Route::post('/sites/importExcel', [SiteController::class, 'importExcel']);
});

Route::middleware(['auth:sanctum', 'permission:site_view'])->group(function () {
    Route::get('/sites/export', [SiteController::class, 'export']);
    Route::get('/sites/template', [SiteController::class, 'downloadTemplate']);
});

Route::middleware(['auth:sanctum', 'permission:cashier|cashier_admin'])->group(function () {
    Route::apiResource('telegram-groups', TelegramController::class)->only(["index"]);
    Route::get('/cashier/sales', [CashierAppController::class, 'index']);
    Route::get('/cashier/site/{site}', [CashierAppController::class, 'getEntrepreneurData']);
    Route::post('/cashier/sales', [CashierAppController::class, 'store']);
    Route::get('/cashier/expenses', [CashierAppController::class, 'getExpenses']);
    Route::post('/cashier/expenses', [CashierAppController::class, 'storeExpenses']);
    Route::get('/cashier/wis', [CashierAppController::class, 'getWiS']);
    Route::post('/cashier/wis', [CashierAppController::class, 'storeWiS']);
    Route::get('/cashier/water', [CashierAppController::class, 'getLatestWater']);
    Route::post('/cashier/water', [CashierAppController::class, 'storeWater']);
    Route::post('/cashier/upload', [CashierAppController::class, 'uploadFile']);
    Route::post('/telegram/sendImageToSite', [TelegramController::class, 'sendImageToSite']);
    Route::apiResource('reminders', ReminderController::class);
    Route::apiResource('cashier-notifications', CashierNotificationController::class);
});

Route::get('/advisor-bonus/export', [AdvisorBonusController::class, 'export']);
Route::get('/f2f/export', [ExcelExportController::class, 'exportF2F']);
Route::get('/ofd/export', [ExcelExportController::class, 'exportOFD']);
Route::get('/activity-indicator/export', [ExcelExportController::class, 'exportActivityIndicator']);
Route::get('/site-analysis/export', [ExcelExportController::class, 'exportSiteAnalysis']);
Route::get('/closure/export', [ExcelExportController::class, 'exportClosure']);
Route::get('/flash-report/export', [ExcelExportController::class, 'exportFlashReport']);
Route::get('/consumables/export', [ExcelExportController::class, 'exportConsumables']);
Route::get('/finance-report/export', [ExcelExportController::class, 'exportFinanceReport']);
Route::get('/quality/export', [ExcelExportController::class, 'exportQuality']);
Route::get('/technical-intervention/export', [ExcelExportController::class, 'exportTechnicalIntervention']);
Route::get('/sales-team-performance/export', [ExcelExportController::class, 'exportSalesTeamPerformance']);
Route::get('/site-alert/export', [ExcelExportController::class, 'exportSiteAlert']);
Route::get('/site-profile/export', [ExcelExportController::class, 'exportSiteProfile']);
Route::get('/vehicle-delivery-impact/export', [ExcelExportController::class, 'exportVehicleDeliveryImpact']);
Route::get('/management-dashboard/export', [ExcelExportController::class, 'exportManagementDashboard']);
Route::get('/site-analysis-technical/export', [ExcelExportController::class, 'exportSiteAnalysisTechnical']);
Route::post('/login', [AuthController::class, 'login']);
Route::post('/logout', [AuthController::class, 'logout']);
Route::post('/commcare', [CommcareController::class, 'store']);
Route::get('/sites/exportFromCloudSQL', [SiteController::class, 'exportFromCloudSQL']);
Route::get('/sensor', [SensorController::class, 'index']);
Route::get('/showtime', [SensorController::class, 'showTime']);

Route::get('/download-template', function () {
    $filePath = 'templates/excelTemplate.xlsx';
    if (Storage::exists($filePath)) {
        return Storage::download($filePath, 'excelTemplate.xlsx');
    } else {

        return response()->json(['error' => 'Template file not found.'], 404);
    }
})->name('api.download.template');

Route::get('/templateSiteTechnician', function () {
    $filePath = 'templates/technician.xlsx';
    if (Storage::exists($filePath)) {
        return Storage::download($filePath, 'technician.xlsx');
    } else {

        return response()->json(['error' => 'Template file not found.'], 404);
    }
})->name('api.download.template');
Route::post('/receivePaymentABA', [InvoiceController::class, 'receivePaymentABA']);
Route::get('/testAPI', [InvoiceController::class, 'testAPI']);
Route::get('/requestEmail', [SampleController::class, 'requestEmail']);
Route::get('/getTransactionDetail', [InvoiceController::class, 'getTransactionDetail']);
Route::get('/sql', [InvoiceController::class, 'sql']);

// Route::get('/translate', [KolController::class, 'translateName']);
