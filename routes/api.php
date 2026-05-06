<?php

use App\Http\Controllers\AuthController;
use App\Http\Controllers\DimensionsController;
use App\Http\Controllers\FactMonthlyController;
use App\Http\Controllers\KpiController;
use App\Http\Controllers\ObjectiveController;
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
});
