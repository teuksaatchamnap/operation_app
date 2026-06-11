<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class Mission extends Model
{
    use HasFactory;

    protected $casts = [
        'start_date'  => 'date:Y-m-d',
        'end_date' => 'date:Y-m-d',
    ];

    protected $fillable = [
        'admin_comment',
        'cost_accomodation',
        'cost_gasoline',
        'cost_per_diem',
        'days_off',
        'distance',
        'end_date',
        'liters',
        'location',
        'nb_days',
        'nb_nights',
        'need_advance',
        'other_expenses',
        'other_expenses_total',
        'position',
        'purpose',
        'requester',
        'requester_fullname',
        'start_date',
        'status',
        'title',
        'total',
        'transportation',
        'validator',
    ];
}
