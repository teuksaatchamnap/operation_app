<?php

use App\Http\Controllers\AuthController;
use App\Http\Controllers\KpiController;
use Illuminate\Support\Facades\Route;

Route::apiResource('kpis', KpiController::class);

Route::post('/login', [AuthController::class, 'login']);

Route::middleware('auth:sanctum')->group(function () {
    Route::get('/getAuth', [AuthController::class, 'getAuth']);
    Route::post('/logout', [AuthController::class, 'logout']);
});
