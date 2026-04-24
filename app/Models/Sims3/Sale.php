<?php

namespace App\Models\Sims3;

use Illuminate\Database\Eloquent\Model;

class Sale extends Model
{
    protected $connection = 'sims3';

    protected $table = 'sales';

    public $timestamps = false;

    protected function performInsert(\Illuminate\Database\Eloquent\Builder $query)
    {
        return false;
    }

    protected function performUpdate(\Illuminate\Database\Eloquent\Builder $query)
    {
        return false;
    }

    protected function performDeleteOnModel()
    {
        return false;
    }
}
