<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class TechnicalProblem extends Model
{
    use HasFactory;
    protected $table = 'technical_problems';
    protected $fillable = ['technical_id', 'problem_category', 'sub_problem', 'solution_list','detail_solution'];

    // Relationship: Each Problem belongs to one Request
    public function technicalRequest()
    {
        return $this->belongsTo(Technical::class,'technical_id', 'id');
    }
}
