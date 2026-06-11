<?php

use Illuminate\Support\Facades\Route;
use Spatie\Browsershot\Browsershot;

/*
|--------------------------------------------------------------------------
| Web Routes
|--------------------------------------------------------------------------
|
| Here is where you can register web routes for your application. These
| routes are loaded by the RouteServiceProvider and all of them will
| be assigned to the "web" middleware group. Make something great!
|
*/

Route::get('/', function () {
    return view('app');
});

// Test routes - only available in non-production environments
if (app()->isProduction()) {

    // Test invoice payment view
    Route::get('/test/invoice', function () {
        $testData = [
            'tran_id' => 'C120250612345678',
            'site' => 'C1',
            'month' => '06/2025',
            'amount' => 150000,
            'status_code' => 'APPROVED',
            'status' => 'settle',
            'transaction_date' => '2025-06-15 14:30:00',
            'generated_at' => now()->format('Y-m-d H:i:s')
        ];
        $html = view('invoices.payment', $testData)->render();
        $image = Browsershot::html($html)
            ->noSandbox()
            ->windowSize(800, 1000)
            ->deviceScaleFactor(2)
            ->fullPage()
            ->screenshot();
        return response($image)->header('Content-Type', 'image/png');
    });
}
