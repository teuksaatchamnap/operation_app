<?php

namespace App\Exports;

use Maatwebsite\Excel\Concerns\FromCollection;
use Maatwebsite\Excel\Concerns\FromArray;
use Maatwebsite\Excel\Concerns\WithHeadings;
class SchoolExport implements FromCollection, WithHeadings
{
    /**
    * @return \Illuminate\Support\Collection
    */
    protected $data;

    public function __construct($data)
    {
        $this->data = collect($data);
    }
    
    public function collection()
    {
        return $this->data->map(function ($row) {
            return [
                $row['site'],
                $row['month'],
                $row['platform'],
                $row['budget'],
                $row['open_days_count'],
                $row['total_school_budget'],
                $row['total_advisor_put_system'],
                $row['difference'],
            ];
        });
    }
    public function headings(): array
    {
        return [
            'Site',
            'Month',
            'Platform',
            'Budget',
            'Open Days',
            'Total School Budget',
            'Total Advisor Put System',
            'Difference',
        ];
    }
}
