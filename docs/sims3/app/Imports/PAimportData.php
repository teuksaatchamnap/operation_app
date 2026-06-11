<?php

namespace App\Imports;

use App\Models\PerformanceApprailsal;
use Maatwebsite\Excel\Concerns\ToModel;
use Maatwebsite\Excel\Concerns\WithHeadingRow;
use Maatwebsite\Excel\Concerns\WithStartRow;
use Maatwebsite\Excel\Imports\HeadingRowFormatter;
class PAimportData implements ToModel,WithHeadingRow ,WithStartRow
{
    /**
    * @param array $row
    *
    * @return \Illuminate\Database\Eloquent\Model|null
    */
    public function model(array $row)
    {
        //dd($row);
        $data = [
            'staff_id' => $row['tsid'],
            'staff_email' => $row['email'],
            'staff_name' => $row['name'],
            'obj1_qualitative' => $row['obj1_qualitative'],
            'detail_obj1_qualitative' => $row['detail_obj1_qualitative'],
            'score_obj1_qualitative' => $row['score_obj1_qualitative'],
            'obj2_qualitative' => $row['obj2_qualitative'],
            'detail_obj2_qualitative' => $row['detail_obj2_qualitative'],
            'score_obj2_qualitative' => $row['score_obj2_qualitative'],
            'obj3_qualitative' => $row['obj3_qualitative'],
            'detail_obj3_qualitative' => $row['detail_obj3_qualitative'],
            'score_obj3_qualitative' => $row['score_obj3_qualitative'],
            'previous_obj1_qualitative' => $row['obj1_qualitative'],
            'previous_detail_obj1_qualitative' => $row['detail_obj1_qualitative'],
            'previous_score_obj1_qualitative' => $row['score_obj1_qualitative'],
            'previous_obj2_qualitative' => $row['obj2_qualitative'],
            'previous_detail_obj2_qualitative' => $row['detail_obj2_qualitative'],
            'previous_score_obj2_qualitative' => $row['score_obj2_qualitative'],
            'previous_obj3_qualitative' => $row['obj3_qualitative'],
            'previous_detail_obj3_qualitative' => $row['detail_obj3_qualitative'],
            'previous_score_obj3_qualitative' => $row['score_obj3_qualitative'],
            'year_obj1_quantitative' =>  $row['kpi1'],
            'year_obj2_quantitative' =>  $row['kpi2'],
            'year_obj3_quantitative' =>  $row['kpi3'],
            'year_obj4_quantitative' =>  $row['kpi4'],
            'year_obj5_quantitative' =>  $row['kpi5'],
            'target_obj1_quantitative' =>  $row['target1'],
            'target_obj2_quantitative' =>  $row['target2'],
            'target_obj3_quantitative' =>  $row['target3'],
            'target_obj4_quantitative' =>  $row['target4'],
            'target_obj5_quantitative' =>  $row['target5'],
            'result_obj1_quantitative' =>  $row['result_kpi1'],
            'result_obj2_quantitative' =>  $row['result_kpi2'],
            'result_obj3_quantitative' =>  $row['result_kpi3'],
            'result_obj4_quantitative' =>  $row['result_kpi4'],
            'result_obj5_quantitative' =>  $row['result_kpi5'],
            'previous_year_obj1_quantitative' =>  $row['kpi1'],
            'previous_year_obj2_quantitative' =>  $row['kpi2'],
            'previous_year_obj3_quantitative' =>  $row['kpi3'],
            'previous_year_obj4_quantitative' =>  $row['kpi4'],
            'previous_year_obj5_quantitative' =>  $row['kpi5'],
            'previous_target_obj1_quantitative' =>  $row['target1'],
            'previous_target_obj2_quantitative' =>  $row['target2'],
            'previous_target_obj3_quantitative' =>  $row['target3'],
            'previous_target_obj4_quantitative' =>  $row['target4'],
            'previous_target_obj5_quantitative' =>  $row['target5'],
            'previous_result_obj1_quantitative' =>  $row['result_kpi1'],
            'previous_result_obj2_quantitative' =>  $row['result_kpi2'],
            'previous_result_obj3_quantitative' =>  $row['result_kpi3'],
            'previous_result_obj4_quantitative' =>  $row['result_kpi4'],
            'previous_result_obj5_quantitative' =>  $row['result_kpi5'],
            'staff_do_pa_date' => \PhpOffice\PhpSpreadsheet\Shared\Date::excelToDateTimeObject(intval($row['staff_do_pa'])),
            'start_pa' => \PhpOffice\PhpSpreadsheet\Shared\Date::excelToDateTimeObject(intval($row['start_pa'])),
            'end_pa' => \PhpOffice\PhpSpreadsheet\Shared\Date::excelToDateTimeObject(intval($row['end_pa'])),
            'duration' => $row['duration'],
            'staff_sex' => $row['sex'],
            'staff_position' => $row['position'],
            'staff_dept' => $row['department'],
            'staff_type_pa' => $row['staff_type_pa'],
            'staff_supervisor_by' => $row['staff_supervisor_by'],
            'total_score' => $row['total_score'],
        ];
        return PerformanceApprailsal::create($data);
    }
    public function __construct() {
        HeadingRowFormatter::default('none');
    }

    public function headingRow():int
    {
        return 1;
    }

    public function startrow():int
    {
        return 2;
    }
    
}
