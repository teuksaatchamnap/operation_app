<?php

namespace App\Exports;

use Maatwebsite\Excel\Concerns\WithMultipleSheets;

class InvoicesMultiSheetExport implements WithMultipleSheets
{
    protected $monthInput;

    public function __construct($monthInput)
    {
        $this->monthInput = $monthInput;
    }

    public function sheets(): array
    {
        // return [
        //     new InvoicesExport($this->monthInput),
        //     new InvoicesRecordExport($this->monthInput),
        // ];
        $advisorSheets = (new InvoicesExport($this->monthInput))->sheets();

        return array_merge($advisorSheets, [
            new InvoicesRecordExport($this->monthInput),
        ]);
    }
}
