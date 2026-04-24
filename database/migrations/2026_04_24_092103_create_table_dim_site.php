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
        Schema::create('sites', function (Blueprint $table) {
            $table->id();
            $table->string("name")->unique();
        });
        Schema::create('advisors', function (Blueprint $table) {
            $table->id();
            $table->string("name")->unique();
        });
        Schema::create('platforms', function (Blueprint $table) {
            $table->id();
            $table->string("name")->unique();
        });
        Schema::create('kpis', function (Blueprint $table) {
            $table->id();
            $table->string("name");
            $table->string("col_name");
            $table->string("unit");
            $table->string("periodicity")->comment("[monthly, year to date, year]");
            $table->string("type")->comment("[quantitative, qualitative, calculated]");
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('dim_site');
    }
};
