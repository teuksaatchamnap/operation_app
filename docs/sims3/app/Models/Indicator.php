<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class Indicator extends Model
{
    use HasFactory;
    protected $table = 'Indicators';
    protected $fillable = [
                'Id_Site',
                'Month',
                'Number_of_Operator',
                'Number_Bottles_in_Operation',
                'Number_Bottles_in_Stock',
                'Number_Bottles_Broken_Lost',
                'Water_Consume',
                'Number_of_Vehicle',
                'Water_begining',
                'Water_end',
                'Machine_begining',
                'Machine_end',
                'Saving_outside_TS',
                'Number_of_disinfection',
                'Number_of_delivery',
    ];
}
