<?php

namespace App\Models\Sims3;

use Illuminate\Database\Eloquent\Builder;
use Illuminate\Database\Eloquent\Model;

// SQL Schema
// CREATE TABLE `DailySales` (
//   `Code_Daily` int(11) NOT NULL,
//   `Id_Site` varchar(255) DEFAULT NULL,
//   `Month` datetime DEFAULT NULL,
//   `Day` datetime DEFAULT NULL,
//   `Total_Sales` float DEFAULT NULL,
//   `Hod_Sales` float DEFAULT NULL,
//   `Shopkeeper_Sales` float DEFAULT NULL,
//   `WiS_Sales` float DEFAULT NULL,
//   `Onsite_Sales` float DEFAULT NULL,
//   `Free_Sales` float DEFAULT NULL,
//   `Bottle_Sales` float DEFAULT NULL,
//   `Other_Sales` float DEFAULT NULL,
//   `Temperature` float DEFAULT NULL,
//   `Rain` float DEFAULT NULL
// ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;

/**
 * @property \DateTimeInterface|null $Month
 * @property \DateTimeInterface|null $Day
 * @property string|null $Id_Site
 */
class DailySale extends Model
{
    protected $connection = 'sims3';

    protected $table = 'DailySales';

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
