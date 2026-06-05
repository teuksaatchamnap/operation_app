<?php

namespace App\Models\Sims3;

use Illuminate\Database\Eloquent\Builder;
use Illuminate\Database\Eloquent\Model;

/**
 * @property string|null $site
 * @property \DateTimeInterface|null $sale_date
 * @property int|null $quantity
 * @property int|null $unit_price
 * @property string|null $type
 * @property int|null $index
 */
class CashierSale extends Model
{
    protected $connection = 'sims3';

    protected $table = 'cashier_sales';

    protected $fillable = [
        'site',
        'sale_date',
        'quantity',
        'unit_price',
        'type',
        'index',
    ];

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
