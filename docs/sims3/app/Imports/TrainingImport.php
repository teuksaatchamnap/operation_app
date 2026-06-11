<?php

namespace App\Imports;

use App\Models\SaleSurvey;
use App\Models\Sample;
use App\Models\Training;
use Maatwebsite\Excel\Concerns\ToModel;
use Maatwebsite\Excel\Concerns\WithHeadingRow;
use Maatwebsite\Excel\Concerns\WithStartRow;

class TrainingImport implements ToModel, WithHeadingRow, WithStartRow
{
    /**
    * @param array $row
    *
    * @return \Illuminate\Database\Eloquent\Model|null
    */
    public function model(array $row)
    {
        $data = [
        'site'=> $row['a'],
        'submitted_date'=> \Carbon\Carbon::parse($row['b']),
        'do_you_know_the_brand'=> $row['c'],
        'what_is_the_brand'=> $row['d'],
        'how_many_bottle_you_change'=> $row['e'],
        'why_not_change_the_water'=> $row['f'],
        'how_many_times_the_entrepreneur_came'=> $row['g'],
        'frequency_how_often_do_you_purchase_o_we'=> $row['h'],
        'specify_other'=> $row['i'],
        'how_satisfied_are_you_with_the_timeliness'=> $row['j'],
        'how_satisfied_are_you_with_the_regularity'=> $row['k'],
        'how_satisfied_are_you_with_the_service'=> $row['l'],
        'overall_how_satisfied_are_you_with_owe_on_a_scale'=> $row['m'],
        'since_starting_you_feel_any_effect'=> $row['n'],
        'specify_other_please'=> $row['o'],
        'would_you_recommend_o_we'=> $row['p'],
        'if_yes_what_would_you_say'=> $row['q'],
        'other_please_specify'=> $row['r'],
        'new_customer_if_no_why_not'=> $row['s'],
        'others_specify_please'=> $row['t'],
        'besides_o_we_you_have_other_sources'=> $row['u'],
        'specify_another_20l_brand'=> $row['v'],
        'specify_another_50l_brand'=> $row['w'],
        'specify_other_brand'=> $row['x'],
        'before_owe_what_did_you_used'=> $row['y'],
        'other_please_specific'=> $row['z'],

        ];

        // $data = [
        //         'staff_email' => $row['staff_email'],
        //         'cooperate_score' => $row['cooperate_score'],
        //         'entrepreneur_score' => $row['entreprenureship'],
        //         'sale_and_maketing_score' => $row['sale_and_maketing_score'],
        //         'water_quality_score' => $row['water_quality_score'],
        //         'entreturnover' => $row['entreturnover'],
        //         'entretraining' => $row['entretraining'],
        //         'owecommittee' => $row['owecommittee'],
        //         'technicianseminar' => $row['technicianseminar'],
        //         'total_score' => $row['total_score'],
        //         'final_result' => $row['final_result'],
        //        ]; 
        // $data =[
        //         'sample_code'=> $row['sample_code'],
        //         'site_open_sample_date'=> \Carbon\Carbon::parse($row['site_open_sample_date']),
        //         'site_open_sample_type'=> $row['site_open_sample_type'],
        //         'site_open_project_type'=> $row['site_open_project_type'],
        //         'sample_kh_location'=> $row['sample_kh_location'],
        //         'sample_en_location'=> $row['sample_en_location'],
        //         'site_open_sample_by'=> $row['site_open_sample_by'],
        //         'laboratory'=> $row['laboratory'],
        //         'received_date'=>  \Carbon\Carbon::parse($row['received_date']),
        //         'analysis_date'=>  \Carbon\Carbon::parse($row['analysis_date']),
        //         'ph'=> $row['ph'],
        //         'conductivity'=> $row['conductivity'],
        //         'tds'=> $row['tds'],
        //         'alkalinity'=> $row['alkalinity'],
        //         'turbidity'=> $row['turbidity'],
        //         'chlorine'=> $row['chlorine'],
        //         'aluminium'=> $row['aluminium'],
        //         'chloride'=> $row['chloride'],
        //         'calcium'=> $row['calcium'],
        //         'hardness'=> $row['hardness'],
        //         'fluoride'=> $row['fluoride'],
        //         'nitrite'=> $row['nitrite'],
        //         'nitrate'=> $row['nitrate'],
        //         'amonia'=> $row['amonia'],
        //         'iron'=> $row['iron'],
        //         'manganese'=> $row['manganese'],
        //         'arsenic'=> $row['arsenic'],
        //         'site_open_comment'=> $row['site_open_comment'],
        //         'site_open_final_judgement'=> $row['site_open_final_judgement'],
        //         'type'=> 'Site_Selection',
        //         'magesuim'=> 'magesuim',
        // ];
            SaleSurvey::create($data);
           // Training::create($data);
             //   Sample::create($data);
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
