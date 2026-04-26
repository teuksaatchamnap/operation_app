<?php

use App\Http\Controllers\KpiController;
use Illuminate\Support\Facades\Route;

Route::apiResource('kpis', KpiController::class);
