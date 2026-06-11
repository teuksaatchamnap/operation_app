<?php

namespace App\Imports;

use App\Models\Site;
use Maatwebsite\Excel\Concerns\ToModel;
use Maatwebsite\Excel\Concerns\WithHeadingRow;
use Maatwebsite\Excel\Concerns\WithStartRow;
use Illuminate\Support\Facades\Log;

class TechnicianSite implements ToModel, WithHeadingRow, WithStartRow
{
    public $errors = [];
    private $rowNumber = 1;

    public function uniqueIdentifier($row)
    {
        return ['Id_Site' => trim($row['site'])];
    }

    public function model(array $row)
    {
        $this->rowNumber++;

        if (empty(trim($row['site']))) {
            $this->errors[] = "Missing or invalid site value in row: " . json_encode($row);
            return null;
        }

        $data1 = [];

        if (isset($row['technician']) && trim((string)$row['technician']) !== '') {
            $data1['technician_site'] = $row['technician'];
        }

        if (isset($row['advisor']) && trim((string)$row['advisor']) !== '') {
            $data1['Advisor'] = $row['advisor'];
        }

        if (isset($row['khmeradvisor']) && trim((string)$row['khmeradvisor']) !== '') {
            $data1['Khmer_advisor'] = $row['khmeradvisor'];
        }

        if (isset($row['status']) && trim((string)$row['status']) !== '') {
            $data1['Status_Site'] = $row['status'];
        }

        if (!empty($data1)) {
            return Site::updateOrCreate($this->uniqueIdentifier($row), $data1);
        }

        return null;
    }

    public function headingRow(): int
    {
        return 1;
    }

    public function startRow(): int
    {
        return 3;
    }
}
