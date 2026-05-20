<?php

namespace App\Models\Sims3;

use Illuminate\Database\Eloquent\Builder;
use Illuminate\Database\Eloquent\Model;

/*
--
-- Table structure for table `indicators`
--
CREATE TABLE `indicators` (
  `Code_Indicator` int(11) NOT NULL,
  `Id_Site` varchar(255) DEFAULT NULL,
  `Month` datetime DEFAULT NULL,
  `Number_of_Operator` int(11) DEFAULT NULL,
  `Number_Bottles_in_Operation` int(11) DEFAULT NULL,
  `Number_Bottles_in_Stock` int(11) DEFAULT NULL,
  `Number_Bottles_Broken_Lost` int(11) DEFAULT NULL,
  `Water_Consume` float DEFAULT NULL,
  `Number_of_Vehicle` int(11) DEFAULT NULL,
  `Water_begining` int(11) DEFAULT NULL,
  `Water_end` int(11) DEFAULT NULL,
  `Machine_begining` int(11) DEFAULT NULL,
  `Machine_end` int(11) DEFAULT NULL,
  `Saving_outside_TS` float DEFAULT NULL,
  `Number_of_disinfection` int(11) DEFAULT NULL,
  `Number_of_delivery` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;
 */

/**
 * @property \DateTimeInterface|null $Month
 * @property string|null $Id_Site
 * @property int|null $Number_of_Operator
 * @property float|null $Water_Consume
 */
class Indicator extends Model
{
    protected $connection = 'sims3';

    protected $table = 'Indicators';

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
