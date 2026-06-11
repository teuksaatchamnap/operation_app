<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class Expense extends Model
{
    use HasFactory;
    public $timestamps = false;
    protected $casts = [
        'Month'  => 'date:Y-m-d',
    ];
    protected $primaryKey = 'Code_expenses';
    protected $table = 'Expenses';
    protected $fillable = [
                'Id_Site',
                'Month',
                'Ref_expenses',
                'Amount_expenses',
                'Paid',
                'Category_expenses'
    ];
    
}
