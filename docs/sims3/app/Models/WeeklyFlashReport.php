<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class WeeklyFlashReport extends Model
{
    use HasFactory;
    protected $table ='WeeklyFlashReport';
    protected $fillable = [
            'Id_Site',
            'Month',
            'Week',
            'Number_jugs_village',
            'Number_jugs_school',
            'Open_days',
    ];
}
