<template>
  <v-container fluid class="pa-6">
    <v-tabs v-model="tab" bg-color="primary">
      <v-tab value="Contamination">Contamination</v-tab>
      <v-tab value="MonthlyResult">Monthly</v-tab>
      <v-tab value="YTDResult">YTD Result</v-tab>
      <v-tab value="Contaminate">Contaminate =>3</v-tab> 
      
    </v-tabs>
    <v-spacer class="mb-4"></v-spacer>

    <v-window v-model="tab">
      <!-- ==================== CONTAMINATION TAB ==================== -->
      <v-window-item value="Contamination">
        <v-row class="mb-4">
          <v-col cols="12" md="2">
            <!-- Month picker – no @change, watcher does the job -->
            <v-text-field v-model="selectedDate" type="month" label="Select Month" outlined density="comfortable" />
          </v-col>

          <v-col cols="12" md="1">
            <v-select v-model="platform" :items="['All', 'BTB', 'SR', 'KSP', 'PP', 'KC']" label="Platform" outlined
              density="comfortable" />
          </v-col>

          <v-col cols="12" md="2">
            <v-select v-model="contamination" :items="[
              { title: 'Machine', value: 'contamination_level_machine' },
              { title: 'Bottle', value: 'contamination_level_bottle' }
            ]" item-title="title" item-value="value" label="Contamination Type" outlined density="comfortable" />
          </v-col>

          <v-col cols="12" md="1">
            <v-select v-model="level" :items="['All', 0, 1, 2, 3]" label="Level" outlined density="comfortable" />
          </v-col>
        </v-row>

        <!-- Two-column layout -->
        <v-row>
          <!-- Table column -->
          <v-col cols="12" md="4">
            <div class="summary-table">
              <h3 class="mb-2" style="text-align: center; color: blue;">
                Contamination {{ selectedDate }}
              </h3>
              <table border="1" cellspacing="0" cellpadding="6">
                <thead>
                  <tr>
                    <th style="width:100px;">Level</th>
                    <th v-for="plat in platforms" :key="plat">{{ plat }}</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="lvl in [0, 1, 2, 3]" :key="lvl">
                    <td style="display:flex;align-items:center;gap:6px;">
                      <span class="color-box" :style="{ backgroundColor: colorByLevel(lvl) }"></span>
                      {{ lvl }}
                    </td>

                    <td v-for="plat in platforms" :key="plat" style="text-align:center;">
                      <a href="#" @click.prevent="zoomToLevelPlatform(plat, lvl)"
                        :style="{ color: 'black', fontWeight: 'bold' }">
                        {{ countByPlatformAndLevel(plat, lvl) }}
                      </a>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </v-col>

          <!-- Map column -->
          <v-col cols="12" md="8">
            <div id="map" class="map-container"></div>
          </v-col>
        </v-row>
      </v-window-item>

      <!-- ==================== MONTHLY RESULT TAB ==================== -->
      <!-- ==================== YTD TAB ==================== -->
      <v-window-item value="Contaminate">
        <v-row class="mt-6">
          <!-- YTD Summary Table (uses dataYTD) -->
         

          <!-- High-Contamination Sites (uses highSites) -->
          <v-col cols="12" md="6">
            <div class="summary-table">
              <h3 class="mb-2" style="text-align: center; color: darkred;">
                High Contamination Sites YTD (≥3 times level 2 or 3)
              </h3>
              <table border="1" cellspacing="0" cellpadding="6" style="width:100%; text-align:center;">
                <thead>
                  <tr style="background:#f0f0f0;">
                    <th rowspan="2">Platform</th>
                    <th colspan="2">Machine</th>
                    <th colspan="2">Bottle</th>
                  </tr>
                  <tr style="background:#f0f0f0;">
                    <th>L2</th>
                    <th>L3</th>
                    <th>L2</th>
                    <th>L3</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(sites, plat) in groupedHighSitesYTD" :key="plat">
                    <td style="font-weight:bold;">{{ plat }}</td>
                    <td>{{ Array.from(sites.machineLevel2).join(", ") || "-" }}</td>
                    <td>{{ Array.from(sites.machineLevel3).join(", ") || "-" }}</td>
                    <td>{{ Array.from(sites.bottleLevel2).join(", ") || "-" }}</td>
                    <td>{{ Array.from(sites.bottleLevel3).join(", ") || "-" }}</td>
                  </tr>
                  <tr v-if="Object.keys(groupedHighSitesYTD).length === 0">
                    <td colspan="5" style="text-align:center; font-style:italic;">No high contamination sites</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </v-col>
        </v-row>
      </v-window-item>

      <!-- ==================== Monthly TAB ==================== -->
      <v-window-item value="MonthlyResult">
        <v-row class="mt-6">
          <v-col cols="12" md="12" class="table-container">
            <table class="styled-table" cellspacing="0" cellpadding="5" style="width: 100%; text-align: center;" align="center">
              <thead>
                <tr class="main-title-row">
                  <th colspan="8" class="1">Water Quality Results Per Platform</th>
                </tr>

                <tr class="header-row">
                  <th colspan="3">Microbiological Parameters</th>
                  <th v-for="(item, index) in resultMonthlyTest" :key="index">
                    {{ item.Platform }}
                  </th>
                </tr>
              </thead>

              <tbody>
                <tr class="section-title-row">
                  <td colspan="8">Monthly sampling by advisor</td>
                </tr>

                <tr>
                  <td colspan="3" class="bold-cell">Number of Sites Sampled</td>
                  <td class="font-title-container" v-for="(item, index) in resultMonthlyTest" :key="'sampled-' + index">
                    {{ item.sites }}
                  </td>
                </tr>

                <tr>
                  <td rowspan="2" colspan="2" class="bold-cell">%WHO compliance E. Coli - 0 CFU/100mL</td>
                  <td class="font-title-container">Treatment system</td>
                  <td v-for="(item, index) in resultMonthlyTest" :key="'ecoli-' + index"
                    :class="bgClass(item.machine_percentage)">
                    {{ item.machine_percentage ? item.machine_percentage + ' %' : '-' }}
                  </td>
                </tr>
                <tr>
                  <td class="font-title-container">Bottle</td>
                  <td v-for="(item, index) in resultMonthlyTest" :key="'bottle-ecoli-' + index"
                    :class="bgClass(item.bottle_percentage)">
                    {{ item.bottle_percentage ? item.bottle_percentage + ' %' : '-' }}
                  </td>
                </tr>

                <tr>
                  <td rowspan="2" colspan="2" class="bold-cell">%WHO compliance Coliforms & E. Coli - 0 CFU/100mL</td>
                  <td class="font-title-container">Treatment system</td>
                  <td v-for="(item, index) in resultMonthlyTest" :key="'colif-' + index"
                    :class="bgClass(item.machine_esch_ecoli)">
                    {{ item.machine_esch_ecoli ? item.machine_esch_ecoli + ' %' : '-' }}
                  </td>
                </tr>
                <tr>
                  <td class="font-title-container">Bottle</td>
                  <td v-for="(item, index) in resultMonthlyTest" :key="'bottle-colif-' + index"
                    :class="bgClass(item.bottle_esch_ecoli)">
                    {{ item.bottle_esch_ecoli ? item.bottle_esch_ecoli + ' %' : '-' }}
                  </td>
                </tr>

                <tr>
                  <td colspan="2" class="bold-cell">#Level 1 Alert</td>
                  <td class="font-title-container">Treatment system</td>
                  <td class="font-title-container" v-for="(item, index) in resultMonthlyTest" :key="'lvl1-' + index">{{
                    item.ma_1 }}</td>
                </tr>
                <tr>
                  <td colspan="2" class="bold-cell">#Level 2 Alert</td>
                  <td class="font-title-container">Treatment system</td>
                  <td class="font-title-container" v-for="(item, index) in resultMonthlyTest" :key="'lvl2-' + index">{{
                    item.ma_2 }}</td>
                </tr>
                <tr>
                  <td colspan="2" class="bold-cell">#Level 3 Alert</td>
                  <td class="font-title-container">Treatment system</td>
                  <td class="font-title-container" v-for="(item, index) in resultMonthlyTest" :key="'lvl3-' + index">{{
                    item.ma_3 }}</td>
                </tr>

                <tr>
                  <td colspan="3" class="bold-cell">Site tested under 24h</td>
                  <td v-for="(item, index) in resultMonthlyTest" :key="'delay-' + index" :class="bgClass(item.delay)">
                    {{ item.delay ? item.delay + ' %' : '-' }}
                  </td>
                </tr>

                <tr class="section-title-row">
                  <td colspan="8">Sampling after technician interventions</td>
                </tr>

                <tr>
                  <td colspan="3" class="bold-cell">#Sites re-tested after technician interventions</td>
                  <td class="font-title-container" v-for="(item, index) in resultAfterIntervention"
                    :key="'retest-' + index">{{ item.sites }}</td>
                </tr>

                <tr>
                  <td rowspan="2" colspan="2" class="bold-cell">%WHO compliance E. Coli - 0 CFU/100mL</td>
                  <td class="font-title-container">Treatment system</td>
                  <td v-for="(item, index) in resultAfterIntervention" :key="'ecoli-int-' + index"
                    :class="bgClass(item.machine_percentage)">
                    {{ item.machine_percentage ? item.machine_percentage + ' %' : '-' }}
                  </td>
                </tr>
                <tr>
                  <td class="font-title-container">Bottle</td>
                  <td v-for="(item, index) in resultAfterIntervention" :key="'bottle-int-' + index"
                    :class="bgClass(item.bottle_percentage)">
                    {{ item.bottle_percentage ? item.bottle_percentage + ' %' : '-' }}
                  </td>
                </tr>

                <tr>
                  <td rowspan="2" colspan="2" class="bold-cell">%WHO compliance Coliforms & E. Coli - 0 CFU/100mL</td>
                  <td class="font-title-container">Treatment system</td>
                  <td v-for="(item, index) in resultAfterIntervention" :key="'colif-int-' + index"
                    :class="bgClass(item.machine_esch_ecoli)">
                    {{ item.machine_esch_ecoli ? item.machine_esch_ecoli + ' %' : '-' }}
                  </td>
                </tr>
                <tr>
                  <td class="font-title-container">Bottle</td>
                  <td v-for="(item, index) in resultAfterIntervention" :key="'bottle-colif-int-' + index"
                    :class="bgClass(item.bottle_esch_ecoli)">
                    {{ item.bottle_esch_ecoli ? item.bottle_esch_ecoli + ' %' : '-' }}
                  </td>
                </tr>

                <tr class="section-title-row">
                  <td colspan="8">Global view after technician interventions</td>
                </tr>

                <tr>
                  <td colspan="2" class="bold-cell">%WHO compliance E. Coli - 0 CFU/100mL</td>
                  <td class="font-title-container">Treatment system</td>
                  <td v-for="(item, index) in resultGlobalView" :key="'global-ecoli-' + index"
                    :class="bgClass(item.machine_percentage)">
                    {{ item.machine_percentage ? item.machine_percentage + ' %' : '-' }}
                  </td>
                </tr>
                <tr>
                  <td colspan="2" class="bold-cell">Calculated on ALL sites</td>
                  <td class="font-title-container">Bottle</td>
                  <td v-for="(item, index) in resultGlobalView" :key="'global-bottle-' + index"
                    :class="bgClass(item.bottle_percentage)">
                    {{ item.bottle_percentage ? item.bottle_percentage + ' %' : '-' }}
                  </td>
                </tr>

                <tr>
                  <td colspan="2" class="bold-cell">%WHO compliance Coliforms & E. Coli - 0 CFU/100mL</td>
                  <td class="font-title-container">Treatment system</td>
                  <td v-for="(item, index) in resultGlobalView" :key="'global-colif-' + index"
                    :class="bgClass(item.machine_esch_ecoli)">
                    {{ item.machine_esch_ecoli ? item.machine_esch_ecoli + ' %' : '-' }}
                  </td>
                </tr>
                <tr>
                  <td colspan="2" class="bold-cell">Calculated on ALL sites</td>
                  <td class="font-title-container">Bottle</td>
                  <td v-for="(item, index) in resultGlobalView" :key="'global-bottle-colif-' + index"
                    :class="bgClass(item.bottle_esch_ecoli)">
                    {{ item.bottle_esch_ecoli ? item.bottle_esch_ecoli + ' %' : '-' }}
                  </td>
                </tr>
              </tbody>
            </table>
          </v-col>
        </v-row>
      </v-window-item>

      <!-- YTD TAB Results Here -->
      <v-window-item value="YTDResult">
        <v-row class="mt-6">
          <v-col cols="12" md="12" class="table-container">
            <table class="styled-table" cellspacing="0" cellpadding="5" style="width: 100%; text-align: center;" align="center">
              <thead>
                <tr class="main-title-row">
                    <th colspan="8" class="1">Water Quality Results Summary {{ selectedDate.split('-')[0] }}</th>
                </tr>

                <tr class="header-row">
                  <th colspan="3">Microbiological Parameters</th>
                  <th v-for="(item, index) in resultYTD" :key="index">
                    {{ item.month }}
                  </th>
                </tr>
              </thead>

              <tbody>
                <tr class="section-title-row">
                  <td colspan="8">Monthly sampling by advisor</td>
                </tr>

                <tr>
                  <td colspan="3" class="bold-cell">Number of Sites Sampled</td>
                  <td class="font-title-container" v-for="(item, index) in resultYTD" :key="'sampled-' + index">
                    {{ item.sites }}
                  </td>
                </tr>

                <tr>
                  <td rowspan="2" colspan="2" class="bold-cell">%WHO compliance E. Coli - 0 CFU/100mL</td>
                  <td class="font-title-container">Treatment system</td>
                  <td v-for="(item, index) in resultYTD" :key="'ecoli-' + index"
                    :class="bgClass(item.machine_percentage)">
                    {{ item.machine_percentage ? item.machine_percentage + ' %' : '-' }}
                  </td>
                </tr>
                <tr>
                  <td class="font-title-container">Bottle</td>
                  <td v-for="(item, index) in resultYTD" :key="'bottle-ecoli-' + index"
                    :class="bgClass(item.bottle_percentage)">
                    {{ item.bottle_percentage ? item.bottle_percentage + ' %' : '-' }}
                  </td>
                </tr>

                <tr>
                  <td rowspan="2" colspan="2" class="bold-cell">%WHO compliance Coliforms & E. Coli - 0 CFU/100mL</td>
                  <td class="font-title-container">Treatment system</td>
                  <td v-for="(item, index) in resultYTD" :key="'colif-' + index"
                    :class="bgClass(item.machine_esch_ecoli)">
                    {{ item.machine_esch_ecoli ? item.machine_esch_ecoli + ' %' : '-' }}
                  </td>
                </tr>
                <tr>
                  <td class="font-title-container">Bottle</td>
                  <td v-for="(item, index) in resultYTD" :key="'bottle-colif-' + index"
                    :class="bgClass(item.bottle_esch_ecoli)">
                    {{ item.bottle_esch_ecoli ? item.bottle_esch_ecoli + ' %' : '-' }}
                  </td>
                </tr>

                <tr>
                  <td colspan="2" class="bold-cell">#Level 1 Alert</td>
                  <td class="font-title-container">Treatment system</td>
                  <td class="font-title-container" v-for="(item, index) in resultYTD" :key="'lvl1-' + index">{{
                    item.ma_1 }}</td>
                </tr>
                <tr>
                  <td colspan="2" class="bold-cell">#Level 2 Alert</td>
                  <td class="font-title-container">Treatment system</td>
                  <td class="font-title-container" v-for="(item, index) in resultYTD" :key="'lvl2-' + index">{{
                    item.ma_2 }}</td>
                </tr>
                <tr>
                  <td colspan="2" class="bold-cell">#Level 3 Alert</td>
                  <td class="font-title-container">Treatment system</td>
                  <td class="font-title-container" v-for="(item, index) in resultYTD" :key="'lvl3-' + index">{{
                    item.ma_3 }}</td>
                </tr>

                <tr>
                  <td colspan="3" class="bold-cell">Site tested under 24h</td>
                  <td v-for="(item, index) in resultYTD" :key="'delay-' + index" :class="bgClass(item.delay)">
                    {{ item.delay ? item.delay + ' %' : '-' }}
                  </td>
                </tr>

                <tr class="section-title-row">
                  <td colspan="8">Sampling after technician interventions</td>
                </tr>

                <tr>
                  <td colspan="3" class="bold-cell">#Sites re-tested after technician interventions</td>
                  <td class="font-title-container" v-for="(item, index) in resultsAfterInterventionYTD"
                    :key="'retest-' + index">{{ item.sites }}</td>
                </tr>

                <tr>
                  <td rowspan="2" colspan="2" class="bold-cell">%WHO compliance E. Coli - 0 CFU/100mL</td>
                  <td class="font-title-container">Treatment system</td>
                  <td v-for="(item, index) in resultsAfterInterventionYTD" :key="'ecoli-int-' + index"
                    :class="bgClass(item.machine_percentage)">
                    {{ item.machine_percentage ? item.machine_percentage + ' %' : '-' }} 
                  </td>
                </tr>
                <tr>
                  <td class="font-title-container">Bottle</td>
                  <td v-for="(item, index) in resultsAfterInterventionYTD" :key="'bottle-int-' + index"
                    :class="bgClass(item.bottle_percentage)">
                    {{ item.bottle_percentage ? item.bottle_percentage + ' %' : '-' }}
                  </td>
                </tr>

                <tr>
                  <td rowspan="2" colspan="2" class="bold-cell">%WHO compliance Coliforms & E. Coli - 0 CFU/100mL</td>
                  <td class="font-title-container">Treatment system</td>
                  <td v-for="(item, index) in resultsAfterInterventionYTD" :key="'colif-int-' + index"
                    :class="bgClass(item.machine_esch_ecoli)">
                    {{ item.machine_esch_ecoli ? item.machine_esch_ecoli + ' %' : '-' }}
                  </td>
                </tr>
                <tr>
                  <td class="font-title-container">Bottle</td>
                  <td v-for="(item, index) in resultsAfterInterventionYTD" :key="'bottle-colif-int-' + index"
                    :class="bgClass(item.bottle_esch_ecoli)">
                    {{ item.bottle_esch_ecoli ? item.bottle_esch_ecoli + ' %' : '-' }}
                  </td>
                </tr>

                <tr class="section-title-row">
                  <td colspan="8">Global view after technician interventions</td>
                </tr>

                <tr>
                  <td colspan="2" class="bold-cell">%WHO compliance E. Coli - 0 CFU/100mL</td>
                  <td class="font-title-container">Treatment system</td>
                  <td v-for="(item, index) in resultGlobalViewYTD" :key="'global-ecoli-' + index"
                    :class="bgClass(item.machine_percentage)">
                    {{ item.machine_percentage ? item.machine_percentage + ' %' : '-' }}
                  </td>
                </tr>
                <tr>
                  <td colspan="2" class="bold-cell">Calculated on ALL sites</td>
                  <td class="font-title-container">Bottle</td>
                  <td v-for="(item, index) in resultGlobalViewYTD" :key="'global-bottle-' + index"
                    :class="bgClass(item.bottle_percentage)">
                    {{ item.bottle_percentage ? item.bottle_percentage + ' %' : '-' }}
                  </td>
                </tr>

                <tr>
                  <td colspan="2" class="bold-cell">%WHO compliance Coliforms & E. Coli - 0 CFU/100mL</td>
                  <td class="font-title-container">Treatment system</td>
                  <td v-for="(item, index) in resultGlobalViewYTD" :key="'global-colif-' + index"
                    :class="bgClass(item.machine_esch_ecoli)">
                    {{ item.machine_esch_ecoli ? item.machine_esch_ecoli + ' %' : '-' }}
                  </td>
                </tr>
                <tr>
                  <td colspan="2" class="bold-cell">Calculated on ALL sites</td>
                  <td class="font-title-container">Bottle</td>
                  <td v-for="(item, index) in resultGlobalViewYTD" :key="'global-bottle-colif-' + index"
                    :class="bgClass(item.bottle_esch_ecoli)">
                    {{ item.bottle_esch_ecoli ? item.bottle_esch_ecoli + ' %' : '-' }}
                  </td>
                </tr>
                <tr class="header-row">
                  <th colspan="3">Physical and chemical parameters</th>
                  <th v-for="(item, index) in physicAndChimical" :key="index">
                    {{ item.month }}
                  </th>
                </tr>
                <tr>
                  <th class="bold-cell" rowspan="2" colspan="2">%Compliance on pH - 6.5 & pH ≤ 8.5</th>
                   <th> #Sites tested</th>
                   <td v-for="(item, index) in physicAndChimical" :key="index" >
                    {{ item.ph_tested }}
                  </td>
                </tr>
                <tr class="bold-cell">
                  <th> % </th>
                   <td v-for="(item, index) in physicAndChimical" :key="index" :class="bgClass(item.normal_ph_percentage)">
                    {{ item.normal_ph_percentage ? item.normal_ph_percentage + ' %' : '-' }}
                  </td>
                </tr>

                <tr>
                  <th class="bold-cell" rowspan="2" colspan="2">%Compliance on turbidity - 2 NTU</th>
                   <th> #Sites tested</th>
                   <td v-for="(item, index) in physicAndChimical" :key="index" >
                    {{ item.turbidity_tested }}
                  </td>
                </tr>
                <tr class="bold-cell">
                  <th> % </th>
                   <td v-for="(item, index) in physicAndChimical" :key="index" :class="bgClass(item.normal_turbidity_percentage)">
                    {{ item.normal_turbidity_percentage ? item.normal_turbidity_percentage + ' %' : '-' }}
                  </td>
                </tr>

                <tr>
                  <th class="bold-cell" rowspan="2" colspan="2">%Compliance on TDS - 250 mg/L</th>
                   <th> #Sites tested</th>
                   <td v-for="(item, index) in physicAndChimical" :key="index" >
                    {{ item.tds_tested }}
                  </td>
                </tr>
                <tr class="bold-cell">
                  <th> % </th>
                   <td v-for="(item, index) in physicAndChimical" :key="index" :class="bgClass(item.normal_tds_percentage)">
                    {{ item.normal_tds_percentage ? item.normal_tds_percentage + ' %' : '-' }}
                  </td>
                </tr>

                <tr>
                  <th class="bold-cell" rowspan="2" colspan="2">%Compliance on Nitrate - 50 mg/L</th>
                   <th> #Sites tested</th>
                   <td v-for="(item, index) in physicAndChimical" :key="index" >
                    {{ item.nitrate_tested }}
                  </td>
                </tr>
                <tr class="bold-cell">
                  <th> % </th>
                  <td v-for="(item, index) in physicAndChimical" :key="index" :class="bgClass(item.normal_nitrate_percentage)">
                    {{ item.normal_nitrate_percentage ? item.normal_nitrate_percentage + ' %' : '-' }}
                  </td>
                </tr>

                <tr>
                  <th class="bold-cell" rowspan="2" colspan="2">%Compliance on Nitrite - 50 mg/L</th>
                   <th> #Sites tested</th>
                   <td v-for="(item, index) in physicAndChimical" :key="index" >
                    {{ item.nitrite_tested }}
                  </td>
                </tr>
                <tr class="bold-cell">
                  <th> % </th>
                   <td v-for="(item, index) in physicAndChimical" :key="index" :class="bgClass(item.normal_nitrite_percentage)">
                    {{ item.normal_nitrite_percentage ? item.normal_nitrite_percentage + ' %' : '-' }}
                  </td>
                </tr>

                <tr>
                  <th class="bold-cell" rowspan="2" colspan="2">%Compliance on Iron - 0.05 mg/L</th>
                   <th> #Sites tested</th>
                   <td v-for="(item, index) in physicAndChimical" :key="index" >
                    {{ item.iron_tested }}
                  </td>
                </tr>
                <tr class="bold-cell">
                  <th> % </th>
                   <td v-for="(item, index) in physicAndChimical" :key="index" :class="bgClass(item.normal_iron_percentage)">
                    {{ item.normal_iron_percentage ? item.normal_iron_percentage + ' %' : '-' }}
                  </td>
                </tr>

                <tr>
                  <th class="bold-cell" rowspan="2" colspan="2">%Compliance on Manganese - 0.05 mg/L</th>
                   <th> #Sites tested</th>
                   <td v-for="(item, index) in physicAndChimical" :key="index">
                    {{ item.manganese_tested }}
                  </td>
                </tr>
                <tr class="bold-cell">
                  <th> % </th>
                   <td v-for="(item, index) in physicAndChimical" :key="index" :class="bgClass(item.normal_manganese_percentage)">
                    {{ item.normal_manganese_percentage ? item.normal_manganese_percentage + ' %' : '-' }}
                  </td>
                </tr>

                <tr>
                  <th class="bold-cell" rowspan="2" colspan="2">%Compliance on Aluminium - 0.2 mg/L</th>
                   <th> #Sites tested</th>
                   <td v-for="(item, index) in physicAndChimical" :key="index" >
                    {{ item.aluminium_tested }}
                  </td>
                </tr>
                <tr class="bold-cell">
                  <th> % </th>
                   <td v-for="(item, index) in physicAndChimical" :key="index" :class="bgClass(item.normal_aluminium_percentage)">
                    {{ item.normal_aluminium_percentage ? item.normal_aluminium_percentage + ' %' : '-' }}
                  </td>
                </tr>
              </tbody>
            </table>
          </v-col>
        </v-row>
      </v-window-item>
    </v-window>
  </v-container>
</template>

<script setup>
import { ref, computed, onMounted, watch, nextTick } from "vue";
import axios from "axios";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import Swal from "sweetalert2";

/* ------------------- Reactive state ------------------- */
const tab = ref("Contamination");
const selectedDate = ref(new Date().toISOString().slice(0, 7)); // YYYY-MM
const platform = ref("All");
const contamination = ref("contamination_level_machine");
const level = ref("All");

const allSamples = ref([]);
const dataYTD = ref({});
const highSites = ref([]);
const resultMonthlyTest = ref([]);
const resultAfterIntervention = ref([]);
const resultGlobalView = ref([]);
const resultYTD = ref([]);
const resultsAfterInterventionYTD = ref([]);
const resultGlobalViewYTD = ref([]);
const physicAndChimical = ref([]);
const map = ref(null);
const markers = ref([]);

const platforms = ["BTB", "SR", "KSP", "PP", "KC"];

/* ------------------- Helpers ------------------- */
const colorByLevel = (lvl) => {
  switch (parseInt(lvl)) {
    case 0: return "darkblue";
    case 1: return "yellow";
    case 2: return "orange";
    case 3: return "red";
    default: return "gray";
  }
};

const bgClass = (value) => {
  const v = parseFloat(value);
  if (v === 100) return "bg-green";
  if (v >= 98.01 && v <= 99.95) return "bg-yellow";
  if (v >= 1 && v <= 98) return "bg-darkred";
  return "";
};

const createLabeledMarker = (idSite, siteName, color) => {
  const label = `${idSite ?? ""} - ${siteName ?? ""}`;
  return L.divIcon({
    className: "custom-marker",
    html: `
      <div style="display:flex;flex-direction:column;align-items:center;">
        <span style="background:${color};width:14px;height:14px;border-radius:50%;border:2px solid white;box-shadow:0 0 3px rgba(0,0,0,0.4);"></span>
        <small style="background:white;color:black;padding:2px 4px;border-radius:4px;margin-top:2px;font-size:9px;font-weight:bold;white-space:nowrap;">
          ${label}
        </small>
      </div>`,
    iconSize: [40, 40],
    iconAnchor: [20, 20],
  });
};

/* ------------------- Map init ------------------- */
const initMap = async () => {
  await nextTick();
  const container = document.getElementById("map");
  if (!container) {
    setTimeout(initMap, 300);
    return;
  }
  if (map.value) return;

  map.value = L.map("map", {
    minZoom: 7,
    maxZoom: 14,
    zoomControl: true,
    maxBounds: [[9.5, 102.3], [15.0, 107.6]],
  }).setView([12.5657, 104.991], 7);

  L.tileLayer("https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png", {
    attribution: "© OpenStreetMap contributors",
    subdomains: "abcd",
    maxZoom: 19,
  }).addTo(map.value);
};

/* ------------------- Data fetch ------------------- */
const fetchMapData = async () => {
  if (!selectedDate.value) return;

  Swal.fire({
    title: "Loading data…",
    allowOutsideClick: false,
    didOpen: () => Swal.showLoading(),
  });

  try {
    const { data } = await axios.get("/api/WQReport", {
      params: { month: `${selectedDate.value}-01` },
    });

    allSamples.value = Array.isArray(data.dataThisMonth) ? data.dataThisMonth : [];
    dataYTD.value = typeof data.dataYTD === "object" && data.dataYTD !== null ? data.dataYTD : {};
    highSites.value = (data.highContaminationSites || []).map(s => ({
      Id_Site: s.Id_Site,
      platform: s.platform,
      machineLevel2: s.machine?.level2 ?? 0,
      machineLevel3: s.machine?.level3 ?? 0,
      bottleLevel2: s.bottle?.level2 ?? 0,
      bottleLevel3: s.bottle?.level3 ?? 0,
    }));

    resultMonthlyTest.value = Array.isArray(data.resultMonthlyTest) ? data.resultMonthlyTest : [];
    resultAfterIntervention.value = Array.isArray(data.resultAfterIntervention) ? data.resultAfterIntervention : [];
    resultGlobalView.value = Array.isArray(data.resultGlobalView) ? data.resultGlobalView : [];
    resultYTD.value = Array.isArray(data.resultYTD) ? data.resultYTD : [];
    resultsAfterInterventionYTD.value = Array.isArray(data.resultsAfterInterventionYTD) ? data.resultsAfterInterventionYTD : [];
    resultGlobalViewYTD.value = Array.isArray(data.resultGlobalViewYTD) ? data.resultGlobalViewYTD : [];
    physicAndChimical.value = Array.isArray(data.physicAndChimical) ? data.physicAndChimical : [];

    renderMarkers(filteredSamples.value);
  } catch (e) {
    console.error(e);
    Swal.fire("Error", "Failed to load data", "error");
  } finally {
    Swal.close();
  }
};

/* ------------------- Computed ------------------- */
const filteredSamples = computed(() => {
  let list = [...allSamples.value];
  if (platform.value !== "All") list = list.filter(s => s.platform === platform.value);
  if (level.value !== "All") {
    list = list.filter(s => {
      const val = contamination.value === "contamination_level_machine"
        ? s.machine_contamination_level
        : s.bottle_contamination;
      return parseInt(val) === parseInt(level.value);
    });
  }
  return list;
});

/* ------------------- Render markers ------------------- */
const renderMarkers = (samples) => {
  if (!map.value) return;
  markers.value.forEach(m => map.value.removeLayer(m));
  markers.value = [];

  const latLngs = [];
  samples.forEach(s => {
    if (!s.latitude || !s.longitude) return;
    const val = contamination.value === "contamination_level_machine"
      ? s.machine_contamination_level
      : s.bottle_contamination;
    const marker = L.marker([s.latitude, s.longitude], {
      icon: createLabeledMarker(s.Id_Site, s.SiteName_En, colorByLevel(val)),
    })
      .bindPopup(`
        <b>Site:</b> ${s.Id_Site}<br>
        <b>Machine Level:</b> ${s.machine_contamination_level}<br>
        <b>Bottle Level:</b> ${s.bottle_contamination}<br>
        <b>Platform:</b> ${s.platform ?? "-"}
      `)
      .addTo(map.value);

    markers.value.push(marker);
    latLngs.push([s.latitude, s.longitude]);
  });

  if (latLngs.length) {
    map.value.fitBounds(L.latLngBounds(latLngs), { padding: [50, 50] });
  } else {
    map.value.setView([12.5657, 104.991], 7);
  }
};

/* ------------------- Table helpers ------------------- */
const countByPlatformAndLevel = (plat, lvl) => {
  return allSamples.value.filter(s => {
    if (platform.value !== "All" && s.platform !== platform.value) return false;
    if (plat !== "All" && s.platform !== plat) return false;
    const val = contamination.value === "contamination_level_machine"
      ? s.machine_contamination_level
      : s.bottle_contamination;
    return parseInt(val) === lvl;
  }).length;
};



const getYTD = (plat, type, lvl) => {
  const field = type === "machine" ? "machine" : "bottle";
  return dataYTD.value?.[plat]?.[field]?.[lvl] ?? 0;
};

const groupedHighSitesYTD = computed(() => {
  const groups = {};
  highSites.value.forEach(s => {
    if (!groups[s.platform]) {
      groups[s.platform] = {
        machineLevel2: new Set(),
        machineLevel3: new Set(),
        bottleLevel2: new Set(),
        bottleLevel3: new Set(),
      };
    }
    if (s.machineLevel2) groups[s.platform].machineLevel2.add(s.Id_Site);
    if (s.machineLevel3) groups[s.platform].machineLevel3.add(s.Id_Site);
    if (s.bottleLevel2) groups[s.platform].bottleLevel2.add(s.Id_Site);
    if (s.bottleLevel3) groups[s.platform].bottleLevel3.add(s.Id_Site);
  });
  return groups;
});

const zoomToLevelPlatform = (plat, lvl) => {
  // temporary – you already have the logic elsewhere
  platform.value = plat;
  level.value = lvl;
};

/* ------------------- Watchers ------------------- */

/* 1. Month change → fetch everything */
watch(selectedDate, (newVal) => {
  if (newVal) fetchMapData();
}, { immediate: true });

/* 2. Filter changes → redraw markers */
watch([platform, contamination, level], () => {
  renderMarkers(filteredSamples.value);
});

/* 3. Tab change → re-init map or refetch data */
watch(tab, async (newTab) => {
  if (newTab === "Contamination") {
    await nextTick();
    initMap();
    renderMarkers(filteredSamples.value);
  }

  // Ensure data is present for the other tabs
  // if (["MonthlyResult", "YTD"].includes(newTab) && selectedDate.value) {
  //   await fetchMapData();
  // }
});

/* ------------------- Mount ------------------- */
onMounted(async () => {
  await nextTick();
  initMap(); // map will be ready when Contamination tab is first shown
});
</script>

<style scoped>
.map-container {
  height: 420px;
  width: 100%;
  border-radius: 10px;
  overflow: hidden;
}

.summary-table {
  margin-bottom: 16px;
}

.legend {
  position: absolute;
  bottom: 15px;
  right: 25px;
  background: white;
  padding: 8px 12px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
  font-size: 12px;
  line-height: 1.4;
}

.legend .circle {
  display: inline-block;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  margin-right: 6px;
  vertical-align: middle;
  border: 1px solid #ccc;
}

.summary-table table {
  border-collapse: collapse;
  width: 100%;
  text-align: center;
}

.summary-table th {
  background: #f0f0f0;
}

.summary-table td,
.summary-table th {
  padding: 6px 12px;
}

.color-box {
  display: inline-block;
  width: 16px;
  height: 16px;
  border-radius: 4px;
  border: 1px solid #555;
}

.styled-table {
  border-collapse: collapse;
  font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
  font-size: 13px;
  color: #333;
  max-width: 90%; /* Adjust this percentage as needed */
  width: auto; /* Let the table size naturally */
  margin: 0 auto; /* This centers the table */
}

.styled-table th,
.styled-table td {
  border: 1px solid #ddd;
  padding: 5px 6px;
  /* less padding */
  line-height: 1.2;
  /* tighter line height */
}

.main-title-row th {
  font-size: 16px;
  /* smaller main title */
  padding: 8px 10px;
}

.header-row th {
  background-color: #a5d6a7;
  color: #1b5e20;
  font-weight: bold;
  font-size: 14px;
  /* slightly smaller header */
  text-align: center;

}

.section-title-row td {
  font-size: 16px;
  /* slightly smaller section titles */
  padding-left: 8px;
  background-color: #e8f5e9;
  color: blue;
  font-weight: bold;
}

.bold-cell {
  font-weight: bold;
  background-color: #f1f8e9;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans", sans-serif;
}

tbody tr:nth-child(even):not(.section-title-row) {
  background-color: #f9fbe7;
}

tbody tr:hover {
  background-color: #c8e6c9;
  transition: background-color 0.3s ease;
}

.bg-darkred {
  background-color: #B71C1C;
  color: white;
  font-weight: bold;
}

.bg-yellow {
  background-color: #FFEB3B;
  color: #333;
  font-weight: bold;
}

.bg-green {
  background-color: #4CAF50;
  color: white;
  font-weight: bold;
}

.font-title-container {
  font-size: 12px;
  font-weight: bold;
  text-align: center;
  margin-bottom: 12px;
}

.head-font-title-container {
  font-size: 20px;
  font-weight: bold;
  text-align: center;
  margin-bottom: 12px;
  color: darkred;
}
</style>
