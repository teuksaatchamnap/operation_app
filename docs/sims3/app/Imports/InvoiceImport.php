<?php

namespace App\Imports;

use App\Models\Invoice;
use Carbon\Carbon;
use Maatwebsite\Excel\Concerns\Importable;
use Maatwebsite\Excel\Concerns\ToModel;
use Maatwebsite\Excel\Concerns\WithHeadingRow;
use Maatwebsite\Excel\Concerns\WithStartRow;
use Maatwebsite\Excel\Imports\HeadingRowFormatter;

class InvoiceImport implements ToModel, WithHeadingRow, WithStartRow
{
    /**
     * @param array $row
     *
     * @return \Illuminate\Database\Eloquent\Model|null
     */
    use Importable;
    public function uniqueIdentifier($row)
    {
        $row = (array) $row;
        return [
            'invoice_ref' => $row['ID'],
        ];
    }
    public function model(array $row)
    {
        $row = (array) $row;

        $month = $row['month'] ?? '';
        $year = $row['year'] ?? '';
        $combinedDate = null;

        if (!empty($month) && !empty($year)) {
            try {
                // Create date with first day of month
                $combinedDate = Carbon::create($year, $month, 1)->format('Y-m-d');
            } catch (\Exception $e) {
                $combinedDate = null;
            }
        }
        $khmerName = ['BT' =>'ថ្លៃប៊ីដុង' ,'C1' => 'ថ្លៃសំភារះ','debts'=> 'បំណុល','DP'=> 'វិភាគទានមធ្យោបាយដឹកជញ្ជូន'
                ,'school-program'=> 'ទឹកសាលា','T1'=> 'វិភាគទាន','TI'=> 'បច្ចេកទេស','WQ'=> 'គុណភាពទឹក'];
        $khmerItemName = $khmerName[$row['stock-type']] ?? null;
        $data = [
            'site' => $row['site'] ?? '',
            'month' => $combinedDate,
            'beginning_balance' => $row['stock-type'] == 'school-program'
                ? ($row['amount-owed-to-entrepreneur'] ?? 0)
                : ($row['amount-owed-to-teuk-saat'] ?? 0),
            'invoice_type' => $row['name'] ?? '',
            'invoice_ref' => $row['ID'] ?? '',
            'invoice_type_khmer_name' => $khmerItemName, //
        ];

        Invoice::updateOrCreate($this->uniqueIdentifier($row), $data);

        return null;
    }
    public function __construct()
    {
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
