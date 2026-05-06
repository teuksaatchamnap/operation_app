<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class Objective extends Model
{
    public $timestamps = false;

    protected $fillable = [
        'kpi_id',
        'start_date',
        'end_date',
        'value',
    ];

    /**
     * @property int $id
     * @property int $kpi_id
     * @property string $start_date
     * @property string $end_date
     * @property string $value
     */
    protected function casts(): array
    {
        return [
            'start_date' => 'date',
            'end_date' => 'date',
        ];
    }

    public function kpi(): BelongsTo
    {
        return $this->belongsTo(Kpi::class);
    }
}
