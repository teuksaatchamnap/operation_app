<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class SaleObjection extends Model
{
    use HasFactory;
    protected $table = 'sale_objection';
    protected $fillable = [
            'question',
            'answer',
    ];
    
}
