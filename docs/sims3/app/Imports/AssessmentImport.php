<?php

namespace App\Imports;

use App\Models\Assessment;
use App\Models\TransportationAssessment;
use Maatwebsite\Excel\Concerns\ToModel;
use Maatwebsite\Excel\Imports\HeadingRowFormatter;
use Maatwebsite\Excel\Concerns\WithHeadingRow;
use Maatwebsite\Excel\Concerns\WithStartRow;
use Maatwebsite\Excel\Concerns\Importable;

class AssessmentImport implements ToModel,WithHeadingRow, WithStartRow
{
    /**
    * @param array $row
    *
    * @return \Illuminate\Database\Eloquent\Model|null
    */
    use Importable;
    
    public function uniqueIdentifier($row)
    {
        return [
                'formid' => $row['formid']
               ];
        // return [
        //         'number' => $row['number']
        //        ];
    }
    public function model(array $row)
    {
        // return new Assessment([
        //     //
        // ]);
        $data =[
             'number'=>$row['number'],
           // 'formid'=>$row['formid'],
            'site'=>$row['site'],
            'technician'=>$row['technician'],
            'a5'=>$row['5'],
            'a6'=>$row['6'],
            'a7'=>$row['7'],
            'a8'=>$row['8'],
            'a9'=>$row['9'],
            'a10'=>$row['10'],
            'a11'=>$row['11'],
            'a12'=>$row['12'],
            'a13'=>$row['13'],
            'a14'=>$row['14'],
            'a15'=>$row['15'],
            'a16'=>$row['16'],
            'a17'=>$row['17'],
            'a18'=>$row['18'],
            'a19'=>$row['19'],
            'a20'=>$row['20'],
            'a21'=>$row['21'],
            'a22'=>$row['22'],
            'a23'=>$row['23'],
            'a24'=>$row['24'],
            'a25'=>$row['25'],
            'a26'=>$row['26'],
            'a27'=>$row['27'],
            'a28'=>$row['28'],
            'a29'=>$row['29'],
            'a30'=>$row['30'],
            'a31'=>$row['31'],
            'a32'=>$row['32'],
            'a33'=>$row['33'],
            'a34'=>$row['34'],
            'a35'=>$row['35'],
            'a36'=>$row['36'],
            'a37'=>$row['37'],
            'a38'=>$row['38'],
            'a39'=>$row['39'],
            'a40'=>$row['40'],
            'a41'=>$row['41'],
            'a42'=>$row['42'],
            'a43'=>$row['43'],
            'a44'=>$row['44'],
            'a45'=>$row['45'],
            'a46'=>$row['46'],
            'a47'=>$row['47'],
            'a48'=>$row['48'],
            'a49'=>$row['49'],
            'a50'=>$row['50'],
            'a51'=>$row['51'],
            'a52'=>$row['52'],
            'a53'=>$row['53'],
            'a54'=>$row['54'],
            'a55'=>$row['55'],
            'a56'=>$row['56'],
            'a57'=>$row['57'],
            'a58'=>$row['58'],
            'a59'=>$row['59'],
            'a60'=>$row['60'],
            'a61'=>$row['61'],
            'a62'=>$row['62'],
            'a63'=>$row['63'],
            'a64'=>$row['64'],
            'a65'=>$row['65'],
            'a66'=>$row['66'],
            'a67'=>$row['67'],
            'a68'=>$row['68'],
            'a69'=>$row['69'],
            'a70'=>$row['70'],
            'a71'=>$row['71'],
            'a72'=>$row['72'],
            'a73'=>$row['73'],
            'a74'=>$row['74'],
            'a75'=>$row['75'],
            'a76'=>$row['76'],
            'a77'=>$row['77'],
            'a78'=>$row['78'],
            'a79'=>$row['79'],
            'a80'=>$row['80'],
            'a81'=>$row['81'],
            'a82'=>$row['82'],
            'a83'=>$row['83'],
            'a84'=>$row['84'],
            'a85'=>$row['85'],
            'a86'=>$row['86'],
            'a87'=>$row['87'],
            'a88'=>$row['88'],
            'a89'=>$row['89'],
            'a90'=>$row['90'],
            'a91'=>$row['91'],
            'a92'=>$row['92'],
            'a93'=>$row['93'],
            'a94'=>$row['94'],
            'a95'=>$row['95'],
            'a96'=>$row['96'],
            'a97'=>$row['97'],
            'a98'=>$row['98'],
            'a99'=>$row['99'],
            'a100'=>$row['100'],
            'a101'=>$row['101'],
            'a102'=>$row['102'],
            'a103'=>$row['103'],
            'a104'=>$row['104'],
            'a105'=>$row['105'],
            'a106'=>$row['106'],
            'a107'=>$row['107'],
            'a108'=>$row['108'],
            'a109'=>$row['109'],
            'a110'=>$row['110'],
            'a111'=>$row['111'],
            'a112'=>$row['112'],
            'a113'=>$row['113'],
            'a114'=>$row['114'],
            'a115'=>$row['115'],
            'a116'=>$row['116'],
            'a117'=>$row['117'],
                        
        ];
        // $data =[
        //     'site'=> $row['site'],
        //     'transportation_type'=> $row['transportation_type'],
        //     'condition_of_transportation'=> $row['condition_of_transportation'],
        //     'condition_of_trolley'=> $row['condition_of_trolley'],
        //     'purchased_date'=> $row['purchased_date'],
        // ];
         Assessment::updateOrCreate($this->uniqueIdentifier($row),$data);
       // return TransportationAssessment::create($data);
    }
    public function __construct() {
        HeadingRowFormatter::default('none');
    }

    public function headingRow(): int
    {
        return 1;
        //return 2;
    }

    public function startRow(): int
    {
        return 2;
        //return 3;
    }
}
