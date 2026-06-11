<?php

namespace App\Models;

// use Illuminate\Contracts\Auth\MustVerifyEmail;
use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Foundation\Auth\User as Authenticatable;
use Illuminate\Notifications\Notifiable;
use Laravel\Sanctum\HasApiTokens;

class User extends Authenticatable
{
    use HasApiTokens, HasFactory, Notifiable;

    protected $primaryKey = 'email';

    public $timestamps = false;

    public $incrementing = false; 
    
    protected $fillable = [
        'email',
        'permissions',
        'manager',
        'position',
        'staff_id',
        'staff_name',
        'staff_sex',
        'staff_position',
        'staff_dept',
        'staff_join_date',
        'staff_supervisor_by',
    ];

    protected $hidden = [
        'remember_token',
    ];

    protected $casts = [
        'permissions' => 'array',
        'staff_join_date' => 'date:Y-m-d',
    ];
}
