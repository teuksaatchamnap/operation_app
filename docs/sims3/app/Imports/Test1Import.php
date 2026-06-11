<?php

namespace App\Imports;

use App\Models\Consumable;
use App\Models\User;
use PhpOffice\PhpSpreadsheet\Shared\Date;
use Carbon\Carbon;
use Maatwebsite\Excel\Concerns\ToModel;
use Maatwebsite\Excel\Concerns\WithHeadingRow;
use Maatwebsite\Excel\Concerns\WithStartRow;
use Maatwebsite\Excel\Concerns\WithMultipleSheets;
use Maatwebsite\Excel\Concerns\WithEvents;
use Maatwebsite\Excel\Events\AfterImport;
use Illuminate\Support\Facades\Log;
use Maatwebsite\Excel\Concerns\WithCalculatedFormulas;
use Maatwebsite\Excel\Validators\Failure;
use Maatwebsite\Excel\Concerns\SkipsOnFailure;
use Maatwebsite\Excel\Concerns\SkipsFailures;
use Maatwebsite\Excel\Concerns\WithValidation;

class Test1Import implements
    WithHeadingRow,
    WithStartRow,
    ToModel,
    WithMultipleSheets,
    WithEvents,
    WithCalculatedFormulas,
    SkipsOnFailure,
    WithValidation
{
    use SkipsFailures;
    public $totalQty = 0;
    public $countInserted = 0;
    public $missingSiteCount = 0;
    public $errors = [];
   // public $email;
    public function sheets(): array
    {
        return [
            0 => $this, // Use the same instance for the first sheet
        ];
    }
    // public function __construct($email)
    // {
    //     $this->email = $email; // Store the email passed from the controller
    //    // Log::info('ConsumableImport constructed with email: ' . $email);
    // }
    public function chunkSize(): int
    {
        return 100;
    }

    public function model(array $row)
    {

        $row = array_change_key_case($row, CASE_LOWER);
        $this->totalQty += (float)($row['totalprice'] ?? 0);
        // Log::info("Updated totalQty: " . $this->totalQty);
        //Log::info('Email in model method: ' . $this->email);
        $this->countInserted++;
        return new Consumable([
            'Id_Site' => $row['site'],
            'Month' => Carbon::instance(Date::excelToDateTimeObject($row['month']))->format('Y-m-01'),
            'Date_submission' => Carbon::now()->format('Y-m-d'),
            'Category' => '3',
            'item' => $row['itemcode'],
            'Number_Item' => $row['qty'],
            'Price_Item' => number_format((float) $row['totalprice'], 4, '.', ''),
            'Khmer_name' => $row['englishname'],
            'English_name' => $row['englishname'],
            'Validate' => 0,
            'Unit' => $row['unit'],
            'Payment_method' => $row['paymenttype'],
            'PO' => $row['po'],
            'Supplier' => $row['supplier'],
            'Remark' => $row['remark'],
            'EmailRequestor' => auth()->user()->email,
        ]);
    }

    public function registerEvents(): array
    {
        return [
            AfterImport::class => function (AfterImport $event) {
                // The totalQty is already available in the instance
                // No need to store in session if we access it directly
                // Log::info("Import complete. Total quantity: " . $this->totalQty);
            },
        ];
    }

    public function headingRow(): int
    {
        return 5;
    }

    public function startRow(): int
    {
        return 7;
    }
    public function rules(): array
    {
        return [
            'site' => 'required',
            'itemcode' => 'required',
            'englishname' => 'required',
            'month' => 'required',
            'qty' => 'required',
        ];
    }

    public function customValidationMessages()
    {
        return [
            'site.required' => 'The Site column is required.',
            'itemcode.required' => 'The Item Code column is required.',
            'englishname.required' => 'The English Name column is required.',
            'month.required' => 'The month column is required.',
            'qty.required' => 'The Quantity column is required.',
        ];
    }
    public function onFailure(Failure ...$failures)
    {
        foreach ($failures as $failure) {
            if ($failure->attribute() === 'site') {
                $this->missingSiteCount++;
            }
            $this->errors[] = [
                'row' => $failure->row(),
                'attribute' => $failure->attribute(),
                'errors' => $failure->errors(),
                'values' => $failure->values(),
            ];
        }
    }
    // public function getTotalQty()
    // {
    //     return $this->totalQty;
    // }
    // public function countRecord()
    // {
    //     return $this->countInserted;
    // }
}
