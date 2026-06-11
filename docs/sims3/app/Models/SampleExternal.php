<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class SampleExternal extends Model
{
    use HasFactory;
    protected $table = 'sample_externals';
    protected $casts = [
        'test_date'  => 'date:Y-m-d',
    ];
    protected $fillable = [
            'site',
            'test_date',
            'upload_path'
    ];
}
