<?php

namespace App\Models\Sims3;

use Illuminate\Database\Eloquent\Builder;
use Illuminate\Database\Eloquent\Model;

/*
--
-- Table structure for table `sites`
--

CREATE TABLE `sites` (
  `Id_Site` varchar(255) NOT NULL,
  `Platform` varchar(255) DEFAULT NULL,
  `Old_Platform` varchar(255) DEFAULT NULL,
  `Province` varchar(255) DEFAULT NULL,
  `Advisor` varchar(255) DEFAULT NULL,
  `Khmer_advisor` varchar(100) DEFAULT NULL,
  `Last_Tier` varchar(255) DEFAULT NULL,
  `Business_Manager` varchar(255) DEFAULT NULL,
  `Longitude` float DEFAULT NULL,
  `Latitude` float DEFAULT NULL,
  `Wave` varchar(255) DEFAULT NULL,
  `Population` float DEFAULT NULL,
  `Family` float DEFAULT NULL,
  `Code_Province` varchar(255) DEFAULT NULL,
  `Advisor_second_semester` varchar(255) DEFAULT NULL,
  `Advisor_first_semester` varchar(255) DEFAULT NULL,
  `SchoolSalesBudget` float DEFAULT NULL,
  `SalesPrevision` float DEFAULT NULL,
  `Population5km` float DEFAULT NULL,
  `Opened_day_this_year` float DEFAULT NULL,
  `Opened_month_last_12months` float DEFAULT NULL,
  `Debt` float DEFAULT NULL,
  `Commune` varchar(255) DEFAULT NULL,
  `District` varchar(255) DEFAULT NULL,
  `Village` varchar(255) DEFAULT NULL,
  `Building_cost` float DEFAULT NULL,
  `Number_Village` float DEFAULT NULL,
  `Households` float DEFAULT NULL,
  `Female` float DEFAULT NULL,
  `Migration` float DEFAULT NULL,
  `Primary_School` float DEFAULT NULL,
  `Classroom` float DEFAULT NULL,
  `Water_Source` varchar(255) DEFAULT NULL,
  `NumberSchoolsWinS` float DEFAULT NULL,
  `NumberStudentsWinS` float DEFAULT NULL,
  `Land_of_kiosk` varchar(255) DEFAULT NULL,
  `Number_Village_5km` float DEFAULT NULL,
  `Project` tinyint(1) DEFAULT NULL,
  `Office` varchar(255) DEFAULT NULL,
  `Commune_khmer` varchar(255) DEFAULT NULL,
  `Village_khmer` varchar(255) DEFAULT NULL,
  `Province_khmer` varchar(255) DEFAULT NULL,
  `District_khmer` varchar(255) DEFAULT NULL,
  `Site_Name` varchar(255) DEFAULT NULL,
  `Site_Name_Khmer` varchar(255) DEFAULT NULL,
  `Code_Village` int(11) DEFAULT NULL,
  `Code_Commune` int(11) DEFAULT NULL,
  `Code_District` varchar(255) DEFAULT NULL,
  `Code_Province_INT` int(11) DEFAULT NULL,
  `Funder_1` varchar(255) DEFAULT NULL,
  `Funder_2` varchar(255) DEFAULT NULL,
  `Funder_3` varchar(255) DEFAULT NULL,
  `Number_Family` float DEFAULT NULL,
  `Number_Households` float DEFAULT NULL,
  `Number_Population` float DEFAULT NULL,
  `Number_Women` float DEFAULT NULL,
  `Number_Migration` float DEFAULT NULL,
  `Number_Family_5km` float DEFAULT NULL,
  `Number_Households_5km` float DEFAULT NULL,
  `Number_Population_5km` float DEFAULT NULL,
  `Number_Women_5km` float DEFAULT NULL,
  `Number_Migration_5km` float DEFAULT NULL,
  `Number_Pagoda` float DEFAULT NULL,
  `Number_Primary_School` float DEFAULT NULL,
  `Road_Leading_to_Kiosk` varchar(255) DEFAULT NULL,
  `Paved_Asphalt_Road` float DEFAULT NULL,
  `Concrete_Road` float DEFAULT NULL,
  `Laterite_Road` float DEFAULT NULL,
  `White_Soiled_Road` float DEFAULT NULL,
  `Well_Pond_Ownership` varchar(255) DEFAULT NULL,
  `Depth_Well_Pond` varchar(255) DEFAULT NULL,
  `Water_Source_Distance_From_Kiosk` varchar(255) DEFAULT NULL,
  `Second_Water_Source` varchar(255) DEFAULT NULL,
  `Well_Pond_Ownership_Second_Source` varchar(255) DEFAULT NULL,
  `Depth_Well_Pond_Second_Source` varchar(255) DEFAULT NULL,
  `Water_Source_Distance_From_Kiosk_Second_Source` float DEFAULT NULL,
  `Main_Power_Source` varchar(255) DEFAULT NULL,
  `Second_Power_Source` varchar(255) DEFAULT NULL,
  `Type_of_Water_Tank` varchar(255) DEFAULT NULL,
  `Monthly_Income_Average_per_Person` varchar(255) DEFAULT NULL,
  `Labour_Market` varchar(255) DEFAULT NULL,
  `Monthly_Income_Average_per_Worker` varchar(255) DEFAULT NULL,
  `ProjectAgreement` datetime DEFAULT NULL,
  `Sale_Starting_Date` datetime DEFAULT NULL,
  `Entrepreneur_English_Name` varchar(255) DEFAULT NULL,
  `Entrepreneur_Khmer_Name` varchar(255) DEFAULT NULL,
  `Sex` varchar(255) DEFAULT NULL,
  `Commune_Entrepreneur` varchar(255) DEFAULT NULL,
  `Province_Entrepreneur` varchar(255) DEFAULT NULL,
  `Date_of_birth` date DEFAULT NULL,
  `Date_start_working` date DEFAULT NULL,
  `Phone_Number` varchar(100) DEFAULT NULL,
  `Education` varchar(255) DEFAULT NULL,
  `Previous_Job` varchar(255) DEFAULT NULL,
  `Resignation` tinyint(1) DEFAULT NULL,
  `Generation` varchar(255) DEFAULT NULL,
  `Education_Background` varchar(255) DEFAULT NULL,
  `Part_Time_Job` varchar(255) DEFAULT NULL,
  `ID_Number` varchar(100) DEFAULT NULL,
  `Reading` varchar(255) DEFAULT NULL,
  `Writing` varchar(255) DEFAULT NULL,
  `Calculating` varchar(255) DEFAULT NULL,
  `Why_working_as_entrepreneur` varchar(255) DEFAULT NULL,
  `sensor_id` bigint(20) UNSIGNED DEFAULT NULL,
  `Project_Date` datetime(5) DEFAULT NULL,
  `Platform_Date` datetime(5) DEFAULT NULL,
  `Move_Site` varchar(100) DEFAULT NULL,
  `technician_site` varchar(200) DEFAULT NULL,
  `picture` varchar(200) DEFAULT NULL,
  `school_program` int(50) DEFAULT NULL,
  `Advisor_email` varchar(60) DEFAULT NULL,
  `Status_Site` varchar(100) DEFAULT NULL,
  `last_updates` text DEFAULT NULL,
  `is_pilot` tinyint(1) NOT NULL DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;
 */

/**
 * @property string $Id_Site
 * @property string|null $Site_Name
 * @property string|null $Platform
 * @property string|null $Advisor
 * @property string|null $Business_Manager
 * @property string|null $Water_Source
 * @property string|null $Status_Site
 * @property string|null $Entrepreneur_English_Name
 * @property string|null $technician_site
 * @property string|null $Last_Tier
 * @property string|null $Commune
 * @property float|null $Population
 * @property float|null $Number_Population
 * @property float|null $Households
 * @property string|null $Date_start_working
 * @property string|null $Project_Date
 * @property float|null $Latitude
 * @property float|null $Longitude
 * @property string|null $Advisor_email
 */
class Site extends Model
{
    protected $connection = 'sims3';

    protected $table = 'Sites';

    public $timestamps = false;

    protected function performInsert(Builder $query)
    {
        return false;
    }

    protected function performUpdate(Builder $query)
    {
        return false;
    }

    protected function performDeleteOnModel(): void {}
}
