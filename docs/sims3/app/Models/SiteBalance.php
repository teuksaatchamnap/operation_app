<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class SiteBalance extends Model
{
    use HasFactory;
    protected $table = 'site_balances';
    protected $fillable = [
        'site',
        'balance',
        'beginning_balance',
    ];
}
