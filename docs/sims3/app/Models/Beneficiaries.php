<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class Beneficiaries extends Model
{
    use HasFactory;
    protected $table = 'Beneficiaries';
    protected $fillable = [
        'Id_Site',
        'Month',
        'Beneficiaries',
        'Beneficiaries12months',
        'Old_Beneficiaries'
    ];
}
