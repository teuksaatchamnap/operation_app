<?php

namespace App\Imports;

use Maatwebsite\Excel\Concerns\WithHeadingRow;
use Maatwebsite\Excel\Imports\HeadingRowFormatter;
use Maatwebsite\Excel\Concerns\WithStartRow;
use Maatwebsite\Excel\Concerns\Importable;
use Maatwebsite\Excel\Concerns\WithCalculatedFormulas;

class SitesImport implements WithHeadingRow, WithStartRow, WithCalculatedFormulas
{

    use Importable;

    
    public function __construct() {
        HeadingRowFormatter::default('none');
    }

    public function headingRow(): int
    {
        return 3;
    }

    public function startRow(): int
    {
        return 5;
    }
}