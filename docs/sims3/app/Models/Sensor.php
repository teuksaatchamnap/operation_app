<?php
namespace App\Models;
use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\HasOne;
class Sensor extends Model
{
    use HasFactory;
    protected $fillable = [
        'water',
        'electricity',
        'voltage',
        'current',
        'flowrate',
        'received_date',
        'd1',
        'd2',
        'd3',
    ];
    public function site(): BelongsTo
    {
        return $this->belongsTo(Site::class, "sensor_id", "sensor_id");
    }
}