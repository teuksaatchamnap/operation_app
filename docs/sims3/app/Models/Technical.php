<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Support\Carbon;

class Technical extends Model
{
    use HasFactory;
    protected $casts = [
        'acknowledge_time'  => 'date:Y-m-d',
        'creation_date' => 'date:Y-m-d',
        'problem_date'  => 'date:Y-m-d',
        'last_update' => 'date:Y-m-d',
        'start_intervention' => 'date:Y-m-d',
        'end_intervention'=>'date:Y-m-d',
        'date_need'=>'date:Y-m-d',
        'last_update' => 'collection'
    ];
    protected $fillable=[
        'site',
        'acknowledge_time',
        'amount',
        'amount_riel',
        'charge_from',
        //change here
        'rt_comment',
       // 'comment',
        'end_intervention',
        'start_intervention',
        'date_need',
        'comment_other',
        'item_platform',
        'comment_problem',
        'distance',
        'technician',
        'technician2',
        'email_quotation',
        'end_point',
        'start_point',
        'entrepreneur_pay',
        'Fixed',
        'gasoline',
        'problem_date',
        'last_update',
        'phone_number',
        'rt_request_stock',
        //'validate_item',
        'item_receiver',
        'price_gasoline',
        'problem_status',
        'site_problem_description',
        'sub_problem_description',
        'stop_work',
        'status',
        'quotation',
        'stock_type',
        'report_by',
        'reporting',
        'rt_advisor',
        'rt_site_problem_description',
        'rt_sub_problem_description',
        'send_quotation',
        'site_platform',
        'rt_solution',
        'totalPriceAllItem',
        'managerValidateItem',
        'allRTProblem',
         'checkPrice'

    ];
    // public function getJobStartAttribute($value) {
    //     if ($value !== null) {
    //         //$value format 'Y:m:d H:i:s' to 'Y-m-d H:i'
    //        return (new Carbon($value))->format('Y-m-d');
    //     }
    //     return $value;
    // }
    public function site(): BelongsTo
    {
        return $this->belongsTo(Site::class,"site","Id_Site");
    }
    public function technicalProblem()
    {
        return $this->hasMany(TechnicalProblem::class,'technical_id', 'id');
    }
}
