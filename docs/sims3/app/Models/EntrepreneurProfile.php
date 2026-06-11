<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class EntrepreneurProfile extends Model
{
    use HasFactory;
    protected $table = 'entrepreneur_profiles';
    protected $fillable = [
        'Id_Site',
        'Status',
        'Entrepreneur_English_name',
        'Entrepreneur_Khmer_name',
        'Sex',
            'Reason_Resign',
            'Detail_Resign',
            'Resignation_Date',
            'Entrepreneur_Phone',
            'DOB',
            'Working_Date',
            'Education',
            'Province',
            'Commune',
            'Previous_Job',
            'Site_Status',
            'Submitted_Date'.
            'Closed_Date',
            'Close_Description',
            'Reason_Closed_Site',
            'Reopen_Date',
            'Contract',
            'Status_Entrepreneur'
    ];
    protected $casts = [
        'Resignation_Date' => 'date:Y-m-d',
        'DOB' => 'date:Y-m-d',
        'Working_Date' => 'date:Y-m-d',
    ];
    public function site()
{
    return $this->belongsTo(Site::class, 'Id_Site', 'Id_Site');
}
}
