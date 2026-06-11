<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class Consumable extends Model
{
    use HasFactory;
    protected $table ='Consumable';
    public $timestamps = false;
    protected $casts = [
        'Month'  => 'date:Y-m-d',
        'Date_submission' => 'date:Y-m-d',
        'Price_Item' => 'decimal:4',
    ];

    protected $fillable = [
        'Id_Site',
        'Code_Consumable',
        'Category',
        'item',
        'Number_Item',
        'Price_Item',
        'Khmer_name',
        'English_name',
        'Validate',
        'Unit',
        'Payment_method',
        'Month',
        'Date_submission',
        'PO',
        'Supplier',
        'Remark',
        'EmailRequestor',
        'EmailApprover',
        'track'
    ];
}
