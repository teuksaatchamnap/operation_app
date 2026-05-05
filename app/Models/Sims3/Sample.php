<?php

namespace App\Models\Sims3;

use Illuminate\Database\Eloquent\Builder;
use Illuminate\Database\Eloquent\Model;

/*
--
-- Table structure for table `samples`
--

CREATE TABLE `samples` (
  `id` bigint(20) UNSIGNED NOT NULL,
  `action_done` varchar(10) DEFAULT NULL,
  `alert_number` varchar(255) DEFAULT NULL,
  `alkalinity` varchar(255) DEFAULT NULL,
  `aluminium` varchar(255) DEFAULT NULL,
  `amonia` varchar(255) DEFAULT NULL,
  `analysis_date` datetime DEFAULT NULL,
  `arsenic` varchar(255) DEFAULT NULL,
  `calcium` varchar(255) DEFAULT NULL,
  `chloride` varchar(255) DEFAULT NULL,
  `chlorine` varchar(255) DEFAULT NULL,
  `color` varchar(255) DEFAULT NULL,
  `comment` text DEFAULT NULL,
  `conductivity` varchar(255) DEFAULT NULL,
  `contamination_level_bottle` int(11) DEFAULT NULL,
  `contamination_level_machine` int(11) DEFAULT NULL,
  `created_by` varchar(255) DEFAULT NULL,
  `delay` int(11) DEFAULT NULL,
  `desinfection` varchar(255) DEFAULT NULL,
  `email_alert` tinyint(1) DEFAULT NULL,
  `escherichia` varchar(255) DEFAULT NULL,
  `escherichia_bottle` varchar(255) DEFAULT NULL,
  `fluoride` varchar(255) DEFAULT NULL,
  `hardness` varchar(255) DEFAULT NULL,
  `iron` varchar(255) DEFAULT NULL,
  `last_updates` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`last_updates`)),
  `manganese` varchar(255) DEFAULT NULL,
  `nitrate` varchar(255) DEFAULT NULL,
  `nitrite` varchar(255) DEFAULT NULL,
  `ph` varchar(255) DEFAULT NULL,
  `pretreatment` varchar(255) DEFAULT NULL,
  `production` varchar(255) DEFAULT NULL,
  `received_date` datetime DEFAULT NULL,
  `response_date` datetime DEFAULT NULL,
  `root_cause` varchar(255) DEFAULT NULL,
  `safe` varchar(255) DEFAULT NULL,
  `sample_date` datetime DEFAULT NULL,
  `silver` varchar(255) DEFAULT NULL,
  `site` varchar(255) DEFAULT NULL,
  `smell` varchar(255) DEFAULT NULL,
  `sulfates` varchar(255) DEFAULT NULL,
  `taste` varchar(255) DEFAULT NULL,
  `tds` varchar(255) DEFAULT NULL,
  `temperature` varchar(255) DEFAULT NULL,
  `test_number` varchar(255) DEFAULT NULL,
  `total_coliform` varchar(255) DEFAULT NULL,
  `total_coliform_bottle` varchar(255) DEFAULT NULL,
  `total_chlore` varchar(255) DEFAULT NULL,
  `turbidity` varchar(255) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL,
  `site_open_sample_type` varchar(200) DEFAULT NULL,
  `site_open_description` text DEFAULT NULL,
  `site_open_sample_by` varchar(100) DEFAULT NULL,
  `site_open_final_judgement` varchar(100) DEFAULT NULL,
  `site_open_comment` text DEFAULT NULL,
  `site_open_judgement` text DEFAULT NULL,
  `site_open_solution` text DEFAULT NULL,
  `site_open_sample_date` datetime(4) DEFAULT NULL,
  `type` varchar(100) DEFAULT NULL,
  `site_open_project_type` varchar(100) DEFAULT NULL,
  `sample_en_location` varchar(100) DEFAULT NULL,
  `sample_kh_location` varchar(100) DEFAULT NULL,
  `laboratory` varchar(100) DEFAULT NULL,
  `sample_code` int(100) DEFAULT NULL,
  `latitude` varchar(100) DEFAULT NULL,
  `longtitude` varchar(100) DEFAULT NULL,
  `magesuim` varchar(100) DEFAULT NULL,
  `email_status` int(10) DEFAULT NULL,
  `raw_water_type` varchar(200) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
 */

/**
 * @property string|null $site
 * @property \DateTimeInterface|null $sample_date
 * @property \DateTimeInterface|null $analysis_date
 * @property string|null $escherichia
 * @property string|null $total_coliform
 */
class Sample extends Model
{
    protected $connection = 'sims3';

    protected $table = 'samples';

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
