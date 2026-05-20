<?php

namespace App\Models\Sims3;

use Illuminate\Database\Eloquent\Builder;
use Illuminate\Database\Eloquent\Model;

class WaterMeter extends Model
{
    protected $connection = 'sims3';

    protected $table = 'water_meters';

    protected $fillable = [
        'site',
        'date',
        'value',
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
}
