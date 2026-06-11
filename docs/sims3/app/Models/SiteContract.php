<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class SiteContract extends Model
{
    use HasFactory;
    protected $table = 'site_contracts';
    protected $fillable = [
        'path',
        'Id_Site',
        'commune_contract', // Add a commune contract field for example
        'training_contract', // Add a training people field for example
        'caption', // Add a caption field for example
    ];

    public function site()
    {
        return $this->belongsTo(Site::class,'Id_Site','Id_Site');
    }
}
