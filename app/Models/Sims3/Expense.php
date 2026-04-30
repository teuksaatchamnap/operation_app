<?php

namespace App\Models\Sims3;

use Illuminate\Database\Eloquent\Builder;
use Illuminate\Database\Eloquent\Model;

// --
// -- Table structure for table `expenses`
// --

// CREATE TABLE `expenses` (
//   `Code_expenses` int(11) NOT NULL,
//   `Id_Site` varchar(255) DEFAULT NULL,
//   `Month` datetime DEFAULT NULL,
//   `Ref_expenses` varchar(255) DEFAULT NULL,
//   `Amount_expenses` float DEFAULT NULL,
//   `Paid` float DEFAULT NULL,
//   `Category_expenses` varchar(255) DEFAULT NULL
// ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;
class Expense extends Model
{
    protected $connection = 'sims3';

    protected $table = 'Expenses';

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
