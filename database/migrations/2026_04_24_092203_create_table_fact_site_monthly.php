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
            $table->foreignId('site_id')->nullable()->constrained()->nullOnDelete();
            $table->foreignId('platform_id')->nullable()->constrained()->nullOnDelete();
            $table->foreignId('advisor_id')->nullable()->constrained()->nullOnDelete();
            $table->date('month');
            $table->string('tier')->nullable();
            $table->integer('sales_volume')->nullable()->comment('Sales Volume (excl. WiS)');
            $table->integer('sales_volume_lfl')->nullable()->comment('Sales Volume like for like (excl. WiS). NULL for sites that were not opened on Jan.');
            $table->integer('days_open')->nullable();
            $table->boolean('active')->nullable();
            $table->boolean('super_tier_1')->nullable();
            $table->integer('bottles_per_day')->nullable();
            $table->integer('expenses')->nullable();
            $table->integer('revenue')->nullable();
            $table->integer('is_profitable')->nullable()->comment('True is site revenue - site expense + salaray entrepreneur >= 200');
            $table->integer('has_3_workers')->nullable()->comment('True is site has more than 3 workers');
            $table->integer('consumers')->nullable()->comment('Number of workers');
            $table->integer('who_compliance')->nullable()->comment('0:no 1:yes');
            $table->integer('contamination_level')->nullable()->comment('0:safe,1,2,3');
            $table->integer('ec_collection')->nullable()->comment('0:no 1:yes, paid > amount_expenses for the Ref_expenses=entrepreneur_contribution');
            $table->unique(['site_id', 'month']);
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
