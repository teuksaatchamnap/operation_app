<?php

namespace App\Models\Sims3;

use Illuminate\Database\Eloquent\Builder;
use Illuminate\Database\Eloquent\Model;

// SQL Schema
//  CREATE TABLE `sales` (
//   `Code_Sales` int(11) NOT NULL,
//   `Id_Site` varchar(255) DEFAULT NULL,
//   `Month` datetime DEFAULT NULL,
//   `Total_Sales` float DEFAULT NULL,
//   `Total_Income` float DEFAULT NULL,
//   `Total_Price_Average` float DEFAULT NULL,
//   `Hod_Sales` float DEFAULT NULL,
//   `Hod_Income` float DEFAULT NULL,
//   `Hod_Price` float DEFAULT NULL,
//   `Shopkeeper_Sales` float DEFAULT NULL,
//   `Shopkeeper_Income` float DEFAULT NULL,
//   `Shopkeeper_Price` float DEFAULT NULL,
//   `WiS_Sales` float DEFAULT NULL,
//   `WiS_Income` float DEFAULT NULL,
//   `WiS_Price` float DEFAULT NULL,
//   `Onsite_Sales` float DEFAULT NULL,
//   `Onsite_Income` float DEFAULT NULL,
//   `Onsite_Price` float DEFAULT NULL,
//   `Free_Sales` float DEFAULT NULL,
//   `Bottle_Sales` float DEFAULT NULL,
//   `Bottle_Income` float DEFAULT NULL,
//   `Bottle_Price` float DEFAULT NULL,
//   `Emergency_Sales` float DEFAULT NULL,
//   `Emergency_Income` float DEFAULT NULL,
//   `Emergency_Price` float DEFAULT NULL,
//   `Number_Open_Days` int(11) DEFAULT NULL,
//   `Tier` varchar(255) DEFAULT NULL,
//   `Other_Sales` float DEFAULT NULL,
//   `Other_Income` float DEFAULT NULL,
//   `Other_Price` float DEFAULT NULL,
//   `Project` tinyint(1) DEFAULT NULL
// ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;

/**
 * @property \DateTimeInterface|null $Month
 * @property string|null $Id_Site
 * @property int|null $Number_Open_Days
 * @property float|null $Total_Sales
 * @property float|null $Total_Income
 * @property float|null $Emergency_Sales
 * @property float|null $Free_Sales
 * @property float|null $Hod_Sales
 * @property float|null $Shopkeeper_Sales
 * @property float|null $WiS_Sales
 * @property float|null $Onsite_Sales
 * @property float|null $Bottle_Sales
 * @property float|null $Hod_Price
 * @property float|null $Shopkeeper_Price
 * @property float|null $WiS_Price
 * @property float|null $Onsite_Price
 * @property float|null $Bottle_Price
 * @property float|null $Emergency_Price
 * @property float|null $Hod_Income
 * @property float|null $Shopkeeper_Income
 * @property float|null $WiS_Income
 * @property float|null $Onsite_Income
 * @property float|null $Bottle_Income
 * @property float|null $Emergency_Income
 */
class Sale extends Model
{
    protected $connection = 'sims3';

    protected $table = 'Sales';

    public $timestamps = false;

    protected function performInsert(Builder $query)
    {
        return false;
    }

    protected function performUpdate(Builder $query)
    {
        return false;
    }

    protected function performDeleteOnModel(): void {}
}
