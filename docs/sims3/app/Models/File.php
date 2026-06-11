<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\MorphTo;

class File extends Model
{
    use HasFactory;

    /**
     * The attributes that are mass assignable.
     *
     * @var array<int, string>
     */
    protected $fillable = [
        'path', 'name', 'type', 'related_date', 'site', 'miniature_path'
    ];

    /**
     * Get the parent model that the file belongs to (polymorphic relation).
     */
    public function fileable(): MorphTo
    {
        return $this->morphTo();
    }
}