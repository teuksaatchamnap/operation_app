<?php

namespace App\Models;

use Database\Factories\KpiFactory;
use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\HasMany;

class Kpi extends Model
{
    /** @use HasFactory<KpiFactory> */
    use HasFactory;

    public $timestamps = false;

    protected $fillable = [
        'name',
        'col_name',
        'unit',
        'type',
        'description',
        'aggregate',
        'legend',
    ];

    protected function casts(): array
    {
        return [
            'legend' => 'array',
        ];
    }

    public function objectives(): HasMany
    {
        return $this->hasMany(Objective::class);
    }
}
