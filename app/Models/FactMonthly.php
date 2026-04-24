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

    protected $table = 'fact_monthly';

    protected $fillable = [
        'site_id',
        'platform_id',
        'advisor_id',
        'month',
        'tier',
        'sales_volume',
        'days_open',
        'expenses',
        'revenue',
        'workers',
        'consumers',
        'who_compliance',
        'profitable',
    ];

    protected function casts(): array
    {
        return [
            'month' => 'date',
            'who_compliance' => 'boolean',
            'profitable' => 'boolean',
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
