<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
class FlashReport extends Model
{
    use HasFactory;
    protected $casts = [
        'Month'  => 'date:Y-m-d',
    ];
    protected $table = 'FlashReport';
    protected $primaryKey = 'Code_Flash_report';
    public $timestamps = false;
    protected $fillable = [
                'Code_Flash_report ',
                'Id_Site',
                'Month',
                'Number_jugs_village',
                'Number_jugs_school',
                'Comment',
                'Number_of_delivery',
                'Number_of_deinfection',
                'Number_bot_displace_people',
                'Moto_cart',
                'Kuyon',
                'market_comparison',
                'Car',
                'Staff',
                'Open_days',
                'Period',
    ];
    public function site(): BelongsTo
    {
        return $this->belongsTo(Site::class,"Id_Site","Id_Site");
    }
}
