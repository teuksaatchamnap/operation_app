<?php

namespace App\Imports;

use App\Models\Site;
use App\Models\Training;
use Maatwebsite\Excel\Concerns\Importable;
use Maatwebsite\Excel\Concerns\ToModel;
use Maatwebsite\Excel\Concerns\WithHeadingRow;
use Maatwebsite\Excel\Concerns\WithStartRow;

class TrainingImport implements  ToModel, WithHeadingRow, WithStartRow
{
    /**
    * @param array $row
    *
    * @return \Illuminate\Database\Eloquent\Model|null
    */
    use Importable;
    public function uniqueIdentifier($row)
    {
        return ['staff_email' => $row['staff_email']];
    }
    public function model(array $row)
    {
        $data1 = [
                // 'staff_email' => $row['staff_email'],
                'cooperate_score' => $row['cooperate_score'],
                'entrepreneur_score' => $row['entrepreneur_score'],
                'sale_and_maketing_score' => $row['sale_and_maketing_score'],
                'water_quality_score' => $row['water_quality_score'],
                'total_score' => $row['total_score'],
                'final_result' => $row['final_result'],
               ];   
                Training::updateOrCreate($this->uniqueIdentifier($row),$data1);

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
