<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class InvoicesRecord extends Model
{
    use HasFactory;
    protected $table = 'invoices_record';
    protected $casts = [
    'month' => 'datetime',
    ];
    protected $fillable = [
        'site',
        'month',
        'transaction_id',
        'amount',
        'issue_date',
        'payment_status',
        'payment_date',
    ];
}
