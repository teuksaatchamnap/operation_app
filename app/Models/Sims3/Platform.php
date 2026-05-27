<?php

namespace App\Models\Sims3;

use Illuminate\Database\Eloquent\Builder;
use Illuminate\Database\Eloquent\Model;

/**
 * @property string $Code_Platform
 * @property float|null $Latitude
 * @property float|null $Longitude
 * @property string|null $Cashier
 * @property string|null $Mail_ROM
 * @property int $new_id
 */
class Platform extends Model
{
    protected $connection = 'sims3';

    protected $table = 'Platform';

    public $timestamps = false;

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
