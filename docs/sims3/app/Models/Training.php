<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class Training extends Model
{
    use HasFactory;
    protected $table ='training';
    protected $fillable = [
            'staff_email',
            'cooperate_score',
            'entrepreneur_score',
            'sale_and_maketing_score',
            'water_quality_score',
            'entreturnover' ,
            'entretraining',
            'owecommittee' ,
            'entreprenureship' ,
            'technicianseminar' ,
            'total_score',
            'final_result',
    ];
}
