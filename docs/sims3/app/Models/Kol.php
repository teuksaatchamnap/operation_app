<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class Kol extends Model
{
    use HasFactory;
    protected $casts = [
        'record_date'  => 'date:Y-m-d',
    ];
    protected $table = 'kol';
    protected $fillable = [
                'site',
                'record_date',
                'village',
                'chief_village',
                'chief_village_contact',
                'total_houses',
                'total_household',
                'distance',
                'expectation',
                'actual_market',
                'market_comparison',
                'remark',
                'penentration',
    ];
   
}
