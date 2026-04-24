<?php

namespace App\Models;

use Database\Factories\KpiFactory;
use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class Kpi extends Model
{
    /** @use HasFactory<KpiFactory> */
    use HasFactory;

    public $timestamps = false;

    protected $fillable = [
        'name',
        'col_name',
        'unit',
        'periodicity',
        'type',
    ];
}
