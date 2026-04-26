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
        Schema::create('fact_monthly', function (Blueprint $table) {
            $table->id();
            $table->foreignId('site_id')->nullable();
            $table->foreignId('platform_id')->nullable();
            $table->foreignId('advisor_id')->nullable();
            $table->date('month');
            $table->string('tier');
            $table->integer('sales_volume')->comment('Sales Volume (excl. WiS)');
            $table->integer('days_open');
            $table->integer('expenses');
            $table->integer('revenue');
            $table->integer('workers')->comment('Number of workers');
            $table->integer('consumers')->comment('Number of workers');
            $table->boolean('who_compliance')->comment('0:no 1:yes');
            $table->boolean('profitable')->comment('0:no 1:yes.  (P&L + Salary Entrepreneur) >= 200 ');
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('fact_monthly');
    }
};
