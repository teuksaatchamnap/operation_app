<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class sales extends Model
{
    use HasFactory;
    public $timestamps = false;
    protected $casts = [
        'Month'  => 'date:Y-m-d',
    ];
    protected $table = 'Sales';
    protected $primaryKey = 'Code_Sales';
    protected $fillable = [
        'Id_Site',
        'Month',
        'Total_Sales',
        'Total_Income',
        'Total_Price_Average',
        'Hod_Sales',
        'Hod_Income',
        'Hod_Price',
        'Shopkeeper_Sales',
        'Shopkeeper_Income',
        'Shopkeeper_Price',
        'WiS_Sales',
        'WiS_Income',
        'WiS_Price',
        'Onsite_Sales',
        'Onsite_Income',
        'Onsite_Price',
        'Free_Sales',
        'Bottle_Sales',
        'Bottle_Income',
        'Bottle_Price',
        'Number_Open_Days',
        'Tier',
        'Other_Sales',
        'Other_Income',
        'Other_Price',
        'Emergency_Sales',
        'Emergency_Income',
        'Emergency_Price',
        'Project',
    ];
}
