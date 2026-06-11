<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class MinimumStock extends Model
{
    use HasFactory;
    protected $table = 'minimum_stocks';
    protected $casts = [
        'month'  => 'date:Y-m-d',
    ];

    protected $fillable = [
        'site',
        'email',
        'item_name',
        'item_code',
        'item_unit',
        'use_qty',
        'month',
        'pay_by'
    ];
}
