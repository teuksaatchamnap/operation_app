<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class Kpi extends Model
{
    use HasFactory;
    protected $table ='kpi';
    protected $fillable = [
        'staff_email',
    'kpi1',
    'kpi2',
    'kpi3',
    'kpi4',
    'kpi5',
   'target1',
   'target2',
   'target3',
   'target4',
   'target5',
   'result_kpi1',
   'result_kpi2',
   'result_kpi3',
   'result_kpi4',
   'result_kpi5',
   'qualitative_kpi1',
   'qualitative_kpi2',
   'qualitative_kpi3',
   'previous_score',
   'year',
    ];
    protected $casts = [
        'created_at' => 'datetime',
        'updated_at' => 'datetime',
    ];

    // Optional: Add validation rules
    public static function rules()
    {
        return [
            'staff_email' => 'required|email',
            'year' => 'required|string|max:4',
            'kpi1' => 'nullable|string',
            'kpi2' => 'nullable|string',
            'kpi3' => 'nullable|string',
            'kpi4' => 'nullable|string',
            'kpi5' => 'nullable|string',
            'target1' => 'nullable|string',
            'target2' => 'nullable|string',
            'target3' => 'nullable|string',
            'target4' => 'nullable|string',
            'target5' => 'nullable|string',
            'result_kpi1' => 'nullable|string',
            'result_kpi2' => 'nullable|string',
            'result_kpi3' => 'nullable|string',
            'result_kpi4' => 'nullable|string',
            'result_kpi5' => 'nullable|string',
            'qualitative_kpi1' => 'nullable|string',
            'qualitative_kpi2' => 'nullable|string',
            'qualitative_kpi3' => 'nullable|string',
            'previous_score' => 'nullable|string',
        ];
    }
   
}
