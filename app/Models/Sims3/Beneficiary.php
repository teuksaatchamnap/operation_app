<?php

namespace App\Models\Sims3;

use Illuminate\Database\Eloquent\Builder;
use Illuminate\Database\Eloquent\Model;

/*
--
-- Table structure for table `beneficiaries`
--
CREATE TABLE `beneficiaries` (
  `Code_Beneficiaries` int(11) NOT NULL,
  `Id_Site` varchar(255) DEFAULT NULL,
  `Month` datetime DEFAULT NULL,
  `Beneficiaries` float DEFAULT NULL,
  `Beneficiaries12months` float DEFAULT NULL,
  `Old_Beneficiaries` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;

 */

/**
 * @property int $Code_Beneficiaries
 * @property string|null $Id_Site
 * @property \DateTimeInterface|null $Month
 * @property float|null $Beneficiaries
 * @property float|null $Beneficiaries12months
 * @property int|null $Old_Beneficiaries
 */
class Beneficiary extends Model
{
    protected $connection = 'sims3';

    protected $table = 'Beneficiaries';

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
