<?php

namespace App\Imports;

use App\Models\SiteBalance;
use League\CommonMark\Extension\CommonMark\Node\Block\Heading;
use Maatwebsite\Excel\Concerns\ToModel;
use Maatwebsite\Excel\Concerns\WithHeadingRow;
use Maatwebsite\Excel\Concerns\WithStartRow;
use Maatwebsite\Excel\Imports\HeadingRowFormatter;

class SiteBalancesImport implements ToModel, WithHeadingRow, WithStartRow
{
    /**
    * @param array $row
    *
    * @return \Illuminate\Database\Eloquent\Model|null
    */

    public function uniqueIdentifier($row)
    {
        $row = (array) $row;
        return ['site' => $row['site_name'],
        ];
    }

    public function model(array $row)
    {
        $row = (array) $row;
        $data = [
            'site' => $row['site_name'] ?? '',
            'balance' => $row['current_balance'] ?? 0,
            'beginning_balance' => $row['current_balance'] ?? 0,
        ];

        SiteBalance::updateOrCreate($this->uniqueIdentifier($row), $data);

        return null;
    }

    public function __construct() {
        HeadingRowFormatter::default('none');
    }
    public function headingRow(): int
    {
        return 1;
    }

    public function startRow(): int
    {
        return 2;
    }
}
