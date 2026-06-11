<template>
    <v-form class="bg-grey-lighten-1 pa-4" @submit.prevent="savePAForm">
        <v-card>
            <v-tabs v-model="tab" bg-color="primary">
                <v-tab value="Profile">Profile</v-tab>
                <!-- <v-tab value="Training_Score">Training_Score</v-tab> -->
                <v-tab value="Previous_kpi" v-if="pa.staff_type_pa == 'Year Appriasal'">Previous_KPI</v-tab>
                <!-- <v-tab value="Previous_kpi">Previous_KPI</v-tab> test -->
                <v-tab value="Qualitative_KPI"> New Qualitative_KPI</v-tab>
                <v-tab value="Quantitative_KPI">Year Quantitative_KPI</v-tab>
                <v-tab value="Carrer_and_Challenges">Carrer & challenges & opportunity</v-tab>
                <v-tab value="result">Result</v-tab>
            </v-tabs>
            <v-card-text>
                <v-window v-model="tab">
                    <v-window-item value="Profile">
                        <v-card prepend-icon="mdi-briefcase-edit" title="Mission details" class="mb-3 rounded-lg">
                            <v-card-text>
                                <v-row>
                                    <v-col cols="12" md="3">
                                        <v-select v-model="pa.staff_type_pa" density="compact" label="Type of Appiasal"
                                            hide-details="auto" :rules="required"
                                            :items="['Mid Appriasal', 'Year Appriasal', 'Probation']" />
                                    </v-col>
                                    <v-col cols="12" md="3">
                                        <v-select v-model="pa.year_pa" density="compact" label="Year of Appiasal"
                                            hide-details="auto" :rules="required" :items="['2026','2025']" />
                                    </v-col>
                                    <v-col cols="12" md="3">
                                        <v-select v-model="pa.staff_email" density="compact" label="Staff Email"
                                            hide-details="auto" :rules="required" :items="get_staff_info"
                                            item-title="email" />
                                    </v-col>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.supervisor_email" density="compact"
                                            label="Your Validator" hide-details="auto" :readonly="true"
                                            :rules="required" />
                                    </v-col>
                                </v-row>
                                <v-row>
                                    <v-col cols="12" md="2">
                                        <v-text-field v-model="pa.staff_id" density="compact" label="Staff ID"
                                            hide-details="auto" :rules="required" />
                                    </v-col>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.staff_name" density="compact" label="Staff Name"
                                            hide-details="auto" :rules="required" />
                                    </v-col>
                                    <v-col cols="12" md="2">
                                        <v-select v-model="pa.staff_sex" density="compact" label="Sex"
                                            hide-details="auto" :rules="required" :items="['Male', 'Female']" />
                                    </v-col>
                                    <v-col cols="12" md="2">
                                        <v-select v-model="pa.staff_position" density="compact" label="Position"
                                            hide-details="auto" :rules="required" :items="[]" />
                                    </v-col>
                                    <v-col cols="12" md="3">
                                        <v-select v-model="pa.staff_dept" density="compact" label="Department"
                                            hide-details="auto" :rules="required" :items="[]" />
                                    </v-col>
                                </v-row>
                                <v-row>

                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.staff_supervisor_by" density="compact"
                                            label="Supervisor By" hide-details="auto" :rules="required" />
                                        <!-- <v-select v-model="pa.staff_supervisor_by" density="compact" label="Supervisor By"
                                            hide-details="auto" :rules="required" :items="['Chamnap', 'Amandine']" /> -->
                                    </v-col>
                                    <!-- <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.staff_join_date" type="date" density="compact"
                                            label="Staff Join Date" hide-details="auto" :readonly="edit" />
                                    </v-col> -->
                                    <v-col cols="12" md="2">
                                        <v-text-field v-model="pa.staff_do_pa_date" type="date" density="compact"
                                            label="Date Do PA" hide-details="auto"  />
                                    </v-col>
                                    <v-col cols="12" md="2">
                                        <v-text-field v-model="pa.start_pa" type="date" density="compact"
                                            label="Start From" hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="2">
                                        <v-text-field v-model="pa.end_pa" type="date" density="compact" label="To Date"
                                            hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="2">
                                        <v-text-field v-model="pa.duration" density="compact" label="Duration as Month"
                                            hide-details="auto" :readonly="true" />
                                    </v-col>
                                </v-row>
                            </v-card-text>
                        </v-card>
                    </v-window-item>

                    <v-window-item value="Training_Score">
                        <v-table fixed-header height="300px">
                            <thead>
                                <tr>
                                    <th class="text-left">
                                        Staff Name
                                    </th>
                                    <th class="text-left">
                                        Cooperate
                                    </th>
                                    <th class="text-left">
                                        Sale & Marketing
                                    </th>
                                    <th class="text-left">
                                        Water Quality
                                    </th>
                                    <th class="text-left">
                                        Entrepreneurship(19)
                                    </th>
                                    <th class="text-left">
                                        Entre-Turnover(36)
                                    </th>
                                    <th class="text-left">
                                        Entre-Training (43)
                                    </th>
                                    <th class="text-left">
                                        O-We-committee (36)
                                    </th>
                                    <th class="text-left">
                                        Technical_Score (100)
                                    </th>
                                </tr>
                            </thead>
                            <tbody>

                                <tr v-for="item in get_staff_training" :key="item.staff_email">
                                    <td >{{ item.staff_email }}</td>
                                    <td class="text-center" :style="{ color: item.cooperate_score >= 10 ? 'blue' : 'red' }">
                                        {{ item.cooperate_score }}
                                    </td>
                                    <td class="text-center" :style="{ color: item.sale_and_maketing_score >= 10 ? 'blue' : 'red' }">
                                        {{ item.sale_and_maketing_score }}
                                    </td>
                                    <td class="text-center" :style="{ color: item.water_quality_score >= 10 ? 'blue' : 'red' }">
                                        {{ item.water_quality_score }}
                                    </td>
                                    <td class="text-center" :style="{ color: item.entrepreneur_score >= 10 ? 'blue' : 'red' }">
                                        {{ item.entrepreneur_score }}
                                    </td>
                                    <td class="text-center" :style="{ color: item.entreturnover >= 18 ? 'blue' : 'red' }">
                                        {{ item.entrepreneur_score }}
                                    </td>
                                    <td class="text-center" :style="{ color: item.entretraining >= 22 ? 'blue' : 'red' }">
                                        {{ item.entrepreneur_score }}
                                    </td>
                                    <td class="text-center" :style="{ color: item.owecommittee >= 18 ? 'blue' : 'red' }">
                                        {{ item.entrepreneur_score }}
                                    </td>
                                    <td class="text-center" :style="{ color: item.technicianseminar >= 50 ? 'blue' : 'red' }">
                                        {{ item.technicianseminar }}
                                    </td>

                                </tr>
                            </tbody>
                        </v-table>
                    </v-window-item>
                    <v-window-item value="Previous_kpi">
                        <!--Qualitative Part-->
                        <v-card prepend-icon="mdi-card-account-details-outline" title="Total Previous Score"
                            class="mb-3 rounded-lg">
                            <v-text-field v-model="pa.score_last_time" density="compact" label="Total Previous Score"
                                hide-details="auto" type="number" />
                        </v-card>
                        <v-card prepend-icon="mdi-card-account-details-outline" title="Previous Qualitative KPI"
                            class="mb-3 rounded-lg">
                            <v-card-text>
                                <v-row>
                                    <v-col cols="12" md="10">
                                        <v-text-field v-model="pa.previous_obj1_qualitative" density="compact"
                                            label="First Objective" hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="2">
                                        <v-text-field v-model="pa.previous_score_obj1_qualitative" density="compact"
                                            label="Score Objective 1" hide-details="auto" type="number" />
                                    </v-col>
                                </v-row>
                                <v-row>
                                    <v-col cols="12" md="12">
                                        <v-textarea v-model="pa.previous_detail_obj1_qualitative" auto-grow
                                            density="compact" label="Manager Remark **" rows="6" />
                                    </v-col>
                                </v-row>
                                <v-row>
                                    <v-col cols="12" md="10">
                                        <v-text-field v-model="pa.previous_obj2_qualitative" density="compact"
                                            label="Second Objective" hide-details="auto"  />
                                    </v-col>
                                    <v-col cols="12" md="2">
                                        <v-text-field v-model="pa.previous_score_obj2_qualitative" density="compact"
                                            label="Score Objective 2" hide-details="auto" type="number" />
                                    </v-col>
                                </v-row>
                                <v-row>
                                    <v-col cols="12" md="12">
                                        <v-textarea v-model="pa.previous_detail_obj2_qualitative" auto-grow
                                            density="compact" label="Manager Remark **" rows="6" />
                                    </v-col>
                                </v-row>
                                <v-row>
                                    <v-col cols="12" md="10">
                                        <v-text-field v-model="pa.previous_obj3_qualitative" density="compact"
                                            label="Third Objective" hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="2">
                                        <v-text-field v-model="pa.previous_score_obj3_qualitative" density="compact"
                                            label="Score Objective 3" hide-details="auto" type="number" />
                                    </v-col>
                                </v-row>
                                <v-row>
                                    <v-col cols="12" md="12">
                                        <v-textarea v-model="pa.previous_detail_obj3_qualitative" auto-grow
                                            density="compact" label="Manager Remark **" rows="6" />
                                    </v-col>
                                </v-row>
                            </v-card-text>
                        </v-card>
                        <v-card prepend-icon="mdi-card-account-details-outline" title="Previous Quantitative KPI"
                            class="mb-3 rounded-lg">
                            <v-card-text>
                                <v-row>
                                    <v-col cols="12" md="8">
                                        <v-text-field v-model="pa.previous_total_score_quantitative" density="compact"
                                            label="Previous Score" hide-details="auto" type="number" />
                                    </v-col>

                                </v-row>
                                <v-row>
                                    <v-col cols="12" md="8">
                                        <v-textarea v-model="pa.previous_year_obj1_quantitative" auto-grow
                                            density="compact" label="KPI 1" rows="2" />
                                    </v-col>
                                    <v-col cols="12" md="2">
                                        <v-text-field v-model="pa.previous_target_obj1_quantitative" density="compact"
                                            label="Target This Year" hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="2">
                                        <v-text-field v-model="pa.previous_result_obj1_quantitative" density="compact"
                                            label="Result" hide-details="auto" />
                                    </v-col>
                                </v-row>

                                <v-row>
                                    <v-col cols="12" md="8">
                                        <v-textarea v-model="pa.previous_year_obj2_quantitative" auto-grow
                                            density="compact" label="KPI 2" rows="2" />
                                    </v-col>
                                    <v-col cols="12" md="2">
                                        <v-text-field v-model="pa.previous_target_obj2_quantitative" density="compact"
                                            label="Target This Year" hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="2">
                                        <v-text-field v-model="pa.previous_result_obj2_quantitative" density="compact"
                                            label=" Result" hide-details="auto" />
                                    </v-col>
                                </v-row>

                                <v-row>
                                    <v-col cols="12" md="8">
                                        <v-textarea v-model="pa.previous_year_obj3_quantitative" auto-grow
                                            density="compact" label="KPI 3" rows="2" />
                                    </v-col>
                                    <v-col cols="12" md="2">
                                        <v-text-field v-model="pa.previous_target_obj3_quantitative" density="compact"
                                            label="Target This Year" hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="2">
                                        <v-text-field v-model="pa.previous_result_obj3_quantitative" density="compact"
                                            label="Result" hide-details="auto" />
                                    </v-col>
                                </v-row>

                                <v-row>
                                    <v-col cols="12" md="8">
                                        <v-textarea v-model="pa.previous_year_obj4_quantitative" auto-grow
                                            density="compact" label="KPI 4" rows="2" />
                                    </v-col>
                                    <v-col cols="12" md="2">
                                        <v-text-field v-model="pa.previous_target_obj4_quantitative" density="compact"
                                            label="Target This Year" hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="2">
                                        <v-text-field v-model="pa.previous_result_obj4_quantitative" density="compact"
                                            label="Result" hide-details="auto" />
                                    </v-col>
                                </v-row>

                                <v-row>
                                    <v-col cols="12" md="8">
                                        <v-textarea v-model="pa.previous_year_obj5_quantitative" auto-grow
                                            density="compact" label="KPI 5" rows="2" />
                                    </v-col>
                                    <v-col cols="12" md="2">
                                        <v-text-field v-model="pa.previous_target_obj5_quantitative" density="compact"
                                            label="Target This Year" hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="2">
                                        <v-text-field v-model="pa.previous_result_obj5_quantitative" density="compact"
                                            label="Result" hide-details="auto" />
                                    </v-col>
                                </v-row>

                            </v-card-text>
                        </v-card>
                    </v-window-item>
                    <v-window-item value="Qualitative_KPI">
                        <v-card prepend-icon="mdi-card-account-details-outline" title="Score Instruction"
                            class="mb-3 rounded-lg headerStyle">
                            <v-card-text>
                                <v-row>
                                    <v-col cols="12" md="12">
                                        <v-table>
                                            <thead>
                                                <tr>
                                                    <th class="text-center">0 %</th>
                                                    <th class="text-center">20% - 39%</th>
                                                    <th class="text-center">40% - 59%</th>
                                                    <th class="text-center">60% - 79%</th>
                                                    <th class="text-center">80% - 99%</th>
                                                    <th class="text-center">100%</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                <tr>
                                                    <td class="text-center headerStyle">Non Evaluate</td>
                                                    <td class="text-center headerStyle">Biginner</td>
                                                    <td class="text-center headerStyle">Insufficient</td>
                                                    <td class="text-center headerStyle">Average</td>
                                                    <td class="text-center headerStyle">Beyond Expectation</td>
                                                    <td class="text-center headerStyle">Expert</td>
                                                </tr>
                                            </tbody>
                                        </v-table>
                                    </v-col>
                                </v-row>
                            </v-card-text>
                        </v-card>

                        <!--Qualitative Part-->
                        <v-card prepend-icon="mdi-card-account-details-outline"
                            title="Qualitative Key Performance Indicator" class="mb-3 rounded-lg">
                            <v-card-text>
                                <v-row>
                                    <v-col cols="12" md="2">
                                        <v-text-field v-model="pa.total_score_qualitative" density="compact"
                                            type="number" label="Total Qualitative Score" hide-details="auto"
                                            :readonly="true" />
                                    </v-col>
                                </v-row>
                                <v-row>
                                    <v-col cols="12" md="10">
                                        <v-text-field v-model="pa.obj1_qualitative" density="compact"
                                            label="First Objective" hide-details="auto" :rules="required" />
                                    </v-col>
                                    <v-col cols="12" md="2">
                                        <v-text-field v-model="pa.score_obj1_qualitative" density="compact"
                                            label="Score Objective 1" hide-details="auto" type="number" />
                                    </v-col>
                                </v-row>
                                <v-row>
                                    <v-col cols="12" md="12">
                                        <v-textarea v-model="pa.detail_obj1_qualitative" auto-grow density="compact"
                                            label="Manager Remart **" rows="6" />
                                    </v-col>
                                </v-row>
                                <v-row>
                                    <v-col cols="12" md="10">
                                        <v-text-field v-model="pa.obj2_qualitative" density="compact"
                                            label="Second Objective" hide-details="auto" :rules="required" />
                                    </v-col>
                                    <v-col cols="12" md="2">
                                        <v-text-field v-model="pa.score_obj2_qualitative" density="compact"
                                            label="Score Objective 2" hide-details="auto" type="number" />
                                    </v-col>
                                </v-row>
                                <v-row>
                                    <v-col cols="12" md="12">
                                        <v-textarea v-model="pa.detail_obj2_qualitative" auto-grow density="compact"
                                            label="Manager Remart **" rows="6" />
                                    </v-col>
                                </v-row>
                                <v-row>
                                    <v-col cols="12" md="10">
                                        <v-text-field v-model="pa.obj3_qualitative" density="compact"
                                            label="Third Objective" hide-details="auto" :rules="required" />
                                    </v-col>
                                    <v-col cols="12" md="2">
                                        <v-text-field v-model="pa.score_obj3_qualitative" density="compact"
                                            label="Score Objective 3" hide-details="auto" type="number" />
                                    </v-col>
                                </v-row>
                                <v-row>
                                    <v-col cols="12" md="12">
                                        <v-textarea v-model="pa.detail_obj3_qualitative" auto-grow density="compact"
                                            label="Manager Remart **" rows="6" />
                                    </v-col>
                                </v-row>
                            </v-card-text>
                        </v-card>
                    </v-window-item>

                    <v-window-item value="Quantitative_KPI">
                        <!-- KPI Qualitative Part-->
                        <v-card prepend-icon="mdi-card-account-details-outline" title="Quantitative KPIs"
                            class="mb-3 rounded-lg">
                            <v-card-text>
                                <v-row>
                                    <v-col cols="12" md="3">
                                        <v-text-field v-model="pa.total_score_quantitative" density="compact"
                                            label="Total Quantitative Score" hide-details="auto" type="number" />
                                    </v-col>
                                </v-row>
                            </v-card-text>
                        </v-card>

                        <v-card p>
                            <v-card-text>
                                <v-row>
                                    <v-col cols="12" md="8">
                                        <v-textarea v-model="pa.year_obj1_quantitative" auto-grow density="compact"
                                            label="KPI 1" rows="2" />
                                    </v-col>
                                    <v-col cols="12" md="2">
                                        <v-text-field v-model="pa.target_obj1_quantitative" density="compact"
                                            label="Target This Year " hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="2">
                                        <v-text-field v-model="pa.result_obj1_quantitative" density="compact"
                                            label="Result" hide-details="auto" />
                                    </v-col>
                                </v-row>

                                <v-row>
                                    <v-col cols="12" md="8">
                                        <v-textarea v-model="pa.year_obj2_quantitative" auto-grow density="compact"
                                            label="KPI 2" rows="2" />
                                    </v-col>
                                    <v-col cols="12" md="2">
                                        <v-text-field v-model="pa.target_obj2_quantitative" density="compact"
                                            label="Target This Year" hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="2">
                                        <v-text-field v-model="pa.result_obj2_quantitative" density="compact"
                                            label="Result" hide-details="auto" />
                                    </v-col>
                                </v-row>

                                <v-row>
                                    <v-col cols="12" md="8">
                                        <v-textarea v-model="pa.year_obj3_quantitative" auto-grow density="compact"
                                            label="KPI 3" rows="2" />
                                    </v-col>
                                    <v-col cols="12" md="2">
                                        <v-text-field v-model="pa.target_obj3_quantitative" density="compact"
                                            label=" Target This Year" hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="2">
                                        <v-text-field v-model="pa.result_obj3_quantitative" density="compact"
                                            label="Result" hide-details="auto" />
                                    </v-col>
                                </v-row>

                                <v-row>
                                    <v-col cols="12" md="8">
                                        <v-textarea v-model="pa.year_obj4_quantitative" auto-grow density="compact"
                                            label="KPI 4" rows="2" />
                                    </v-col>
                                    <v-col cols="12" md="2">
                                        <v-text-field v-model="pa.target_obj4_quantitative" density="compact"
                                            label="Target This Year" hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="2">
                                        <v-text-field v-model="pa.result_obj4_quantitative" density="compact"
                                            label="Result" hide-details="auto" />
                                    </v-col>
                                </v-row>

                                <v-row>
                                    <v-col cols="12" md="8">
                                        <v-textarea v-model="pa.year_obj5_quantitative" auto-grow density="compact"
                                            label="KPI 5" rows="2" />
                                    </v-col>
                                    <v-col cols="12" md="2">
                                        <v-text-field v-model="pa.target_obj5_quantitative" density="compact"
                                            label="Target This Year" hide-details="auto" />
                                    </v-col>
                                    <v-col cols="12" md="2">
                                        <v-text-field v-model="pa.result_obj5_quantitative" density="compact"
                                            label="Result" hide-details="auto" />
                                    </v-col>
                                </v-row>

                            </v-card-text>
                        </v-card>
                    </v-window-item>

                    <v-window-item value="Carrer_and_Challenges">
                        <v-card prepend-icon="mdi-card-account-details-outline"
                            title="Carrer pathway, challenges, and interest" class="mb-3 rounded-lg">
                            <v-card-text>
                                <v-row>
                                    <v-col cols="12" md="12">
                                        <v-textarea v-model="pa.comments" auto-grow density="compact"
                                            label="Comment and Appreciation" rows="4" />
                                    </v-col>
                                </v-row>
                                <v-row>
                                    <v-col cols="12" md="12">
                                        <v-textarea v-model="pa.challenges" auto-grow density="compact"
                                            label="What challeges have you found in your carrer?" rows="5" />
                                    </v-col>
                                </v-row>
                                <v-row>
                                    <v-col cols="12" md="12">
                                        <v-textarea v-model="pa.opportunity" auto-grow density="compact"
                                            label="Opportunity / like in organization" rows="5" />
                                    </v-col>
                                </v-row>
                            </v-card-text>
                        </v-card>
                    </v-window-item>
                    <v-window-item value="result">
                        <!-- <v-card prepend-icon="mdi-card-account-details-outline"
                            title="Previous Result" class="mb-3 rounded-lg">
                            <v-card-text>
                                <v-row>
                                    <v-col cols="12" md="12">
                                    <v-table >
                                        <thead>
                                            <tr>
                                                <th class="text-left">Staff Name</th>
                                                <th class="text-center">Evaluation Type</th>
                                                <th class="text-center">Year</th>
                                                <th class="text-right">Score</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            <tr v-for="item in get_staff_previous_kpi" :key="item.staff_email">
                                    <td class="text-left">{{ item.staff_email }}</td>
                                    <td class="text-center">{{ item.staff_type_pa }}</td>
                                    <td class="text-center">{{ item.staff_do_pa_date }}</td>
                                    <td class="text-center">{{ item.water_quality_score }}</td>
                                    <td class="text-left">{{ item.total_score }}</td>
                                </tr>
                                        </tbody>
                                    </v-table>
                                </v-col>
                                </v-row>
                            </v-card-text>
                        </v-card> -->
                        <v-card prepend-icon="mdi-card-account-details-outline" title="Result Score This Time"
                            class="mb-3 rounded-lg">
                            <v-card-text>
                                <v-row>
                                    <v-col cols="12" md="12">
                                        <v-text-field v-model="pa.total_score" density="compact" type="number"
                                            label="Total Score This time" hide-details="auto" :readonly="true" />
                                    </v-col>
                                </v-row>
                            </v-card-text>
                            <v-card-text>
                                <v-row>
                                    <v-col cols="12" md="12">
                                        <v-table>
                                            <thead>
                                                <tr>
                                                    <th class="text-left"> Below 50% </th>
                                                    <th class="text-center"> 50%-60%</th>
                                                    <th class="text-center">60%-70%</th>
                                                    <th class="text-center">70%-99%</th>
                                                    <th class="text-center">100%</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                <tr>
                                                    <td class="text-left">Termination</td>
                                                    <td class="text-center">Position Rotation</td>
                                                    <td class="text-center">Capacity Building</td>
                                                    <td class="text-center">Motivation</td>
                                                    <td class="text-center">Potential Promotion</td>
                                                </tr>
                                            </tbody>
                                        </v-table>
                                    </v-col>
                                </v-row>
                            </v-card-text>
                        </v-card>
                    </v-window-item>
                </v-window>
            </v-card-text>
        </v-card>
        <!-- Add  -->
        <div v-if="tab == 'result'">
            <v-row class="ma-2" justify="center">
                <v-btn prepend-icon="mdi-cancel" rounded="lg" color="error" class="ma-4" size="large"
                    @click="$router.go(-1)">
                    Cancel
                </v-btn>
                <v-btn prepend-icon="mdi-content-save" rounded="lg" color="green" class="ma-4" size="large"
                    type="submit">
                    Save As Draft
                </v-btn>
                <v-btn prepend-icon="mdi-content-save" rounded="lg" color="primary" class="ma-4" size="large"
                    @click="saveAndSendEmail()">
                    Save & Send-Email
                </v-btn>
            </v-row>
        </div>
    </v-form>
</template>
<script>
import axios from 'axios';
import Swal from "sweetalert2";
import { el } from 'vuetify/locale';
export default {
    name: 'FormPa',
    data: function () {
        return {
            pa: {
                staff_email: '',
                supervisor_email: '',
                year_pa: '',
                staff_id: '',
                staff_position: '',
                staff_sex: '',
                staff_name: '',
                staff_dept: '',
                staff_do_pa_date: new Date().toJSON().slice(0, 10),
                start_pa: new Date().toJSON().slice(0, 10),
                end_pa: new Date().toJSON().slice(0, 10),
                duration: 0,
                staff_supervisor_by: '',
                staff_type_pa: '',
                score_last_time: 0,
                total_score: 0,
                total_score_qualitative: 0,
                obj1_qualitative: '',
                obj2_qualitative: '',
                obj3_qualitative: '',
                score_obj1_qualitative: 0,
                score_obj2_qualitative: 0,
                score_obj3_qualitative: 0,
                detail_obj1_qualitative: '',
                detail_obj2_qualitative: '',
                detail_obj3_qualitative: '',
                total_score_quantitative: 0,
                year_obj1_qualitative: '',
                year_obj2_qualitative: '',
                year_obj3_qualitative: '',
                year_obj1_quantitative: '',
                target_obj1_quantitative: '',
                result_obj1_quantitative: '',
                year_obj2_quantitative: '',
                target_obj2_quantitative: '',
                result_obj2_quantitative: '',
                year_obj3_quantitative: '',
                target_obj3_quantitative: '',
                result_obj3_quantitative: '',
                year_obj4_quantitative: '',
                target_obj4_quantitative: '',
                result_obj4_quantitative: '',
                year_obj5_quantitative: '',
                target_obj5_quantitative: '',
                result_obj5_quantitative: '',
                previous_total_score_quantitative: 0,
                previous_target_obj1_quantitative: '',
                previous_result_obj1_quantitative: '',
                previous_year_obj2_quantitative: '',
                previous_target_obj2_quantitative: '',
                previous_result_obj2_quantitative: '',
                previous_year_obj3_quantitative: '',
                previous_target_obj3_quantitative: '',
                previous_result_obj3_quantitative: '',
                previous_year_obj4_quantitative: '',
                previous_target_obj4_quantitative: '',
                previous_result_obj4_quantitative: '',
                previous_year_obj5_quantitative: '',
                previous_target_obj5_quantitative: '',
                previous_result_obj5_quantitative: '',
                comments: '',
                opportunity: '',
                challenges: '',
                previous_obj1_qualitative: '',
                previous_score_obj1_qualitative: 0,
                previous_detail_obj1_qualitative: '',
                previous_obj2_qualitative: '',
                previous_score_obj2_qualitative: 0,
                previous_detail_obj2_qualitative: '',
                previous_obj3_qualitative: '',
                previous_score_obj3_qualitative: 0,
                previous_detail_obj3_qualitative: '',
                previous_obj1_quantitative: '',
                previous_obj2_quantitative: '',
                previous_obj3_quantitative: '',
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

        "pa.staff_email": function () {
            if (!this.pa.staff_email || !this.pa.year_pa) {
                Swal.fire({
                    icon: 'error',
                    title: 'Oops...',
                    text: 'Please select Staff Email and Year of Appraisal!',
                })
            }
            else {
                if (this.edit == false) {
                    const a = this.get_staff_info.find(s => s.email == this.pa.staff_email);
                    if (a) {
                        this.pa.supervisor_email = a.manager
                        this.pa.staff_id = a.staff_id
                        this.pa.staff_name = a.staff_name
                        this.pa.staff_sex = a.staff_sex
                        this.pa.staff_position = a.staff_position
                        this.pa.staff_dept = a.staff_dept
                        this.pa.staff_supervisor_by = a.manager
                    }
                    axios.get("/api/getTraining/" + this.pa.staff_email).then(response => {
                        console.log(response.data);
                        this.get_staff_training = response.data;
                    })
                    axios.get("/api/getPreviousPA/" + this.pa.staff_email + "?year=" + this.pa.year_pa).then(response => {

                        this.get_staff_previous_kpi = response.data.previousPA;
                        const previous_result = this.get_staff_previous_kpi.find(s => s.staff_email == this.pa.staff_email);
                        console.log(response.data.current)
                        if (previous_result) {
                            // Fill the previous data of previous qualitative
                            this.pa.previous_obj1_qualitative = previous_result.obj1_qualitative
                            this.pa.previous_score_obj1_qualitative = previous_result.score_obj1_qualitative
                            this.pa.previous_detail_obj1_qualitative = previous_result.detail_obj1_qualitative
                            this.pa.previous_obj2_qualitative = previous_result.obj2_qualitative
                            this.pa.previous_score_obj2_qualitative = previous_result.score_obj2_qualitative
                            this.pa.previous_detail_obj2_qualitative = previous_result.detail_obj2_qualitative
                            this.pa.previous_obj3_qualitative = previous_result.obj3_qualitative
                            this.pa.previous_score_obj3_qualitative = previous_result.score_obj3_qualitative
                            this.pa.previous_detail_obj3_qualitative = previous_result.detail_obj3_qualitative
                            // end of previous qualitative
                            // Fill the previous data of new quantitative
                            if (this.pa.staff_type_pa == 'Year Appriasal') {
                                this.pa.obj1_qualitative = ""
                                this.pa.obj2_qualitative = ""
                                this.pa.obj3_qualitative = ""
                                this.pa.score_obj1_qualitative = 0
                                this.pa.score_obj2_qualitative = 0
                                this.pa.score_obj3_qualitative = 0
                                this.pa.detail_obj1_qualitative = ""
                                this.pa.detail_obj2_qualitative = ""
                                this.pa.detail_obj3_qualitative = ""
                                this.total_score_qualitative = 0
                                this.total_score_quantitative = 0
                            }
                            else
                            {
                                this.pa.obj1_qualitative = previous_result.obj1_qualitative
                                this.pa.obj2_qualitative = previous_result.obj2_qualitative
                                this.pa.obj3_qualitative = previous_result.obj3_qualitative
                                this.pa.score_obj1_qualitative = 0
                                this.pa.score_obj2_qualitative = 0
                                this.pa.score_obj3_qualitative = 0

                                // this.pa.score_obj1_qualitative = previous_result.score_obj1_qualitative
                                // this.pa.score_obj2_qualitative = previous_result.score_obj2_qualitative
                                // this.pa.score_obj3_qualitative = previous_result.score_obj3_qualitative

                                this.pa.detail_obj1_qualitative = previous_result.detail_obj1_qualitative
                                this.pa.detail_obj2_qualitative = previous_result.detail_obj2_qualitative
                                this.pa.detail_obj3_qualitative = previous_result.detail_obj3_qualitative
                            }

                            // end of new qualitative
                            // Fill the previous data of previous quantitative
                            // need to check condition of type of PA
                            this.pa.previous_year_obj3_quantitative = response.data.current[0].kpi3
                            this.pa.previous_year_obj4_quantitative = response.data.current[0].kpi4
                            this.pa.previous_year_obj5_quantitative = response.data.current[0].kpi5
                            this.pa.previous_target_obj3_quantitative = response.data.current[0].target3
                            this.pa.previous_target_obj4_quantitative = response.data.current[0].target4
                            this.pa.previous_target_obj5_quantitative = response.data.current[0].target5
                            this.pa.previous_result_obj3_quantitative = response.data.current[0].result_kpi3
                            this.pa.previous_result_obj4_quantitative = response.data.current[0].result_kpi4
                            this.pa.previous_result_obj5_quantitative = response.data.current[0].result_kpi5
                            // load data KPI
                           // this.pa.previous_year_obj1_quantitative = previous_result.year_obj1_quantitative
                            this.pa.previous_year_obj1_quantitative = response.data.current[0].kpi1
                            this.pa.previous_year_obj2_quantitative = response.data.current[0].kpi2
                            this.pa.previous_target_obj1_quantitative = response.data.current[0].target1
                            this.pa.previous_target_obj2_quantitative = response.data.current[0].target2
                            this.pa.previous_result_obj1_quantitative = response.data.current[0].result_kpi1
                            this.pa.previous_result_obj2_quantitative = response.data.current[0].result_kpi2
                            // this.pa.year_obj1_quantitative = response.data.current[0].kpi1
                            // this.pa.year_obj2_quantitative = response.data.current[0].kpi2
                            // this.pa.year_obj3_quantitative = response.data.current[0].kpi3
                            // this.pa.year_obj4_quantitative = response.data.current[0].kpi4
                            // this.pa.year_obj5_quantitative = response.data.current[0].kpi5
                            // this.pa.target_obj1_quantitative = response.data.current[0].target1
                            // this.pa.target_obj2_quantitative = response.data.current[0].target2
                            // this.pa.target_obj3_quantitative = response.data.current[0].target3
                            // this.pa.target_obj4_quantitative = response.data.current[0].target4
                            // this.pa.target_obj5_quantitative = response.data.current[0].target5
                            // this.pa.result_obj1_quantitative = response.data.current[0].result_kpi1
                            // this.pa.result_obj2_quantitative = response.data.current[0].result_kpi2
                            // this.pa.result_obj3_quantitative = response.data.current[0].result_kpi3
                            // this.pa.result_obj4_quantitative = response.data.current[0].result_kpi4
                            // this.pa.result_obj5_quantitative = response.data.current[0].result_kpi5
                        }
                        else {
                            this.pa.previous_obj1_qualitative = ''
                            this.pa.previous_score_obj1_qualitative = ''
                            this.pa.previous_detail_obj1_qualitative = ''
                            this.pa.previous_obj2_qualitative = ''
                            this.pa.previous_score_obj2_qualitative = ''
                            this.pa.previous_detail_obj2_qualitative = ''
                            this.pa.previous_obj3_qualitative = ''
                            this.pa.previous_score_obj3_qualitative = ''
                            this.pa.previous_detail_obj3_qualitative = ''
                            this.pa.previous_obj1_quantitative = ''
                            this.pa.previous_obj2_quantitative = ''
                            this.pa.previous_obj3_quantitative = ''
                            this.pa.previous_year_obj1_quantitative = ''
                            this.pa.previous_year_obj2_quantitative = ''
                            this.pa.previous_year_obj3_quantitative = ''
                            this.pa.previous_year_obj4_quantitative = ''
                            this.pa.previous_year_obj5_quantitative = ''
                            this.pa.previous_target_obj1_quantitative = ''
                            this.pa.previous_target_obj2_quantitative = ''
                            this.pa.previous_target_obj3_quantitative = ''
                            this.pa.previous_target_obj4_quantitative = ''
                            this.pa.previous_target_obj5_quantitative = ''
                            this.pa.previous_result_obj1_quantitative = ''
                            this.pa.previous_result_obj2_quantitative = ''
                            this.pa.previous_result_obj3_quantitative = ''
                            this.pa.previous_result_obj4_quantitative = ''
                            this.pa.previous_result_obj5_quantitative = ''
                            // empty data KPI
                            // this.pa.year_obj1_quantitative = ''
                            // this.pa.year_obj2_quantitative = ''
                            // this.pa.year_obj3_quantitative = ''
                            // this.pa.year_obj4_quantitative = ''
                            // this.pa.year_obj5_quantitative = ''
                            // this.pa.target_obj1_quantitative = ''
                            // this.pa.target_obj2_quantitative = ''
                            // this.pa.target_obj3_quantitative = ''
                            // this.pa.target_obj4_quantitative = ''
                            // this.pa.target_obj5_quantitative = ''
                            // this.pa.result_obj1_quantitative = ''
                            // this.pa.result_obj2_quantitative = ''
                            // this.pa.result_obj3_quantitative = ''
                            // this.pa.result_obj4_quantitative = ''
                            // this.pa.result_obj5_quantitative = ''
                        }
                    })
                    axios.get("/api/getKPI/" + this.pa.staff_email).then(response => {
                        //console.log(response.data.current[0].kpi3);
                        this.getKPI = response.data.current[0];
                        //const previous_kpi = this.getKPI.find(s => s.staff_email == this.pa.staff_email);
                        if (this.getKPI) {
                            this.pa.year_obj1_quantitative = response.data.current[0].kpi1
                            this.pa.year_obj2_quantitative = response.data.current[0].kpi2
                            this.pa.year_obj3_quantitative = response.data.current[0].kpi3
                            this.pa.year_obj4_quantitative = response.data.current[0].kpi4
                            this.pa.year_obj5_quantitative = response.data.current[0].kpi5
                            this.pa.target_obj1_quantitative = response.data.current[0].target1
                            this.pa.target_obj2_quantitative = response.data.current[0].target2
                            this.pa.target_obj3_quantitative = response.data.current[0].target3
                            this.pa.target_obj4_quantitative = response.data.current[0].target4
                            this.pa.target_obj5_quantitative = response.data.current[0].target5
                            this.pa.result_obj1_quantitative = response.data.current[0].result_kpi1
                            this.pa.result_obj2_quantitative = response.data.current[0].result_kpi2
                            this.pa.result_obj3_quantitative = response.data.current[0].result_kpi3
                            this.pa.result_obj4_quantitative = response.data.current[0].result_kpi4
                            this.pa.result_obj5_quantitative = response.data.current[0].result_kpi5
                        }
                        else {
                            this.pa.year_obj1_quantitative = ''
                            this.pa.year_obj2_quantitative = ''
                            this.pa.year_obj3_quantitative = ''
                            this.pa.year_obj4_quantitative = ''
                            this.pa.year_obj5_quantitative = ''
                            this.pa.target_obj1_quantitative = ''
                            this.pa.target_obj2_quantitative = ''
                            this.pa.target_obj3_quantitative = ''
                            this.pa.target_obj4_quantitative = ''
                            this.pa.target_obj5_quantitative = ''
                            this.pa.result_obj1_quantitative = ''
                            this.pa.result_obj2_quantitative = ''
                            this.pa.result_obj3_quantitative = ''
                            this.pa.result_obj4_quantitative = ''
                            this.pa.result_obj5_quantitative = ''
                        }
                    })
                }
            }
        },
        "pa.previous_score_obj1_qualitative": function () {
            this.pa.score_last_time = this.totalPreviousQualitative(this.pa.previous_score_obj1_qualitative, this.pa.previous_score_obj2_qualitative, this.pa.previous_score_obj3_qualitative, this.pa.previous_total_score_quantitative);
            //console.log(this.pa.previous_score_obj1_qualitative,this.pa.previous_score_obj2_qualitative,this.pa.previous_score_obj3_qualitative,this.pa.previous_total_score_quantitative );
        },
        "pa.previous_score_obj2_qualitative": function () {
            this.pa.score_last_time = this.totalPreviousQualitative(this.pa.previous_score_obj1_qualitative, this.pa.previous_score_obj2_qualitative, this.pa.previous_score_obj3_qualitative, this.pa.previous_total_score_quantitative);

        },
        "pa.previous_score_obj3_qualitative": function () {
            this.pa.score_last_time = this.totalPreviousQualitative(this.pa.previous_score_obj1_qualitative, this.pa.previous_score_obj2_qualitative, this.pa.previous_score_obj3_qualitative, this.pa.previous_total_score_quantitative);

        },
        "pa.previous_total_score_quantitative": function () {
            this.pa.score_last_time = this.totalPreviousQualitative(this.pa.previous_score_obj1_qualitative, this.pa.previous_score_obj2_qualitative, this.pa.previous_score_obj3_qualitative, this.pa.previous_total_score_quantitative);
            if(this.pa.staff_type_pa == 'Year Appriasal')
            {
                this.pa.total_score = this.pa.score_last_time
            }
        },
        "pa.previous_total_score_qualitative": function () {
            this.pa.score_last_time = this.totalPreviousQualitative(this.pa.previous_score_obj1_qualitative, this.pa.previous_score_obj2_qualitative, this.pa.previous_score_obj3_qualitative, this.pa.previous_total_score_quantitative);
            if(this.pa.staff_type_pa == 'Year Appriasal')
            {
                this.pa.total_score = this.pa.score_last_time
            }
        },
        "pa.score_obj1_qualitative": function () {
            this.pa.total_score_qualitative = Math.round((parseFloat(this.pa.score_obj1_qualitative) + parseFloat(this.pa.score_obj2_qualitative) + parseFloat(this.pa.score_obj3_qualitative)) / 3)

        },
        "pa.score_obj2_qualitative": function () {
            this.pa.total_score_qualitative = Math.round((parseFloat(this.pa.score_obj1_qualitative) + parseFloat(this.pa.score_obj2_qualitative) + parseFloat(this.pa.score_obj3_qualitative)) / 3)

        },
        "pa.score_obj3_qualitative": function () {
            this.pa.total_score_qualitative = Math.round((parseFloat(this.pa.score_obj1_qualitative) + parseFloat(this.pa.score_obj2_qualitative) + parseFloat(this.pa.score_obj3_qualitative)) / 3)
        },
        "pa.total_score_qualitative": function () {
            if(this.pa.staff_type_pa != 'Year Appriasal')
            {
                this.pa.total_score = Math.round(parseInt(this.pa.total_score_qualitative) + parseInt(this.pa.total_score_quantitative)) / 2
            }

        },
        "pa.total_score_quantitative": function () {
            if(this.pa.staff_type_pa != 'Year Appriasal')
            {
                this.pa.total_score = Math.round(parseInt(this.pa.total_score_qualitative) + parseInt(this.pa.total_score_quantitative)) / 2
            }
        },
        "pa.start_pa": function () {
            this.pa.duration = this.calculateMonth(this.pa.start_pa, this.pa.end_pa);
        },
        "pa.end_pa": function () {
            this.pa.duration = this.calculateMonth(this.pa.start_pa, this.pa.end_pa);
        },
        // "pa.score_obj1_qualitative": function () {
        //     this.pa.total_score_qualitative = (parseFloat(this.pa.score_obj1_qualitative) + parseFloat(this.pa.score_obj2_qualitative) + parseFloat(this.pa.score_obj3_qualitative))/3
        //     this.pa.total_score = Math.round(((parseFloat(this.pa.total_score_qualitative)) + (parseFloat(this.pa.total_score_quantitative))) /2)
        // },
        // "pa.score_obj2_qualitative": function () {
        //     this.pa.total_score_qualitative = (parseFloat(this.pa.score_obj1_qualitative) + parseFloat(this.pa.score_obj2_qualitative) + parseFloat(this.pa.score_obj3_qualitative))/3
        //     this.pa.total_score = Math.round(((parseFloat(this.pa.total_score_qualitative)) + (parseFloat(this.pa.total_score_quantitative) )) /2)
        // },
        // "pa.score_obj3_qualitative": function () {
        //     this.pa.total_score_qualitative = (parseFloat(this.pa.score_obj1_qualitative) + parseFloat(this.pa.score_obj2_qualitative) + parseFloat(this.pa.score_obj3_qualitative))/3
        //     this.pa.total_score = Math.round(((parseFloat(this.pa.total_score_qualitative)) + (parseFloat(this.pa.total_score_quantitative))) /2)
        // }

    },
    methods: {
        savePAForm(validationEvent) {
            validationEvent.then(result => {
                if (result.valid === true) {
                    Swal.fire({
                        text: "Are you sure you want to save as draft",
                        icon: 'warning',
                        showCancelButton: true,
                        confirmButtonColor: '#3085d6',
                        cancelButtonColor: '#d33',
                        confirmButtonText: 'Yes, save it!'
                    }).then((result) => {
                        if (result.isConfirmed)
                {
                    // Display loading modal
                    Swal.fire({
                        title: 'Sending...',
                        text: 'Please wait while we send your PA.',
                        allowOutsideClick: false,
                        didOpen: () => {
                            Swal.showLoading(); // Show the loading spinner
                        }
                    });

                    // Determine whether to send a PUT or POST request
                    if (this.$route.params.id) {
                        // PUT request (update PA)
                        axios.put("/api/pa/update/" + this.$route.params.id, {
                            pa: this.pa,
                            additionalVariable: ""
                        })
                            .then((response) => {
                                Swal.close(); // Close the loading modal
                                Swal.fire(
                                    'Sent!',
                                    'Your PA has been saved.',
                                    'success'
                                );
                                this.$router.go(-1); // Navigate back
                            })
                            .catch((error) => {
                                Swal.close(); // Close the loading modal
                                Swal.fire(
                                    'Error!',
                                    'There was an error modifying your PA.',
                                    'error'
                                );
                            })
                            .finally(() => {
                                this.loading = false; // Reset loading state
                            });
                    } else {
                        // Check for required fields
                        if (this.pa.staff_email === '' || this.pa.year_pa === '') {
                            Swal.close(); // Close the loading modal
                            Swal.fire({
                                icon: 'error',
                                title: 'Oops...',
                                text: 'Please select staff email and year of appraisal!',
                            });
                        } else {
                            // POST request (store new PA)
                            this.loading = true;
                            axios.post('/api/pa/store', {
                                pa: this.pa,
                                additionalVariable: ""
                            })
                                .then((response) => {
                                    Swal.close(); // Close the loading modal
                                    Swal.fire(
                                        'Sent!',
                                        'Your PA has been saved.',
                                        'success'
                                    );
                                    this.$router.go(-1); // Navigate back
                                })
                                .catch((error) => {
                                    Swal.close(); // Close the loading modal
                                    Swal.fire(
                                        'Missing Data',
                                        'There are some missing info, please check read color field in each tab',
                                        'error'
                                    );
                                })
                                .finally(() => {
                                    this.loading = false; // Reset loading state
                                });
                        }
                    }
                }
                    })
                }
            })
        },
        saveAndSendEmail() {
            Swal.fire({
                text: "Are you sure you want to send this PA with Email?",
                icon: 'warning',
                showCancelButton: true,
                confirmButtonColor: '#3085d6',
                cancelButtonColor: '#d33',
                confirmButtonText: 'Yes, send it!',
            }).then((result) => {
                if (result.isConfirmed)
                {
                    // Display loading modal
                    Swal.fire({
                        title: 'Sending...',
                        text: 'Please wait while we send your PA.',
                        allowOutsideClick: false,
                        didOpen: () => {
                            Swal.showLoading(); // Show the loading spinner
                        }
                    });

                    // Determine whether to send a PUT or POST request
                    if (this.$route.params.id) {
                        // PUT request (update PA)
                        axios.put("/api/pa/update/" + this.$route.params.id, {
                            pa: this.pa,
                            additionalVariable: "withEmail"
                        })
                            .then((response) => {
                                Swal.close(); // Close the loading modal
                                Swal.fire(
                                    'Sent!',
                                    'Your PA has been saved.',
                                    'success'
                                );
                                this.$router.go(-1); // Navigate back
                            })
                            .catch((error) => {
                                Swal.close(); // Close the loading modal
                                Swal.fire(
                                    'Error!',
                                    'There was an error modifying your PA.',
                                    'error'
                                );
                            })
                            .finally(() => {
                                this.loading = false; // Reset loading state
                            });
                    } else {
                        // Check for required fields
                        if (this.pa.staff_email === '' || this.pa.year_pa === '') {
                            Swal.close(); // Close the loading modal
                            Swal.fire({
                                icon: 'error',
                                title: 'Oops...',
                                text: 'Please select staff email and year of appraisal!',
                            });
                        } else {
                            // POST request (store new PA)
                            this.loading = true;
                            axios.post('/api/pa/store', {
                                pa: this.pa,
                                additionalVariable: "withEmail"
                            })
                                .then((response) => {
                                    Swal.close(); // Close the loading modal
                                    Swal.fire(
                                        'Sent!',
                                        'Your PA has been saved.',
                                        'success'
                                    );
                                    this.$router.go(-1); // Navigate back
                                })
                                .catch((error) => {
                                    Swal.close(); // Close the loading modal
                                    Swal.fire(
                                        'Error!',
                                        'You miss some data in your form. Please check it.',
                                        'error'
                                    );
                                })
                                .finally(() => {
                                    this.loading = false; // Reset loading state
                                });
                        }
                    }
                }
            });
        },

        calculateMonth(startDate, endDate) {
            const monthDifference = (new Date(endDate).getFullYear() * 12 + new Date(endDate).getMonth()) - (new Date(startDate).getFullYear() * 12 + new Date(startDate).getMonth());
            return monthDifference;
        },
        totalPreviousQualitative(a, b, c, total_score_quantitative) {
            const sum = Math.round((parseFloat(a || 0) + parseFloat(b || 0) + parseFloat(c || 0)) / 3);
            const result = Math.round(parseFloat(sum) + parseFloat(total_score_quantitative || 0)) / 2;
            return result;
        },
    },
    mounted() {
        if (this.$route.params.id) {
            var email = '';
            axios.get("/api/pa/" + this.$route.params.id).then(response => {
                console.log(response.data);
                this.pa = response.data;
                //  this.pa.staff_supervisor_by= response.data.staff_supervisor_by
                this.pa.supervisor_email = response.data.staff_supervisor_by
                this.edit = true;
                this.email = response.data.staff_email;
            })
            // console.log(email);
            // axios.get("/api/getTraining/" + this.email).then(response => {
            //     this.get_staff_training = response.data;
            // })
        }
        else {
            axios.get("/api/staffInfo").then(response => {
                console.log(response.data);
                this.get_staff_info = response.data;
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
