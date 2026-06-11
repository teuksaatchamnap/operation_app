<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class TransportationAssessment extends Model
{
    use HasFactory;
    protected $fillable = [
        'site',
        'transportation_type',
        'condition_of_transportation',
        'condition_of_trolley',
        'purchased_date',
];
}
