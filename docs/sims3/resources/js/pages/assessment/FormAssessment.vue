<template>
    <v-form class="bg-grey-lighten-1 pa-4" @submit.prevent="savePAForm">
        <v-card>
            <v-tabs v-model="tab" bg-color="primary">
                <v-tab value="basic_info">Basic Info</v-tab>
                <v-tab value="solar_panel">Solar Panel</v-tab>
                <v-tab value="Pretreatment">Pretreatment</v-tab>
                <v-tab value="Final_Treatment">Final Treatment</v-tab>
                <v-tab value="bottle_washing">Bottle Washing</v-tab>
            </v-tabs>
            <v-card-text>
                <v-window v-model="tab">
                    <v-window-item value="basic_info">
                        <v-card prepend-icon="mdi-briefcase-edit" title="Basic Information" class="mb-3 rounded-lg">
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
                                        <v-text-field v-model="pa.date_form" density="compact" label="date"
                                            hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.main_person_the_water_kiosk" density="compact"
                                            label="main_person_the_water_kiosk" hide-details="auto" />
                                    </v-col>
                                </v-row>
                                <v-row>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.form_do_you_want_to_do" density="compact"
                                            label="form_do_you_want_to_do" hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.first_site_assessment" density="compact"
                                            label="first_site_assessment" hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.which_part_do_you_want_to_modify" density="compact"
                                            label="which_part_do_you_want_to_modify" hide-details="auto" />
                                    </v-col>
                                </v-row>
                            </v-card-text>
                        </v-card>
                        <v-card prepend-icon="mdi-briefcase-edit" title="Water Source" class="mb-3 rounded-lg">
                            <v-card-text>
                                <v-row>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.main_source_of_water" density="compact"
                                            label="main_source_of_water" hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.second_source_of_water" density="compact"
                                            label="second_source_of_water" hide-details="auto" />
                                    </v-col>
                                </v-row>
                            </v-card-text>
                        </v-card>

                        <v-card prepend-icon="mdi-briefcase-edit" title="Electricity Source" class="mb-3 rounded-lg">
                            <v-card-text>
                                <v-row>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.main_source_of_electricity" density="compact"
                                            label="main_source_of_electricity" hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.electric_cabinet" density="compact"
                                            label="electric_cabinet" hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.initial_installation_or_last_change" density="compact"
                                            label="initial_installation_or_last_change" hide-details="auto" />
                                    </v-col>
                                </v-row>

                            </v-card-text>
                        </v-card>
                        <v-card prepend-icon="mdi-briefcase-edit" title="Stabilizer" class="mb-3 rounded-lg">
                            <v-card-text>
                                <v-row>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.ground_cable" density="compact" label="ground_cable"
                                            hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.stabilizer" density="compact" label="stabilizer"
                                            hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.last_change_stabilizer" density="compact"
                                            label="last_change_stabilizer" hide-details="auto" />
                                    </v-col>
                                </v-row>
                            </v-card-text>
                        </v-card>
                    </v-window-item>
                    <v-window-item value="solar_panel">
                        <v-card prepend-icon="mdi-briefcase-edit" title="Solar Panel" class="mb-3 rounded-lg">
                            <v-card-text>
                                <v-row>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.solar_panel" density="compact" label="solar_panel"
                                            hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.date_installation_solar_panel" density="compact"
                                            label="date_of_initial_installation" hide-details="auto" />
                                    </v-col>
                                </v-row>
                            </v-card-text>
                        </v-card>

                        <v-card prepend-icon="mdi-briefcase-edit" title="Solar Charge Controller"
                            class="mb-3 rounded-lg">
                            <v-card-text>
                                <v-row>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.solar_charge_controller" density="compact"
                                            label="solar_charge_controller" hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.date_change_solar_charge_controller" density="compact"
                                            label="date_change_solar_charge_controller" hide-details="auto" />
                                    </v-col>
                                </v-row>
                            </v-card-text>
                        </v-card>

                        <v-card prepend-icon="mdi-briefcase-edit" title="Battery" class="mb-3 rounded-lg">
                            <v-card-text>
                                <v-row>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.condition_batteries" density="compact"
                                            label="condition_batteries" hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.date_last_change_batteries" density="compact"
                                            label="date_last_change_batteries" hide-details="auto" />
                                    </v-col>
                                </v-row>
                            </v-card-text>
                        </v-card>
                        <v-card prepend-icon="mdi-briefcase-edit" title="Inverter" class="mb-3 rounded-lg">
                            <v-card-text>
                                <v-row>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.condition_inverter_dc_to_ac" density="compact"
                                            label="condition_inverter_dc_to_ac" hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.date_change_inverter" density="compact"
                                            label="date_change_inverter" hide-details="auto" />
                                    </v-col>
                                </v-row>
                            </v-card-text>
                        </v-card>
                    </v-window-item>
                    <v-window-item value="Pretreatment">
                        <v-card prepend-icon="mdi-briefcase-edit" title="Pre-Treatment Process" class="mb-3 rounded-lg">
                            <v-card-text>
                                <v-row>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.pre_treatment_process_1" density="compact"
                                            label="pre-treatment_process_number_1" hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.pre_treatment_process_2" density="compact"
                                            label="pre-treatment_number_2" hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.pre_treatment_process_3" density="compact"
                                            label="pre-treatment_.number_3" hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.pre_treatment_process_4" density="compact"
                                            label="pre-treatment_number_4" hide-details="auto" />
                                    </v-col>
                                </v-row>
                                <v-row>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.pre_treatment_process_5" density="compact"
                                            label="pre-treatment_number_5" hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.pre_treatment_process_6" density="compact"
                                            label="pre-treatment_number_6" hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.pre_treatment_process_7" density="compact"
                                            label="pre-treatment_number_7" hide-details="auto" />
                                    </v-col>
                                </v-row>
                            </v-card-text>
                        </v-card>
                        <v-card
                            v-if="pa.pre_treatment_process_1 == 'ធុងទឹកឆៅ/Raw water tank' || pa.pre_treatment_process_2 == 'ធុងទឹកឆៅ/Raw water tank' || pa.pre_treatment_process_3 == 'ធុងទឹកឆៅ/Raw water tank' ||
                                pa.pre_treatment_process_4 == 'ធុងទឹកឆៅ/Raw water tank' || pa.pre_treatment_process_5 == 'ធុងទឹកឆៅ/Raw water tank' || pa.pre_treatment_process_6 == 'ធុងទឹកឆៅ/Raw water tank' || pa.pre_treatment_process_7 == 'ធុងទឹកឆៅ/Raw water tank'"
                            prepend-icon="mdi-briefcase-edit" title="Raw Water Tank" class="mb-3 rounded-lg">
                            <v-card-text>
                                <v-row>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.type_of_raw_water_tank" density="compact"
                                            label="type_of_water_tank" hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.raw_water_tank_h_cm" density="compact" label="h_cm"
                                            hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.raw_water_tank_d_cm" density="compact" label="d_cm"
                                            hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.raw_water_tank_v_liter" density="compact"
                                            label="v_liter" hide-details="auto" />
                                    </v-col>
                                </v-row>
                            </v-card-text>
                        </v-card>
                        <v-card
                            v-if="pa.pre_treatment_process_1 == 'ចម្រោះខ្សាច់/Sand filter' || pa.pre_treatment_process_2 == 'ចម្រោះខ្សាច់/Sand filter' || pa.pre_treatment_process_3 == 'ចម្រោះខ្សាច់/Sand filter' ||
                                pa.pre_treatment_process_4 == 'ចម្រោះខ្សាច់/Sand filter' || pa.pre_treatment_process_5 == 'ចម្រោះខ្សាច់/Sand filter' || pa.pre_treatment_process_6 == 'ចម្រោះខ្សាច់/Sand filter' || pa.pre_treatment_process_7 == 'ចម្រោះខ្សាច់/Sand filter'"
                            prepend-icon="mdi-briefcase-edit" title="Sand Filter" class="mb-3 rounded-lg">
                            <v-card-text>
                                <v-row>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.type_of_sand_filter_tank" density="compact"
                                            label="type_of_sand_filter_tank" hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.sand_filter_tank_h_cm" density="compact" label="h_cm"
                                            hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.sand_filter_tank_d_cm" density="compact" label="d_cm"
                                            hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.sand_filter_tank_v_liter" density="compact"
                                            label="v_iter" hide-details="auto" />
                                    </v-col>
                                </v-row>
                                <v-row>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.sand_filter_tank__height_from_the_top_cm"
                                            density="compact" label="the_height_from_the_top_cm" hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.date_change_sand_filter_tank" density="compact"
                                            label="date_change_sand_filter_tank" hide-details="auto" />
                                    </v-col>
                                </v-row>
                            </v-card-text>
                        </v-card>
                        <!-- Sand & Zmag -->
                        <v-card
                            v-if="pa.pre_treatment_process_1 == 'ប្រភេទនៃធុងចម្រោះខ្សាច់ & zmax/ type_of_sand_and_zmax' || pa.pre_treatment_process_2 == 'ប្រភេទនៃធុងចម្រោះខ្សាច់ & zmax/ type_of_sand_and_zmax' || pa.pre_treatment_process_3 == 'ប្រភេទនៃធុងចម្រោះខ្សាច់ & zmax/ type_of_sand_and_zmax' ||
                                pa.pre_treatment_process_4 == 'ប្រភេទនៃធុងចម្រោះខ្សាច់ & zmax/ type_of_sand_and_zmax' || pa.pre_treatment_process_5 == 'ប្រភេទនៃធុងចម្រោះខ្សាច់ & zmax/ type_of_sand_and_zmax' || pa.pre_treatment_process_6 == 'ប្រភេទនៃធុងចម្រោះខ្សាច់ & zmax/ type_of_sand_and_zmax' || pa.pre_treatment_process_7 == 'ប្រភេទនៃធុងចម្រោះខ្សាច់ & zmax/ type_of_sand_and_zmax'"
                            prepend-icon="mdi-briefcase-edit" title="Sand Filter & Zmag" class="mb-3 rounded-lg">
                            <v-card-text>
                                <v-row>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.type_of_sand_filter_and_Zmag_tank" density="compact"
                                            label="type_of_sand_filter_and_Zmag_tank" hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.sand_filter_and_zmag_d_cm" density="compact"
                                            label="h_cm" hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.sand_filter_and_zmag_h_cm" density="compact"
                                            label="d_cm" hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.sand_filter_and_zmag_v_iter" density="compact"
                                            label="v_iter" hide-details="auto" />
                                    </v-col>
                                </v-row>
                                <v-row>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.sand_filter_and_zmag_the_height_from_the_top_cm"
                                            density="compact" label="the_height_from_the_top_cm" hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.sand_filter_and_zmag_date_change_sand_filter_tank"
                                            density="compact" label="date_change_sand_filter_and_Zmag_tank"
                                            hide-details="auto" />
                                    </v-col>
                                </v-row>
                            </v-card-text>
                        </v-card>
                        <!-- AFM -->
                        <v-card
                            v-if="pa.pre_treatment_process_1 == 'AFM Filter' || pa.pre_treatment_process_2 == 'AFM Filter' || pa.pre_treatment_process_3 == 'AFM Filter' ||
                                pa.pre_treatment_process_4 == 'AFM Filter' || pa.pre_treatment_process_5 == 'AFM Filter' || pa.pre_treatment_process_6 == 'AFM Filter' || pa.pre_treatment_process_7 == 'AFM Filter'"
                            prepend-icon="mdi-briefcase-edit" title="AFM Tank" class="mb-3 rounded-lg">
                            <v-card-text>
                                <v-row>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.type_of_afm" density="compact" label="type_of_afm"
                                            hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.afm_d_cm" density="compact" label="d_cm"
                                            hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.afm_h_cm" density="compact" label="h_cm"
                                            hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.afm_v_iter" density="compact" label="v_iter"
                                            hide-details="auto" />
                                    </v-col>
                                </v-row>
                                <v-row>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.afm_the_height_from_the_top_cm" density="compact"
                                            label="the_height_from_the_top_cm" hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.afm_date_change_sand_filter_tank" density="compact"
                                            label="date_change_sand_filter_tank" hide-details="auto" />
                                    </v-col>
                                </v-row>
                            </v-card-text>
                        </v-card>
                        <!-- ZMag-->
                        <v-card
                            v-if="pa.pre_treatment_process_1 == 'ZMag zeolite' || pa.pre_treatment_process_2 == 'ZMag zeolite' || pa.pre_treatment_process_3 == 'ZMag zeolite' ||
                                pa.pre_treatment_process_4 == 'ZMag zeolite' || pa.pre_treatment_process_5 == 'ZMag zeolite' || pa.pre_treatment_process_6 == 'ZMag zeolite' || pa.pre_treatment_process_7 == 'ZMag zeolite'"
                            prepend-icon="mdi-briefcase-edit" title="ZMag" class="mb-3 rounded-lg">
                            <v-card-text>
                                <v-row>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.type_of_Zmag" density="compact" label="type_of_Zmag"
                                            hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.zmag_d_cm" density="compact" label="d_cm"
                                            hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.zmag_h_cm" density="compact" label="h_cm"
                                            hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.zmag_v_iter" density="compact" label="v_liter"
                                            hide-details="auto" />
                                    </v-col>
                                </v-row>
                                <v-row>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.zmag_the_height_from_the_top_cm" density="compact"
                                            label="the_height_from_the_top_cm" hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.zmag_date_change_sand_filter_tank" density="compact"
                                            label="date_change_sand_filter_tank" hide-details="auto" />
                                    </v-col>
                                </v-row>
                            </v-card-text>
                        </v-card>
                        <v-card
                            v-if="pa.pre_treatment_process_1 == 'ចម្រោះធ្យូង/Activated Carbon filter' || pa.pre_treatment_process_2 == 'ចម្រោះធ្យូង/Activated Carbon filter' || pa.pre_treatment_process_3 == 'ចម្រោះធ្យូង/Activated Carbon filter' ||
                                pa.pre_treatment_process_4 == 'ចម្រោះធ្យូង/Activated Carbon filter' || pa.pre_treatment_process_5 == 'ចម្រោះធ្យូង/Activated Carbon filter' || pa.pre_treatment_process_6 == 'ចម្រោះធ្យូង/Activated Carbon filter' || pa.pre_treatment_process_7 == 'ចម្រោះធ្យូង/Activated Carbon filter'"
                            prepend-icon="mdi-briefcase-edit" title="AC Filter" class="mb-3 rounded-lg">
                            <v-card-text>
                                <v-row>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.type_of_ac_filter_tank" density="compact"
                                            label="type_of_ac_filter_tank" hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.ac_filter_tank_h_cm" density="compact" label="h_cm"
                                            hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.ac_filter_tank_d_cm" density="compact" label="d_cm"
                                            hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.ac_filter_tank_v_liter" density="compact"
                                            label="ac_filter_tank.v_m" hide-details="auto" />
                                    </v-col>
                                </v-row>
                                <v-row>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.ac_filter_tank_media_height_from_the_top"
                                            density="compact" label="media_height_from_the_top" hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.date_change_ac_filter_tank" density="compact"
                                            label="date_change_ac_filter_tank" hide-details="auto" />
                                    </v-col>
                                </v-row>
                            </v-card-text>
                        </v-card>
                        <v-card
                            v-if="pa.pre_treatment_process_1 == 'ចម្ររ៉េស៊ីន/Resin filter' || pa.pre_treatment_process_2 == 'ចម្ររ៉េស៊ីន/Resin filter' || pa.pre_treatment_process_3 == 'ចម្ររ៉េស៊ីន/Resin filter' ||
                                pa.pre_treatment_process_4 == 'ចម្ររ៉េស៊ីន/Resin filter' || pa.pre_treatment_process_5 == 'ចម្ររ៉េស៊ីន/Resin filter' || pa.pre_treatment_process_6 == 'ចម្ររ៉េស៊ីន/Resin filter' || pa.pre_treatment_process_7 == 'ចម្ររ៉េស៊ីន/Resin filter'"
                            prepend-icon="mdi-briefcase-edit" title="Resin Filter" class="mb-3 rounded-lg">
                            <v-card-text>
                                <v-row>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.type_of_resin_filter_tank" density="compact"
                                            label="type_of_resin_filter_tank" hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.resin_filter_tank_h_cm" density="compact" label="h_cm"
                                            hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.resin_filter_tank_d_cm" density="compact" label="d_cm"
                                            hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.resin_filter_tank_v_liter" density="compact"
                                            label="resin_filter_tank.v_m" hide-details="auto" />
                                    </v-col>
                                </v-row>
                                <v-row>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.resin_filter_tank_media_height_from_the_top"
                                            density="compact" label="media_height_from_the_top" hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.date_change_resin_filter_tank" density="compact"
                                            label="date_change_resin_filter_tank" hide-details="auto" />
                                    </v-col>
                                </v-row>
                            </v-card-text>
                        </v-card>
                        <v-card
                            v-if="pa.pre_treatment_process_1 == 'ធុងទឹកថ្លា/Clear water tank' || pa.pre_treatment_process_2 == 'ធុងទឹកថ្លា/Clear water tank' || pa.pre_treatment_process_3 == 'ធុងទឹកថ្លា/Clear water tank' ||
                                pa.pre_treatment_process_4 == 'ធុងទឹកថ្លា/Clear water tank' || pa.pre_treatment_process_5 == 'ធុងទឹកថ្លា/Clear water tank' || pa.pre_treatment_process_6 == 'ធុងទឹកថ្លា/Clear water tank' || pa.pre_treatment_process_7 == 'ធុងទឹកថ្លា/Clear water tank'"
                            prepend-icon="mdi-briefcase-edit" title="Clear Water Tank" class="mb-3 rounded-lg">
                            <v-card-text>
                                <v-row>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.type_of_clear_water_tank" density="compact"
                                            label="type_of_clear_water_tank" hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.clear_water_tank_h_cm" density="compact" label="h_cm"
                                            hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.clear_water_tank_d_cm" density="compact" label="d_cm"
                                            hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.clear_water_tank_v_liter" density="compact"
                                            label="v_m" hide-details="auto" />
                                    </v-col>
                                </v-row>
                            </v-card-text>
                        </v-card>
                        <v-card prepend-icon="mdi-briefcase-edit" title="Flocculation" class="mb-3 rounded-lg">
                            <v-card-text>
                                <v-row>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.flocculation_and_coagulation_process"
                                            density="compact" label="flocculation_and_coagulation_process"
                                            hide-details="auto" />
                                    </v-col>
                                </v-row>
                            </v-card-text>
                        </v-card>
                        <v-card prepend-icon="mdi-briefcase-edit" title="Reverse Osmose" class="mb-3 rounded-lg">
                            <v-card-text>
                                <v-row>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.reverse_osmose" density="compact"
                                            label="reverse_osmose" hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.date_change_reverse_osmose" density="compact"
                                            label="date_change" hide-details="auto" />
                                    </v-col>
                                </v-row>
                            </v-card-text>
                        </v-card>
                        <v-card
                            v-if="pa.pre_treatment_process_1 == 'ចម្រោះ UF/Ultrafiltration' || pa.pre_treatment_process_2 == 'ចម្រោះ UF/Ultrafiltration' || pa.pre_treatment_process_3 == 'ចម្រោះ UF/Ultrafiltration' ||
                                pa.pre_treatment_process_4 == 'ចម្រោះ UF/Ultrafiltration' || pa.pre_treatment_process_5 == 'ចម្រោះ UF/Ultrafiltration' || pa.pre_treatment_process_6 == 'ចម្រោះ UF/Ultrafiltration' || pa.pre_treatment_process_7 == 'ចម្រោះ UF/Ultrafiltration'"
                            prepend-icon="mdi-briefcase-edit" title="UF" class="mb-3 rounded-lg">
                            <v-card-text>
                                <v-row>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.ultrafiltration" density="compact"
                                            label="ultrafiltration" hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.date_change_ultrafiltration" density="compact"
                                            label="ultrafiltration" hide-details="auto" />
                                    </v-col>
                                </v-row>
                            </v-card-text>
                        </v-card>
                        <v-card prepend-icon="mdi-briefcase-edit" title="Raw Water Pump" class="mb-3 rounded-lg">
                            <v-card-text>
                                <v-row>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.raw_water_pump" density="compact"
                                            label="raw_water_pump" hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.raw_water_pump_maximum_flow" density="compact"
                                            label="maximum_flow_water_pump" hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.raw_water_pump_height_hmax" density="compact"
                                            label="height_hmax_raw_water_pump" hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.raw_water_pump_power" density="compact"
                                            label="power_raw_water_pump" hide-details="auto" />
                                    </v-col>
                                </v-row>
                            </v-card-text>
                        </v-card>
                        <v-card prepend-icon="mdi-briefcase-edit" title="Back Wash Pump" class="mb-3 rounded-lg">
                            <v-card-text>
                                <v-row>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.back_wash_pump" density="compact"
                                            label="back_wash_pump" hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.back_wash_pump_flow_qmax" density="compact"
                                            label="maximum_flow_water_pump" hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.back_wash_pump_height_hmax" density="compact"
                                            label="height_hmax_raw_water_pump" hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.back_wash_pump_power" density="compact"
                                            label="power_raw_water_pump" hide-details="auto" />
                                    </v-col>
                                </v-row>
                            </v-card-text>
                        </v-card>
                        <v-card
                            v-if="pa.pre_treatment_process_1 == 'ចម្រោះ R.O/Reverse Osmose' || pa.pre_treatment_process_2 == 'ចម្រោះ R.O/Reverse Osmose' || pa.pre_treatment_process_3 == 'ចម្រោះ R.O/Reverse Osmose' ||
                                pa.pre_treatment_process_4 == 'ចម្រោះ R.O/Reverse Osmose' || pa.pre_treatment_process_5 == 'ចម្រោះ R.O/Reverse Osmose' || pa.pre_treatment_process_6 == 'ចម្រោះ R.O/Reverse Osmose' || pa.pre_treatment_process_7 == 'ចម្រោះ R.O/Reverse Osmose'"
                            prepend-icon="mdi-briefcase-edit" title="reverse_osmose_pump" class="mb-3 rounded-lg">
                            <v-card-text>
                                <v-row>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.reverse_osmose_pump" density="compact"
                                            label="reverse_osmose_pump" hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.reverse_osmose_pump_flow_qmax" density="compact"
                                            label="flow_qmax_reverse_osmose_pump" hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.reverse_osmose_pump_height_hmax" density="compact"
                                            label="height_hmax_reverse_osmose_pump" hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.reverse_osmose_pump_power" density="compact"
                                            label="power_reverse_osmose_pump" hide-details="auto" />
                                    </v-col>
                                </v-row>
                            </v-card-text>
                        </v-card>
                    </v-window-item>
                    <v-window-item value="Final_Treatment">
                        <v-card prepend-icon="mdi-briefcase-edit" title="Filter 50m" class="mb-3 rounded-lg">
                            <v-card-text>
                                <v-row>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.filter_50_item" density="compact"
                                            label="item 50µm Filter" hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.date_change_filter_50" density="compact"
                                            label="date_change_50m_filter" hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.filter_50_condition" density="compact"
                                            label="condition" hide-details="auto" />
                                    </v-col>
                                </v-row>
                            </v-card-text>
                        </v-card>
                        <v-card prepend-icon="mdi-briefcase-edit" title="Filter 10m" class="mb-3 rounded-lg">
                            <v-card-text>
                                <v-row>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.filter_10_item" density="compact"
                                            label="item_10m_filter" hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.date_change_10m_filter" density="compact"
                                            label="date_change_10m_filter" hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.filter_10_condition" density="compact"
                                            label="condition" hide-details="auto" />
                                    </v-col>
                                </v-row>
                            </v-card-text>
                        </v-card>
                        <v-card prepend-icon="mdi-briefcase-edit" title="Filter 5m" class="mb-3 rounded-lg">
                            <v-card-text>
                                <v-row>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.item_5m_filter" density="compact"
                                            label="item_5m_filter" hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.date_change_5m_filter" density="compact"
                                            label="date_change_5m_filter" hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.filter_5_condition" density="compact"
                                            label="condition" hide-details="auto" />
                                    </v-col>
                                </v-row>
                            </v-card-text>
                        </v-card>
                        <v-card prepend-icon="mdi-briefcase-edit" title="Filter 1m" class="mb-3 rounded-lg">
                            <v-card-text>
                                <v-row>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.item_1m_filter" density="compact"
                                            label="item_1m_filter" hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.date_change_1m_filter" density="compact"
                                            label="date_change_1m_filter" hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.filter_1_condition" density="compact"
                                            label="condition" hide-details="auto" />
                                    </v-col>
                                </v-row>
                            </v-card-text>
                        </v-card>
                        <v-card prepend-icon="mdi-briefcase-edit" title="UV Lamp" class="mb-3 rounded-lg">
                            <v-card-text>
                                <v-row>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.uv_lamp" density="compact" label="uv_lamp"
                                            hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.date_change_uv_lamp" density="compact"
                                            label="date_change_uv_lamp" hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.uv_lamp_condition" density="compact" label="condition"
                                            hide-details="auto" />
                                    </v-col>
                                </v-row>
                            </v-card-text>
                        </v-card>
                        <v-card prepend-icon="mdi-briefcase-edit" title="UV Controller" class="mb-3 rounded-lg">
                            <v-card-text>
                                <v-row>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.uv_controller" density="compact" label="uv_controller"
                                            hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.date_change_uv_controller" density="compact"
                                            label="date_change_uv_controller" hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.uv_controller_condition" density="compact"
                                            label="condition" hide-details="auto" />
                                    </v-col>
                                </v-row>
                            </v-card-text>
                        </v-card>
                        <v-card prepend-icon="mdi-briefcase-edit" title="UV Ballast" class="mb-3 rounded-lg">
                            <v-card-text>
                                <v-row>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.uv_ballast" density="compact" label="uv_ballast"
                                            hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.date_change_uv_ballast" density="compact"
                                            label="date_change_uv_ballast" hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.uv_ballast_condition" density="compact"
                                            label="condition" hide-details="auto" />
                                    </v-col>
                                </v-row>
                            </v-card-text>
                        </v-card>
                        <v-card prepend-icon="mdi-briefcase-edit" title="UV Sensor" class="mb-3 rounded-lg">
                            <v-card-text>
                                <v-row>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.uv_sensor" density="compact" label="uv_sensor"
                                            hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.date_change_uv_sensor" density="compact"
                                            label="date_change_uv_sensor" hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.uv_sensor_condition" density="compact"
                                            label="condition" hide-details="auto" />
                                    </v-col>
                                </v-row>
                            </v-card-text>
                        </v-card>
                        <v-card prepend-icon="mdi-briefcase-edit" title="CIP" class="mb-3 rounded-lg">
                            <v-card-text>
                                <v-row>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.l_tank_for_cip" density="compact"
                                            label="l_tank_for_cip" hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.date_change_200l_tank_for_cip" density="compact"
                                            label="date_change_200l_tank_for_cip" hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.l_tank_for_cip_condition" density="compact"
                                            label="condition" hide-details="auto" />
                                    </v-col>
                                </v-row>
                            </v-card-text>
                        </v-card>
                        <v-card prepend-icon="mdi-briefcase-edit" title="Micro Filter Pump" class="mb-3 rounded-lg">
                            <v-card-text>
                                <v-row>
                                    <v-col cols="12" md="2">
                                        <v-text-field v-model="pa.micro_filter_pump" density="compact"
                                            label="micro-filter_pump" hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.micro_filter_pump_maximum_flow_qmax_lpm"
                                            density="compact" label="maximum_flow_qmax_lpm" hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.micro_filter_pump_maximum_height_hmax_m"
                                            density="compact" label="maximum_height_hmax_m" hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="2">
                                        <v-text-field v-model="pa.micro_filter_pump_power_kwhp" density="compact"
                                            label="power_kwhp" hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="2">
                                        <v-text-field v-model="pa.micro_filter_pump_voltage_v" density="compact"
                                            label="voltage_v" hide-details="auto" />
                                    </v-col>
                                </v-row>
                            </v-card-text>
                        </v-card>
                    </v-window-item>
                    <v-window-item value="bottle_washing">
                        <v-card prepend-icon="mdi-briefcase-edit" title="Bottle Shelf" class="mb-3 rounded-lg">
                            <v-card-text>
                                <v-row>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.bottle_washing_area_dirty_bottle_shelf"
                                            density="compact" label="dirty_bottle_shelf" hide-details="auto" />
                                    </v-col>
                                </v-row>
                            </v-card-text>
                        </v-card>
                        <v-card prepend-icon="mdi-briefcase-edit" title="Bottle Washing Area" class="mb-3 rounded-lg">
                            <v-card-text>
                                <v-row>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.bottle_washing_area_washing_station" density="compact"
                                            label="washing_station" hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="3">
                                        <v-text-field
                                            v-model="pa.bottle_washing_area_specific_tank_for_lid_disinfection"
                                            density="compact" label="specific_tank_for_lid_disinfection"
                                            hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.bottle_washing_area_chlorine_tank" density="compact"
                                            label="chlorine_tank" hide-details="auto" />
                                    </v-col>
                                </v-row>
                            </v-card-text>
                        </v-card>
                        <v-card prepend-icon="mdi-briefcase-edit" title="Rinsing Station" class="mb-3 rounded-lg">
                            <v-card-text>
                                <v-row>
                                    <v-col cols="12" md="3">
                                        <v-text-field
                                            v-model="pa.bottle_washing_area_disinfection_bottle_shelf_or_table_storage"
                                            density="compact" label="disinfection_bottle_shelf_or_table_storage"
                                            hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.bottle_washing_area_rinsing_station" density="compact"
                                            label="rinsing_station" hide-details="auto" />
                                    </v-col>
                                </v-row>
                            </v-card-text>
                        </v-card>
                        <v-card prepend-icon="mdi-briefcase-edit" title="Filling Station" class="mb-3 rounded-lg">
                            <v-card-text>
                                <v-row>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.filling_area_filling_station" density="compact"
                                            label="filling_station" hide-details="auto" />
                                    </v-col>
                                </v-row>
                            </v-card-text>
                        </v-card>
                        <v-card prepend-icon="mdi-briefcase-edit" title="Poster" class="mb-3 rounded-lg">
                            <v-card-text>
                                <v-row>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.poster_for_om_poster_for_om" density="compact"
                                            label="poster_for_om" hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.poster_for_om_date_change" density="compact"
                                            label="date_change" hide-details="auto" />
                                    </v-col>
                                </v-row>
                            </v-card-text>
                        </v-card>
                        <v-card prepend-icon="mdi-briefcase-edit" title="Tramsportation" class="mb-3 rounded-lg">
                            <v-card-text>
                                <v-row>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.how_many_transportation_do_you_have" density="compact"
                                            label="how_many_transportation_do_you_have" hide-details="auto" />
                                    </v-col>
                                </v-row>
                            </v-card-text>
                        </v-card>
                    </v-window-item>
                </v-window>
            </v-card-text>
        </v-card>
        <!-- Add  -->
        <v-row class="ma-2" justify="center">
            <v-btn prepend-icon="mdi-cancel" rounded="lg" color="error" class="ma-4" size="large"
                @click="$router.go(-1)">
                Cancel
            </v-btn>
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
                date_form: '',
                main_person_the_water_kiosk: '',
                form_do_you_want_to_do: '',
                first_site_assessment: '',
                which_part_do_you_want_to_modify: '',
                main_source_of_water: '',
                main_source_of_electricity: '',
                second_source_of_water: '',
                electric_cabinet: '',
                initial_installation_or_last_change: '',
                ground_cable: '',
                stabilizer: '',
                last_change_stabilizer: '',
                solar_panel: '',
                date_installation_solar_panel: '',
                solar_charge_controller: '',
                date_change_solar_charge_controller: '',
                condition_batteries: '',
                date_last_change_batteries: '',
                condition_inverter_dc_to_ac: '',
                date_change_inverter: '',
                pre_treatment_process_1: '',
                pre_treatment_process_2: '',
                pre_treatment_process_3: '',
                pre_treatment_process_4: '',
                pre_treatment_process_5: '',
                pre_treatment_process_6: '',
                pre_treatment_process_7: '',
                type_of_raw_water_tank: '',
                raw_water_tank_h_cm: '',
                raw_water_tank_d_cm: '',
                raw_water_tank_v_liter: '',
                type_of_sand_filter_tank: '',
                sand_filter_tank_h_cm: '',
                sand_filter_tank_d_cm: '',
                sand_filter_tank_v_liter: '',
                sand_filter_tank__height_from_the_top_cm: '',
                date_change_sand_filter_tank: '',
                type_of_ac_filter_tank: '',
                ac_filter_tank_h_cm: '',
                ac_filter_tank_d_cm: '',
                ac_filter_tank_v_liter: '',
                ac_filter_tank_media_height_from_the_top: '',
                date_change_ac_filter_tank: '',
                type_of_resin_filter_tank: '',
                resin_filter_tank_h_cm: '',
                resin_filter_tank_d_cm: '',
                resin_filter_tank_v_liter: '',
                resin_filter_tank_media_height_from_the_top: '',
                date_change_resin_filter_tank: '',
                type_of_clear_water_tank: '',
                clear_water_tank_h_cm: '',
                clear_water_tank_d_cm: '',
                clear_water_tank_v_liter: '',
                flocculation_and_coagulation_process: '',
                reverse_osmose: '',
                date_change_reverse_osmose: '',
                ultrafiltration: '',
                date_change_ultrafiltration: '',
                raw_water_pump: '',
                raw_water_pump_maximum_flow: '',
                raw_water_pump_height_hmax: '',
                raw_water_pump_power: '',
                back_wash_pump: '',
                back_wash_pump_flow_qmax: '',
                back_wash_pump_height_hmax: '',
                back_wash_pump_power: '',
                reverse_osmose_pump: '',
                reverse_osmose_pump_flow_qmax: '',
                reverse_osmose_pump_height_hmax: '',
                reverse_osmose_pump_power: '',
                filter_50_item: '',
                date_change_filter_50: '',
                filter_50_condition: '',
                filter_10_item: '',
                date_change_10m_filter: '',
                filter_10_condition: '',
                item_5m_filter: '',
                date_change_5m_filter: '',
                filter_5_condition: '',
                item_1m_filter: '',
                date_change_1m_filter: '',
                filter_1_condition: '',
                uv_lamp: '',
                date_change_uv_lamp: '',
                uv_lamp_condition: '',
                uv_controller: '',
                date_change_uv_controller: '',
                uv_controller_condition: '',
                uv_ballast: '',
                date_change_uv_ballast: '',
                uv_ballast_condition: '',
                uv_sensor: '',
                date_change_uv_sensor: '',
                uv_sensor_condition: '',
                l_tank_for_cip: '',
                date_change_200l_tank_for_cip: '',
                l_tank_for_cip_condition: '',
                micro_filter_pump: '',
                micro_filter_pump_maximum_flow_qmax_lpm: '',
                micro_filter_pump_maximum_height_hmax_m: '',
                micro_filter_pump_power_kwhp: '',
                micro_filter_pump_voltage_v: '',
                bottle_washing_area_dirty_bottle_shelf: '',
                bottle_washing_area_washing_station: '',
                bottle_washing_area_specific_tank_for_lid_disinfection: '',
                bottle_washing_area_chlorine_tank: '',
                bottle_washing_area_disinfection_bottle_shelf_or_table_storage: '',
                bottle_washing_area_rinsing_station: '',
                filling_area_filling_station: '',
                poster_for_om_poster_for_om: '',
                poster_for_om_date_change: '',
                how_many_transportation_do_you_have: '',
                transportation_type: '',
                type_of_afm: '',
                afm_d_cm: '',
                afm_h_cm: '',
                afm_v_iter: '',
                afm_the_height_from_the_top_cm: '',
                afm_date_change_sand_filter_tank: '',
                type_of_Zmag: '',
                zmag_d_cm: '',
                zmag_h_cm: '',
                zmag_v_iter: '',
                zmag_the_height_from_the_top_cm: '',
                zmag_date_change_sand_filter_tank: '',
                type_of_sand_filter_and_Zmag_tank: '',
                sand_filter_and_zmag_d_cm: '',
                sand_filter_and_zmag_h_cm: '',
                sand_filter_and_zmag_v_iter: '',
                sand_filter_and_zmag_the_height_from_the_top_cm: '',
                sand_filter_and_zmag_date_change_sand_filter_tank: '',
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
                    return 'This field is required so much.'
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
                        axios.put("/api/formAssessment/update/" + this.$route.params.id, this.pa).then((response) => {
                            console.log(response.data.message)
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
            axios.get("/api/formAssessment/" + this.$route.params.id).then(response => {
                this.pa = response.data;
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