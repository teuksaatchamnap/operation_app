<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::table('fact_monthly', function (Blueprint $table) {
            $table->string('treatment_process')->nullable()->after('water_source');
        });
    }

    public function down(): void
    {
        Schema::table('fact_monthly', function (Blueprint $table) {
            $table->dropColumn('treatment_process');
        });
    }
};
