<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class WaterMeter extends Model
{
    use HasFactory;

    protected $table = 'water_meters';

    protected $fillable = [
        'site',
        'date',
        'value',
    ];
}
