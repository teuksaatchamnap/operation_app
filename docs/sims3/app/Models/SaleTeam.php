<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class SaleTeam extends Model
{
    use HasFactory;
    protected $casts = [
        'sale_date'  => 'date:Y-m-d',
    ];
    protected $table = 'sale_team';
    protected $fillable = [
       'site',
           'sale_date',
           'sale_officer1',
           'sale_officer2',
           'sale_officer3',
           'sale_officer4',
           'sale_type',
           'customer',
           'sex',
           'customer_type',
           'village',
           'contact',
           'delivery_status',
           'payment_type',
           'free',
           'lending_bottle',
           'price_lending_bottle',
           'new_bottle',
           'price_new_bottle',
           'refill',
           'price_refill',
           'total_refill_sell',
           'total_bottle_sell',
           'total_lending_bottle_sell',
           'total_revenue',
           'drinking_water_type',
           'water_source',
              'water_type',
    ];
    public function siteInfo()
{
    return $this->belongsTo(Site::class, 'site', 'Id_Site');
}
}
