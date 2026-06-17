<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Support\Facades\DB;

return new class extends Migration
{
    public function up(): void
    {
        DB::statement(
            "ALTER TABLE fact_monthly CHANGE ec_collection collection_rate FLOAT NULL COMMENT 'Collection rate: SUM(Paid) / SUM(Amount_expenses) for 6 expense categories'"
        );
    }

    public function down(): void
    {
        DB::statement(
            "ALTER TABLE fact_monthly CHANGE collection_rate ec_collection INTEGER NULL COMMENT '0:no 1:yes, paid > amount_expenses for the Ref_expenses=entrepreneur_contribution'"
        );
    }
};
