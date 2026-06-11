<?php

namespace App\Imports;

use App\Models\Kpi;
use App\Models\Site;
use Illuminate\Support\Carbon;
use Maatwebsite\Excel\Concerns\Importable;
use Maatwebsite\Excel\Concerns\ToModel;
use Maatwebsite\Excel\Concerns\WithHeadingRow;
use Maatwebsite\Excel\Concerns\WithStartRow;
use Maatwebsite\Excel\Imports\HeadingRowFormatter;

class KpiImport implements ToModel,WithHeadingRow, WithStartRow
{
    /**
    * @param array $row
    *
    * @return \Illuminate\Database\Eloquent\Model|null
    */
    use Importable;
    private static $createdCount = 0;
    private static $updatedCount = 0;
    public function uniqueIdentifier($row)
    {
        $row = (array) $row;
        return [
        'staff_email' => $row['mail'],
        'year'=> $row['year'] 
        ];
        // return [
        //         'Id_Site' => $row['Site']
        //         ];

    }
    public function model(array $row)
    {
       // dd($row);
        // $data =[
        //     //'Id_Site' => $row['Site'], 
        //     'Advisor_email' => $row['Email']
        //     //'Water_Source' => $row['Source']
        // ];
        $row = (array) $row;
        $data = [
            //'staff_email' => $row['Email'],
            'kpi1' => $row['kpi1'],
            'kpi2' => $row['kpi2'],
            'kpi3' => $row['kpi3'],
            'kpi4' => $row['kpi4'],
            'kpi5' => $row['kpi5'],
            'target1' => $row['target1'],
            'target2' => $row['target2'],
            'target3' => $row['target3'],
            'target4' => $row['target4'],
            'target5' => $row['target5'],
            'result_kpi1' => $row['result_kpi1'],
            'result_kpi2' => $row['result_kpi2'],
            'result_kpi3' => $row['result_kpi3'],
            'result_kpi4' => $row['result_kpi4'],
            'result_kpi5' => $row['result_kpi5'],

        ];
         //return Kpi::create($data);
         //Kpi::updateOrCreate($this->uniqueIdentifier($row),$data);
         //dd($data);
        

        $kpi = Kpi::updateOrCreate($this->uniqueIdentifier($row), $data);

        if ($kpi->wasRecentlyCreated) {
            self::$createdCount++;
        } else {
            self::$updatedCount++;
        }
        return $kpi;
        
        //echo "Created: $createdCount, Updated: $updatedCount";

    }
    public function __construct() {
        HeadingRowFormatter::default('none');
    }
    public function getCounts()
    {
        return [
            'created' => self::$createdCount,
            'updated' => self::$updatedCount,
        ];
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
