<?php

namespace App\Models\Sims3;

use Illuminate\Database\Eloquent\Builder;
use Illuminate\Database\Eloquent\Model;

class Sale extends Model
{
    protected $connection = 'sims3';

    protected $table = 'sales';

    public $timestamps = false;

    protected function performInsert(Builder $query)
    {
        return false;
    }

    protected function performUpdate(Builder $query)
    {
        return false;
    }

    protected function performDeleteOnModel()
    {
        return false;
    }
}
