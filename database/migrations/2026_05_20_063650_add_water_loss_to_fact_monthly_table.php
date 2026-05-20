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
            $table->float('water_loss')->nullable()->after('ec_collection')->comment('Water loss percentage: (Water_Consume - (Total_Sales * 20)) / (Water_Consume * 100)');
            $table->integer('is_water_loss_ok')->nullable()->after('water_loss')->comment('0 if water_loss between 15-25%, 1 otherwise, null if no data');
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::table('fact_monthly', function (Blueprint $table) {
            $table->dropColumn(['water_loss', 'is_water_loss_ok']);
        });
    }
};
