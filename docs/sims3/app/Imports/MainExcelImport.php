<?php

namespace App\Imports;

use Illuminate\Support\Collection;
use Maatwebsite\Excel\Concerns\WithMultipleSheets;

class MainExcelImport implements  WithMultipleSheets
{
    /**
    * @param Collection $collection
    */
    public function sheets(): array
    {
        return [
            'invoices' => new InvoiceImport(),
            'supply points' => new SiteBalancesImport(),
        ];
    }
}
