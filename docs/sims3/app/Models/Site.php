<?php

namespace App\Models;

use Google\Service\Dfareporting\SiteContact;
use Illuminate\Database\Eloquent\Model;

class Site extends Model
{
    protected $primaryKey = 'Id_Site';
    protected $table = 'Sites';
    public $incrementing = false; 
    protected $keyType = 'string';
    public $timestamps = false;
    
    protected $fillable = [
        'Id_Site',
        'technician_site',
        'Platform',
        'Last_Tier',
        'picture',
        'Project_Date',
        'Platform_Date',
        'Move_Site',
        'Advisor',
        'Khmer_advisor',
        'Date_start_working',
        'Old_Platform',
        'Code_Village', 'Village', 'Village_khmer', 'Commune', 'Commune_khmer', 'District', 'District_khmer', 'Code_Province', 'Province', 'Province_khmer', 'Latitude', 'Longitude',
        'ProjectAgreement', 'Wave', 'Funder_1', 'Funder_2', 'Funder_3',
        'Number_Village', 'Number_Family', 'Number_Population','Number_Population_5km',
        'Number_Pagoda', 'Number_Primary_School', 'Land_of_kiosk', 'Road_Leading_to_Kiosk', 'Paved_Asphalt_Road', 'Concrete_Road', 'Laterite_Road', 'White_Soiled_Road',
        'Water_Source', 'Well_Pond_Ownership', 'Depth_Well_Pond', 'Water_Source_Distance_From_Kiosk',
          'Second_Water_Source', 'Well_Pond_Ownership_Second_Source', 'Depth_Well_Pond_Second_Source', 'Water_Source_Distance_From_Kiosk_Second_Source',
          'Main_Power_Source', 'Second_Power_Source', 'Type_of_Water_Tank','school_program','Advisor_email','Entrepreneur_English_Name', "Entrepreneur_Khmer_Name", "Sex", "Commune_Entrepreneur", "Province_Entrepreneur", "Date_of_birth", "Date_start_working", "Phone_Number",
          "Education", "Previous_Job", "Resignation", "Education_Background", "Part_Time_Job", "ID_Number", "Reading", "Writing", "Calculating", "Why_working_as_entrepreneur","Status_Site"
    ];
    
    public function siteContract()
    {
        return $this->hasOne(SiteContract::class,'Id_Site','Id_Site');
    }
    public function schoolProgram()
    {
        return $this->hasMany(SchoolProgram::class,'Id_Site','Id_Site');
    }
    public function samples()
    {
        return $this->hasMany(Sample::class, 'site', 'Id_Site');
    }
    public function entrepreneurProfiles()
    {
        return $this->hasMany(EntrepreneurProfile::class, 'Id_Site', 'Id_Site');
    }
    public function invoices()
    {
        return $this->hasMany(Invoice::class, 'site', 'Id_Site');
    }
    public function dailySales()
    {
        return $this->hasMany(DailySales::class, 'Id_Site', 'Id_Site');
    }
    // Get latest invoice (if needed)
    // public function latestInvoice()
    // {
    //     return $this->hasOne(Invoice::class, 'Id_Site', 'Id_Site')->latestOfMany();
    // }
}
