<?php

namespace App\Models;

use Database\Factories\FactMonthlyFactory;
use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class FactMonthly extends Model
{
    /** @use HasFactory<FactMonthlyFactory> */
    use HasFactory;

    public $timestamps = false;

    protected $table = 'fact_monthly';

    protected $fillable = [
        'site_id',
        'platform_id',
        'advisor_id',
        'month',
        'tier',
        'sales_volume',
        'sales_volume_lfl',
        'days_open',
        'active',
        'super_tier_1',
        'bottles_per_day',
        'expenses',
        'revenue',
        'is_profitable',
        'has_3_workers',
        'consumers',
        'who_compliance',
        'contamination_level',
        'ec_collection',
    ];

    protected function casts(): array
    {
        return [
            'month' => 'date',
        ];
    }

    public function site(): BelongsTo
    {
        return $this->belongsTo(Site::class);
    }

    public function platform(): BelongsTo
    {
        return $this->belongsTo(Platform::class);
    }

    public function advisor(): BelongsTo
    {
        return $this->belongsTo(Advisor::class);
    }
}
