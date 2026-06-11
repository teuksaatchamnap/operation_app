<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class DailySales extends Model
{
    use HasFactory;
    protected $table = 'DailySales';
    protected $fillable = [
                'Id_Site',
                'Month',
                'Day',
                'Total_Sales',
                'Hod_Sales',
                'Shopkeeper_Sales',
                'WiS_Sales',
                'Onsite_Sales',
                'Free_Sales',
                'Number_open_days',
                'Bottle_Sales',
                'Other_Sales',
                'Temperature',
                'Rain',

    ];
    public function site()
    {
        return $this->belongsTo(Site::class, 'Id_Site', 'Id_Site');
    }
}
