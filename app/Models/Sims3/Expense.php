<?php

namespace App\Models\Sims3;

use Illuminate\Database\Eloquent\Builder;
use Illuminate\Database\Eloquent\Model;

/**
 * @property string|null $Id_Site
 * @property \DateTimeInterface|null $Month
 * @property string|null $Ref_expenses
 * @property float|null $Amount_expenses
 * @property float|null $Paid
 * @property string|null $Category_expenses
 */
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
