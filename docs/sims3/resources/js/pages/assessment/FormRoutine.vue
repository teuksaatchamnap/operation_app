<template>
    <v-form class="bg-grey-lighten-1 pa-4" @submit.prevent="savePAForm">
        <v-btn color="red" class="mx" icon="mdi-arrow-left" size="30px" @click="$router.go(-1)" />
        <v-spacer> &nbsp;</v-spacer>
        <v-card>
            <v-tabs v-model="tab" bg-color="primary">
                <v-tab value="basic_info">Basic Info</v-tab>
                <v-tab value="pre_treatment">Pre-Treatment</v-tab>
                <v-tab value="Hygience">Hygience</v-tab>
                <v-tab value="drinking_water_quality">Drinking_Water</v-tab>
                <v-tab value="Final_Treatment">Final Treatment</v-tab>
                <v-tab value="Electricity">Bottle Washing</v-tab>
            </v-tabs>
            <v-card-text>
                <v-window v-model="tab">
                    <v-window-item value="basic_info">
                        <v-card prepend-icon="mdi-briefcase-edit" title="Basic Info" class="mb-3 rounded-lg">
                            <v-card-text>
                                <v-row>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.site" density="compact" label="Site"
                                            hide-details="auto" :readonly="true" :rules="required" />
                                    </v-col>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.technician" density="compact" label="technician"
                                            hide-details="auto" :readonly="true" :rules="required" />
                                    </v-col>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.date" density="compact" label="date"
                                            hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.main_person_the_water_kiosk_with_you"
                                            density="compact" label="main_person_the_water_kiosk_with_you"
                                            hide-details="auto" />
                                    </v-col>
                                </v-row>
                                <v-row>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.form_do_you_want_to_do" density="compact"
                                            label="form_do_you_want_to_do" hide-details="auto" />
                                    </v-col>
                                </v-row>
                            </v-card-text>
                        </v-card>
                    </v-window-item>
                    <v-window-item value="pre_treatment">
                        <v-card prepend-icon="mdi-briefcase-edit" title="raw_water_tank" class="mb-3 rounded-lg">
                            <v-card-text>
                                <v-row>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.condition_of_raw_water_tank" density="compact"
                                            label="condition_of_raw_water_tank" hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.raw_water_tank_did_you_clean" density="compact"
                                            label="did_you_clean_with_the_entrepreneur_today" hide-details="auto" />
                                    </v-col>
                                </v-row>
                            </v-card-text>
                        </v-card>
                        <v-card prepend-icon="mdi-briefcase-edit" title="sand_filter_tank" class="mb-3 rounded-lg">
                            <v-card-text>
                                <v-row>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.condition_of_sand_filter_tank" density="compact"
                                            label="condition_of_sand_filter_tank" hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.sand_filter_last_backwash_date" density="compact"
                                            label="last_backwash_date" hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.sand_filter_frequency_of_the_backwash"
                                            density="compact" label="frequency_of_the_backwash" hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.sand_filter_cleaning_and_backwash_done"
                                            density="compact"
                                            label="cleaning_and_backwash_done_on_site_with_the_entrepeneur"
                                            hide-details="auto" />
                                    </v-col>
                                </v-row>
                            </v-card-text>
                        </v-card>
                        <v-card prepend-icon="mdi-briefcase-edit" title="ac_filter_tank" class="mb-3 rounded-lg">
                            <v-card-text>
                                <v-row>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.condition_of_ac_filter_tank" density="compact"
                                            label="condition_of_ac_filter_tank" hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.ac_filter_last_backwash_date" density="compact"
                                            label="last_backwash_date" hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.ac_filter_frequency_of_the_backwash" density="compact"
                                            label="frequency_of_the_backwash" hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.ac_filter_last_regeneration_or_sterilization_date"
                                            density="compact" label="last_regeneration_or_sterilization_date"
                                            hide-details="auto" />
                                    </v-col>
                                </v-row>
                                <v-row>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.ac_filter_cleaning_and_backwash_done"
                                            density="compact"
                                            label="cleaning_and_backwash_done_on_site_with_the_entrepeneur"
                                            hide-details="auto" />
                                    </v-col>
                                </v-row>
                            </v-card-text>
                        </v-card>
                        <v-card prepend-icon="mdi-briefcase-edit" title="Resin_filter_tank" class="mb-3 rounded-lg">
                            <v-card-text>
                                <v-row>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.condition_of_resin_filter_tank" density="compact"
                                            label="condition_of_ac_filter_tank" hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.resin_filter_last_backwash_date" density="compact"
                                            label="last_backwash_date" hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.resin_filter_frequency_of_the_backwash"
                                            density="compact" label="frequency_of_the_backwash" hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.resin_filter_last_regeneration_or_sterilization_date"
                                            density="compact" label="last_regeneration_or_sterilization_date"
                                            hide-details="auto" />
                                    </v-col>
                                </v-row>
                                <v-row>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.resin_filter_cleaning_and_backwash_done"
                                            density="compact"
                                            label="cleaning_and_backwash_done_on_site_with_the_entrepeneur"
                                            hide-details="auto" />
                                    </v-col>
                                </v-row>
                            </v-card-text>
                        </v-card>
                        <v-card prepend-icon="mdi-briefcase-edit" title="clear_water_tank" class="mb-3 rounded-lg">
                            <v-card-text>
                                <v-row>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.condition_of_clear_water_tank" density="compact"
                                            label="condition_of_clear_water_tank" hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.clear_water_tank_did_you_clean" density="compact"
                                            label="did_you_clean_with_the_entrepreneur_today" hide-details="auto" />
                                    </v-col>
                                </v-row>
                            </v-card-text>
                        </v-card>
                        <v-card prepend-icon="mdi-briefcase-edit" title="RO" class="mb-3 rounded-lg">
                            <v-card-text>
                                <v-row>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.condition_of_ro" density="compact"
                                            label="condition_of_ro" hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.ro_last_backwash_date" density="compact"
                                            label="last_backwash_date" hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.ro_frequently_of_the_backwash" density="compact"
                                            label="frequently_of_the_backwash" hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.ro_last_cip_date" density="compact"
                                            label="last_cip_date" hide-details="auto" />
                                    </v-col>
                                </v-row>
                                <v-row>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.ro_cleaning_and_backwash_done_on_site"
                                            density="compact"
                                            label="cleaning_and_backwash_done_on_site_with_the_entrepeneur"
                                            hide-details="auto" />
                                    </v-col>
                                </v-row>
                            </v-card-text>
                        </v-card>
                        <v-card prepend-icon="mdi-briefcase-edit" title="Ultrafiltration" class="mb-3 rounded-lg">
                            <v-card-text>
                                <v-row>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.condition_of_ultrafiltration" density="compact"
                                            label="condition_of_ultrafiltration" hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.ultrafiltration_last_backwash_date" density="compact"
                                            label="last_backwash_date" hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.ultrafiltration_frequency_of_the_backwash"
                                            density="compact" label="frequently_of_the_backwash" hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="3">
                                        <v-text-field
                                            v-model="pa.ultrafiltration_last_regeneration_or_sterilization_date"
                                            density="compact" label="last_regeneration_or_sterilization_date"
                                            hide-details="auto" />
                                    </v-col>
                                </v-row>
                                <v-row>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.ultrafiltration_cleaning_and_backwash_done"
                                            density="compact"
                                            label="cleaning_and_backwash_done_on_site_with_the_entrepeneur"
                                            hide-details="auto" />
                                    </v-col>
                                </v-row>
                            </v-card-text>
                        </v-card>
                        <v-card prepend-icon="mdi-briefcase-edit" title="pipe_network_of_the_pre-treatment"
                            class="mb-3 rounded-lg">
                            <v-card-text>
                                <v-row>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.are_pre_treatment_pipes_leaking" density="compact"
                                            label="is_pre-treatment_pipes_are_leaking" hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.are_pre_treatment_valves_broken" density="compact"
                                            label="is_pre-treatment_valves_are_broken" hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.did_you_repair_pretreatment_on_site" density="compact"
                                            label="did_you_repair_it_on_site" hide-details="auto" />
                                    </v-col>
                                </v-row>
                            </v-card-text>
                        </v-card>
                    </v-window-item>
                    <v-window-item value="Hygience">
                        <v-card prepend-icon="mdi-briefcase-edit" title="hygiene_outside_kiosk" class="mb-3 rounded-lg">
                            <v-card-text>
                                <v-row>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.is_it_clean_in_front_of_kiosk" density="compact"
                                            label="is_it_clean_in_front_of_kiosk" hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.did_you_clean_front_of_kiosk_w_entrepreneur"
                                            density="compact" label="did_you_clean_with_the_entrepreneur_today"
                                            hide-details="auto" />
                                    </v-col>
                                    <!-- <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.please_take_a_picture_in_front_of_kiosk"
                                            density="compact" label="please_take_a_picture_in_front_of_kiosk"
                                            hide-details="auto" />
                                    </v-col> -->
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.is_it_clean_behind_the_kiosk" density="compact"
                                            label="is_it_clean_behind_the_kiosk" hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.did_you_clean_behind_the_kiosk_with_the_enterpreneur"
                                            density="compact" label="did_you_clean_behind_with_the_entrepreneur_today"
                                            hide-details="auto" />
                                    </v-col>
                                </v-row>
                                <v-row>
                                    
                                    <!-- <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.take_a_picture_behind_kiosk" density="compact"
                                            label="take_a_picture_behind_kiosk" hide-details="auto" />
                                    </v-col> -->
                                </v-row>
                            </v-card-text>
                        </v-card>
                        <v-card prepend-icon="mdi-briefcase-edit" title="hygiene_inside_kiosk" class="mb-3 rounded-lg">
                            <v-card-text>
                                <v-row>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.is_the_pre_treatment_clean" density="compact"
                                            label="is_the_pre-treatment_clean" hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.did_you_clean_pre_treatment_with_the_entrepreneur"
                                            density="compact"
                                            label="did_you_clean_pre-treatment_with_the_entrepreneur_today"
                                            hide-details="auto" />
                                    </v-col>
                                    <!-- <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.please_take_a_picture_of_pre_treatment"
                                            density="compact" label="please_take_a_picture_of_pre-treatment"
                                            hide-details="auto" />
                                    </v-col> -->
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.is_it_clean_of_washing_bottle_area" density="compact"
                                            label="is_it_clean_of_washing_bottle_area" hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="3">
                                        <v-text-field
                                            v-model="pa.did_you_clean_washing_bottle_area_with_the_entrepreneur"
                                            density="compact"
                                            label="cleaning_washing_bottle_area_on_site_with_the_entrepeneur"
                                            hide-details="auto" />
                                    </v-col>
                                </v-row>
                                <v-row>
                                    
                                    <!-- <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.take_a_photo_of_washing_bottle_area" density="compact"
                                            label="take_a_photo_of_washing_bottle_area" hide-details="auto" />
                                    </v-col> -->
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.is_it_clean_bottling_area" density="compact"
                                            label="is_it_clean_bottling_area" hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="3">
                                        <v-text-field
                                            v-model="pa.did_you_clean_cleaning_bottle_area_with_the_entrepreneur"
                                            density="compact"
                                            label="did_you_clean_cleaning_bottle_area_with_the_entrepreneur_today"
                                            hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.is_kiosk_flooding_during_rainy_season"
                                            density="compact" label="is_it_clean_of_washing_bottle_area"
                                            hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.items_stored_no_linked_with_ts_in_or_nearby"
                                            density="compact" label="items_stored_no_linked_with_ts_in_or_nearby"
                                            hide-details="auto" />
                                    </v-col>
                                </v-row>
                                <v-row>
                                    <!-- <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.take_a_picture_of_bottling_area" density="compact"
                                            label="take_a_picture_of_bottling_area" hide-details="auto" />
                                    </v-col> -->
                                    
                                </v-row>
                            </v-card-text>
                        </v-card>
                        <v-card prepend-icon="mdi-briefcase-edit" title="chlorine" class="mb-3 rounded-lg">
                            <v-card-text>
                                <v-row>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.chlorine_bucket_for_bottle_disinfection"
                                            density="compact" label="chlorine_bucket_for_bottle_disinfection"
                                            hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.chlorine_bucket_for_caps_disinfection"
                                            density="compact" label="chlorine_bucket_for_caps_disinfection"
                                            hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.weighing_scale_2_kg" density="compact"
                                            label="weighing_scale_2_kg" hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.measuring_spoon" density="compact"
                                            label="measuring_spoon" hide-details="auto" />
                                    </v-col>
                                </v-row>
                            </v-card-text>
                        </v-card>
                    </v-window-item>
                    <v-window-item value="drinking_water_quality">
                        <v-card prepend-icon="mdi-briefcase-edit" title="conductivity." class="mb-3 rounded-lg">
                            <v-card-text>
                                <v-row>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.conductivity_raw_water" density="compact"
                                            label="raw_water" hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.conductivity_drinking_water" density="compact"
                                            label="drinking_water" hide-details="auto" />
                                    </v-col>
                                </v-row>
                            </v-card-text>
                        </v-card>
                        <v-card prepend-icon="mdi-briefcase-edit" title="PH" class="mb-3 rounded-lg">
                            <v-card-text>
                                <v-row>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.pH_raw_water" density="compact" label="raw_water"
                                            hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.pH_drinking_water" density="compact"
                                            label="drinking_water" hide-details="auto" />
                                    </v-col>
                                </v-row>
                            </v-card-text>
                        </v-card>
                        <v-card prepend-icon="mdi-briefcase-edit" title="TDS" class="mb-3 rounded-lg">
                            <v-card-text>
                                <v-row>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.TDS_raw_water" density="compact" label="raw_water"
                                            hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.TDS_drinking_water" density="compact"
                                            label="drinking_water" hide-details="auto" />
                                    </v-col>
                                </v-row>
                            </v-card-text>
                        </v-card>
                        <v-card prepend-icon="mdi-briefcase-edit" title="turbidity" class="mb-3 rounded-lg">
                            <v-card-text>
                                <v-row>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.Turbidity_raw_water" density="compact"
                                            label="raw_water" hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.Turbidity_drinking_water" density="compact"
                                            label="drinking_water" hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.what_is_taste_of_the_drinking_water" density="compact"
                                            label="what_is_taste_of_the_drinking_water" hide-details="auto" />
                                    </v-col>
                                </v-row>
                            </v-card-text>
                        </v-card>
                    </v-window-item>
                    <v-window-item value="Final_Treatment">
                        <v-card prepend-icon="mdi-briefcase-edit" title="UV lamp" class="mb-3 rounded-lg">
                            <v-card-text>
                                <v-row>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.maximum_flow_of_the_micro_filtration_pump"
                                            density="compact" label="maximum_flow_of_the_micro-filtration_pump"
                                            hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.set_the_maximum_flow_below_40_lpm" density="compact"
                                            label="set_the_maximum_flow_below_40_lpm" hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.uv_intensity" density="compact" label="uv_intensity"
                                            hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.uv_lamp_number_of_hours" density="compact"
                                            label="nnumber_of_hours" hide-details="auto" />
                                    </v-col>
                                </v-row>
                                <v-row>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.last_cleaning_of_the_uv_quartz_and_sensor"
                                            density="compact" label="last_cleaning_of_the_uv_quartz_and_sensor"
                                            hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.uv_quartz_and_sensor_cleaning_done_on_site_with_the_entrepeneur" density="compact"
                                            label="uv_quartz_and_sensor_cleaning_done_on_site" hide-details="auto" />
                                    </v-col>
                                </v-row>
                            </v-card-text>
                        </v-card>
                        <v-card prepend-icon="mdi-briefcase-edit" title="filter_50m" class="mb-3 rounded-lg">
                            <v-card-text>
                                <v-row>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.condition_of_50m_filter" density="compact"
                                            label="condition_of_50m_filter" hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.last_cartridge_change_50m_filter" density="compact"
                                            label="last_cartridge_change" hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="3">
                                        <v-text-field
                                            v-model="pa.replace_the_cartridge_filters_done_on_site_with_the_entrepeneur_50m_filter"
                                            density="compact" label="replace_the_cartridge_filters"
                                            hide-details="auto" />
                                    </v-col>
                                </v-row>
                            </v-card-text>
                        </v-card>
                        <v-card prepend-icon="mdi-briefcase-edit" title="filter_10m" class="mb-3 rounded-lg">
                            <v-card-text>
                                <v-row>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.condition_of_10m_filter" density="compact"
                                            label="condition_of_10m_filter" hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.last_cartridge_change_10m_filter" density="compact"
                                            label="last_cartridge_change" hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="3">
                                        <v-text-field
                                            v-model="pa.replace_the_cartridge_filters_done_on_site_with_the_entrepeneur_10m_filter"
                                            density="compact" label="replace_the_cartridge_filters"
                                            hide-details="auto" />
                                    </v-col>
                                </v-row>
                            </v-card-text>
                        </v-card>
                        <v-card prepend-icon="mdi-briefcase-edit" title="filter_5m" class="mb-3 rounded-lg">
                            <v-card-text>
                                <v-row>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.condition_of_5m_filter" density="compact"
                                            label="condition_of_5m_filter" hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.last_cartridge_change_5m_filter" density="compact"
                                            label="last_cartridge_change" hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="3">
                                        <v-text-field
                                            v-model="pa.replace_the_cartridge_filters_done_on_site_with_the_entrepeneur_5m_filter"
                                            density="compact" label="replace_the_cartridge_filters"
                                            hide-details="auto" />
                                    </v-col>
                                </v-row>
                            </v-card-text>
                        </v-card>
                        <v-card prepend-icon="mdi-briefcase-edit" title="filter_1m" class="mb-3 rounded-lg">
                            <v-card-text>
                                <v-row>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.condition_of_1m_filter" density="compact"
                                            label="condition_of_1m_filter" hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.last_cartridge_change_1m_filter" density="compact"
                                            label="last_cartridge_change" hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="3">
                                        <v-text-field
                                            v-model="pa.replace_the_cartridge_filters_done_on_site_with_the_entrepeneur_1m_filter"
                                            density="compact" label="replace_the_cartridge_filters"
                                            hide-details="auto" />
                                    </v-col>
                                </v-row>
                            </v-card-text>
                        </v-card>
                        <v-card prepend-icon="mdi-briefcase-edit" title="CIP" class="mb-3 rounded-lg">
                            <v-card-text>
                                <v-row>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.is_it_possible_to_perform_cip_on_pipes"
                                            density="compact" label="is_it_possible_to_perform_cip_on_pipes"
                                            hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.last_cip_date_on_pipes" density="compact"
                                            label="last_cip_date" hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.frequency_of_the_cip_on_pipes" density="compact"
                                            label="replace_the_cartridge_filters" hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.cip_done_on_site_with_the_entrepeneneur"
                                            density="compact" label="cip_done_on_site_with_the_entrepeneur"
                                            hide-details="auto" />
                                    </v-col>
                                </v-row>
                            </v-card-text>
                        </v-card>
                        <v-card prepend-icon="mdi-briefcase-edit" title="pipe_network_of_the_final_treatment"
                            class="mb-3 rounded-lg">
                            <v-card-text>
                                <v-row>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.is_final_treatment_pipes_are_leaking"
                                            density="compact" label="is_final-treatment_pipes_are_leaking"
                                            hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.is_final_treatment_valves_are_broken"
                                            density="compact" label="is_final-treatment_valves_are_broken"
                                            hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.did_you_repair_it_on_site_valves" density="compact"
                                            label="is_final-treatment_valves_are_broken" hide-details="auto" />
                                    </v-col>
                                </v-row>
                            </v-card-text>
                        </v-card>
                    </v-window-item>
                    <v-window-item value="Electricity">
                        <v-card prepend-icon="mdi-briefcase-edit" title="electric_cabinet" class="mb-3 rounded-lg">
                            <v-row>
                                <v-col cols="12" md="3">
                                    <v-text-field v-model="pa.condition_electrical_cabinet" density="compact"
                                        label="condition" hide-details="auto" />
                                </v-col>
                                <v-col cols="12" md="3">
                                    <v-text-field v-model="pa.did_you_repair_it_on_site_electrical_cabinet"
                                        density="compact" label="did_you_repair_it_on_site" hide-details="auto" />
                                </v-col>
                            </v-row>
                        </v-card>
                        <v-card prepend-icon="mdi-briefcase-edit" title="wiring" class="mb-3 rounded-lg">
                            <v-row>
                                <v-col cols="12" md="3">
                                    <v-text-field v-model="pa.condition_wiring" density="compact" label="wiring"
                                        hide-details="auto" />
                                </v-col>
                                <v-col cols="12" md="3">
                                    <v-text-field v-model="pa.did_you_repair_it_on_site_wiring" density="compact"
                                        label="did_you_repair_it_on_site" hide-details="auto" />
                                </v-col>
                            </v-row>
                        </v-card>
                        <v-card prepend-icon="mdi-briefcase-edit" title="micro-filtration_pump" class="mb-3 rounded-lg">
                            <v-row>
                                <v-col cols="12" md="3">
                                    <v-text-field v-model="pa.does_it_work_properly_micro_filtration_pump"
                                        density="compact" label="does_it_work_properly" hide-details="auto" />
                                </v-col>
                                <v-col cols="12" md="3">
                                    <v-text-field v-model="pa.did_you_repair_it_on_site_micro_filtration_pump"
                                        density="compact" label="did_you_repair_it_on_site" hide-details="auto" />
                                </v-col>
                                <!-- <v-col cols="12" md="3">
                                    <v-text-field v-model="pa.take_a_picture_micro_filtration" density="compact"
                                        label="take_a_picture" hide-details="auto" />
                                </v-col> -->
                            </v-row>
                        </v-card>
                        <v-card prepend-icon="mdi-briefcase-edit" title="raw_water_pump" class="mb-3 rounded-lg">
                            <v-row>
                                <v-col cols="12" md="3">
                                    <v-text-field v-model="pa.does_it_work_properly_raw_water_pump" density="compact"
                                        label="does_it_work_properly" hide-details="auto" />
                                </v-col>
                                <v-col cols="12" md="3">
                                    <v-text-field v-model="pa.did_you_repair_it_on_site_raw_water_pump"
                                        density="compact" label="did_you_repair_it_on_site" hide-details="auto" />
                                </v-col>
                                <!-- <v-col cols="12" md="3">
                                    <v-text-field v-model="pa.take_a_picture_raw_water_pump" density="compact"
                                        label="take_a_picture" hide-details="auto" />
                                </v-col> -->
                            </v-row>
                        </v-card>
                        <v-card prepend-icon="mdi-briefcase-edit" title="float_switch" class="mb-3 rounded-lg">
                            <v-row>
                                <v-col cols="12" md="3">
                                    <v-text-field v-model="pa.is_there_any_float_switch" density="compact"
                                        label="is_there_any_float_switch" hide-details="auto" />
                                </v-col>
                                <v-col cols="12" md="3">
                                    <v-text-field v-model="pa.does_it_work_properly_float_witch" density="compact"
                                        label="does_it_work_properly" hide-details="auto" />
                                </v-col>
                            </v-row>
                        </v-card>
                        <v-card prepend-icon="mdi-briefcase-edit" title="Solar" class="mb-3 rounded-lg">
                            <v-row>
                                <v-col cols="12" md="3">
                                    <v-text-field v-model="pa.condition_solar" density="compact" label="condition"
                                        hide-details="auto" />
                                </v-col>
                                <v-col cols="12" md="3">
                                    <v-text-field v-model="pa.cleaning_done_on_site_with_the_entrepeneur_solar"
                                        density="compact" label="cleaning_done_on_site_with_the_entrepeneur"
                                        hide-details="auto" />
                                </v-col>
                            </v-row>
                        </v-card>
                        <v-card prepend-icon="mdi-briefcase-edit" title="battery" class="mb-3 rounded-lg">
                            <v-row>
                                <v-col cols="12" md="3">
                                    <v-text-field v-model="pa.condition_battery" density="compact" label="condition"
                                        hide-details="auto" />
                                </v-col>
                                <v-col cols="12" md="3">
                                    <v-text-field v-model="pa.works_capacity_in_hours_battery" density="compact"
                                        label="works_capacity_in_hours" hide-details="auto" />
                                </v-col>
                            </v-row>
                        </v-card>
                        <v-card prepend-icon="mdi-briefcase-edit" title="satisfication" class="mb-3 rounded-lg">
                            <v-row>
                                <v-col cols="12" md="3">
                                    <v-text-field v-model="pa.is_the_entrepreneur_satisfied_with_teuksaats_services"
                                        density="compact" label="is_the_entrepreneur_satisfied_with_teuksaats_services"
                                        hide-details="auto" />
                                </v-col>
                                <v-col cols="12" md="3">
                                    <v-text-field v-model="pa.are_beneficiaries_satisfied_with_the_taste_of_owe_water"
                                        density="compact"
                                        label="are_beneficiaries_satisfied_with_the_taste_of_owe_water"
                                        hide-details="auto" />
                                </v-col>
                                <v-col cols="12" md="3">
                                    <v-text-field v-model="pa.comment" density="compact" label="comment"
                                        hide-details="auto" />
                                </v-col>
                            </v-row>
                        </v-card>
                    </v-window-item>
                </v-window>
            </v-card-text>
        </v-card>
        <!-- Add  -->
        <v-row class="ma-2" justify="center">

            <v-btn v-if="$store.state.user.permissions.includes('edit_technical')" prepend-icon="mdi-content-save"
                rounded="lg" color="primary" class="ma-4" size="large" type="submit">
                Save
            </v-btn>
        </v-row>
    </v-form>
</template>
<script>
import axios from 'axios';
export default {
    name: 'FormPa',
    data: function () {
        return {
            pa: {
                site: '',
                technician: '',
                date: '',
                main_person_the_water_kiosk_with_you: '',
                form_do_you_want_to_do: '',
                condition_of_raw_water_tank: '',
                raw_water_tank_did_you_clean: '',
                condition_of_sand_filter_tank: '',
                sand_filter_last_backwash_date: '',
                sand_filter_frequency_of_the_backwash: '',
                sand_filter_cleaning_and_backwash_done: '',
                condition_of_ac_filter_tank: '',
                ac_filter_last_backwash_date: '',
                ac_filter_frequency_of_the_backwash: '',
                ac_filter_last_regeneration_or_sterilization_date: '',
                ac_filter_cleaning_and_backwash_done: '',
                condition_of_resin_filter_tank: '',
                resin_filter_last_backwash_date: '',
                resin_filter_frequency_of_the_backwash: '',
                resin_filter_last_regeneration_or_sterilization_date: '',
                resin_filter_cleaning_and_backwash_done: '',
                condition_of_clear_water_tank: '',
                clear_water_tank_did_you_clean: '',
                condition_of_ro: '',
                ro_last_backwash_date: '',
                ro_frequently_of_the_backwash: '',
                ro_last_cip_date: '',
                ro_cleaning_and_backwash_done_on_site: '',
                condition_of_ultrafiltration: '',
                ultrafiltration_last_backwash_date: '',
                ultrafiltration_frequency_of_the_backwash: '',
                ultrafiltration_last_regeneration_or_sterilization_date: '',
                ultrafiltration_cleaning_and_backwash_done: '',
                are_pre_treatment_pipes_leaking: '',
                are_pre_treatment_valves_broken: '',
                did_you_repair_pretreatment_on_site: '',
                is_it_clean_in_front_of_kiosk: '',
                did_you_clean_front_of_kiosk_with_the_entrepreneur: '',
                please_take_a_picture_in_front_of_kiosk: '',
                is_it_clean_behind_the_kiosk: '',
                did_you_clean_behind_the_kiosk_with_the_entrepreneur: '',
                take_a_picture_behind_kiosk: '',
                is_the_pre_treatment_clean: '',
                did_you_clean_pre_treatment_with_the_entrepreneur: '',
                please_take_a_picture_of_pre_treatment: '',
                is_it_clean_of_washing_bottle_area: '',
                did_you_clean_washing_bottle_area_with_the_entrepreneur: '',
                take_a_photo_of_washing_bottle_area: '',
                is_it_clean_bottling_area: '',
                did_you_clean_cleaning_bottle_area_with_the_entrepreneur: '',
                take_a_picture_of_bottling_area: '',
                is_kiosk_flooding_during_rainy_season: '',
                items_stored_no_linked_with_ts_in_or_nearby: '',
                chlorine_bucket_for_bottle_disinfection: '',
                chlorine_bucket_for_caps_disinfection: '',
                weighing_scale_2_kg: '',
                measuring_spoon: '',
                conductivity_raw_water: '',
                conductivity_drinking_water: '',
                pH_raw_water: '',
                pH_drinking_water: '',
                TDS_raw_water: '',
                TDS_drinking_water: '',
                Turbidity_raw_water: '',
                Turbidity_drinking_water: '',
                what_is_taste_of_the_drinking_water: '',
                maximum_flow_of_the_micro_filtration_pump: '',
                set_the_maximum_flow_below_40_lpm: '',
                uv_intensity: '',
                uv_lamp_number_of_hours: '',
                last_cleaning_of_the_uv_quartz_and_sensor: '',
                uv_quartz_and_sensor_cleaning_done: '',
                condition_of_50m_filter: '',
                last_cartridge_change_50m_filter: '',
                replace_the_cartridge_filters_done_50m_filter: '',
                condition_of_10m_filter: '',
                last_cartridge_change_10m_filter: '',
                replace_the_cartridge_filters_done_10m_filter: '',
                condition_of_5m_filter: '',
                last_cartridge_change_5m_filter: '',
                replace_the_cartridge_filters_done_5m_filter: '',
                condition_of_1m_filter: '',
                last_cartridge_change_1m_filter: '',
                replace_the_cartridge_filters_done_1m_filter: '',
                is_it_possible_to_perform_cip_on_pipes: '',
                last_cip_date_on_pipes: '',
                frequency_of_the_cip_on_pipes: '',
                cip_done_on_pipes: '',
                is_final_treatment_pipes_are_leaking: '',
                is_final_treatment_valves_are_broken: '',
                did_you_repair_it_on_site_valves: '',
                condition_electrical_cabinet: '',
                did_you_repair_it_on_site_electrical_cabinet: '',
                condition_wiring: '',
                did_you_repair_it_on_site_wiring: '',
                does_it_work_properly_micro_filtration_pump: '',
                did_you_repair_it_on_site_micro_filtration_pump: '',
                take_a_picture_micro_filtration: '',
                does_it_work_properly_raw_water_pump: '',
                did_you_repair_it_on_site_raw_water_pump: '',
                take_a_picture_raw_water_pump: '',
                is_there_any_float_switch: '',
                does_it_work_properly_float_witch: '',
                condition_solar: '',
                cleaning_done_solar: '',
                condition_battery: '',
                works_capacity_in_hours_battery: '',
                is_the_entrepreneur_satisfied_with_teuksaats_services: '',
                are_beneficiaries_satisfied_with_the_taste_of_owe_water: '',
                comment:'',
            },
            get_staff_info: [],
            get_staff_previous_kpi: [],
            get_staff_training: [],
            getKPI: [],
            tab: null,
            a: '',
            required: [
                value => {
                    if (value) return true
                    return 'This field is required.'
                },
            ],
            checkNumber: [
                value => {
                    if (value && value <= 101) return true
                    return 'Score must be <= 100'
                }
            ],
            loading: true,
            edit: false,
        }
    },
    computed: {
    },
    watch: {

    },
    methods: {
        savePAForm(validationEvent) {
            validationEvent.then(result => {
                if (result.valid === true) {
                    if (this.$route.params.id) {
                        this.loading = true
                        axios.put("/api/formRoutine/update/" + this.$route.params.id, this.pa).then((response) => {
                            //    // console.log(response.data.result)
                            //         if(response.data.result)
                            //     {
                            //         alert(response.data.result)
                            //     }
                            this.$router.go(-1)
                        }).catch(() => {
                        })
                        this.loading = false;
                    }
                    else {
                        // this.loading = true
                        // axios.post('/api/pa/store', this.pa).then((response) => {
                        //     this.$router.go(-1)
                        // }).catch(() => {
                        // })
                        // this.loading = false;
                    }
                }
            })
        },

    },
    mounted() {
        if (this.$route.params.id) {
            axios.get("/api/formRoutine/" + this.$route.params.id).then(response => {
                this.pa = response.data.result;
            })
        }
    }
}

</script>
<style>
.headerStyle {
    color: blueviolet;
}
</style>