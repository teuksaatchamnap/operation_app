<?php

namespace App\Models\Sims3;

use Illuminate\Database\Eloquent\Builder;
use Illuminate\Database\Eloquent\Model;

/**
 * @property int $id
 * @property string|null $path
 * @property string $Id_Site
 * @property string|null $commune_contract
 * @property string|null $training_contract
 * @property string|null $caption
 */
class SiteContract extends Model
{
    protected $connection = 'sims3';

    protected $table = 'site_contracts';

    public $timestamps = false;

    protected $fillable = [
        'path',
        'Id_Site',
        'commune_contract',
        'training_contract',
        'caption',
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
