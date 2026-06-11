<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class CashierSale extends Model
{
    use HasFactory;

    protected $table = 'cashier_sales';

    protected $fillable = [
        'site',
        'sale_date',
        'quantity',
        'unit_price',
        'type',
        'index'
    ];
}
