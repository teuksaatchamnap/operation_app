<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    /**
     * Run the migrations.
     */
    public function up(): void
    {
        Schema::table('fact_monthly', function (Blueprint $table) {
            $table->integer('data_collection')->nullable()->after('is_water_loss_ok')->comment('0:no data, 1:partial, 2:all (expense+sales+water)');
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::table('fact_monthly', function (Blueprint $table) {
            $table->dropColumn('data_collection');
        });
    }
};
