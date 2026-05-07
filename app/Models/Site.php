<?php

namespace App\Models;

use Database\Factories\SiteFactory;
use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\HasMany;

/**
 * @property int $id
 * @property string $name
 * @property float|null $latitude
 * @property float|null $longitude
 */
class Site extends Model
{
    /** @use HasFactory<SiteFactory> */
    use HasFactory;

    public $timestamps = false;

    protected $fillable = [
        'name',
        'latitude',
        'longitude',
    ];

    public function factMonthlies(): HasMany
    {
        return $this->hasMany(FactMonthly::class);
    }
}
