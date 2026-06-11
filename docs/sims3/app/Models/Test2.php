<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Casts\Attribute;
use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Support\Carbon;

class Test2 extends Model
{
    use HasFactory;
    protected $table = 'sales';
    // protected $casts = [
    //     'Month' => 'datetime',
    // ];
    // public function scopeBetweenYears($query, $startYear, $endYear)
    // {
    //     return $query->whereBetween('year(Month)', [$startYear, $endYear]);
    // }
    // protected function month(): Attribute
    // {
    //     return Attribute::get(function ($value) {
    //         if ($value instanceof Carbon) {
    //             return $value->month;
    //         }

    //         return $value ? $value->month : null;
    //     });
    // }
}
