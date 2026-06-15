<?php

namespace App\Models\Sims3;

use Illuminate\Database\Eloquent\Builder;
use Illuminate\Database\Eloquent\Model;

/**
 * @property int $id
 * @property string|null $Id_Site
 * @property string|null $Status
 * @property string|null $Entrepreneur_English_name
 * @property string|null $Entrepreneur_Khmer_name
 * @property string|null $Sex
 * @property string|null $Reason_Resign
 * @property string|null $Detail_Resign
 * @property string|null $Resignation_Date
 * @property string|null $Entrepreneur_Phone
 * @property string|null $DOB
 * @property string|null $Working_Date
 * @property string|null $Education
 * @property string|null $Province
 * @property string|null $Commune
 * @property string|null $Previous_Job
 * @property string|null $Site_Status
 * @property string|null $Submitted_Date
 * @property string|null $Closed_Date
 * @property string|null $Close_Description
 * @property string|null $Reason_Closed_Site
 * @property string|null $Reopen_Date
 * @property string|null $Contract
 * @property string|null $Status_Entrepreneur
 */
class EntrepreneurProfile extends Model
{
    protected $connection = 'sims3';

    protected $table = 'entrepreneur_profiles';

    public $timestamps = false;

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
        'Submitted_Date',
        'Closed_Date',
        'Close_Description',
        'Reason_Closed_Site',
        'Reopen_Date',
        'Contract',
        'Status_Entrepreneur',
    ];

    protected function performInsert(Builder $query)
    {
        return false;
    }

    protected function performUpdate(Builder $query)
    {
        return false;
    }

    protected function performDeleteOnModel(): void {}

    public function site()
    {
        return $this->belongsTo(Site::class, 'Id_Site', 'Id_Site');
    }
}
