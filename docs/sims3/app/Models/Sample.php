<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class Sample extends Model
{
    use HasFactory;

    protected $casts = [
        'analysis_date'  => 'date:Y-m-d',
        'site_open_sample_date' => 'date:Y-m-d',
        'received_date' => 'date:Y-m-d',
        'response_date'  => 'date:Y-m-d',
        'sample_date' => 'date:Y-m-d',
        'last_updates' => 'collection',

    ];

    protected $fillable = [
        'action_done',
        'alert_number',
        'alkalinity',
        'aluminium',
        'amonia',
        'analysis_date',
        'arsenic',
        'calcium',
        'chloride',
        'chlorine',
        'color',
        'comment',
        'conductivity',
        'contamination_level_bottle',
        'contamination_level_machine',
        'created_by',
        'delay',
        'desinfection',
        'email_alert',
        'escherichia',
        'escherichia_bottle',
        'enterocoque',
        'enterocoque_bottle',
        'fluoride',
        'hardness',
        'iron',
        'last_updates',
        'manganese',
        'nitrate',
        'nitrite',
        'ph',
        'pretreatment',
        'production',
        'received_date',
        'response_date',
        'root_cause',
        'safe',
        'sample_date',
        'silver',
        'site',
        'smell',
        'sulfates',
        'taste',
        'tds',
        'temperature',
        'test_number',
        'total_coliform',
        'total_coliform_bottle',
        'total_chlore',
        'turbidity',
        'site_open_sample_type',
        'site_open_description',
        'site_open_sample_by',
        'site_open_final_judgement',
        'site_open_comment',
        'site_open_judgement',
        'site_open_solution',
        'site_open_sample_date',
        'site_open_project_type',
        'type',
        'sample_code',
        'sample_en_location',
        'sample_kh_location',
        'laboratory',
        'latitude',
        'longtitude',
        'email_status',
        'raw_water_type'
    ];
    public function uploadPicture()
    {
        return $this->hasMany(UploadPicture::class);
    }
    public function siteRelation()
    {
        return $this->belongsTo(Site::class, 'site', 'Id_Site');
    }
    public function site()
    {
        // 'site' column in Sample points to Sites.Id_Site
        return $this->belongsTo(Site::class, 'site', 'Id_Site');
    }
    public function sampleSiteRelation()
{
    return $this->belongsTo(Site::class, 'site', 'Id_Site');
}

}
