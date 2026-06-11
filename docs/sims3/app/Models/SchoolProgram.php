<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class SchoolProgram extends Model
{
    use HasFactory;
    
    protected $fillable = [
             'Id_Site',
            'en_name_english',
             'en_name_khmer',
            'en_phone_number',
            'commune_english',
            'province',
            'status_bottle',
            'school_code',
            'school_director_name_english',
            'school_director_phone_number',
            'school_director_signature',
            'school_name_english',
            'village_english',
            'academy_end',
            'academy_start',
            'school_grade',
           'number_of_boys',
           'number_of_children',
           'number_of_classes',
           'number_of_girls',
           'bottle_number_by_entre',
           'bottle_requested_by_school',
           'status',
           'bottle_approved',
            'en_name_khmer',
            'commune_khmer',
            'school_director_name_khmer',
            'school_name_khmer',
            'village_khmer',
            'academy_year',
    ];
    public function site()
    {
        return $this->belongsTo(Site::class);
    }
}
