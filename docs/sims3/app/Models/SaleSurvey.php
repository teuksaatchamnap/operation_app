<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class SaleSurvey extends Model
{
    use HasFactory;
    protected $table = 'sale_survey';
    protected $casts = [
        'submitted_date'  => 'date:Y-m-d',
    ];
    protected $fillable = [
        'site',
        'submitted_date',
        'do_you_know_the_brand',
        'what_is_the_brand',
        'how_many_bottle_you_change',
        'why_not_change_the_water',
        'how_many_times_the_entrepreneur_came',
        'frequency_how_often_do_you_purchase_o_we',
        'specify_other',
        'how_satisfied_are_you_with_the_timeliness',
        'how_satisfied_are_you_with_the_regularity',
        'how_satisfied_are_you_with_the_service',
        'overall_how_satisfied_are_you_with_owe_on_a_scale',
        'since_starting_you_feel_any_effect',
        'specify_other_please',
        'would_you_recommend_o_we',
        'if_yes_what_would_you_say',
        'other_please_specify',
        'new_customer_if_no_why_not',
        'others_specify_please',
        'besides_o_we_you_have_other_sources',
        'specify_another_20l_brand',
        'specify_another_50l_brand',
        'specify_other_brand',
        'before_owe_what_did_you_used',
        'other_please_specific',
    ];
}
