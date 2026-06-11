<?php

namespace App\Models;

use Exception;
use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class Invoice extends Model
{
    use HasFactory;
    protected $table = 'invoices';
    protected $casts = [
    'month' => 'datetime',
];
    protected $fillable = [
        'site',
        'month',
        'beginning_balance',
        'transaction_amount',
        'receipt_number',
        'invoice_type',
        'invoice_type_khmer_name',
        'remain_amount',
        'pictureQR',
        'picture_invoice',
        'status',
        'invoice_ref',
        'aba_status_code',
        'aba_amount',
        'aba_date',
        'aba_transaction_id',
    ];
    public function siteObject()
    {
        return $this->belongsTo(Site::class, 'site', 'Id_Site');
    }
    public function getFormattedAbaDateAttribute()
{
    // Check if the date is empty or is the zero date
    if (empty($this->aba_date) || 
        $this->aba_date === '0000-00-00 00:00:00' || 
        $this->aba_date === '0000-00-00') {
        return null;
    }
    
    // If we have a valid date, format it
    try {
        return date('Y-m-d', strtotime($this->aba_date));
    } catch (Exception $e) {
        return null;
    }
}
}
