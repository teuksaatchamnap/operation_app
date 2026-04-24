<?php

namespace App\Models;

use Database\Factories\SiteFactory;
use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\HasMany;

class Site extends Model
{
    /** @use HasFactory<SiteFactory> */
    use HasFactory;

    public $timestamps = false;

    protected $fillable = [
        'name',
    ];

    public function factMonthlies(): HasMany
    {
        return $this->hasMany(FactMonthly::class);
    }
}
