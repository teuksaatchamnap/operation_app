<?php

namespace App\Http\Controllers;


use ZipStream\Option\Archive;
use ZipStream\ZipStream;

use App\Mail\EntrepreneurEmail;
use App\Mail\SchoolRequest;
use App\Mail\SiteCloseButHaveData;
use App\Models\Assessment;
use App\Models\Consumable;
use App\Models\EntrepreneurProfile;
use App\Models\Expense;
use App\Models\Kol;
use App\Models\Rountine;
use App\Models\SaleSurvey;
use App\Models\SaleTeam;
use App\Models\SchoolProgram;
use App\Models\Site;
use App\Models\TransportationAssessment;
use Google\Cloud\Datastore\DatastoreClient;
use Google\Cloud\Datastore\Query\Query;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Log;
use Illuminate\Support\Facades\Mail;
use Illuminate\Support\Str;
use Imagick;
use ZipArchive;
class CommcareController extends Controller
{

    public $projectId = "sims-2-140009";

    public function __construct()
    {
        $this->projectId = "sims-2-140009";
        putenv('GOOGLE_APPLICATION_CREDENTIALS=' . storage_path('app/datastore_writer_appengine.json'));
    }
    public function normalizeField($value, $fallback = null)
    {
        return ($value === '' || $value === null) ? $fallback : $value;
    }

    function normalizeDateField($value, $fallback = null)
    {
        try {
            return !empty($value) ? \Carbon\Carbon::parse($value)->format('Y-m-d') : (($fallback !== '0000-00-00') ? $fallback : null);
        } catch (\Exception $e) {
            return ($fallback !== '0000-00-00') ? $fallback : null;
        }
    }
    function normalizeNumberField($value, $fallback = null)
    {
        // Remove any non-digit, non-dot, non-comma characters (e.g. letters like 'L')
        $cleaned = preg_replace('/[^\d.,\-]/', '', $value ?? '');

        // Replace comma if used as thousand separator (e.g. 1,500 => 1500)
        $cleaned = str_replace(',', '', $cleaned);

        // Final check: is it a valid number?
        return is_numeric($cleaned) ? (float) $cleaned : $fallback;
    }

    public function store(Request $request)
    {
        $datastore = new DatastoreClient([
            'projectId' => $this->projectId
        ]);
        $message = json_decode($request->getContent());
        if (property_exists($message, "form") && property_exists($message->form, "@name")) {
            if ($message->form->{'@name'} == "7. Request Form") {
                $result ='';
                // put auto order sticker for bottle.
                if (isset($message->form->site_confirmed->category1->c401002))
                    {
                        $bottleItemNumber = $message->form->site_confirmed->category1->c401002;
                        $bottleItem = floatval($bottleItemNumber);
                        $i='';
                        if ($bottleItem < 100) {
                                $i = 1;
                            } elseif ($bottleItem == 100) {
                                $i = 1;
                            } elseif ($bottleItem > 100 && $bottleItem <= 1000) {
                                $i = ceil($bottleItem / 100);
                            } else {
                                $i = 10; // or whatever for > 1000
                            }

                        if (!empty($bottleItem) && $bottleItem !== "" && $bottleItem > 0)
                        {
                            $d = $message->form->date;
                            $newDate = \Carbon\Carbon::parse($d)->addMonth()->day(1);
                            $consumable = new Consumable();
                            $consumable->Id_Site = $message->form->site_name ?? null;
                            $consumable->Month = $newDate->format('Y-m-d');
                            $consumable->Date_submission = $d;
                            $consumable->Category = 1;
                            $consumable->Number_Item = $i;
                            $consumable->Item = '401008';
                            $consumable->Price_Item = 21200;
                            $consumable->English_name = 'O-We sticker for bottle';
                            $consumable->Khmer_name = 'ឡូហ្គោ O-WE (22cm x  9.5cm)';
                            $consumable->Unit = 'Packet (100 Pc)';
                            $consumable->Payment_method = 'Invoice';
                            $consumable->save();
                        }
                    }
                $received = substr($message->received_on, 0, 10);
                $cut = \Carbon\Carbon::parse(substr($received, 0, 10));
                $exactDate = substr($cut->addMonth(1), 0, 10);

                $month = substr($exactDate, 5, 2);
                $special_month = substr($month, 0, 1);
                if ($special_month == "0") {
                    $add_month = substr($month, 1, 1);
                    $year = substr($exactDate, 0, 4);
                    $month = $add_month . "-" . $year;
                } else {
                    $year = substr($exactDate, 0, 4);
                    $month = $month . "-" . $year;
                }
            } else {
                if (isset($message->form->month) && isset($message->form->year)) {
                    $month = $message->form->month . "-" . $message->form->year;
                } else {
                    $month = "undefined";
                }
            }
            // Insert site assessment and Routine
            if ($message->form->{'@name'} == "Site assessment and routine check") {
                $s = Str::ucfirst($message->form->site_confirmed->basic_information->site);
                $data = Assessment::where('site', $s)
                    ->orderBy('created_at', 'desc')->first();
                if ($message->form->site_confirmed->which_form_do_you_want_to_do == "site_assessment") {
                    $ass = new Assessment();
                    $ass->number = "1000";
                    $ass->formid = $message->id;
                    $ass->site = Str::ucfirst($message->form->site_confirmed->basic_information->site);
                    $ass->technician = $message->form->site_confirmed->basic_information->technician_name;
                    $ass->date_form = substr($message->form->meta->timeEnd, 0, 10) ?? null;
                    $ass->main_person_the_water_kiosk = $message->form->site_confirmed->basic_information->who_is_in_main_person_the_water_kiosk_with_you ?? null;
                    $ass->form_do_you_want_to_do = $message->form->site_confirmed->which_form_do_you_want_to_do ?? null;
                    $ass->first_site_assessment = $message->form->site_confirmed->is_it_the_first_site_assessment ?? null;
                    // $ass->a9= !empty($message->form->site_confirmed->which_part_do_you_want_to_modify)? $message->form->site_confirmed->which_part_do_you_want_to_modify : $data->a9;
                    if ($message->form->site_confirmed->is_it_the_first_site_assessment == "no") {
                        $ass->which_part_do_you_want_to_modify =  $message->form->site_confirmed->which_part_do_you_want_to_modify ?? null;
                        $ass->main_source_of_water = !empty($message->form->site_confirmed->site_assessment->water_source->what_is_main_source_of_water) ? $message->form->site_confirmed->site_assessment->water_source->what_is_main_source_of_water : ($data->main_source_of_water ?? null);
                        $ass->main_source_of_electricity = !empty($message->form->site_confirmed->site_assessment->water_source->what_is_main_source_of_electricity) ? $message->form->site_confirmed->site_assessment->water_source->what_is_main_source_of_electricity : ($data->main_source_of_electricity ?? null);
                        $ass->second_source_of_water = !empty($message->form->site_confirmed->site_assessment->water_source->what_is_second_source_of_water) ? $message->form->site_confirmed->site_assessment->water_source->what_is_second_source_of_water : ($data->second_source_of_water ?? null);
                        $ass->electric_cabinet = !empty($message->form->site_confirmed->site_assessment->water_source->electric_cabinet) ? $message->form->site_confirmed->site_assessment->water_source->electric_cabinet : ($data->electric_cabinet ?? null);
                        $ass->initial_installation_or_last_change = $this->normalizeDateField($message->form->site_confirmed->site_assessment->water_source->date_of_initial_installation_or_last_change ?? null, $data->initial_installation_or_last_change ?? null);
                        $ass->ground_cable = !empty($message->form->site_confirmed->site_assessment->water_source->ground_cable) ? $message->form->site_confirmed->site_assessment->water_source->ground_cable : ($data->ground_cable ?? null);
                        $ass->stabilizer = !empty($message->form->site_confirmed->site_assessment->water_source->stabilizer) ? $message->form->site_confirmed->site_assessment->water_source->stabilizer : ($data->stabilizer ?? null);
                        $ass->last_change_stabilizer = !empty($message->form->site_confirmed->site_assessment->water_source->date_of_initial_installation_or_last_change) ? $message->form->site_confirmed->site_assessment->water_source->date_of_initial_installation_or_last_change : ($data->last_change_stabilizer ?? null);
                        $ass->solar_panel = !empty($message->form->site_confirmed->site_assessment->solar_panel_part->solar_panel) ? $message->form->site_confirmed->site_assessment->solar_panel_part->solar_panel : ($data->solar_panel ?? null);
                        $ass->date_installation_solar_panel = $this->normalizeDateField($message->form->site_confirmed->site_assessment->solar_panel_part->date_of_initial_installation_or_last_change_solar ?? null, $data->date_installation_solar_panel ?? null);
                        $ass->solar_charge_controller = !empty($message->form->site_confirmed->site_assessment->solar_panel_part->solar_charge_controller) ? $message->form->site_confirmed->site_assessment->solar_panel_part->solar_charge_controller : ($data->solar_charge_controller ?? null);
                        $ass->date_change_solar_charge_controller = $this->normalizeDateField($message->form->site_confirmed->site_assessment->solar_panel_part->date_of_initial_installation_or_last_change_solar_charge_controller ?? null, $data->date_change_solar_charge_controller ?? null);
                        $ass->condition_batteries = !empty($message->form->site_confirmed->site_assessment->solar_panel_part->condition_batteries) ? $message->form->site_confirmed->site_assessment->solar_panel_part->condition_batteries : ($data->condition_batteries ?? null);
                        $ass->date_last_change_batteries = $this->normalizeDateField($message->form->site_confirmed->site_assessment->solar_panel_part->date_of_initial_installation_or_last_change_batteries ?? null, $data->date_last_change_batteries ?? null);
                        $ass->condition_inverter_dc_to_ac = !empty($message->form->site_confirmed->site_assessment->solar_panel_part->condition_inverter_dc_to_ac) ? $message->form->site_confirmed->site_assessment->solar_panel_part->condition_inverter_dc_to_ac : ($data->condition_inverter_dc_to_ac ?? null);
                        $ass->date_change_inverter = $this->normalizeDateField($message->form->site_confirmed->site_assessment->solar_panel_part->date_of_initial_installation_or_last_change_inverter ?? null, $data->date_change_inverter ?? null);
                        $ass->pre_treatment_process_1 = !empty($message->form->site_confirmed->site_assessment->{'pre-treatment'}->{'pre-treatment_process_flow_chart_-_start_from_the_raw_water_tank_to_pre-tre'}->process_number_1) ? $message->form->site_confirmed->site_assessment->{'pre-treatment'}->{'pre-treatment_process_flow_chart_-_start_from_the_raw_water_tank_to_pre-tre'}->process_number_1 : ($data->pre_treatment_process_1 ?? null);
                        $ass->pre_treatment_process_2 = !empty($message->form->site_confirmed->site_assessment->{'pre-treatment'}->{'pre-treatment_process_flow_chart_-_start_from_the_raw_water_tank_to_pre-tre'}->number_2) ? $message->form->site_confirmed->site_assessment->{'pre-treatment'}->{'pre-treatment_process_flow_chart_-_start_from_the_raw_water_tank_to_pre-tre'}->number_2 : ($data->pre_treatment_process_2 ?? null);
                        $ass->pre_treatment_process_3 = !empty($message->form->site_confirmed->site_assessment->{'pre-treatment'}->{'pre-treatment_process_flow_chart_-_start_from_the_raw_water_tank_to_pre-tre'}->number_3) ? $message->form->site_confirmed->site_assessment->{'pre-treatment'}->{'pre-treatment_process_flow_chart_-_start_from_the_raw_water_tank_to_pre-tre'}->number_3 : ($data->pre_treatment_process_3 ?? null);
                        $ass->pre_treatment_process_4 = !empty($message->form->site_confirmed->site_assessment->{'pre-treatment'}->{'pre-treatment_process_flow_chart_-_start_from_the_raw_water_tank_to_pre-tre'}->number_4) ? $message->form->site_confirmed->site_assessment->{'pre-treatment'}->{'pre-treatment_process_flow_chart_-_start_from_the_raw_water_tank_to_pre-tre'}->number_4 : ($data->pre_treatment_process_4 ?? null);
                        $ass->pre_treatment_process_5 = !empty($message->form->site_confirmed->site_assessment->{'pre-treatment'}->{'pre-treatment_process_flow_chart_-_start_from_the_raw_water_tank_to_pre-tre'}->number_5) ? $message->form->site_confirmed->site_assessment->{'pre-treatment'}->{'pre-treatment_process_flow_chart_-_start_from_the_raw_water_tank_to_pre-tre'}->number_5 : ($data->pre_treatment_process_5 ?? null);
                        $ass->pre_treatment_process_6 = !empty($message->form->site_confirmed->site_assessment->{'pre-treatment'}->{'pre-treatment_process_flow_chart_-_start_from_the_raw_water_tank_to_pre-tre'}->number_6) ? $message->form->site_confirmed->site_assessment->{'pre-treatment'}->{'pre-treatment_process_flow_chart_-_start_from_the_raw_water_tank_to_pre-tre'}->number_6 : ($data->pre_treatment_process_6 ?? null);
                        $ass->pre_treatment_process_7 = !empty($message->form->site_confirmed->site_assessment->{'pre-treatment'}->{'pre-treatment_process_flow_chart_-_start_from_the_raw_water_tank_to_pre-tre'}->number_7) ? $message->form->site_confirmed->site_assessment->{'pre-treatment'}->{'pre-treatment_process_flow_chart_-_start_from_the_raw_water_tank_to_pre-tre'}->number_7 : ($data->pre_treatment_process_7 ?? null);
                        $ass->type_of_raw_water_tank = !empty($message->form->site_confirmed->site_assessment->{'pre-treatment'}->raw_water_tank->type_of_water_tank) ? $message->form->site_confirmed->site_assessment->{'pre-treatment'}->raw_water_tank->type_of_water_tank : ($data->type_of_raw_water_tank ?? null);
                        $ass->raw_water_tank_h_cm = $this->normalizeNumberField($message->form->site_confirmed->site_assessment->{'pre-treatment'}->raw_water_tank->h_cm ?? null, $data->raw_water_tank_h_cm ?? null);
                        $ass->raw_water_tank_d_cm = $this->normalizeNumberField($message->form->site_confirmed->site_assessment->{'pre-treatment'}->raw_water_tank->d_cm ?? null, $data->raw_water_tank_d_cm ?? null);
                        $ass->raw_water_tank_v_liter = $this->normalizeNumberField($message->form->site_confirmed->site_assessment->{'pre-treatment'}->raw_water_tank->v_liter ?? null, $data->raw_water_tank_v_liter ?? null);
                        $ass->type_of_sand_filter_tank = !empty($message->form->site_confirmed->site_assessment->{'pre-treatment'}->sand_filter_tank->type_of_sand_filter_tank) ? $message->form->site_confirmed->site_assessment->{'pre-treatment'}->sand_filter_tank->type_of_sand_filter_tank : ($data->type_of_sand_filter_tank ?? null);
                        $ass->sand_filter_tank_h_cm = $this->normalizeNumberField($message->form->site_confirmed->site_assessment->{'pre-treatment'}->sand_filter_tank->h_cm ?? null, $data->sand_filter_tank_h_cm ?? null);
                        $ass->sand_filter_tank_d_cm = $this->normalizeNumberField($message->form->site_confirmed->site_assessment->{'pre-treatment'}->sand_filter_tank->d_cm ?? null, $data->sand_filter_tank_d_cm ?? null);
                        $ass->sand_filter_tank_v_liter = $this->normalizeNumberField($message->form->site_confirmed->site_assessment->{'pre-treatment'}->sand_filter_tank->v_liter ?? null, $data->sand_filter_tank_v_liter ?? null);
                        $ass->sand_filter_tank__height_from_the_top_cm = $this->normalizeNumberField($message->form->site_confirmed->site_assessment->{'pre-treatment'}->sand_filter_tank->the_height_from_the_top_of_the_tank_to_the_media_mm ?? null, $data->sand_filter_tank__height_from_the_top_cm ?? null);
                        $ass->date_change_sand_filter_tank = $this->normalizeDateField($message->form->site_confirmed->site_assessment->{'pre-treatment'}->sand_filter_tank->date_of_media_initial_installation_or_last_change_sand_filter_tank ?? null, $data->date_change_sand_filter_tank ?? null);
                        $ass->type_of_ac_filter_tank = !empty($message->form->site_confirmed->site_assessment->{'pre-treatment'}->ac_filter_tank->type_of_ac_filter_tank) ? $message->form->site_confirmed->site_assessment->{'pre-treatment'}->ac_filter_tank->type_of_ac_filter_tank : ($data->type_of_ac_filter_tank ?? null);
                        $ass->ac_filter_tank_h_cm = $this->normalizeNumberField($message->form->site_confirmed->site_assessment->{'pre-treatment'}->ac_filter_tank->h_cm ?? null, $data->ac_filter_tank_h_cm ?? null);
                        $ass->ac_filter_tank_d_cm = $this->normalizeNumberField($message->form->site_confirmed->site_assessment->{'pre-treatment'}->ac_filter_tank->d_cm ?? null, $data->ac_filter_tank_d_cm ?? null);
                        $ass->ac_filter_tank_v_liter = $this->normalizeNumberField($message->form->site_confirmed->site_assessment->{'pre-treatment'}->ac_filter_tank->v_m ?? null, $data->ac_filter_tank_v_liter ?? null);
                        $ass->ac_filter_tank_media_height_from_the_top = $this->normalizeNumberField($message->form->site_confirmed->site_assessment->{'pre-treatment'}->ac_filter_tank->media_height_from_the_top_of_the_tank ?? null, $data->ac_filter_tank_media_height_from_the_top ?? null);
                        $ass->date_change_ac_filter_tank = $this->normalizeDateField($message->form->site_confirmed->site_assessment->{'pre-treatment'}->ac_filter_tank->date_of_media_initial_installation_or_last_change_ac_filter_tank ?? null, $data->date_change_ac_filter_tank ?? null);
                        $ass->type_of_resin_filter_tank = !empty($message->form->site_confirmed->site_assessment->{'pre-treatment'}->resin_filter_tank->type_of_resin_filter_tank) ? $message->form->site_confirmed->site_assessment->{'pre-treatment'}->resin_filter_tank->type_of_resin_filter_tank : ($data->type_of_resin_filter_tank ?? null);
                        $ass->resin_filter_tank_h_cm = $this->normalizeNumberField($message->form->site_confirmed->site_assessment->{'pre-treatment'}->resin_filter_tank->h_cm ?? null, $data->resin_filter_tank_h_cm ?? null);
                        $ass->resin_filter_tank_d_cm = $this->normalizeNumberField($message->form->site_confirmed->site_assessment->{'pre-treatment'}->resin_filter_tank->d_cm ?? null, $data->resin_filter_tank_d_cm ?? null);
                        $ass->resin_filter_tank_v_liter = $this->normalizeNumberField($message->form->site_confirmed->site_assessment->{'pre-treatment'}->resin_filter_tank->v_m ?? null, $data->resin_filter_tank_v_liter ?? null);
                        $ass->resin_filter_tank_media_height_from_the_top = $this->normalizeNumberField($message->form->site_confirmed->site_assessment->{'pre-treatment'}->resin_filter_tank->media_height_from_the_top_of_the_tank ?? null, $data->resin_filter_tank_media_height_from_the_top ?? null);
                        $ass->date_change_resin_filter_tank = $this->normalizeDateField($message->form->site_confirmed->site_assessment->{'pre-treatment'}->resin_filter_tank->date_of_media_initial_installation_or_last_change_resin_filter_tank ?? null, $data->date_change_resin_filter_tank ?? null);
                        $ass->type_of_clear_water_tank = !empty($message->form->site_confirmed->site_assessment->{'pre-treatment'}->clear_water_tank->type_of_clear_water_tank) ? $message->form->site_confirmed->site_assessment->{'pre-treatment'}->clear_water_tank->type_of_clear_water_tank : ($data->type_of_clear_water_tank ?? null);
                        $ass->clear_water_tank_h_cm = $this->normalizeNumberField($message->form->site_confirmed->site_assessment->{'pre-treatment'}->clear_water_tank->h_cm ?? null, $data->clear_water_tank_h_cm ?? null);
                        $ass->clear_water_tank_d_cm = $this->normalizeNumberField($message->form->site_confirmed->site_assessment->{'pre-treatment'}->clear_water_tank->d_cm ?? null, $data->clear_water_tank_d_cm ?? null);
                        $ass->clear_water_tank_v_liter = $this->normalizeNumberField($message->form->site_confirmed->site_assessment->{'pre-treatment'}->clear_water_tank->v_m ?? null, $data->clear_water_tank_v_liter ?? null);
                        $ass->flocculation_and_coagulation_process = !empty($message->form->site_confirmed->site_assessment->{'pre-treatment'}->flocculation_and_coagulation_process->flocculation_and_coagulation_process) ? $message->form->site_confirmed->site_assessment->{'pre-treatment'}->flocculation_and_coagulation_process->flocculation_and_coagulation_process : ($data->flocculation_and_coagulation_process ?? null);
                        $ass->reverse_osmose = !empty($message->form->site_confirmed->site_assessment->{'pre-treatment'}->reverse_osmose->reverse_osmose) ? $message->form->site_confirmed->site_assessment->{'pre-treatment'}->reverse_osmose->reverse_osmose : ($data->reverse_osmose ?? null);
                        $ass->date_change_reverse_osmose = $this->normalizeDateField($message->form->site_confirmed->site_assessment->{'pre-treatment'}->reverse_osmose->date_of_initial_installation_or_last_change_ro ?? null, $data->date_change_reverse_osmose ?? null);
                        $ass->ultrafiltration = !empty($message->form->site_confirmed->site_assessment->{'pre-treatment'}->ultrafiltration->ultrafiltration) ? $message->form->site_confirmed->site_assessment->{'pre-treatment'}->ultrafiltration->ultrafiltration : ($data->ultrafiltration ?? null);
                        $ass->date_change_ultrafiltration = $this->normalizeDateField($message->form->site_confirmed->site_assessment->{'pre-treatment'}->ultrafiltration->date_of_initial_installation_or_last_change_ultrafiltration ?? null, $data->date_change_ultrafiltration ?? null);
                        $ass->raw_water_pump = !empty($message->form->site_confirmed->site_assessment->{'pre-treatment'}->raw_water_pump->raw_water_pump) ? $message->form->site_confirmed->site_assessment->{'pre-treatment'}->raw_water_pump->raw_water_pump : ($data->raw_water_pump ?? null);
                        $ass->raw_water_pump_maximum_flow = $this->normalizeNumberField($message->form->site_confirmed->site_assessment->{'pre-treatment'}->raw_water_pump->{'manufacturer_specification_-_maximum_flow_qmax_raw_water_pump'} ?? null, $data->raw_water_pump_maximum_flow ?? null);
                        $ass->raw_water_pump_height_hmax = $this->normalizeNumberField($message->form->site_confirmed->site_assessment->{'pre-treatment'}->raw_water_pump->{'manufacturer_specification_-_maximum_height_hmax_raw_water_pump'} ?? null, $data->raw_water_pump_height_hmax ?? null);
                        $ass->raw_water_pump_power = $this->normalizeNumberField($message->form->site_confirmed->site_assessment->{'pre-treatment'}->raw_water_pump->{'manufacturer_specification_-_power_raw_water_pump'} ?? null, $data->raw_water_pump_power ?? null);
                        $ass->back_wash_pump = !empty($message->form->site_confirmed->site_assessment->{'pre-treatment'}->back_wash_pump->back_wash_pump) ? $message->form->site_confirmed->site_assessment->{'pre-treatment'}->back_wash_pump->back_wash_pump : ($data->back_wash_pump ?? null);
                        $ass->back_wash_pump_flow_qmax = $this->normalizeNumberField($message->form->site_confirmed->site_assessment->{'pre-treatment'}->back_wash_pump->{'manufacturer_specification_-_maximum_flow_qmax_back_wash_pump'} ?? null, $data->back_wash_pump_flow_qmax ?? null);
                        $ass->back_wash_pump_height_hmax = $this->normalizeNumberField($message->form->site_confirmed->site_assessment->{'pre-treatment'}->back_wash_pump->{'manufacturer_specification_-_maximum_height_hmax_back_wash_pump'} ?? null, $data->back_wash_pump_height_hmax ?? null);
                        $ass->back_wash_pump_power = $this->normalizeNumberField($message->form->site_confirmed->site_assessment->{'pre-treatment'}->back_wash_pump->{'manufacturer_specification_-_power_back_wash_pump'} ?? null, $data->back_wash_pump_power ?? null);
                        $ass->reverse_osmose_pump = !empty($message->form->site_confirmed->site_assessment->{'pre-treatment'}->reverse_osmose_pump->reverse_osmose_pump) ? $message->form->site_confirmed->site_assessment->{'pre-treatment'}->reverse_osmose_pump->reverse_osmose_pump : ($data->reverse_osmose_pump ?? null);
                        $ass->reverse_osmose_pump_flow_qmax = $this->normalizeNumberField($message->form->site_confirmed->site_assessment->{'pre-treatment'}->reverse_osmose_pump->{'manufacturer_specification_-_maximum_flow_qmax_reverse_osmose_pump'} ?? null, $data->reverse_osmose_pump_flow_qmax ?? null);
                        $ass->reverse_osmose_pump_height_hmax = $this->normalizeNumberField($message->form->site_confirmed->site_assessment->{'pre-treatment'}->reverse_osmose_pump->{'manufacturer_specification_-_maximum_height_hmax_reverse_osmose_pump'} ?? null, $data->reverse_osmose_pump_height_hmax ?? null);
                        $ass->reverse_osmose_pump_power = $this->normalizeNumberField($message->form->site_confirmed->site_assessment->{'pre-treatment'}->reverse_osmose_pump->{'manufacturer_specification_-_power_reverse_osmose_pump'} ?? null, $data->reverse_osmose_pump_power ?? null);
                        $ass->filter_50_item = !empty($message->form->site_confirmed->site_assessment->final_treatment->filter_50->item_50m_filter) ? $message->form->site_confirmed->site_assessment->final_treatment->filter_50->item_50m_filter : ($data->filter_50_item ?? null);
                        $ass->date_change_filter_50 = $this->normalizeDateField($message->form->site_confirmed->site_assessment->final_treatment->filter_50->date_of_initial_installation_or_last_change_50m_filter ?? null, $data->date_change_filter_50 ?? null);
                        $ass->filter_50_condition = !empty($message->form->site_confirmed->site_assessment->final_treatment->filter_50->condition) ? $message->form->site_confirmed->site_assessment->final_treatment->filter_50->condition : ($data->filter_50_condition ?? null);
                        $ass->filter_10_item = !empty($message->form->site_confirmed->site_assessment->final_treatment->filter_10->item_10m_filter) ? $message->form->site_confirmed->site_assessment->final_treatment->filter_10->item_10m_filter : ($data->filter_10_item ?? null);
                        $ass->date_change_10m_filter = $this->normalizeDateField($message->form->site_confirmed->site_assessment->final_treatment->filter_10->date_of_initial_installation_or_last_change_10m_filter ?? null, $data->date_change_10m_filter ?? null);
                        $ass->filter_10_condition = !empty($message->form->site_confirmed->site_assessment->final_treatment->filter_10->condition) ? $message->form->site_confirmed->site_assessment->final_treatment->filter_10->condition : ($data->filter_10_condition ?? null);
                        $ass->item_5m_filter = !empty($message->form->site_confirmed->site_assessment->final_treatment->filter_5->item_5m_filter) ? $message->form->site_confirmed->site_assessment->final_treatment->filter_5->item_5m_filter : ($data->item_5m_filter ?? null);
                        $ass->date_change_5m_filter = $this->normalizeDateField($message->form->site_confirmed->site_assessment->final_treatment->filter_5->date_of_initial_installation_or_last_change_5m_filter ?? null, $data->date_change_5m_filter ?? null);
                        $ass->filter_5_condition = !empty($message->form->site_confirmed->site_assessment->final_treatment->filter_5->condition) ? $message->form->site_confirmed->site_assessment->final_treatment->filter_5->condition : ($data->filter_5_condition ?? null);
                        $ass->item_1m_filter = !empty($message->form->site_confirmed->site_assessment->final_treatment->filter_1->item_1m_filter) ? $message->form->site_confirmed->site_assessment->final_treatment->filter_1->item_1m_filter : ($data->item_1m_filter ?? null);
                        $ass->date_change_1m_filter = $this->normalizeDateField($message->form->site_confirmed->site_assessment->final_treatment->filter_1->date_of_initial_installation_or_last_change_5m_filter ?? null, $data->date_change_1m_filter ?? null);
                        $ass->filter_1_condition = !empty($message->form->site_confirmed->site_assessment->final_treatment->filter_1->condition) ? $message->form->site_confirmed->site_assessment->final_treatment->filter_1->condition : ($data->filter_1_condition ?? null);
                        $ass->uv_lamp = !empty($message->form->site_confirmed->site_assessment->final_treatment->uv_lamp->uv_lamp) ? $message->form->site_confirmed->site_assessment->final_treatment->uv_lamp->uv_lamp : ($data->uv_lamp ?? null);
                        $ass->date_change_uv_lamp = $this->normalizeDateField($message->form->site_confirmed->site_assessment->final_treatment->uv_lamp->date_of_initial_installation_or_last_change_uv_lamp ?? null, $data->date_change_uv_lamp ?? null);
                        $ass->uv_lamp_condition = !empty($message->form->site_confirmed->site_assessment->final_treatment->uv_lamp->condition) ? $message->form->site_confirmed->site_assessment->final_treatment->uv_lamp->condition : ($data->uv_lamp_condition ?? null);
                        $ass->uv_controller = !empty($message->form->site_confirmed->site_assessment->final_treatment->uv_controller->uv_controller) ? $message->form->site_confirmed->site_assessment->final_treatment->uv_controller->uv_controller : ($data->uv_controller ?? null);
                        $ass->date_change_uv_controller = $this->normalizeDateField($message->form->site_confirmed->site_assessment->final_treatment->uv_controller->date_of_initial_installation_or_last_change_uv_controller ?? null, $data->date_change_uv_controller ?? null);
                        $ass->uv_controller_condition = !empty($message->form->site_confirmed->site_assessment->final_treatment->uv_controller->condition) ? $message->form->site_confirmed->site_assessment->final_treatment->uv_controller->condition : ($data->uv_controller_condition ?? null);
                        $ass->uv_ballast = !empty($message->form->site_confirmed->site_assessment->final_treatment->uv_ballast->uv_ballast) ? $message->form->site_confirmed->site_assessment->final_treatment->uv_ballast->uv_ballast : ($data->uv_ballast ?? null);
                        $ass->date_change_uv_ballast = $this->normalizeDateField($message->form->site_confirmed->site_assessment->final_treatment->uv_ballast->date_of_initial_installation_or_last_change_uv_ballast ?? null, $data->date_change_uv_ballast ?? null);
                        $ass->uv_ballast_condition = !empty($message->form->site_confirmed->site_assessment->final_treatment->uv_ballast->condition) ? $message->form->site_confirmed->site_assessment->final_treatment->uv_ballast->condition : ($data->uv_ballast_condition ?? null);
                        $ass->uv_sensor = !empty($message->form->site_confirmed->site_assessment->final_treatment->uv_sensor->uv_sensor) ? $message->form->site_confirmed->site_assessment->final_treatment->uv_sensor->uv_sensor : ($data->uv_sensor ?? null);
                        $ass->date_change_uv_sensor = $this->normalizeDateField($message->form->site_confirmed->site_assessment->final_treatment->uv_sensor->date_of_initial_installation_or_last_change_uv_sensor ?? null, $data->date_change_uv_sensor ?? null);
                        $ass->uv_sensor_condition = !empty($message->form->site_confirmed->site_assessment->final_treatment->uv_sensor->condition) ? $message->form->site_confirmed->site_assessment->final_treatment->uv_sensor->condition : ($data->uv_sensor_condition ?? null);
                        $ass->l_tank_for_cip = !empty($message->form->site_confirmed->site_assessment->final_treatment->l_tank_for_cip->l_tank_for_cip) ? $message->form->site_confirmed->site_assessment->final_treatment->l_tank_for_cip->l_tank_for_cip : ($data->l_tank_for_cip ?? null);
                        $ass->date_change_200l_tank_for_cip = $this->normalizeDateField($message->form->site_confirmed->site_assessment->final_treatment->l_tank_for_cip->date_of_initial_installation_or_last_change_200l_tank_for_cip ?? null, $data->date_change_200l_tank_for_cip ?? null);
                        $ass->l_tank_for_cip_condition = !empty($message->form->site_confirmed->site_assessment->final_treatment->l_tank_for_cip->condition) ? $message->form->site_confirmed->site_assessment->final_treatment->l_tank_for_cip->condition : ($data->l_tank_for_cip_condition ?? null);
                        $ass->micro_filter_pump = !empty($message->form->site_confirmed->site_assessment->final_treatment->{'micro-filter_pump'}->{'micro-filter_pump'}) ? $message->form->site_confirmed->site_assessment->final_treatment->{'micro-filter_pump'}->{'micro-filter_pump'} : ($data->micro_filter_pump ?? null);
                        $ass->micro_filter_pump_maximum_flow_qmax_lpm = $this->normalizeNumberField($message->form->site_confirmed->site_assessment->final_treatment->{'micro-filter_pump'}->{'manufacturer_specification_-_maximum_flow_qmax_lpm'} ?? null, $data->micro_filter_pump_maximum_flow_qmax_lpm ?? null);
                        $ass->micro_filter_pump_maximum_height_hmax_m = $this->normalizeNumberField($message->form->site_confirmed->site_assessment->final_treatment->{'micro-filter_pump'}->{'manufacturer_specification_-_maximum_height_hmax_m'} ?? null, $data->micro_filter_pump_maximum_height_hmax_m ?? null);
                        $ass->micro_filter_pump_power_kwhp = $this->normalizeNumberField($message->form->site_confirmed->site_assessment->final_treatment->{'micro-filter_pump'}->{'manufacturer_specification_-_power_kwhp'} ?? null, $data->micro_filter_pump_power_kwhp ?? null);
                        $ass->micro_filter_pump_voltage_v = $this->normalizeNumberField($message->form->site_confirmed->site_assessment->final_treatment->{'micro-filter_pump'}->voltage_v ?? null, $data->micro_filter_pump_voltage_v ?? null);
                        $ass->bottle_washing_area_dirty_bottle_shelf = !empty($message->form->site_confirmed->site_assessment->bottle_washing_area->bottle_washing_area->dirty_bottle_shelf) ? $message->form->site_confirmed->site_assessment->bottle_washing_area->bottle_washing_area->dirty_bottle_shelf : ($data->bottle_washing_area_dirty_bottle_shelf ?? null);
                        $ass->bottle_washing_area_washing_station = !empty($message->form->site_confirmed->site_assessment->bottle_washing_area->bottle_washing_area->washing_station) ? $message->form->site_confirmed->site_assessment->bottle_washing_area->bottle_washing_area->washing_station : ($data->bottle_washing_area_washing_station ?? null);
                        $ass->bottle_washing_area_specific_tank_for_lid_disinfection = $this->normalizeNumberField($message->form->site_confirmed->site_assessment->bottle_washing_area->bottle_washing_area->specific_tank_for_lid_disinfection ?? null, $data->bottle_washing_area_specific_tank_for_lid_disinfection ?? null);
                        $ass->bottle_washing_area_chlorine_tank = !empty($message->form->site_confirmed->site_assessment->bottle_washing_area->bottle_washing_area->chlorine_tank_for_bottle_disinfection) ? $message->form->site_confirmed->site_assessment->bottle_washing_area->bottle_washing_area->chlorine_tank_for_bottle_disinfection : ($data->bottle_washing_area_chlorine_tank ?? null);
                        $ass->bottle_washing_area_disinfection_bottle_shelf_or_table_storage = $this->normalizeNumberField(!empty($message->form->site_confirmed->site_assessment->bottle_washing_area->bottle_washing_area->disinfection_bottle_shelf_or_table_storage) ? $message->form->site_confirmed->site_assessment->bottle_washing_area->bottle_washing_area->disinfection_bottle_shelf_or_table_storage : ($data->bottle_washing_area_disinfection_bottle_shelf_or_table_storage ?? null));
                        $ass->bottle_washing_area_rinsing_station = !empty($message->form->site_confirmed->site_assessment->bottle_washing_area->bottle_washing_area->rinsing_station) ? $message->form->site_confirmed->site_assessment->bottle_washing_area->bottle_washing_area->rinsing_station : ($data->bottle_washing_area_rinsing_station ?? null);
                        $ass->filling_area_filling_station = !empty($message->form->site_confirmed->site_assessment->filling_area->filling_station) ? $message->form->site_confirmed->site_assessment->filling_area->filling_station : ($data->filling_area_filling_station ?? null);
                        $ass->poster_for_om_poster_for_om = !empty($message->form->site_confirmed->site_assessment->poster_for_operation_and_maintenance->poster_for_om->poster_for_om) ? $message->form->site_confirmed->site_assessment->poster_for_operation_and_maintenance->poster_for_om->poster_for_om : ($data->poster_for_om_poster_for_om ?? null);
                        $ass->poster_for_om_date_change = $this->normalizeDateField($message->form->site_confirmed->site_assessment->poster_for_operation_and_maintenance->poster_for_om->date_of_initial_installation_or_last_change ?? null, $data->poster_for_om_date_change ?? null);
                        $ass->how_many_transportation_do_you_have =  !empty($message->form->site_confirmed->site_assessment->transportation_means->how_many_transportation_do_you_have) ? $message->form->site_confirmed->site_assessment->transportation_means->how_many_transportation_do_you_have : ($data->how_many_transportation_do_you_have ?? null);
                        $ass->type_of_afm = !empty($message->form->site_confirmed->site_assessment->{'pre-treatment'}->afm_resin->type_of_afm_resin) ? $message->form->site_confirmed->site_assessment->{'pre-treatment'}->afm_resin->type_of_afm_resin : ($data->type_of_afm ?? null);
                        $ass->afm_d_cm = !empty($message->form->site_confirmed->site_assessment->{'pre-treatment'}->afm_resin->d_cm) ? $message->form->site_confirmed->site_assessment->{'pre-treatment'}->afm_resin->d_cm : ($data->afm_d_cm ?? null);
                        $ass->afm_h_cm = !empty($message->form->site_confirmed->site_assessment->{'pre-treatment'}->afm_resin->h_cm) ? $message->form->site_confirmed->site_assessment->{'pre-treatment'}->afm_resin->h_cm : ($data->afm_h_cm ?? null);
                        $ass->afm_v_iter = !empty($message->form->site_confirmed->site_assessment->{'pre-treatment'}->afm_resin->v_liter) ? $message->form->site_confirmed->site_assessment->{'pre-treatment'}->afm_resin->v_liter : ($data->afm_v_iter ?? null);
                        $ass->afm_the_height_from_the_top_cm = !empty($message->form->site_confirmed->site_assessment->{'pre-treatment'}->afm_resin->the_height_from_the_top_of_the_tank_to_the_media_mm) ? $message->form->site_confirmed->site_assessment->{'pre-treatment'}->afm_resin->the_height_from_the_top_of_the_tank_to_the_media_mm : ($data->afm_the_height_from_the_top_cm ?? null);
                        $ass->afm_date_change_sand_filter_tank = !empty($message->form->site_confirmed->site_assessment->{'pre-treatment'}->afm_resin->date_of_media_initial_installation_or_last_change_sand_filter_tank) ? $message->form->site_confirmed->site_assessment->{'pre-treatment'}->afm_resin->date_of_media_initial_installation_or_last_change_sand_filter_tank : ($data->afm_date_change_sand_filter_tank ?? null);
                        $ass->type_of_Zmag = !empty($message->form->site_confirmed->site_assessment->{'pre-treatment'}->zmag->type_of_zmag) ? $message->form->site_confirmed->site_assessment->{'pre-treatment'}->zmag->type_of_zmag : ($data->type_of_Zmag ?? null);
                        $ass->zmag_d_cm = !empty($message->form->site_confirmed->site_assessment->{'pre-treatment'}->zmag->d_cm) ? $message->form->site_confirmed->site_assessment->{'pre-treatment'}->zmag->d_cm : ($data->zmag_d_cm ?? null);
                        $ass->zmag_h_cm = !empty($message->form->site_confirmed->site_assessment->{'pre-treatment'}->zmag->h_cm) ? $message->form->site_confirmed->site_assessment->{'pre-treatment'}->zmag->h_cm : ($data->zmag_h_cm ?? null);
                        $ass->zmag_v_iter = !empty($message->form->site_confirmed->site_assessment->{'pre-treatment'}->zmag->v_liter) ? $message->form->site_confirmed->site_assessment->{'pre-treatment'}->zmag->v_liter : ($data->zmag_v_iter ?? null);
                        $ass->zmag_the_height_from_the_top_cm = !empty($message->form->site_confirmed->site_assessment->{'pre-treatment'}->zmag->the_height_from_the_top_of_the_tank_to_the_media_mm) ? $message->form->site_confirmed->site_assessment->{'pre-treatment'}->zmag->the_height_from_the_top_of_the_tank_to_the_media_mm : ($data->zmag_the_height_from_the_top_cm ?? null);
                        $ass->zmag_date_change_sand_filter_tank = !empty($message->form->site_confirmed->site_assessment->{'pre-treatment'}->zmag->date_of_media_initial_installation_or_last_change_sand_filter_tank) ? $message->form->site_confirmed->site_assessment->{'pre-treatment'}->zmag->date_of_media_initial_installation_or_last_change_sand_filter_tank : ($data->zmag_date_change_sand_filter_tank ?? null);
                        $ass->type_of_sand_filter_and_Zmag_tank = !empty($message->form->site_confirmed->site_assessment->{'pre-treatment'}->sand__zmax->type_of_sand_and_zmax) ? $message->form->site_confirmed->site_assessment->{'pre-treatment'}->sand__zmax->type_of_sand_and_zmax : ($data->type_of_sand_filter_and_Zmag_tank ?? null);
                        $ass->sand_filter_and_zmag_d_cm = !empty($message->form->site_confirmed->site_assessment->{'pre-treatment'}->sand__zmax->h_cm) ? $message->form->site_confirmed->site_assessment->{'pre-treatment'}->sand__zmax->h_cm : ($data->sand_filter_and_zmag_d_cm ?? null);
                        $ass->sand_filter_and_zmag_h_cm = !empty($message->form->site_confirmed->site_assessment->{'pre-treatment'}->sand__zmax->d_cm) ? $message->form->site_confirmed->site_assessment->{'pre-treatment'}->sand__zmax->d_cm : ($data->sand_filter_and_zmag_h_cm ?? null);
                        $ass->sand_filter_and_zmag_v_iter = !empty($message->form->site_confirmed->site_assessment->{'pre-treatment'}->sand__zmax->v_liter) ? $message->form->site_confirmed->site_assessment->{'pre-treatment'}->sand__zmax->v_liter : ($data->sand_filter_and_zmag_v_iter ?? null);
                        $ass->sand_filter_and_zmag_the_height_from_the_top_cm = !empty($message->form->site_confirmed->site_assessment->{'pre-treatment'}->sand__zmax->the_height_from_the_top_of_the_tank_to_the_media_mm) ? $message->form->site_confirmed->site_assessment->{'pre-treatment'}->sand__zmax->the_height_from_the_top_of_the_tank_to_the_media_mm : ($data->sand_filter_and_zmag_the_height_from_the_top_cm ?? null);
                        $ass->sand_filter_and_zmag_date_change_sand_filter_tank = $this->normalizeDateField($message->form->site_confirmed->site_assessment->{'pre-treatment'}->sand__zmax->date_of_media_initial_installation_or_last_change_sand_filter_tank_and_zmax ?? null, $data->sand_filter_and_zmag_date_change_sand_filter_tank ?? null);
                        $transport = $message->form->site_confirmed->site_assessment->transportation_means->how_many_transportation_do_you_have ?? 0;
                        //dd($transport);

                        if (!empty($transport) && (int)$transport == 1) {
                            // Prepare the data to be inserted
                            $insertData = [
                                'site' => Str::ucfirst($message->form->site_confirmed->basic_information->site),
                                'transportation_type' => $message->form->site_confirmed->site_assessment->transportation_means->transportation->transportation->what_is_your_transportation,
                                'condition_of_transportation' => $message->form->site_confirmed->site_assessment->transportation_means->transportation->transportation->how_is_the_condition_of_transportation,
                                'condition_of_trolley' => $message->form->site_confirmed->site_assessment->transportation_means->transportation->transportation->how_is_the_condition_of_trolley,
                                'purchased_date' => $message->form->site_confirmed->site_assessment->transportation_means->transportation->transportation->purchased_date,
                            ];
                            TransportationAssessment::create($insertData);
                        } else if (!empty($transport) && (int)$transport > 1) {
                            if ($transport) {
                                foreach ($message->form->site_confirmed->site_assessment->transportation_means->transportation as $transportation) {
                                    // Extract data from the transportation array
                                    $siteId = Str::ucfirst($message->form->site_confirmed->basic_information->site);
                                    $transportationType = $transportation->transportation->what_is_your_transportation ?? null;
                                    $conditionOfTransportation = $transportation->transportation->how_is_the_condition_of_transportation ?? null;
                                    $conditionOfTrolley = $transportation->transportation->how_is_the_condition_of_trolley ?? null;
                                    $purchasedDate = $transportation->transportation->purchased_date;
                                    TransportationAssessment::insert([
                                        'site' => $siteId,
                                        'transportation_type' => $transportationType,
                                        'condition_of_transportation' => $conditionOfTransportation,
                                        'condition_of_trolley' => $conditionOfTrolley,
                                        'purchased_date' => $purchasedDate,
                                    ]);
                                }
                            }
                        }
                        $ass->transportation_type = "just replace data";
                    } else {
                        $ass->which_part_do_you_want_to_modify =  $message->form->site_confirmed->which_part_do_you_want_to_modify ?? null;
                        $ass->main_source_of_water = $message->form->site_confirmed->site_assessment->water_source->what_is_main_source_of_water ?? null;
                        $ass->main_source_of_electricity = $message->form->site_confirmed->site_assessment->water_source->what_is_main_source_of_electricity ?? null;
                        $ass->second_source_of_water = $message->form->site_confirmed->site_assessment->water_source->what_is_second_source_of_water ?? null;
                        $ass->electric_cabinet = $message->form->site_confirmed->site_assessment->water_source->electric_cabinet ?? null;
                        $ass->initial_installation_or_last_change = $message->form->site_confirmed->site_assessment->water_source->date_of_initial_installation_or_last_change ?? null;
                        $ass->ground_cable = $message->form->site_confirmed->site_assessment->water_source->ground_cable ?? null;
                        $ass->stabilizer = $message->form->site_confirmed->site_assessment->water_source->stabilizer ?? null;
                        $ass->last_change_stabilizer = $message->form->site_confirmed->site_assessment->water_source->date_of_initial_installation_or_last_change_stabilizer ?? null;
                        $ass->solar_panel = $message->form->site_confirmed->site_assessment->solar_panel_part->solar_panel ?? null;
                        $ass->date_installation_solar_panel = $message->form->site_confirmed->site_assessment->solar_panel_part->date_of_initial_installation_or_last_change_solar ?? null;
                        $ass->solar_charge_controller = $message->form->site_confirmed->site_assessment->solar_panel_part->solar_charge_controller ?? null;
                        $ass->date_change_solar_charge_controller = $message->form->site_confirmed->site_assessment->solar_panel_part->date_of_initial_installation_or_last_change_solar_charge_controller ?? null;
                        $ass->condition_batteries = $message->form->site_confirmed->site_assessment->solar_panel_part->condition_batteries ?? null;
                        $ass->date_last_change_batteries = $message->form->site_confirmed->site_assessment->solar_panel_part->date_of_initial_installation_or_last_change_batteries ?? null;
                        $ass->condition_inverter_dc_to_ac = $message->form->site_confirmed->site_assessment->solar_panel_part->condition_inverter_dc_to_ac ?? null;
                        $ass->date_change_inverter = $message->form->site_confirmed->site_assessment->solar_panel_part->date_of_initial_installation_or_last_change_inverter ?? null;
                        $ass->pre_treatment_process_1 = $message->form->site_confirmed->site_assessment->{'pre-treatment'}->{'pre-treatment_process_flow_chart_-_start_from_the_raw_water_tank_to_pre-tre'}->process_number_1 ?? null;
                        $ass->pre_treatment_process_2 = $message->form->site_confirmed->site_assessment->{'pre-treatment'}->{'pre-treatment_process_flow_chart_-_start_from_the_raw_water_tank_to_pre-tre'}->number_2 ?? null;
                        $ass->pre_treatment_process_3 = $message->form->site_confirmed->site_assessment->{'pre-treatment'}->{'pre-treatment_process_flow_chart_-_start_from_the_raw_water_tank_to_pre-tre'}->number_3 ?? null;
                        $ass->pre_treatment_process_4 = $message->form->site_confirmed->site_assessment->{'pre-treatment'}->{'pre-treatment_process_flow_chart_-_start_from_the_raw_water_tank_to_pre-tre'}->number_4 ?? null;
                        $ass->pre_treatment_process_5 = $message->form->site_confirmed->site_assessment->{'pre-treatment'}->{'pre-treatment_process_flow_chart_-_start_from_the_raw_water_tank_to_pre-tre'}->number_5 ?? null;
                        $ass->pre_treatment_process_6 = $message->form->site_confirmed->site_assessment->{'pre-treatment'}->{'pre-treatment_process_flow_chart_-_start_from_the_raw_water_tank_to_pre-tre'}->number_6 ?? null;
                        $ass->pre_treatment_process_7 = $message->form->site_confirmed->site_assessment->{'pre-treatment'}->{'pre-treatment_process_flow_chart_-_start_from_the_raw_water_tank_to_pre-tre'}->number_7 ?? null;
                        $ass->type_of_raw_water_tank = $message->form->site_confirmed->site_assessment->{'pre-treatment'}->raw_water_tank->type_of_water_tank ?? null;
                        $ass->raw_water_tank_h_cm = $this->normalizeNumberField($message->form->site_confirmed->site_assessment->{'pre-treatment'}->raw_water_tank->h_cm ?? null);
                        $ass->raw_water_tank_d_cm = $this->normalizeNumberField($message->form->site_confirmed->site_assessment->{'pre-treatment'}->raw_water_tank->d_cm ?? null);
                        $ass->raw_water_tank_v_liter = $this->normalizeNumberField($message->form->site_confirmed->site_assessment->{'pre-treatment'}->raw_water_tank->v_liter ?? null);
                        $ass->type_of_sand_filter_tank = $message->form->site_confirmed->site_assessment->{'pre-treatment'}->sand_filter_tank->type_of_sand_filter_tank ?? null;
                        $ass->sand_filter_tank_h_cm = $this->normalizeNumberField($message->form->site_confirmed->site_assessment->{'pre-treatment'}->sand_filter_tank->h_cm ?? null);
                        $ass->sand_filter_tank_d_cm = $this->normalizeNumberField($message->form->site_confirmed->site_assessment->{'pre-treatment'}->sand_filter_tank->d_cm ?? null);
                        $ass->sand_filter_tank_v_liter = $this->normalizeNumberField($message->form->site_confirmed->site_assessment->{'pre-treatment'}->sand_filter_tank->v_liter ?? null);
                        $ass->sand_filter_tank__height_from_the_top_cm = $this->normalizeNumberField($message->form->site_confirmed->site_assessment->{'pre-treatment'}->sand_filter_tank->the_height_from_the_top_of_the_tank_to_the_media_mm ?? null);
                        $ass->date_change_sand_filter_tank = $message->form->site_confirmed->site_assessment->{'pre-treatment'}->sand_filter_tank->date_of_media_initial_installation_or_last_change_sand_filter_tank ?? null;
                        $ass->type_of_ac_filter_tank = $message->form->site_confirmed->site_assessment->{'pre-treatment'}->ac_filter_tank->type_of_ac_filter_tank ?? null;
                        $ass->ac_filter_tank_h_cm = $this->normalizeNumberField($message->form->site_confirmed->site_assessment->{'pre-treatment'}->ac_filter_tank->h_cm ?? null);
                        $ass->ac_filter_tank_d_cm = $this->normalizeNumberField($message->form->site_confirmed->site_assessment->{'pre-treatment'}->ac_filter_tank->d_cm ?? null);
                        $ass->ac_filter_tank_v_liter = $this->normalizeNumberField($message->form->site_confirmed->site_assessment->{'pre-treatment'}->ac_filter_tank->v_m ?? null);
                        $ass->ac_filter_tank_media_height_from_the_top = $this->normalizeNumberField($message->form->site_confirmed->site_assessment->{'pre-treatment'}->ac_filter_tank->media_height_from_the_top_of_the_tank ?? null);
                        $ass->date_change_ac_filter_tank = $message->form->site_confirmed->site_assessment->{'pre-treatment'}->ac_filter_tank->date_of_media_initial_installation_or_last_change_ac_filter_tank ?? null;
                        $ass->type_of_resin_filter_tank = $message->form->site_confirmed->site_assessment->{'pre-treatment'}->resin_filter_tank->type_of_resin_filter_tank ?? null;
                        $ass->resin_filter_tank_h_cm = $this->normalizeNumberField($message->form->site_confirmed->site_assessment->{'pre-treatment'}->resin_filter_tank->h_cm ?? null);
                        $ass->resin_filter_tank_d_cm = $this->normalizeNumberField($message->form->site_confirmed->site_assessment->{'pre-treatment'}->resin_filter_tank->d_cm ?? null);
                        $ass->resin_filter_tank_v_liter = $this->normalizeNumberField($message->form->site_confirmed->site_assessment->{'pre-treatment'}->resin_filter_tank->v_m ?? null);
                        $ass->resin_filter_tank_media_height_from_the_top = $this->normalizeNumberField($message->form->site_confirmed->site_assessment->{'pre-treatment'}->resin_filter_tank->media_height_from_the_top_of_the_tank ?? null);
                        $ass->date_change_resin_filter_tank = $message->form->site_confirmed->site_assessment->{'pre-treatment'}->resin_filter_tank->date_of_media_initial_installation_or_last_change_resin_filter_tank ?? null;
                        $ass->type_of_clear_water_tank = $message->form->site_confirmed->site_assessment->{'pre-treatment'}->clear_water_tank->type_of_clear_water_tank ?? null;
                        $ass->clear_water_tank_h_cm = $this->normalizeNumberField($message->form->site_confirmed->site_assessment->{'pre-treatment'}->clear_water_tank->h_cm ?? null);
                        $ass->clear_water_tank_d_cm = $this->normalizeNumberField($message->form->site_confirmed->site_assessment->{'pre-treatment'}->clear_water_tank->d_cm ?? null);
                        $ass->clear_water_tank_v_liter = $this->normalizeNumberField($message->form->site_confirmed->site_assessment->{'pre-treatment'}->clear_water_tank->v_m ?? null);
                        $ass->flocculation_and_coagulation_process = $message->form->site_confirmed->site_assessment->{'pre-treatment'}->flocculation_and_coagulation_process->flocculation_and_coagulation_process ?? null;
                        $ass->reverse_osmose = $message->form->site_confirmed->site_assessment->{'pre-treatment'}->reverse_osmose->reverse_osmose ?? null;
                        $ass->date_change_reverse_osmose = $message->form->site_confirmed->site_assessment->{'pre-treatment'}->reverse_osmose->date_of_initial_installation_or_last_change_ro ?? null;
                        $ass->ultrafiltration = $message->form->site_confirmed->site_assessment->{'pre-treatment'}->ultrafiltration->ultrafiltration ?? null;
                        $ass->date_change_ultrafiltration = $message->form->site_confirmed->site_assessment->{'pre-treatment'}->ultrafiltration->date_of_initial_installation_or_last_change_ultrafiltration ?? null;
                        $ass->raw_water_pump = $message->form->site_confirmed->site_assessment->{'pre-treatment'}->raw_water_pump->raw_water_pump ?? null;
                        $ass->raw_water_pump_maximum_flow = $this->normalizeNumberField($message->form->site_confirmed->site_assessment->{'pre-treatment'}->raw_water_pump->{'manufacturer_specification_-_maximum_flow_qmax_raw_water_pump'} ?? null);
                        $ass->raw_water_pump_height_hmax = $this->normalizeNumberField($message->form->site_confirmed->site_assessment->{'pre-treatment'}->raw_water_pump->{'manufacturer_specification_-_maximum_height_hmax_raw_water_pump'} ?? null);
                        $ass->raw_water_pump_power = $this->normalizeNumberField($message->form->site_confirmed->site_assessment->{'pre-treatment'}->raw_water_pump->{'manufacturer_specification_-_power_raw_water_pump'} ?? null);
                        $ass->back_wash_pump = $message->form->site_confirmed->site_assessment->{'pre-treatment'}->back_wash_pump->back_wash_pump ?? null;
                        $ass->back_wash_pump_flow_qmax = $this->normalizeNumberField($message->form->site_confirmed->site_assessment->{'pre-treatment'}->back_wash_pump->{'manufacturer_specification_-_maximum_flow_qmax_back_wash_pump'} ?? null);
                        $ass->back_wash_pump_height_hmax = $this->normalizeNumberField($message->form->site_confirmed->site_assessment->{'pre-treatment'}->back_wash_pump->{'manufacturer_specification_-_maximum_height_hmax_back_wash_pump'} ?? null);
                        $ass->back_wash_pump_power = $this->normalizeNumberField($message->form->site_confirmed->site_assessment->{'pre-treatment'}->back_wash_pump->{'manufacturer_specification_-_power_back_wash_pump'} ?? null);
                        $ass->reverse_osmose_pump = $message->form->site_confirmed->site_assessment->{'pre-treatment'}->reverse_osmose_pump->reverse_osmose_pump ?? null;

                        $ass->reverse_osmose_pump_flow_qmax = $this->normalizeNumberField($message->form->site_confirmed->site_assessment->{'pre-treatment'}->reverse_osmose_pump->{'manufacturer_specification_-_maximum_flow_qmax_reverse_osmose_pump'} ?? null);
                        $ass->reverse_osmose_pump_height_hmax = $this->normalizeNumberField($message->form->site_confirmed->site_assessment->{'pre-treatment'}->reverse_osmose_pump->{'manufacturer_specification_-_maximum_height_hmax_reverse_osmose_pump'} ?? null);
                        $ass->reverse_osmose_pump_power = $this->normalizeNumberField($message->form->site_confirmed->site_assessment->{'pre-treatment'}->reverse_osmose_pump->{'manufacturer_specification_-_power_reverse_osmose_pump'} ?? null);
                        $ass->filter_50_item = $message->form->site_confirmed->site_assessment->final_treatment->filter_50->item_50m_filter ?? null;
                        $ass->date_change_filter_50 = $message->form->site_confirmed->site_assessment->final_treatment->filter_50->date_of_initial_installation_or_last_change_50m_filter ?? null;
                        $ass->filter_50_condition = $message->form->site_confirmed->site_assessment->final_treatment->filter_50->condition ?? null;
                        $ass->filter_10_item = $message->form->site_confirmed->site_assessment->final_treatment->filter_10->item_10m_filter ?? null;
                        $ass->date_change_10m_filter = $message->form->site_confirmed->site_assessment->final_treatment->filter_10->date_of_initial_installation_or_last_change_10m_filter ?? null;
                        $ass->filter_10_condition = $message->form->site_confirmed->site_assessment->final_treatment->filter_10->condition ?? null;
                        $ass->item_5m_filter = $message->form->site_confirmed->site_assessment->final_treatment->filter_5->item_5m_filter ?? null;
                        $ass->date_change_5m_filter = $message->form->site_confirmed->site_assessment->final_treatment->filter_5->date_of_initial_installation_or_last_change_5m_filter ?? null;
                        $ass->filter_5_condition = $message->form->site_confirmed->site_assessment->final_treatment->filter_5->condition ?? null;
                        $ass->item_1m_filter = $message->form->site_confirmed->site_assessment->final_treatment->filter_1->item_1m_filter ?? null;
                        $ass->date_change_1m_filter = $message->form->site_confirmed->site_assessment->final_treatment->filter_1->date_of_initial_installation_or_last_change_5m_filter ?? null;
                        $ass->filter_1_condition = $message->form->site_confirmed->site_assessment->final_treatment->filter_1->condition ?? null;
                        $ass->uv_lamp = $message->form->site_confirmed->site_assessment->final_treatment->uv_lamp->uv_lamp ?? null;
                        $ass->date_change_uv_lamp = $message->form->site_confirmed->site_assessment->final_treatment->uv_lamp->date_of_initial_installation_or_last_change_uv_lamp ?? null;
                        $ass->uv_lamp_condition = $message->form->site_confirmed->site_assessment->final_treatment->uv_lamp->condition ?? null;
                        $ass->uv_controller = $message->form->site_confirmed->site_assessment->final_treatment->uv_controller->uv_controller ?? null;
                        $ass->date_change_uv_controller = $message->form->site_confirmed->site_assessment->final_treatment->uv_controller->date_of_initial_installation_or_last_change_uv_controller ?? null;
                        $ass->uv_controller_condition = $message->form->site_confirmed->site_assessment->final_treatment->uv_controller->condition ?? null;
                        $ass->uv_ballast = $message->form->site_confirmed->site_assessment->final_treatment->uv_ballast->uv_ballast ?? null;
                        $ass->date_change_uv_ballast = $message->form->site_confirmed->site_assessment->final_treatment->uv_ballast->date_of_initial_installation_or_last_change_uv_ballast ?? null;
                        $ass->uv_ballast_condition = $message->form->site_confirmed->site_assessment->final_treatment->uv_ballast->condition ?? null;
                        $ass->uv_sensor = $message->form->site_confirmed->site_assessment->final_treatment->uv_sensor->uv_sensor ?? null;
                        $ass->date_change_uv_sensor = $message->form->site_confirmed->site_assessment->final_treatment->uv_sensor->date_of_initial_installation_or_last_change_uv_sensor ?? null;
                        $ass->uv_sensor_condition = $message->form->site_confirmed->site_assessment->final_treatment->uv_sensor->condition ?? null;
                        $ass->l_tank_for_cip = $message->form->site_confirmed->site_assessment->final_treatment->l_tank_for_cip->l_tank_for_cip ?? null;
                        $ass->date_change_200l_tank_for_cip = $message->form->site_confirmed->site_assessment->final_treatment->l_tank_for_cip->date_of_initial_installation_or_last_change_200l_tank_for_cip ?? null;
                        $ass->l_tank_for_cip_condition = $message->form->site_confirmed->site_assessment->final_treatment->l_tank_for_cip->condition ?? null;
                        $ass->micro_filter_pump = $message->form->site_confirmed->site_assessment->final_treatment->{'micro-filter_pump'}->{'micro-filter_pump'} ?? null;
                        $ass->micro_filter_pump_maximum_flow_qmax_lpm = $this->normalizeNumberField($message->form->site_confirmed->site_assessment->final_treatment->{'micro-filter_pump'}->{'manufacturer_specification_-_maximum_flow_qmax_lpm'} ?? null);
                        $ass->micro_filter_pump_maximum_height_hmax_m = $this->normalizeNumberField($message->form->site_confirmed->site_assessment->final_treatment->{'micro-filter_pump'}->{'manufacturer_specification_-_maximum_height_hmax_m'} ?? null);
                        $ass->micro_filter_pump_power_kwhp = $this->normalizeNumberField($message->form->site_confirmed->site_assessment->final_treatment->{'micro-filter_pump'}->{'manufacturer_specification_-_power_kwhp'} ?? null);
                        $ass->micro_filter_pump_voltage_v = $this->normalizeNumberField($message->form->site_confirmed->site_assessment->final_treatment->{'micro-filter_pump'}->voltage_v ?? null);
                        $ass->bottle_washing_area_dirty_bottle_shelf = $message->form->site_confirmed->site_assessment->bottle_washing_area->bottle_washing_area->dirty_bottle_shelf ?? null;
                        $ass->bottle_washing_area_washing_station = $message->form->site_confirmed->site_assessment->bottle_washing_area->bottle_washing_area->washing_station ?? null;
                        $ass->bottle_washing_area_specific_tank_for_lid_disinfection = $this->normalizeNumberField($message->form->site_confirmed->site_assessment->bottle_washing_area->bottle_washing_area->specific_tank_for_lid_disinfection ?? null);
                        $ass->bottle_washing_area_chlorine_tank = $message->form->site_confirmed->site_assessment->bottle_washing_area->bottle_washing_area->chlorine_tank_for_bottle_disinfection ?? null;
                        $ass->bottle_washing_area_disinfection_bottle_shelf_or_table_storage = $this->normalizeNumberField($message->form->site_confirmed->site_assessment->bottle_washing_area->bottle_washing_area->disinfection_bottle_shelf_or_table_storage ?? null);
                        $ass->bottle_washing_area_rinsing_station = $message->form->site_confirmed->site_assessment->bottle_washing_area->bottle_washing_area->rinsing_station ?? null;
                        $ass->filling_area_filling_station = $message->form->site_confirmed->site_assessment->filling_area->filling_station ?? null;
                        $ass->poster_for_om_poster_for_om = $message->form->site_confirmed->site_assessment->poster_for_operation_and_maintenance->poster_for_om->poster_for_om ?? null;
                        $ass->poster_for_om_date_change = $message->form->site_confirmed->site_assessment->poster_for_operation_and_maintenance->poster_for_om->date_of_initial_installation_or_last_change ?? null;
                        $ass->how_many_transportation_do_you_have = $this->normalizeNumberField($message->form->site_confirmed->site_assessment->transportation_means->how_many_transportation_do_you_have ?? null);

                        $ass->type_of_afm = $message->form->site_confirmed->site_assessment->{'pre-treatment'}->afm_resin->type_of_afm_resin ?? null;
                        $ass->afm_d_cm = $message->form->site_confirmed->site_assessment->{'pre-treatment'}->afm_resin->d_cm ?? null;
                        $ass->afm_h_cm = $message->form->site_confirmed->site_assessment->{'pre-treatment'}->afm_resin->h_cm ?? null;
                        $ass->afm_v_iter = $message->form->site_confirmed->site_assessment->{'pre-treatment'}->afm_resin->v_liter ?? null;
                        $ass->afm_the_height_from_the_top_cm = $message->form->site_confirmed->site_assessment->{'pre-treatment'}->afm_resin->the_height_from_the_top_of_the_tank_to_the_media_mm ?? null;
                        $ass->afm_date_change_sand_filter_tank = $message->form->site_confirmed->site_assessment->{'pre-treatment'}->afm_resin->date_of_media_initial_installation_or_last_change_sand_filter_tank ?? null;
                        $ass->type_of_Zmag = $message->form->site_confirmed->site_assessment->{'pre-treatment'}->zmag->type_of_zmag ?? null;
                        $ass->zmag_d_cm = $message->form->site_confirmed->site_assessment->{'pre-treatment'}->zmag->d_cm ?? null;
                        $ass->zmag_h_cm = $message->form->site_confirmed->site_assessment->{'pre-treatment'}->zmag->h_cm ?? null;
                        $ass->zmag_v_iter = $message->form->site_confirmed->site_assessment->{'pre-treatment'}->zmag->v_liter ?? null;
                        $ass->zmag_the_height_from_the_top_cm = $message->form->site_confirmed->site_assessment->{'pre-treatment'}->zmag->the_height_from_the_top_of_the_tank_to_the_media_mm ?? null;
                        $ass->zmag_date_change_sand_filter_tank = $message->form->site_confirmed->site_assessment->{'pre-treatment'}->zmag->date_of_media_initial_installation_or_last_change_sand_filter_tank ?? null;
                        $ass->type_of_sand_filter_and_Zmag_tank = $message->form->site_confirmed->site_assessment->{'pre-treatment'}->sand__zmax->type_of_sand_and_zmax ?? null;
                        $ass->sand_filter_and_zmag_d_cm = $message->form->site_confirmed->site_assessment->{'pre-treatment'}->sand__zmax->h_cm ?? null;
                        $ass->sand_filter_and_zmag_h_cm = $message->form->site_confirmed->site_assessment->{'pre-treatment'}->sand__zmax->d_cm ?? null;
                        $ass->sand_filter_and_zmag_v_iter = $message->form->site_confirmed->site_assessment->{'pre-treatment'}->sand__zmax->v_liter ?? null;
                        $ass->sand_filter_and_zmag_the_height_from_the_top_cm = $message->form->site_confirmed->site_assessment->{'pre-treatment'}->sand__zmax->the_height_from_the_top_of_the_tank_to_the_media_mm ?? null;
                        $ass->sand_filter_and_zmag_date_change_sand_filter_tank = $message->form->site_confirmed->site_assessment->{'pre-treatment'}->sand__zmax->date_of_media_initial_installation_or_last_change_sand_filter_tank_and_zmax ?? null;
                        $transport = $message->form->site_confirmed->site_assessment->transportation_means->how_many_transportation_do_you_have ?? 0;
                        if (!empty($transport) && (int)$transport == 1) {
                            // Prepare the data to be inserted
                            $insertData = [
                                'site' => Str::ucfirst($message->form->site_confirmed->basic_information->site),
                                'transportation_type' => $message->form->site_confirmed->site_assessment->transportation_means->transportation->transportation->what_is_your_transportation ?? null,
                                'condition_of_transportation' => $message->form->site_confirmed->site_assessment->transportation_means->transportation->transportation->how_is_the_condition_of_transportation ?? null,
                                'condition_of_trolley' => $message->form->site_confirmed->site_assessment->transportation_means->transportation->transportation->how_is_the_condition_of_trolley ?? null,
                                'purchased_date' => $message->form->site_confirmed->site_assessment->transportation_means->transportation->transportation->purchased_date,
                            ];
                            TransportationAssessment::create($insertData);
                        } else if (!empty($transport) && (int)$transport > 1) {
                            if ($transport) {
                                foreach ($message->form->site_confirmed->site_assessment->transportation_means->transportation as $transportation) {
                                    // Extract data from the transportation array
                                    $siteId = Str::ucfirst($message->form->site_confirmed->basic_information->site);
                                    $transportationType = $transportation->transportation->what_is_your_transportation ?? null;
                                    $conditionOfTransportation = $transportation->transportation->how_is_the_condition_of_transportation ?? null;
                                    $conditionOfTrolley = $transportation->transportation->how_is_the_condition_of_trolley ?? null;
                                    $purchasedDate = $transportation->transportation->purchased_date;
                                    TransportationAssessment::insert([
                                        'site' => $siteId,
                                        'transportation_type' => $transportationType,
                                        'condition_of_transportation' => $conditionOfTransportation,
                                        'condition_of_trolley' => $conditionOfTrolley,
                                        'purchased_date' => $purchasedDate,
                                    ]);
                                }
                            }
                        }
                        $ass->transportation_type = "just replace data";
                    }
                    $ass->save();
                }
                // check routine check form
                if ($message->form->site_confirmed->which_form_do_you_want_to_do == "routine_check") {
                    //dd($message->form->site_confirmed->routine_check->{'pre-treatment_operation_and_maintenance'}->sand_filter_tank->condition_of_sand_filter_tank);
                    $routin = new Rountine();
                    $routin->number = "1000";
                    $routin->formid = $message->id;
                    $routin->site = Str::ucfirst($message->form->site_confirmed->basic_information->site);
                    $routin->technician = $message->form->site_confirmed->basic_information->technician_name;
                    $routin->date = $message->form->site_confirmed->basic_information->date;
                    $routin->main_person_the_water_kiosk_with_you = $message->form->site_confirmed->basic_information->who_is_in_main_person_the_water_kiosk_with_you ?? null;
                    $routin->form_do_you_want_to_do = $message->form->site_confirmed->which_form_do_you_want_to_do ?? null;
                    $routin->condition_of_raw_water_tank = $message->form->site_confirmed->routine_check->{'pre-treatment_operation_and_maintenance'}->raw_water_tank->condition_of_raw_water_tank ?? null;
                    $routin->raw_water_tank_did_you_clean = $message->form->site_confirmed->routine_check->{'pre-treatment_operation_and_maintenance'}->raw_water_tank->did_you_clean_with_the_entrepreneur_today ?? null;
                    $routin->condition_of_sand_filter_tank = $message->form->site_confirmed->routine_check->{'pre-treatment_operation_and_maintenance'}->sand_filter_tank->condition_of_sand_filter_tank ?? null;
                    $routin->sand_filter_last_backwash_date = $message->form->site_confirmed->routine_check->{'pre-treatment_operation_and_maintenance'}->sand_filter_tank->last_backwash_date ?? null;
                    $routin->sand_filter_frequency_of_the_backwash = $message->form->site_confirmed->routine_check->{'pre-treatment_operation_and_maintenance'}->sand_filter_tank->frequency_of_the_backwash ?? null;
                    $routin->sand_filter_cleaning_and_backwash_done = $message->form->site_confirmed->routine_check->{'pre-treatment_operation_and_maintenance'}->sand_filter_tank->cleaning_and_backwash_done_on_site_with_the_entrepeneur ?? null;
                    $routin->condition_of_ac_filter_tank = $message->form->site_confirmed->routine_check->{'pre-treatment_operation_and_maintenance'}->ac_filter_tank->condition_of_ac_filter_tank ?? null;
                    $routin->ac_filter_last_backwash_date = $message->form->site_confirmed->routine_check->{'pre-treatment_operation_and_maintenance'}->ac_filter_tank->last_backwash_date ?? null;
                    $routin->ac_filter_frequency_of_the_backwash = $message->form->site_confirmed->routine_check->{'pre-treatment_operation_and_maintenance'}->ac_filter_tank->frequency_of_the_backwash ?? null;
                    $routin->ac_filter_last_regeneration_or_sterilization_date = $message->form->site_confirmed->routine_check->{'pre-treatment_operation_and_maintenance'}->ac_filter_tank->last_regeneration_or_sterilization_date ?? null;
                    $routin->ac_filter_cleaning_and_backwash_done = $message->form->site_confirmed->routine_check->{'pre-treatment_operation_and_maintenance'}->ac_filter_tank->cleaning_and_backwash_done_on_site_with_the_entrepeneur ?? null;
                    $routin->condition_of_resin_filter_tank = $message->form->site_confirmed->routine_check->{'pre-treatment_operation_and_maintenance'}->resin_filter_tank->condition_of_resin_filter_tank ?? null;
                    $routin->resin_filter_last_backwash_date = $message->form->site_confirmed->routine_check->{'pre-treatment_operation_and_maintenance'}->resin_filter_tank->last_backwash_date ?? null;
                    $routin->resin_filter_frequency_of_the_backwash = $message->form->site_confirmed->routine_check->{'pre-treatment_operation_and_maintenance'}->resin_filter_tank->frequency_of_the_backwash ?? null;
                    $routin->resin_filter_last_regeneration_or_sterilization_date = $message->form->site_confirmed->routine_check->{'pre-treatment_operation_and_maintenance'}->resin_filter_tank->last_regeneration_or_sterilization_date ?? null;
                    $routin->resin_filter_cleaning_and_backwash_done = $message->form->site_confirmed->routine_check->{'pre-treatment_operation_and_maintenance'}->resin_filter_tank->cleaning_and_backwash_done_on_site_with_the_entrepeneur ?? null;
                    $routin->condition_of_clear_water_tank = $message->form->site_confirmed->routine_check->{'pre-treatment_operation_and_maintenance'}->clear_water_tank->condition_of_clear_water_tank ?? null;
                    $routin->clear_water_tank_did_you_clean = $message->form->site_confirmed->routine_check->{'pre-treatment_operation_and_maintenance'}->clear_water_tank->did_you_clean_with_the_entrepreneur_today ?? null;
                    $routin->condition_of_ro = $message->form->site_confirmed->routine_check->{'pre-treatment_operation_and_maintenance'}->ro->condition_of_ro ?? null;
                    $routin->ro_last_backwash_date = $message->form->site_confirmed->routine_check->{'pre-treatment_operation_and_maintenance'}->ro->last_backwash_date ?? null;
                    $routin->ro_frequently_of_the_backwash = $message->form->site_confirmed->routine_check->{'pre-treatment_operation_and_maintenance'}->ro->frequently_of_the_backwash ?? null;
                    $routin->ro_last_cip_date = $message->form->site_confirmed->routine_check->{'pre-treatment_operation_and_maintenance'}->ro->last_cip_date ?? null;
                    $routin->ro_cleaning_and_backwash_done_on_site = $message->form->site_confirmed->routine_check->{'pre-treatment_operation_and_maintenance'}->ro->cleaning_and_backwash_done_on_site_with_the_entrepeneur ?? null;
                    $routin->condition_of_ultrafiltration = $message->form->site_confirmed->routine_check->{'pre-treatment_operation_and_maintenance'}->ultrafiltration->condition_of_ultrafiltration ?? null;
                    $routin->ultrafiltration_last_backwash_date = $message->form->site_confirmed->routine_check->{'pre-treatment_operation_and_maintenance'}->ultrafiltration->last_backwash_date ?? null;
                    $routin->ultrafiltration_frequency_of_the_backwash = $message->form->site_confirmed->routine_check->{'pre-treatment_operation_and_maintenance'}->ultrafiltration->frequently_of_the_backwash ?? null;
                    $routin->ultrafiltration_last_regeneration_or_sterilization_date = $message->form->site_confirmed->routine_check->{'pre-treatment_operation_and_maintenance'}->ultrafiltration->last_regeneration_or_sterilization_date ?? null;
                    $routin->ultrafiltration_cleaning_and_backwash_done = $message->form->site_confirmed->routine_check->{'pre-treatment_operation_and_maintenance'}->ultrafiltration->cleaning_and_backwash_done_on_site_with_the_entrepeneur ?? null;
                    $routin->are_pre_treatment_pipes_leaking = $message->form->site_confirmed->routine_check->{'pre-treatment_operation_and_maintenance'}->{'pipe_network_of_the_pre-treatment'}->{'is_pre-treatment_pipes_are_leaking'} ?? null;
                    $routin->are_pre_treatment_valves_broken = $message->form->site_confirmed->routine_check->{'pre-treatment_operation_and_maintenance'}->{'pipe_network_of_the_pre-treatment'}->{'is_pre-treatment_valves_are_broken'} ?? null;
                    $routin->did_you_repair_pretreatment_on_site = $message->form->site_confirmed->routine_check->{'pre-treatment_operation_and_maintenance'}->{'pipe_network_of_the_pre-treatment'}->did_you_repair_it_on_site ?? null;
                    $routin->is_it_clean_in_front_of_kiosk = $message->form->site_confirmed->routine_check->hygiene->hygiene_outside_kiosk->is_it_clean_in_front_of_kiosk ?? null;
                    $routin->did_you_clean_front_of_kiosk_with_the_entrepreneur = $message->form->site_confirmed->routine_check->hygiene->hygiene_outside_kiosk->did_you_clean_with_the_entrepreneur_today ?? null;
                    $routin->please_take_a_picture_in_front_of_kiosk = $message->form->site_confirmed->routine_check->hygiene->hygiene_outside_kiosk->please_take_a_picture_in_front_of_kiosk ?? null;
                    $routin->is_it_clean_behind_the_kiosk = $message->form->site_confirmed->routine_check->hygiene->hygiene_outside_kiosk->is_it_clean_behind_the_kiosk ?? null;
                    $routin->did_you_clean_behind_the_kiosk_with_the_entrepreneur = $message->form->site_confirmed->routine_check->hygiene->hygiene_outside_kiosk->did_you_clean_behind_with_the_entrepreneur_today ?? null;
                    $routin->take_a_picture_behind_kiosk = $message->form->site_confirmed->routine_check->hygiene->hygiene_outside_kiosk->take_a_picture_behind_kiosk ?? null;
                    $routin->is_the_pre_treatment_clean = $message->form->site_confirmed->routine_check->hygiene->hygiene_inside_kiosk->{'is_the_pre-treatment_clean'} ?? null;
                    $routin->did_you_clean_pre_treatment_with_the_entrepreneur = $message->form->site_confirmed->routine_check->hygiene->hygiene_inside_kiosk->{'did_you_clean_pre-treatment_with_the_entrepreneur_today'} ?? null;
                    $routin->please_take_a_picture_of_pre_treatment = $message->form->site_confirmed->routine_check->hygiene->hygiene_inside_kiosk->{'please_take_a_picture_of_pre-treatment'} ?? null;
                    $routin->is_it_clean_of_washing_bottle_area = $message->form->site_confirmed->routine_check->hygiene->hygiene_inside_kiosk->is_it_clean_of_washing_bottle_area ?? null;
                    $routin->did_you_clean_washing_bottle_area_with_the_entrepreneur = $message->form->site_confirmed->routine_check->hygiene->hygiene_inside_kiosk->cleaning_washing_bottle_area_on_site_with_the_entrepeneur ?? null;
                    $routin->take_a_photo_of_washing_bottle_area = $message->form->site_confirmed->routine_check->hygiene->hygiene_inside_kiosk->take_a_photo_of_washing_bottle_area ?? null;
                    $routin->is_it_clean_bottling_area = $message->form->site_confirmed->routine_check->hygiene->hygiene_inside_kiosk->is_it_clean_bottling_area ?? null;
                    $routin->did_you_clean_cleaning_bottle_area_with_the_entrepreneur = $message->form->site_confirmed->routine_check->hygiene->hygiene_inside_kiosk->did_you_clean_cleaning_bottle_area_with_the_entrepreneur_today ?? null;
                    $routin->take_a_picture_of_bottling_area = $message->form->site_confirmed->routine_check->hygiene->hygiene_inside_kiosk->take_a_picture_of_bottling_area ?? null;
                    $routin->is_kiosk_flooding_during_rainy_season = $message->form->site_confirmed->routine_check->hygiene->other_specification->is_kiosk_flooding_during_rainy_season ?? null;
                    $routin->items_stored_no_linked_with_ts_in_or_nearby = $message->form->site_confirmed->routine_check->hygiene->other_specification->items_stored_no_linked_with_ts_in_or_nearby ?? null;
                    $routin->chlorine_bucket_for_bottle_disinfection = $message->form->site_confirmed->routine_check->hygiene->chlorine->chlorine_bucket_for_bottle_disinfection ?? null;
                    $routin->chlorine_bucket_for_caps_disinfection = $message->form->site_confirmed->routine_check->hygiene->chlorine->chlorine_bucket_for_caps_disinfection ?? null;
                    $routin->weighing_scale_2_kg = $message->form->site_confirmed->routine_check->hygiene->chlorine->weighing_scale_2_kg ?? null;
                    $routin->measuring_spoon = $message->form->site_confirmed->routine_check->hygiene->chlorine->measuring_spoon ?? null;
                    $routin->conductivity_raw_water = $message->form->site_confirmed->routine_check->drinking_water_quality->conductivity->raw_water ?? null;
                    $routin->conductivity_drinking_water = $message->form->site_confirmed->routine_check->drinking_water_quality->conductivity->drinking_water ?? null;
                    $routin->pH_raw_water = $message->form->site_confirmed->routine_check->drinking_water_quality->ph->raw_water ?? null;
                    $routin->pH_drinking_water = $message->form->site_confirmed->routine_check->drinking_water_quality->ph->drinking_water ?? null;
                    $routin->TDS_raw_water = $message->form->site_confirmed->routine_check->drinking_water_quality->tds->raw_water ?? null;
                    $routin->TDS_drinking_water = $message->form->site_confirmed->routine_check->drinking_water_quality->tds->drinking_water ?? null;
                    $routin->Turbidity_raw_water = $message->form->site_confirmed->routine_check->drinking_water_quality->turbidity->raw_water ?? null;
                    $routin->Turbidity_drinking_water = $message->form->site_confirmed->routine_check->drinking_water_quality->turbidity->drinking_water ?? null;
                    $routin->what_is_taste_of_the_drinking_water = $message->form->site_confirmed->routine_check->drinking_water_quality->taste_of_the_drinking_water->what_is_taste_of_the_drinking_water ?? null;
                    $routin->maximum_flow_of_the_micro_filtration_pump = $message->form->site_confirmed->routine_check->final_treatment_operation_and_maintenance->{'maximum_flow_of_the_micro-filtration_pump_when_all_taps_are_opened_to_measu'} ?? null;
                    $routin->set_the_maximum_flow_below_40_lpm = $message->form->site_confirmed->routine_check->final_treatment_operation_and_maintenance->set_the_maximum_flow_below_40_lpm ?? null;
                    $routin->uv_intensity = $message->from->site_confirmed->routine_check->final_treatment_operation_and_maintenance->uv_lamp->uv_intensity ?? null;
                    $routin->uv_lamp_number_of_hours = $message->form->site_confirmed->routine_check->final_treatment_operation_and_maintenance->uv_lamp->number_of_hours ?? null;
                    $routin->last_cleaning_of_the_uv_quartz_and_sensor = $message->form->site_confirmed->routine_check->final_treatment_operation_and_maintenance->uv_lamp->last_cleaning_of_the_uv_quartz_and_sensor ?? null;
                    $routin->uv_quartz_and_sensor_cleaning_done_on_site_with_the_entrepeneur = $message->form->site_confirmed->routine_check->final_treatment_operation_and_maintenance->uv_lamp->uv_quartz_and_sensor_cleaning_done_on_site_with_the_entrepeneur ?? null;
                    $routin->condition_of_50m_filter = $message->form->site_confirmed->routine_check->final_treatment_operation_and_maintenance->filter_50m->condition_of_50m_filter ?? null;
                    $routin->last_cartridge_change_50m_filter = $message->form->site_confirmed->routine_check->final_treatment_operation_and_maintenance->filter_50m->last_cartridge_change ?? null;
                    $routin->replace_the_cartridge_filters_done_with_50m_filter = $message->form->site_confirmed->routine_check->final_treatment_operation_and_maintenance->filter_50m->replace_the_cartridge_filters_done_on_site_with_the_entrepeneur ?? null;
                    $routin->condition_of_10m_filter = $message->form->site_confirmed->routine_check->final_treatment_operation_and_maintenance->filter_10m->condition_of_10m_filter ?? null;
                    $routin->last_cartridge_change_10m_filter = $message->form->site_confirmed->routine_check->final_treatment_operation_and_maintenance->filter_10m->last_cartridge_change ?? null;
                    $routin->replace_the_cartridge_filters_done_with_10m_filter = $message->form->site_confirmed->routine_check->final_treatment_operation_and_maintenance->filter_10m->replace_the_cartridge_filters_done_on_site_with_the_entrepeneur ?? null;
                    $routin->condition_of_5m_filter = $message->form->site_confirmed->routine_check->final_treatment_operation_and_maintenance->filter_5m->condition_of_5m_filter ?? null;
                    $routin->last_cartridge_change_5m_filter = $message->form->site_confirmed->routine_check->final_treatment_operation_and_maintenance->filter_5m->last_cartridge_change ?? null;
                    $routin->replace_the_cartridge_filters_done_with_5m_filter = $message->form->site_confirmed->routine_check->final_treatment_operation_and_maintenance->filter_5m->replace_the_cartridge_filters_done_on_site_with_the_entrepeneur ?? null;
                    $routin->condition_of_1m_filter = $message->form->site_confirmed->routine_check->final_treatment_operation_and_maintenance->filter_1m->condition_of_1m_filter ?? null;
                    $routin->last_cartridge_change_1m_filter = $message->form->site_confirmed->site_assessment->final_treatment->filter_5->item_5m_filter ?? null;
                    $routin->replace_the_cartridge_filters_done_with_1m_filter = $message->form->site_confirmed->routine_check->final_treatment_operation_and_maintenance->filter_1m->last_cartridge_change ?? null;
                    $routin->is_it_possible_to_perform_cip_on_pipes = $message->form->form->site_confirmed->routine_check->final_treatment_operation_and_maintenance->cip->is_it_possible_to_perform_cip_on_pipes ?? null;
                    $routin->last_cip_date_on_pipes = $message->form->site_confirmed->routine_check->final_treatment_operation_and_maintenance->cip->last_cip_date ?? null;
                    $routin->frequency_of_the_cip_on_pipes = $message->form->site_confirmed->routine_check->final_treatment_operation_and_maintenance->cip->frequency_of_the_cip ?? null;
                    $routin->cip_done_on_pipes = $message->form->site_confirmed->routine_check->final_treatment_operation_and_maintenance->cip->cip_done_on_site_with_the_entrepeneur ?? null;
                    $routin->is_final_treatment_pipes_are_leaking = $message->form->site_confirmed->routine_check->final_treatment_operation_and_maintenance->pipe_network_of_the_final_treatment->{'is_final-treatment_pipes_are_leaking'} ?? null;
                    $routin->is_final_treatment_valves_are_broken = $message->form->site_confirmed->routine_check->final_treatment_operation_and_maintenance->pipe_network_of_the_final_treatment->{'is_final-treatment_valves_are_broken'} ?? null;
                    $routin->did_you_repair_it_on_site_valves = $message->form->site_confirmed->routine_check->final_treatment_operation_and_maintenance->pipe_network_of_the_final_treatment->did_you_repair_it_on_site ?? null;
                    $routin->condition_electrical_cabinet = $message->form->site_confirmed->routine_check->electricity->electric_cabinet->condition ?? null;
                    $routin->did_you_repair_it_on_site_electrical_cabinet = $message->form->site_confirmed->routine_check->electricity->electric_cabinet->did_you_repair_it_on_site ?? null;
                    $routin->condition_wiring = $message->form->site_confirmed->routine_check->electricity->wiring->wiring ?? null;
                    $routin->did_you_repair_it_on_site_wiring = $message->form->site_confirmed->routine_check->electricity->wiring->did_you_repair_it_on_site ?? null;
                    $routin->does_it_work_properly_micro_filtration_pump = $message->form->site_confirmed->routine_check->electricity->{'micro-filtration_pump'}->does_it_work_properly ?? null;
                    $routin->did_you_repair_it_on_site_micro_filtration_pump = $message->form->site_confirmed->routine_check->electricity->{'micro-filtration_pump'}->did_you_repair_it_on_site ?? null;
                    $routin->take_a_picture_micro_filtration = $message->form->site_confirmed->routine_check->electricity->{'micro-filtration_pump'}->take_a_picture ?? null;
                    $routin->does_it_work_properly_raw_water_pump = $message->form->site_confirmed->routine_check->electricity->raw_water_pump->does_it_work_properly ?? null;
                    $routin->did_you_repair_it_on_site_raw_water_pump = $message->form->site_confirmed->routine_check->electricity->raw_water_pump->did_you_repair_it_on_site ?? null;
                    $routin->take_a_picture_raw_water_pump = $message->form->site_confirmed->routine_check->electricity->raw_water_pump->take_a_picture ?? null;
                    $routin->is_there_any_float_switch = $message->form->site_confirmed->routine_check->electricity->float_switch->is_there_any_float_switch ?? null;
                    $routin->does_it_work_properly_float_witch = $message->form->site_confirmed->routine_check->electricity->float_switch->does_it_work_properly ?? null;
                    $routin->condition_solar = $message->form->site_confirmed->routine_check->electricity->solar_panel->condition ?? null;
                    $routin->cleaning_done_solar = $message->form->site_confirmed->routine_check->electricity->solar_panel->cleaning_done_on_site_with_the_entrepeneur ?? null;
                    $routin->condition_battery = $message->form->site_confirmed->routine_check->electricity->battery->condition ?? null;
                    $routin->works_capacity_in_hours_battery = $message->form->site_confirmed->routine_check->electricity->battery->works_capacity_in_hours ?? null;
                    $routin->is_the_entrepreneur_satisfied_with_teuksaats_services = $message->form->site_confirmed->routine_check->satisfaction->satisfication_from_entrepreneur->is_the_entrepreneur_satisfied_with_teuksaats_services ?? null;
                    $routin->are_beneficiaries_satisfied_with_the_taste_of_owe_water = $message->form->site_confirmed->routine_check->satisfaction->satisfication_from_entrepreneur->are_beneficiaries_satisfied_with_the_taste_of_owe_water ?? null;
                    $routin->comment = $message->form->site_confirmed->routine_check->satisfaction->satisfication_from_entrepreneur->comment ?? null;
                    $routin->save();
                }
            }
            // Insert form here
            if ($message->form->{'@name'} == "Sale Record Data") {
                if ($message->form->{'copy-1-of-site_name'}->which_form_do_you_want_to_do == "record_customer") {
                    $sale = new SaleTeam();
                    $sale->site = Str::ucfirst($message->form->{'copy-1-of-site_name'}->sale_customer->group_info->input_site_name);
                    $sale->sale_date = \Carbon\Carbon::parse($message->form->{'copy-1-of-site_name'}->sale_customer->group_info->sale_date);
                    $sale->sale_officer1 = $message->form->{'copy-1-of-site_name'}->sale_customer->group_info->name_first_sale_officer;
                    $sale->sale_officer2 = isset($message->form->{'copy-1-of-site_name'}->sale_customer->group_info->name_second_sale_officer) ? $message->form->{'copy-1-of-site_name'}->sale_customer->group_info->name_second_sale_officer : null;
                    $sale->sale_officer3 = isset($message->form->{'copy-1-of-site_name'}->sale_customer->group_info->name_third_sale_officer) ? $message->form->{'copy-1-of-site_name'}->sale_customer->group_info->name_third_sale_officer : null;
                    $sale->sale_officer4 = isset($message->form->{'copy-1-of-site_name'}->sale_customer->group_info->name_fourth_sale_officer) ? $message->form->{'copy-1-of-site_name'}->sale_customer->group_info->name_fourth_sale_officer : null;
                    $sale->customer = $message->form->{'copy-1-of-site_name'}->sale_customer->group_info->customer_name;
                    $sale->sex = $message->form->{'copy-1-of-site_name'}->sale_customer->group_info->sex;
                    $sale->sale_type = $message->form->{'copy-1-of-site_name'}->sale_customer->group_info->is_it_opening_site_or_intervention;
                    $sale->customer_type = $message->form->{'copy-1-of-site_name'}->sale_customer->group_info->customer_type;
                    $sale->village = $message->form->{'copy-1-of-site_name'}->sale_customer->group_info->village_name;
                    $sale->contact = $message->form->{'copy-1-of-site_name'}->sale_customer->group_info->contact;

                    $sale->drinking_water_type = isset($message->form->{'copy-1-of-site_name'}->sale_customer->group_info->what_are_you_drinking_nowday) ? $message->form->{'copy-1-of-site_name'}->sale_customer->group_info->what_are_you_drinking_nowday : null;
                    $sale->water_source = isset($message->form->{'copy-1-of-site_name'}->sale_customer->group_info->what_kind_of_water_source) ? $message->form->{'copy-1-of-site_name'}->sale_customer->group_info->what_kind_of_water_source : null;
                    $sale->water_type = isset($message->form->{'copy-1-of-site_name'}->sale_customer->group_info->what_kind_of_water) ? $message->form->{'copy-1-of-site_name'}->sale_customer->group_info->what_kind_of_water : null;

                    $sale->delivery_status = $message->form->{'copy-1-of-site_name'}->sale_customer->sell_info->delivery_status;
                    $sale->payment_type = $message->form->{'copy-1-of-site_name'}->sale_customer->sell_info->payment_type;
                    $sale->free = isset($message->form->{'copy-1-of-site_name'}->sale_customer->sell_info->free_bottle) ? $message->form->{'copy-1-of-site_name'}->sale_customer->sell_info->free_bottle : 0;
                    $sale->new_bottle = isset($message->form->{'copy-1-of-site_name'}->sale_customer->sell_info->new_bottle_sell) ? $message->form->{'copy-1-of-site_name'}->sale_customer->sell_info->new_bottle_sell : 0;
                    $sale->price_new_bottle = isset($message->form->{'copy-1-of-site_name'}->sale_customer->sell_info->price_new_bottle_sell) ? $message->form->{'copy-1-of-site_name'}->sale_customer->sell_info->price_new_bottle_sell : 0;
                    $sale->lending_bottle = isset($message->form->{'copy-1-of-site_name'}->sale_customer->sell_info->bottle_lending) ? $message->form->{'copy-1-of-site_name'}->sale_customer->sell_info->bottle_lending : 0;
                    $sale->price_lending_bottle = isset($message->form->{'copy-1-of-site_name'}->sale_customer->sell_info->price_lending_bottle) ? $message->form->{'copy-1-of-site_name'}->sale_customer->sell_info->price_lending_bottle : 0;
                    $sale->refill = isset($message->form->{'copy-1-of-site_name'}->sale_customer->sell_info->refill_bottle_number) ? $message->form->{'copy-1-of-site_name'}->sale_customer->sell_info->refill_bottle_number : 0;
                    $sale->price_refill = isset($message->form->{'copy-1-of-site_name'}->sale_customer->sell_info->price_refill_bottle) ? $message->form->{'copy-1-of-site_name'}->sale_customer->sell_info->price_refill_bottle : 0;
                    $sale->total_refill_sell = isset($message->form->{'copy-1-of-site_name'}->sale_customer->sell_info->total_refill_sell) ? $message->form->{'copy-1-of-site_name'}->sale_customer->sell_info->total_refill_sell : 0;
                    $sale->total_bottle_sell = isset($message->form->{'copy-1-of-site_name'}->sale_customer->sell_info->total_bottle_sell) ? $message->form->{'copy-1-of-site_name'}->sale_customer->sell_info->total_bottle_sell : 0;
                    $sale->total_lending_bottle_sell = isset($message->form->{'copy-1-of-site_name'}->sale_customer->sell_info->total_lending_bottle_sell) ? $message->form->{'copy-1-of-site_name'}->sale_customer->sell_info->total_lending_bottle_sell : 0;
                    $sale->total_revenue = isset($message->form->{'copy-1-of-site_name'}->sale_customer->sell_info->total_revenue) ? $message->form->{'copy-1-of-site_name'}->sale_customer->sell_info->total_revenue : 0;
                    $sale->social = $message->form->{'copy-1-of-site_name'}->sale_customer->does_shehe_like_our_facebook;
                    $sale->save();
                }
                // Insert KOL data
                if ($message->form->{'copy-1-of-site_name'}->which_form_do_you_want_to_do == "kol") {
                    $kol = new Kol();
                    $kol->site = Str::ucfirst($message->form->{'copy-1-of-site_name'}->kol->input_site_name);
                    $kol->record_date = \Carbon\Carbon::parse($message->form->{'copy-1-of-site_name'}->kol->record_date);
                    $kol->village = $message->form->{'copy-1-of-site_name'}->kol->village;
                    $kol->chief_village = $message->form->{'copy-1-of-site_name'}->kol->chief_villager_name;
                    $kol->chief_village_contact = $message->form->{'copy-1-of-site_name'}->kol->chief_villager_contact;
                    $kol->total_houses = $message->form->{'copy-1-of-site_name'}->kol->total_amount_of_houses;
                    $kol->total_household = $message->form->{'copy-1-of-site_name'}->kol->total_household;
                    $kol->distance = $message->form->{'copy-1-of-site_name'}->kol->distance_from_commune;
                    $kol->expectation = $message->form->{'copy-1-of-site_name'}->kol->expected_market_share;
                    $kol->actual_market = $message->form->{'copy-1-of-site_name'}->kol->actual_market_share;
                    $kol->market_comparison = "";
                    $kol->remark = $message->form->{'copy-1-of-site_name'}->kol->suggestion;
                    $kol->penentration = "";
                    $kol->save();
                }
                if ($message->form->{'copy-1-of-site_name'}->which_form_do_you_want_to_do == "interview_new_customer") {

                    $interview = new SaleSurvey();
                    $interview->site = $message->form->{'copy-1-of-site_name'}->new_customer->input_site_name?? null;
                    $interview->submitted_date = \Carbon\Carbon::parse($message->received_on)->format('Y-m-d')?? null;
                    $interview->do_you_know_the_brand = $message->form->{'copy-1-of-site_name'}->new_customer->do_you_know_the_brand_of_the_water_you_drink_everyday?? null;
                    $interview->what_is_the_brand = $message->form->{'copy-1-of-site_name'}->new_customer->what_is_the_brand_name__write_in_english?? null;
                    $interview->how_many_bottle_you_change = $message->form->{'copy-1-of-site_name'}->new_customer->how_many_bottle_do_you_change_since_we_come_last_time?? null;
                    $interview->why_not_change_the_water = $message->form->{'copy-1-of-site_name'}->new_customer->if_0__why_you_did_not_change_the_water?? null;
                    $interview->how_many_times_the_entrepreneur_came = $message->form->{'copy-1-of-site_name'}->new_customer->how_many_times_the_entrepreneur_came_to_change_the_water?? null;
                    $interview->frequency_how_often_do_you_purchase_o_we = $message->form->{'copy-1-of-site_name'}->new_customer->{'frequency_how_often_do_you_purchase_o-we'}?? null;
                    $interview->specify_other = $message->form->{'copy-1-of-site_name'}->new_customer->specify_other?? null;
                    $interview->how_satisfied_are_you_with_the_timeliness = $message->form->{'copy-1-of-site_name'}->new_customer->{'how_satisfied_are_you_with_the_timeliness_of_the_delivery_service_-_on_a_sc'}?? null;
                    $interview->how_satisfied_are_you_with_the_regularity = $message->form->{'copy-1-of-site_name'}->new_customer->{'how_satisfied_are_you_with_the_regularity_of_the_delivery_service_-_on_a_sc'}?? null;
                    $interview->how_satisfied_are_you_with_the_service = $message->form->{'copy-1-of-site_name'}->new_customer->{'how_satisfied_are_you_with_the_service_provided_by_the_entrepreneur_-_on_a_'}?? null;
                    $interview->overall_how_satisfied_are_you_with_owe_on_a_scale = $message->form->{'copy-1-of-site_name'}->new_customer->{'overall_how_satisfied_are_you_with_owe_-_on_a_scale_from_0_to_10_enumerator'}?? null;
                    $interview->since_starting_you_feel_any_effect = $message->form->{'copy-1-of-site_name'}->new_customer->{'since_starting_to_consume_o-we_water_do_you_feel_any_effect_on_your_overall'}?? null;
                    $interview->specify_other_please = $message->form->{'copy-1-of-site_name'}->new_customer->specify_other_please?? null;
                    $interview->would_you_recommend_o_we = $message->form->{'copy-1-of-site_name'}->new_customer->{'would_you_recommend_o-we_water_to_other_individuals'}?? null;
                    $interview->if_yes_what_would_you_say = $message->form->{'copy-1-of-site_name'}->new_customer->if_yes_what_would_you_say_to_convince_them_to_purchase?? null;
                    $interview->other_please_specify = $message->form->{'copy-1-of-site_name'}->new_customer->other_please_specify?? null;
                    $interview->new_customer_if_no_why_not = $message->form->{'copy-1-of-site_name'}->new_customer->if_no_why_not?? null;
                    $interview->others_specify_please = $message->form->{'copy-1-of-site_name'}->new_customer->others_specify_please?? null;
                    $interview->besides_o_we_you_have_other_sources = $message->form->{'copy-1-of-site_name'}->new_customer->{'besides_o-we_water_what_are_your_other_sources_of_drinking_water_enumerator'}?? null;
                    $interview->specify_another_20l_brand = $message->form->{'copy-1-of-site_name'}->new_customer->specify_another_20l_brand?? null;
                    $interview->specify_another_50l_brand = $message->form->{'copy-1-of-site_name'}->new_customer->specify_another_50l_brand?? null;
                    $interview->specify_other_brand = $message->form->{'copy-1-of-site_name'}->new_customer->specify_other_brand?? null;
                    $interview->before_owe_what_did_you_used = $message->form->{'copy-1-of-site_name'}->new_customer->before_owe_what_did_you_used?? null;
                    $interview->other_please_specific = $message->form->{'copy-1-of-site_name'}->new_customer->other_please_specific?? null;
                    $interview->save();
                }

            }
            // school program
            if ($message->form->{'@name'} == "School Program") {
                $findSite = Str::ucfirst($message->form->site_name);
                $s = Site::find($findSite);
                $sum = (int) SchoolProgram::where('Id_Site', $findSite)->sum('bottle_approved');
                $totalSum = $sum + (int) $message->form->{'copy-1-of-site_name'}->school_information->number_of_bottle_maximum_per_day_to_offer;
                $platform = $s->Platform ?? "Stop";
                $school_limit = $s->school_program ?? 0;
                $result = $totalSum - $school_limit;
                //dd($over);
                $school = new SchoolProgram();
                $school->Id_Site = Str::ucfirst($message->form->site_name);
                $school->platform = $platform ?? null;
                $school->en_name_english = $message->form->{'copy-1-of-site_name'}->entrepreneur_site->entrepreneur_name_english ?? null;
                $school->en_name_khmer = $message->form->{'copy-1-of-site_name'}->entrepreneur_site->entrepreneur_name_khmer ?? null;
                $school->bottle_number_by_entre = $message->form->{'copy-1-of-site_name'}->school_information->number_of_bottle_maximum_per_day_to_offer ?? null;
                $school->en_phone_number = $message->form->{'copy-1-of-site_name'}->entrepreneur_site->phone_number ?? null;
                $school->commune_english = $message->form->{'copy-1-of-site_name'}->school_director_information->commune_english ?? null;
                $school->commune_khmer = $message->form->{'copy-1-of-site_name'}->school_director_information->commune_khmer ?? null;
                $school->province = $message->form->{'copy-1-of-site_name'}->school_director_information->province ?? null;
                $school->school_code = $message->form->{'copy-1-of-site_name'}->school_director_information->school_code ?? null;
                $school->school_director_name_english = $message->form->{'copy-1-of-site_name'}->school_director_information->school_director_name_english ?? null;
                $school->school_director_name_khmer = $message->form->{'copy-1-of-site_name'}->school_director_information->school_director_name_khmer ?? null;
                $school->bottle_requested_by_school = $message->form->{'copy-1-of-site_name'}->school_information->bottle_requested_by_school ?? null;
                $school->school_director_phone_number = $message->form->{'copy-1-of-site_name'}->school_director_information->school_director_phone_number ?? null;
                $school->school_director_signature = $message->form->{'copy-1-of-site_name'}->school_director_signature ?? null;
                $school->school_name_english = $message->form->{'copy-1-of-site_name'}->school_director_information->school_name_english ?? null;
                $school->school_name_khmer = $message->form->{'copy-1-of-site_name'}->school_director_information->school_name_khmer ?? null;
                $school->village_english = $message->form->{'copy-1-of-site_name'}->school_director_information->village_english ?? null;
                $school->village_khmer = $message->form->{'copy-1-of-site_name'}->school_director_information->village_khmer ?? null;
                $school->academy_end = \Carbon\Carbon::parse($message->form->{'copy-1-of-site_name'}->school_information->academy_end) ?? null;
                $school->academy_start = \Carbon\Carbon::parse($message->form->{'copy-1-of-site_name'}->school_information->academy_starts) ?? null;
                $school->start_grade = $message->form->{'copy-1-of-site_name'}->school_information->start_from_grade ?? 0;
                $school->end_grade = $message->form->{'copy-1-of-site_name'}->school_information->until_grade ?? 0;
                $school->number_of_boys = $message->form->{'copy-1-of-site_name'}->school_information->number_of_boys ?? 0;
                $school->number_of_children = $message->form->{'copy-1-of-site_name'}->school_information->number_of_children ?? 0;
                $school->number_of_classes = $message->form->{'copy-1-of-site_name'}->school_information->number_of_classes ?? 0;
                $school->academy_year = 2025;
                $school->number_of_girls = $message->form->{'copy-1-of-site_name'}->school_information->number_of_girls ?? 0;
                $school->status = "waiting_validation";
                $school->bottle_approved = $school->bottle_number_by_entre = $message->form->{'copy-1-of-site_name'}->school_information->number_of_bottle_maximum_per_day_to_offer ?? 0;
                if ($result > 0) {
                    $over = "Over School Limit " . $result . " bottle";
                    $ok = "Over";
                } else {
                    $over = "Not over limit amount";
                    $ok = "Ok";
                }
                $school->status_bottle = $ok;
                $school->save();
                $body = [
                    "id" => $school->id,
                    "School_program" => $over,
                    "ok" => $ok,
                    "Site" => Str::ucfirst($message->form->site_name),
                    "Report_By" => $message->form->meta->username,
                    "Entrepreneur_Name" => $message->form->{'copy-1-of-site_name'}->entrepreneur_site->entrepreneur_name_english,
                    "Province" => $message->form->{'copy-1-of-site_name'}->school_director_information->province,
                    "School_Name" => $message->form->{'copy-1-of-site_name'}->school_director_information->school_name_english,
                    "School_directore_name" => $message->form->{'copy-1-of-site_name'}->school_director_information->school_director_name_english,
                    "Entrepreneur_requests_bottle" => $message->form->{'copy-1-of-site_name'}->school_information->number_of_bottle_maximum_per_day_to_offer,
                    "School_requests_bottle" => $message->form->{'copy-1-of-site_name'}->school_information->bottle_requested_by_school
                ];
                // send mail
                if ($result > 0) {
                    //$this->schoolRequest($body);
                }
            }
            // end school program
            if ($message->form->{'@name'} == "6. Site Checklist") {
                $siteSearch = $message->form->site_name;
                $site = Site::find($siteSearch);
                $site->Phone_Number = $message->form->site_confirmed->station_mgmt_sales->entrepreneur->entrepreneur_phone_number ?? null;
                $site->Entrepreneur_Khmer_Name = $message->form->site_confirmed->station_mgmt_sales->entrepreneur->name_of_entrepreneur ?? null;
                $site->Entrepreneur_English_Name = $message->form->site_confirmed->station_mgmt_sales->entrepreneur->english_name_of_entrepreneur ?? null;
                $site->Sex = $message->form->site_confirmed->station_mgmt_sales->entrepreneur->sex ?? null;
                $site->Advisor = $message->form->meta->username;
                $site->save();
            }
            //expense insert
            if ($message->form->{'@name'} == "3. Register Expenses" || $message->form->{'@name'} == "2. Register Expenses") {
                try {
                    $siteConfirmed = $message->form->site_confirmed ?? null;
                    if (!$siteConfirmed || !isset($siteConfirmed->expenses)) {
                        \Log::info('No expenses data in submission, skipping', ['form' => $message->form->{'@name'}]);
                        return response()->json(['status' => 'ok']);
                    }
                    $expenses = $siteConfirmed->expenses;
                    $s = $message->form->site_name;
                    $m = \Carbon\Carbon::parse($message->form->{'last-day-of-month'})->format('Y-m-01');
                    $result = Expense::where('Id_Site', $s)
                        ->where('Month', $m)
                        ->get();
                    $excludeList = [
                        'consumable_teuk_saat_1001',
                        'bottle_from_teuksaat_1001',
                        'entrepreneur_contribution',
                        'technical_intervention',
                        'water_quality_intervention',
                        'upload_electricity_bill',
                        'delivery_program',
                        'water quality alert',
                        'technical intervention',
                        'WinS_invoice',
                        'delivery_program_fee',
                        'bottle_invoice',
                        'stock_ts',
                        'entrepreneur_contribution'
                    ];
                    // Check if expenses already exist for this site and month
                    if ($result->isNotEmpty()) {
                        Expense::where('Id_Site', $s)
                            ->where('Month', $m)
                            ->whereNotIn('Ref_expenses', $excludeList)
                            ->delete();
                    }
                    foreach ($expenses as $category => $items) {
                        $items = is_object($items) ? (array)$items : $items;
                        if (is_array($items)) {

                            foreach ($items as $expense_name => $amount) {
                                // Only process valid amounts that aren't in exclude list
                                if (!is_null($amount) && $amount !== '' && !in_array($expense_name, $excludeList)) {
                                    Expense::updateOrCreate([
                                        'Id_Site' => $message->form->site_name,
                                        'Month' => \Carbon\Carbon::parse($message->form->{'last-day-of-month'})->format('Y-m-01'),
                                        'Ref_expenses' => $expense_name,
                                        'Amount_expenses' => $amount,
                                        'Paid' => 0, // Note: Typo here? Should this be 'Paid'?
                                        'Category_expenses' => $category, // This should now work
                                    ]);
                                }
                            }
                        }
                    }
                } catch (\Exception $e) {
                    \Log::error('Expense insert failed: ' . $e->getMessage());
                    return response()->json(['error' => $e->getMessage()], 500);
                }
            }

            // Alert email for entrepreneur from
            if ($message->form->{'@name'} == "8. Entrepreneur Form") {
                $titlemail = $message->form->site_confirmed->what_do_you_want_to_do;
                $d = "";
                if ($message->form->site_name == "M34_1")
                {
                    $d= "M34";
                }
                else
                {
                    $d = $message->form->site_name;
                }
                $sitePlatform = Site::select('Platform','Entrepreneur_English_Name','Resignation','Status_Site')->where("Id_Site", $d)->first();
                $platform = $sitePlatform ? $sitePlatform->Platform : null;

                //dd($platform);
                $entre = EntrepreneurProfile::where("Id_Site", $d)
                    ->where("Status", "new_entrepreneur_coming")
                    ->orderBy("Submitted_Date", "desc")
                    ->first();
                $body = "";
                if ($titlemail == "site_closure") {
                    $body = [
                        "site" => $d,
                        "report_by" => $message->form->meta->username,
                        "close_date" => $message->form->site_confirmed->site_closure->closed_date,
                        "reason" => $message->form->site_confirmed->site_closure->reason_closed_site,
                        "reason_detail" => $message->form->site_confirmed->site_closure->close_description
                    ];
                    $profile = new EntrepreneurProfile();
                    $profile->Id_Site = $d;
                    $profile->Status = $message->form->site_confirmed->what_do_you_want_to_do ?? null;
                    $profile->Closed_Date = \Carbon\Carbon::parse($message->form->site_confirmed->site_closure->closed_date) ?? null;
                    $profile->Close_Description = $message->form->site_confirmed->site_closure->close_description ?? null;
                    $profile->Reason_Closed_Site = $message->form->site_confirmed->site_closure->reason_closed_site ?? null;
                    $profile->Submitted_Date = \Carbon\Carbon::parse($message->form->site_confirmed->site_closure->closed_date) ?? null;
                    $profile->save();
                    $siteUpdate = Site::find($d);
                    if ($siteUpdate) {
                        $siteUpdate->Status_Site = "inactive";
                        $siteUpdate->save();
                    } else {
                        \Log::warning("Site not found when processing entrepreneur form: {$d}");
                        return response()->json(['error' => "Site {$d} not found"], 404);
                    }
                    //$body = "site : " . $d . "<br>" . "Report by : " . $message->form->meta->username . "<br>" . "site is closed on: " . $message->form->site_confirmed->site_closure->closed_date . "<br>" . "Reason close : " . $message->form->site_confirmed->site_closure->reason_closed_site . "<br>" . "Close detail : " . $message->form->site_confirmed->site_closure->close_description;
                } else if ($titlemail == "entrepreneur_resignation") {
                    $body = [
                        "site" => $d,
                        "report_by" => $message->form->meta->username,
                        "entrepreneur_name" => $message->form->site_confirmed->entrepreneur_resignation->entrepreneur_english_name,
                        "reason" => $message->form->site_confirmed->entrepreneur_resignation->reason_for_leaving,
                        "detail" => $message->form->site_confirmed->entrepreneur_resignation->detail_reason
                    ];
                    $site = Site::find($d);
                    $site->Resignation = 0;
                    $site->save();
                    $siteSearch = EntrepreneurProfile::where('Id_Site', $d)
                        ->where('Status', 'new_entrepreneur_coming')
                        ->latest('Submitted_Date')
                        ->first();
                    if ($siteSearch) {
                        $siteSearch->Status_Entrepreneur = "stop";
                        $siteSearch->save();
                    }
                    $profile = new EntrepreneurProfile();
                    $profile->Id_Site = $d;
                    $profile->Entrepreneur_Khmer_name = $message->form->site_confirmed->entrepreneur_resignation->entrepreneur_khmer_name ?? null;
                    $profile->Entrepreneur_English_name = $message->form->site_confirmed->entrepreneur_resignation->entrepreneur_english_name ?? null;
                    $profile->Sex = $message->form->site_confirmed->entrepreneur_resignation->sex ?? null;
                    $profile->Reason_Resign = $message->form->site_confirmed->entrepreneur_resignation->reason_for_leaving ?? null;
                    $profile->Detail_Resign = $message->form->site_confirmed->entrepreneur_resignation->detail_reason ?? null;
                    $profile->Resignation_Date = \Carbon\Carbon::parse($message->form->site_confirmed->entrepreneur_resignation->when_did_heshe_resign) ?? null;
                    $profile->Submitted_Date = \Carbon\Carbon::parse($message->form->site_confirmed->entrepreneur_resignation->when_did_heshe_resign) ?? null;
                    $profile->Site_Status = $message->form->site_confirmed->entrepreneur_resignation->site_status ?? null;
                    $profile->Status = $message->form->site_confirmed->what_do_you_want_to_do ?? null;
                    $profile->Working_Date = $entre->Working_Date ?? null;
                    $profile->Status_Entrepreneur = "active" ?? null;
                    $profile->save();
                    // $body = "site : " . $d . "<br>" . "Report by : " . $message->form->meta->username . "<br>" . "Entrepreneur Name: " . $message->form->site_confirmed->entrepreneur_resignation->entrepreneur_english_name . "<br>" . "Reason for leaving : " . $message->form->site_confirmed->entrepreneur_resignation->reason_for_leaving . "<br>" . "Detail reason: " . $message->form->site_confirmed->entrepreneur_resignation->detail_reason;
                } else if ($titlemail == "new_entrepreneur_coming") {
                    $siteSearch = $d;
                    $site = Site::find($siteSearch);
                    $site->Entrepreneur_English_Name = $message->form->site_confirmed->new_entrepreneur_recruitment->entrepreneur_name_english;
                    $site->Entrepreneur_Khmer_Name = $message->form->site_confirmed->new_entrepreneur_recruitment->entrepreneur_khmer_name;
                    $site->sex = $message->form->site_confirmed->new_entrepreneur_recruitment->sex;
                    $site->Commune_Entrepreneur = $message->form->site_confirmed->new_entrepreneur_recruitment->commune__village;
                    $site->Province_Entrepreneur = $message->form->site_confirmed->new_entrepreneur_recruitment->province;
                    $site->Date_of_birth = \Carbon\Carbon::parse($message->form->site_confirmed->new_entrepreneur_recruitment->date_of_birth);
                    $site->Date_start_working = \Carbon\Carbon::parse($message->form->site_confirmed->new_entrepreneur_recruitment->date_start_working_in_station);
                    $site->Phone_Number = $message->form->site_confirmed->new_entrepreneur_recruitment->first_phone_number;
                    $site->Education = $message->form->site_confirmed->new_entrepreneur_recruitment->education;
                    $site->Previous_Job = $message->form->site_confirmed->new_entrepreneur_recruitment->what_does_he_do_before_joining_ts;
                    $site->Resignation = 1;
                    $site->save();

                    $profile = new EntrepreneurProfile();
                    $profile->Id_Site = $d;
                    $profile->Status = $message->form->site_confirmed->what_do_you_want_to_do ?? null;
                    $profile->Entrepreneur_Khmer_name = $message->form->site_confirmed->new_entrepreneur_recruitment->entrepreneur_khmer_name ?? null;
                    $profile->Entrepreneur_English_name = $message->form->site_confirmed->new_entrepreneur_recruitment->entrepreneur_name_english ?? null;
                    $profile->Sex = $message->form->site_confirmed->new_entrepreneur_recruitment->sex ?? null;
                    $profile->Commune = $message->form->site_confirmed->new_entrepreneur_recruitment->commune__village ?? null;
                    $profile->DOB = \Carbon\Carbon::parse($message->form->site_confirmed->new_entrepreneur_recruitment->date_of_birth) ?? null;
                    $profile->Working_Date = \Carbon\Carbon::parse($message->form->site_confirmed->new_entrepreneur_recruitment->date_start_working_in_station) ?? null;
                    $profile->Submitted_Date = \Carbon\Carbon::parse($message->form->site_confirmed->new_entrepreneur_recruitment->date_start_working_in_station) ?? null;
                    $profile->Education = $message->form->site_confirmed->new_entrepreneur_recruitment->education ?? null;
                    $profile->Entrepreneur_Phone = $message->form->site_confirmed->new_entrepreneur_recruitment->first_phone_number ?? null;
                    $profile->Province = $message->form->site_confirmed->new_entrepreneur_recruitment->province ?? null;
                    $profile->Previous_Job = $message->form->site_confirmed->new_entrepreneur_recruitment->what_does_he_do_before_joining_ts ?? null;
                    $profile->Status_Entrepreneur = "active" ?? null;
                    $profile->save();

                    $body = [
                        "site" => $d,
                        "report_by" => $message->form->meta->username,
                        "entrepreneur_name" => $message->form->site_confirmed->new_entrepreneur_recruitment->entrepreneur_name_english,
                        "DOB" => $message->form->site_confirmed->new_entrepreneur_recruitment->date_of_birth,
                        "phone_number" => $message->form->site_confirmed->new_entrepreneur_recruitment->first_phone_number,
                        "what_he_does_before" => $message->form->site_confirmed->new_entrepreneur_recruitment->what_does_he_do_before_joining_ts,
                        "education" =>  $message->form->site_confirmed->new_entrepreneur_recruitment->education,
                        "sex" =>  $message->form->site_confirmed->new_entrepreneur_recruitment->sex,
                    ];
                    // $body = "site : " . $d . "<br>" . "Report by : " . $message->form->meta->username . "<br>" . "New Entrepreneur Name: " . $message->form->site_confirmed->new_entrepreneur_recruitment->entrepreneur_name_english . "<br>" . "DOB : " . $message->form->site_confirmed->new_entrepreneur_recruitment->date_of_birth . "<br>" . "Phone number: " . $message->form->site_confirmed->new_entrepreneur_recruitment->first_phone_number . "<br>" . "what he does before: " . $message->form->site_confirmed->new_entrepreneur_recruitment->what_does_he_do_before_joining_ts;
                } else if ($titlemail == "site_reopen") {
                    $body = [
                        "site" => $d,
                        "report_by" => $message->form->meta->username,
                        "open_date" => $message->form->site_confirmed->site_reopen->reopen_date
                    ];
                    $profile = new EntrepreneurProfile();
                    $profile->Id_Site = $d;
                    $profile->Status = $message->form->site_confirmed->what_do_you_want_to_do ?? null;
                    $profile->Reopen_Date = \Carbon\Carbon::parse($message->form->site_confirmed->site_reopen->reopen_date) ?? null;
                    $profile->Submitted_Date = \Carbon\Carbon::parse($message->form->site_confirmed->site_reopen->reopen_date) ?? null;
                    $profile->save();
                    $siteUpdate = Site::find($d);
                    if ($siteUpdate) {
                        $siteUpdate->Status_Site = "active";
                        $siteUpdate->save();
                    } else {
                        \Log::warning("Site not found when processing entrepreneur form: {$d}");
                        return response()->json(['error' => "Site {$d} not found"], 404);
                    }
                    //$body = "site : " . $d . "<br>" . "Report by : " . $message->form->meta->username . "<br>" . "Open date: " . $message->form->site_confirmed->site_reopen->reopen_date;
                }
                $this->entrepreneurEmail($titlemail, $body, $sitePlatform);
            }
            $formName = ["7. Request Form", "3. Register Expenses", "2. Register Expenses", "6. Site Checklist"
            , "School Program","1. Register Sales","4. Deposit and Withdrawal Form","3. Settle Invoices"];
            $siteAlert = $message->form->site_name;
            $siteData = Site::select('Platform','Entrepreneur_English_Name','Resignation','Status_Site')->where("Id_Site", $siteAlert)->first();
            $p = ["PP","SR","KC","KSP","BTB"];

            $form = $datastore->entity('Pivot', [
                "app_id" => "AZURE_" . $message->app_id,
                "integration_date" => now(),
                "form" => $message->form->{'@name'},
                "version" => $message->form->meta->app_build_version,
                "user" => $message->form->meta->username,
                "submit_date" => \Carbon\Carbon::parse($message->form->meta->timeEnd),
                "status" =>  $message->form->site_confirmed->are_you_advisor_or_academy_staff ?? null,
                "academy_site" => $message->form->site_confirmed->which_site_do_you_want_to_test ?? null,
                "training_session" => $message->form->site_confirmed->what_training_type_do_you_want_to_do ?? null,
                "entrepreneur_name" => $message->form->site_confirmed->entrepreneur_profile->what_is_entrepreneur_name ?? null,
                "evaluator" =>  $message->form->site_confirmed->what_is_the_name_of_evaluator ?? null,
                "result_test" =>  $message->form->site_confirmed->pass_or_fail ?? null,
                "water_result" =>  $message->form->site_confirmed->water_quality->total_water_quality_part_percentage ?? null,
                "leadership_result" =>  $message->form->site_confirmed->leadership->total_entrepreneurship_part_percentage ?? null,
                "marketing_result" =>  $message->form->site_confirmed->marketing_and_delivery->total_marketing_and_delivery_part_percentage ?? null,
                "finance_result" =>  $message->form->site_confirmed->finance_strategy->total_finance_strategy_percentage ?? null,
                "id" =>  $message->id,
                "data" => $request->getContent(),
                "site" => $message->form->site_name ?? "undefined",
                "month" => $month,
            ]);
            $form->setExcludeFromIndexes(['data']);
            $datastore->insert($form);
            if ( $siteData && $siteData->Status_Site != 'active')
                    {
                        if (in_array($siteData->Platform, $p) && in_array($message->form->{'@name'}, $formName))
                            {
                                $formSubmitted = $message->form->{'@name'};
                                Site::where('Id_Site', $siteAlert)->update(['Status_Site' => 'active']);
                                    $emailBody = [
                                        'site' => $siteAlert,
                                        'status' => $siteData->Status_Site,
                                        'form_name' => $formSubmitted,
                                        'report_by' => $message->form->meta->username,
                                        'date' => \Carbon\Carbon::parse($message->received_on)->format('Y-m-d')
                                        ];
                                    $this->siteCloseButHaveData($emailBody,$siteData);
                            }
                    }
            return $form->key()->pathEnd()['id'];
        } else {
            return "message->form->@name is not present. message ignored.";
        }
    }
    private function entrepreneurEmail($title, $body, $sitePlatform1)
    {
        $sitePlatform = trim($sitePlatform1->Platform);
        $rom = '';
        $cashier = '';
        if ($sitePlatform == "SR") {
            $rom = "kimhong.p@teuksaat1001.com";
            $cashier = "porleng.h@teuksaat1001.com";
        } else if ($sitePlatform == "KSP") {
            $rom = "rethy.m@teuksaat1001.com";
            $cashier = "sorvy.m@teuksaat1001.com";
        } else if ($sitePlatform == "KC") {
            $rom = "bun.ph@teuksaat1001.com";
            $cashier = "sreyrath.h@teuksaat1001.com";
        } else if ($sitePlatform == "PP") {
            $rom = "lim.t@teuksaat1001.com";
            $cashier = "sorvy.m@teuksaat1001.com";
        } else if ($sitePlatform == "BTB") {
            $rom = "vanra.p@teuksaat1001.com";
            $cashier = "chamroeun.no@teuksaat1001.com";
        }
        if ($title == "new_entrepreneur_coming") {
            $recipients = ['yet.y@teuksaat1001.com','reaksmey.p@teuksaat1001.com','q.pelletier@1001fontaines.com','axel.liber@1001fontaines.com',$cashier, 'chamnap.keo@teuksaat1001.com', $rom, 'amandine.chaussinand@teuksaat1001.com', 'finance@teuksaat1001.com'];
        } else {
            $recipients = ['yet.y@teuksaat1001.com','reaksmey.p@teuksaat1001.com','q.pelletier@1001fontaines.com','axel.liber@1001fontaines.com','chamnap.keo@teuksaat1001.com', $rom, 'amandine.chaussinand@teuksaat1001.com', 'finance@teuksaat1001.com'];
        }
        $recipients = array_values(array_filter($recipients));
        Mail::to($recipients)->send(new EntrepreneurEmail($title, $body, $cashier));
    }
    private function siteCloseButHaveData($body, $sitePlatform1)
    {
        $sitePlatform = trim($sitePlatform1->Platform);
        $rom = '';
        $cashier = '';
        $junior = '';
        if ($sitePlatform == "SR") {
            $rom = "kimhong.p@teuksaat1001.com";
            $cashier = "porleng.h@teuksaat1001.com";
        } else if ($sitePlatform == "KSP") {
            $rom = "rethy.m@teuksaat1001.com";
            $cashier = "sorvy.m@teuksaat1001.com";
        } else if ($sitePlatform == "KC") {
            $rom = "bun.ph@teuksaat1001.com";
            $cashier = "sreyrath.h@teuksaat1001.com";
        } else if ($sitePlatform == "PP") {
            $rom = "lim.t@teuksaat1001.com";
            $cashier = "sorvy.m@teuksaat1001.com";
            $junior = "chivorn.c@teuksaat1001.com";
        } else if ($sitePlatform == "BTB") {
            $rom = "yet.y@teuksaat1001.com";
            $cashier = "chamroeun.no@teuksaat1001.com";
            $junior = "vanra.p@teuksaat1001.com";
        }
        $recipients = ['q.pelletier@1001fontaines.com','axel.liber@1001fontaines.com','chamnap.keo@teuksaat1001.com', $rom,
        'amandine.chaussinand@teuksaat1001.com', 'finance@teuksaat1001.com', $cashier, 'reaksmey.p@teuksaat1001.com', $junior];
        $recipients = array_values(array_filter($recipients));
        Mail::to($recipients)->send(new SiteCloseButHaveData($body, $cashier));
    }
    private function schoolRequest($body)
    {

        $site = $body['Site'];
        $data = Site::where("Id_Site", $site)->first();
        // if ($data->Platform =='SR')
        // {
        //      $recipients = ['chamnap.keo@teuksaat1001.com','rbm@teuksaat1001.com'];
        // }
        $recipients = ['chamnap.keo@teuksaat1001.com', 'rbm@teuksaat1001.com'];
        Mail::to($recipients)->send(new SchoolRequest($body));
    }
    public function getRegisterSalesSchoolProgram(Request $request)
    {
        $datastore = new DatastoreClient(['projectId' => $this->projectId]);
        $query = $datastore->query()
            ->kind('Pivot')
            ->filter('month', '=', $request->month)
            ->filter('form', '=', '1. Register Sales')
            ->order('integration_date', Query::ORDER_DESCENDING)
            ->limit(300);
        $school_program_from_settle = [];
        $cursor = '';
        $sites = Site::query()->get(["Id_Site", "Platform"]);
        do {
            $query->start($cursor);
            $result = $datastore->runQuery($query);
            $startCursor = $cursor;
            foreach ($result as $sales) {
                $data_sales = json_decode($sales->get()["data"]);
                if (!isset($data_sales->form->site_confirmed)) {
                    continue;
                }
                $channels = $this->normalizeCCObject($data_sales->form->site_confirmed->{'sale-channel'});
                $days_in_month = $data_sales->form->{'days-in-month'};
                $daily_sale = 0;
                for ($i = 0; $i < $days_in_month; $i++) {
                    foreach ($channels as $channel) {
                        if (is_object($channel) && is_object($channel->{'enforce-repeats'})) {
                            if ($channel->{'enforce-repeats'}->{'channel-list'}->{'channel'} == "school") {
                                $daily_sale += ($channel->{'enforce-repeats'}->{'daily-sales'}->{'day'}[$i]->sales * $channel->{'enforce-repeats'}->{'channel-list'}->{'price'});
                            }
                        }
                    }
                }
                if ($daily_sale < 0) {
                    $school_program_from_settle[$sales->get()["site"]] = array(
                        "id" => $sales->key()->pathEnd()['id'],
                        "pf" => $sites->where("Id_Site", $sales->get()["site"])->first()->Platform,
                        'site' => $sales->get()["site"],
                        'save_debt' => 0,
                        'advisor' => $this->getUserName($data_sales),
                        'date' => $this->getDateSent($data_sales),
                        'cash_receipt' => "unsettled school program",
                        'invoice_ref' => "school-program",
                        'invoice_type' => "school-program",
                        'received' => 0,
                        'amount' => -1 * $daily_sale,
                        'amount_begin' => -1 * $daily_sale,
                        'remaining' => -1 * $daily_sale,
                        'validated' => false,
                        'validated_text' => 'no',
                        'pictures' => ""
                    );
                }
            }
        } while ($startCursor !== $cursor);
        return $school_program_from_settle;
    }

    public function getSchoolPictures(Request $request)
    {
        Log::info('[SchoolPictures] params', ['site' => $request->site, 'month' => $request->month]);

        $datastore = new DatastoreClient(['projectId' => $this->projectId]);
        $query = $datastore->query()
            ->kind('Pivot')
            ->filter('month', '=', $request->month)
            ->filter('site',  '=', $request->site)
            ->filter('form',  '=', '1. Register Sales')
            ->order('integration_date', Query::ORDER_DESCENDING)
            ->limit(300);

        $pictures = [];
        $cursor   = '';

        do {
            $query->start($cursor);
            $result      = $datastore->runQuery($query);
            $startCursor = $cursor;

            foreach ($result as $record) {
                $data  = $record->get();
                $data1 = json_decode($data['data'] ?? '{}');

                // Collect only the school picture filenames from the form
                $schoolPicKeys = [
                    'please_take_a_picture_of_first_school',
                    'please_take_a_picture_of_second_school',
                    'please_take_a_picture_of_third_school',
                    'please_take_a_picture_of_fourth_school',
                    'please_take_a_picture_of_fifth_school',
                ];
                $pictureObj = $data1->form->site_confirmed->new_production->picture ?? null;
                $schoolFilenames = [];
                if ($pictureObj) {
                    foreach ($schoolPicKeys as $key) {
                        $val = $pictureObj->$key ?? '';
                        if (!empty($val)) {
                            $schoolFilenames[] = $val;
                        }
                    }
                }
                //correct filenames if they have "fakepath" (common in some browsers)
                // Match against attachments
                if (!empty($schoolFilenames) && !empty($data1->attachments)) {
                    foreach ($schoolFilenames as $filename) {
                        $attachment = ((array) $data1->attachments)[$filename] ?? null;
                        if ($attachment && !empty($attachment->url)) {
                            $pictures[] = [
                                'filename'         => $filename,
                                'url'              => $attachment->url,
                                'site'             => $data['site']             ?? null,
                                'integration_date' => $data['integration_date'] ?? null,
                            ];
                        }
                    }
                }
            }
        } while ($startCursor !== $cursor);

        Log::info('[SchoolPictures] returning ' . count($pictures) . ' pictures');
        return response()->json($pictures);
    }

    public function getDepositWithdrawalForms(Request $request)
    {
        $datastore = new DatastoreClient(['projectId' => $this->projectId]);
        $query = $datastore->query()
            ->kind('Pivot')
            ->filter('month', '=', $request->month)
            ->filter('form', '=', '4. Deposit and Withdrawal Form')
            ->order('integration_date', Query::ORDER_DESCENDING);
        $cursor = '';
        $sites = Site::query()->get(["Id_Site", "Platform"]);
        $data = [];
        do {
            $query->start($cursor);
            $result = $datastore->runQuery($query);
            $startCursor = $cursor;
            foreach ($result as $sales) {
                $data_deposit = json_decode($sales->get()["data"]);
                if (isset($data_deposit->form->site_confirmed->deposit)) {
                    $data[] = array(
                        "id" => $sales->key()->pathEnd()['id'],
                        "pf" => $sites->where("Id_Site", $sales->get()["site"])->first()->Platform,
                        'site' => $data_deposit->form->site_name,
                        'save_debt' => "",
                        'advisor' => $this->getUserName($data_deposit),
                        'date' => $this->getDateSent($data_deposit),
                        'cash_receipt' => "saving",
                        'amount' => -1 * intval($data_deposit->form->site_confirmed->deposit->deposit->deposit_amount),
                        'invoice_ref' => "saving",
                        'invoice_type' => "saving",
                        'received' => -1 * intval($data_deposit->form->site_confirmed->deposit->deposit->deposit_amount),
                        'amount_begin' => -1 * intval($data_deposit->form->prev_balance),
                        'remaining' => -1 * intval($data_deposit->form->current_balance),
                        'validated' => '',
                        'validated_text' => '',
                        'pictures' => '',
                    );
                } else if (isset($data_deposit->form->site_confirmed->withdraw)) {
                    $data[] = array(
                        "id" => $sales->key()->pathEnd()['id'],
                        "pf" => $sites->where("Id_Site", $sales->get()["site"])->first()->Platform,
                        'site' => $data_deposit->form->site_name,
                        'save_debt' => "",
                        'advisor' => $this->getUserName($data_deposit),
                        'date' => $this->getDateSent($data_deposit),
                        'cash_receipt' => "withdraw",
                        'amount' => intval($data_deposit->form->site_confirmed->withdraw->withdraw->withdraw_amount),
                        'invoice_ref' => "withdraw",
                        'invoice_type' => "withdraw",
                        'received' => intval($data_deposit->form->site_confirmed->withdraw->withdraw->withdraw_amount),
                        'amount' => intval($data_deposit->form->site_confirmed->withdraw->withdraw->withdraw_amount),
                        'amount_begin' => -1 * intval($data_deposit->form->prev_balance),
                        'remaining' => -1 * intval($data_deposit->form->current_balance),
                        'validated' => '',
                        'validated_text' => '',
                        'pictures' => '',
                    );
                }
            }
        } while ($startCursor !== $cursor);
        return $data;
    }

    public function getSiteStatus(Request $request)
    {
        $request->validate([
            'month' => 'required',
        ]);
        $sites = Site::all();
        $siteMap = [];
        foreach ($sites as $site) {
            $siteMap[$site->Id_Site] = $site->Platform;
        }
        $datastore = new DatastoreClient(['projectId' => $this->projectId]);
        $query = $datastore->query()
            ->kind('Pivot')
            ->filter('month', '=', $request->month)
            ->filter('form', '=', '8. Entrepreneur Form')
            ->order('integration_date', Query::ORDER_DESCENDING);
        $result = $datastore->runQuery($query);
        $re = array();
        foreach ($result as $entity) {
            $data = json_decode($entity->get()["data"]);
            $siteName = $data->form->site_name;
            $re[] = [
                "site" => $siteName,
                "status" => $data->form->site_confirmed->what_do_you_want_to_do,
                "platform" => $siteMap[$siteName] ?? null,
                "open_date" =>  $data->form->site_confirmed->site_reopen->reopen_date ?? "",
                "closed_date" =>  $data->form->site_confirmed->site_closure->closed_date ?? "",
                "reason_closed" =>  $data->form->site_confirmed->site_closure->reason_closed_site ?? "",
                "closed_detail" =>  $data->form->site_confirmed->site_closure->close_description ?? "",
                "date_entre_work" => $data->form->site_confirmed->new_entrepreneur_recruitment->date_start_working_in_station ?? "",
                "entre_name" => $data->form->site_confirmed->new_entrepreneur_recruitment->entrepreneur_name_english ?? "",
                "when_resign" => $data->form->site_confirmed->entrepreneur_resignation->when_did_heshe_resign ?? "",
                "reason_resign" => $data->form->site_confirmed->entrepreneur_resignation->reason_for_leaving ?? "",
                "detail_resign" => $data->form->site_confirmed->entrepreneur_resignation->detail_reason ?? "",
            ];
        }

        if ($request->has("excel")) {
            $inputFileName = storage_path('app/templates/siteStatus.xlsx');
            $TBS = new \clsTinyButStrong();
            $ok = class_exists('clsOpenTBS', true); // hack to force class loading of TBS
            $TBS->Plugin(\TBS_INSTALL, \OPENTBS_PLUGIN);
            $TBS->OtbsMsExcelExplicitRef = false;
            $TBS->LoadTemplate($inputFileName, \OPENTBS_ALREADY_UTF8);
            $TBS->SetOption("noerr", true);
            $TBS->MergeBlock('a', $re);
            $TBS->MergeField('month', ["month" => $request->month]);
            //$TBS->PlugIn(OPENTBS_DEBUG_XML_CURRENT);
            $filename = $request->month . "_siteStatus.xlsx";
            $TBS->Show(OPENTBS_DOWNLOAD, $filename);
        }
        return $re;
    }

    public function getSettleInvoiceForms(Request $request)
    {
        $request->validate([
            'month' => 'required',
        ]);
        $dataPicture = [];
        $school_program_from_settle = $this->getRegisterSalesSchoolProgram($request);
        $datastore = new DatastoreClient(['projectId' => $this->projectId]);
        $query = $datastore->query()
            ->kind('Pivot')
            ->filter('month', '=', $request->month)
            ->filter('form', 'IN', ['2. Settle Invoices', '3. Settle Invoices'])
            ->order('integration_date', Query::ORDER_DESCENDING);

        $return = [];
        $cursor = '';
        $sites = Site::query()->get(["Id_Site", "Platform"]);

        do {
            $query->start($cursor);
            $result = $datastore->runQuery($query);
            $startCursor = $cursor;

            foreach ($result as $entity) {
                $data = json_decode($entity->get()["data"]);
                $validated_invoices = json_decode($entity->isFinanceValidated);
                if (!is_array($validated_invoices)) {
                    $validated_invoices = [];
                }
                $picture_qr_urls = [];
                $pictures_receipt_urls = [];
                foreach ($data->attachments as $filename => $attachment) {

                    // Skip form.xml and check if it's an image by content type
                    if ($filename !== "form.xml" && strpos($attachment->content_type, 'image/') === 0) {
                        if (isset($data->form->site_confirmed->{'entrepreneur-owes-teuk-saat'}->please_take_a_photo_of_qr_transaction) &&
            $data->form->site_confirmed->{'entrepreneur-owes-teuk-saat'}->please_take_a_photo_of_qr_transaction === $filename) {
            $picture_qr_urls[] = $attachment->url;
        }

        // Cash receipt picture
        if (isset($data->form->site_confirmed->{'transaction-summary'}->{'cash-receipt-picture'}) &&
            $data->form->site_confirmed->{'transaction-summary'}->{'cash-receipt-picture'} === $filename) {
            $pictures_receipt_urls[] = $attachment->url;
        }
                    }
                }

                if (isset($data->form->invoice->item)) {
                    $invoices_data = $this->normalizeCCObject($data->form->invoice->item);
                    foreach ($invoices_data as $invoice) {
                        if ($invoice->name == "school-program") {
                            $received = -1 * $invoice->{'amount-owed-to-entrepreneur'};
                            $amount = -1 * $invoice->{'amount-owed-to-entrepreneur'};
                            $amount_begin = -1 * $invoice->{'amount-owed-to-entrepreneur'};
                            $remaining = 0;
                            $invoice->external_id = "school-program";
                        } else if ($invoice->paid == 1) {
                            $received = $invoice->{'amount-owed-to-teuk-saat'};
                            $amount = $invoice->{'original-amount-owed-to-teuk-saat'};
                            $amount_begin = $invoice->{'amount-owed-to-teuk-saat'};
                            $remaining = 0;
                        } else if ($invoice->{'partially-paid'} == 1) {
                            $received = $invoice->{'partially-pay'}->{'amount-paid'};
                            $amount = $invoice->{'original-amount-owed-to-teuk-saat'};
                            $amount_begin = $invoice->{'partially-pay'}->{'old-amount-owed-to-teuk-saat'};
                            $remaining = $invoice->{'partially-pay'}->{'new-amount-owed-to-teuk-saat'};
                        } else {
                            $received = 0;
                            $amount = 0;
                            $amount_begin = $invoice->{'original-amount-owed-to-teuk-saat'};
                            $remaining = $invoice->{'amount-owed-to-teuk-saat'};
                        }

                        $school_program_from_settle[$entity->site] = "done";
                        if ($invoice->external_id == "") {
                            $invoice->external_id = $entity->site . str_replace(' ', '', $invoice->name);
                        }

                        $return[] = [
                            "id" => $entity->key()->pathEnd()['id'],
                            "site" => $entity->get()["site"],
                            "pf" => $sites->where("Id_Site", $entity->get()["site"])->first()->Platform,
                            "month" => $entity->get()["month"],
                            "advisor" => $this->getUserName($data),
                            'save_debt' => intval($data->form->last_balance1 ?? 0),
                            'date' => $this->getDateSent($data),
                            'cash_receipt' => $data->form->site_confirmed->{'transaction-summary'}->cash_transaction_reference ?? "",
                            'invoice_ref' => $invoice->external_id,
                            'invoice_type' => $invoice->name,
                            'received' => intval($received),
                            'amount' => intval($amount),
                            'amount_begin' => intval($amount_begin),
                            'remaining' => intval($remaining),
                            'validated' => in_array($invoice->external_id, $validated_invoices),
                            'validated_text' => in_array($invoice->external_id, $validated_invoices) ? "yes" : "no",
                            'pictures' => $picture_qr_urls,
                            'receipt' => $pictures_receipt_urls,
                            'payment_method' => $data->form->site_confirmed->{'entrepreneur-owes-teuk-saat'}->are_you_paying_by_cash_or_qr ?? "",
                        ];
                    }
                }
            }
        } while ($startCursor !== $cursor);


        foreach ($school_program_from_settle as $site => $value) {
            if (is_array($value)) {
                $return[] = $value;
            }
        }
        //dd($dataPicture);
        $return = array_merge($return, $this->getDepositWithdrawalForms($request));
        if ($request->has("excel")) {
            $inputFileName = storage_path('app/templates/accountant_report_template.xlsx');
            $TBS = new \clsTinyButStrong();
            $ok = class_exists('clsOpenTBS', true); // hack to force class loading of TBS
            $TBS->Plugin(\TBS_INSTALL, \OPENTBS_PLUGIN);
            $TBS->OtbsMsExcelExplicitRef = false;
            $TBS->LoadTemplate($inputFileName, \OPENTBS_ALREADY_UTF8);
            $TBS->SetOption("noerr", true);
            $TBS->MergeBlock('data', $return);
            $TBS->MergeField('month', ["month" => $request->month]);
            //$TBS->PlugIn(OPENTBS_DEBUG_XML_CURRENT);
            $filename = $request->month . "_payment_received.xlsx";
            $TBS->Show(OPENTBS_DOWNLOAD, $filename);
        }
        return $return;
    }

//     public function downloadPictures(Request $request)
// {
//     $request->validate([
//         'month' => 'required',
//     ]);

//     // Big downloads: no time limit + keep streaming even if client disconnects
//     set_time_limit(0);
//     ignore_user_abort(true);

//     // Build list: one picture per site
//     $datastore = new DatastoreClient(['projectId' => $this->projectId]);
//     $query = $datastore->query()
//         ->kind('Pivot')
//         ->filter('month', '=', $request->month)
//         ->filter('form', 'IN', ['2. Settle Invoices', '3. Settle Invoices']);

//     $cursor = '';
//     $sites = Site::all()->keyBy('Id_Site');
//     $sitePictures = [];

//     do {
//         $query->start($cursor);
//         $result = $datastore->runQuery($query);
//         $startCursor = $cursor;

//         foreach ($result as $entity) {
//             $siteId = $entity->get()['site'];
//             $data   = json_decode($entity->get()['data']);

//             if (!isset($data->attachments) || !is_object($data->attachments)) {
//                 continue;
//             }

//             foreach ($data->attachments as $filename => $attachment) {
//                 if ($filename !== "form.xml" && isset($attachment->content_type) && strpos($attachment->content_type, 'image/') === 0) {
//                     if (!isset($sitePictures[$siteId])) {
//                         $sitePictures[$siteId] = $attachment->url; // first image per site only
//                     }
//                 }
//             }
//         }
//     } while ($startCursor !== $cursor);

//     if (empty($sitePictures)) {
//         return response()->json(['error' => 'No pictures found for this month'], 404);
//     }

//     $username = config('services.commcare.username');
//     $password = config('services.commcare.password');

//     // If any output buffering exists, clear it so headers from ZipStream can be sent cleanly
//     if (function_exists('ob_get_level')) {
//         while (ob_get_level() > 0) { @ob_end_clean(); }
//     }

//     $zipName = "pictures_{$request->month}_" . date('Ymd_His') . ".zip";

//     // Create ZipStream: no Archive options class needed
//     $zip = new ZipStream($zipName);

//     foreach ($sitePictures as $siteId => $url) {
//         try {
//             $resp = Http::withBasicAuth($username, $password)
//                         ->timeout(60)
//                         ->get($url);

//             if ($resp->ok()) {
//                 // Safe filename: SiteName_original.jpg (replace unsafe chars)
//                 $siteLabel = $sites[$siteId]->Platform ?? (string)$siteId;
//                 $safeSite  = preg_replace('/[^\w\-.]+/u', '_', $siteLabel);
//                 $basename  = basename(parse_url($url, PHP_URL_PATH) ?? ('img_' . $siteId . '.jpg'));

//                 $zip->addFile("{$safeSite}_{$basename}", $resp->body());
//             }
//         } catch (\Throwable $e) {
//             \Log::error("ZipStream fetch error for site {$siteId} ({$url}): {$e->getMessage()}");
//             // Optionally add a small text file noting the error:
//             // $zip->addFile("{$safeSite}_ERROR.txt", "Failed to fetch image for site {$siteId}");
//         }
//     }

//     // Finish and flush to client
//     $zip->finish();
//     return; // important: don't return another Laravel response after ZipStream
// }
    private function normalizeCCObject($object)
    {
        if (is_object($object)) {
            $channels = array();
            array_push($channels, $object);
        } else {
            $channels = $object;
        }
        return $channels;
    }

    private function getDateSent($data)
    {
        if (is_object($data->metadata))
            return substr($data->metadata->timeEnd, 0, 10);
        else if (is_object($data->form->meta))
            return substr($data->form->meta->timeEnd, 0, 10);
        else
            return "unknown date";
    }

    private function getUserName($data)
    {
        if (is_object($data->metadata))
            return $data->metadata->username;
        else if (is_object($data->form->meta))
            return $data->form->meta->username;
        else
            return "unknown user";
    }

    function getPicture($path)
    {
        try {
            // $username = "chamnap.ts1001@gmail.com";
            // $password = "Teuks@@t1oo1";
            $username = config('services.commcare.username');
            $password = config('services.commcare.password');

            // Fetch image with Basic Auth
            $response = Http::withBasicAuth($username, $password)->get($path);

            if (!$response->ok()) {
                throw new \Exception("Failed to fetch image: " . $response->status());
            }

            return $response->body();
        } catch (\Exception $e) {
          //  Log::error("getPicture failed: " . $e->getMessage());
            return null;
        }
    }
    public function showPicture(Request $request)
    {
        $path = $request->query('path');
        $imageContent = $this->getPicture($path);

        if (!$imageContent) {
            return response()->json(['error' => 'Unable to fetch image'], 500);
        }

        return response($imageContent)->header('Content-Type', 'image/jpeg');
    }
}
