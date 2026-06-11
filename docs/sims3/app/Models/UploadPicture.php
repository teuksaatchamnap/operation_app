<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class UploadPicture extends Model
{
    use HasFactory;
    protected $fillable = [
        'path',
        'sample_id',
        'caption', // Add a caption field for example
    ];

    public function sample()
    {
        return $this->belongsTo(Sample::class);
    }
}
