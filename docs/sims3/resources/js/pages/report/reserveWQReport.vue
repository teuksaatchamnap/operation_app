<template>
  <v-container fluid class="pa-6">
    <!-- Filters -->
    <v-row class="mb-4">
      <v-col cols="12" md="2">
        <v-text-field v-model="selectedDate" type="month" label="Select Month" outlined density="comfortable"
          @change="fetchMapData" />
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
          <h3 class="mb-2" style="text-align: center; color: blue;">Contamination {{ selectedDate }} </h3>
          <table border="1" cellspacing="0" cellpadding="6">
            <thead>
              <tr>
                <th style="width:100px;">Level</th>
                <th v-for="plat in platforms" :key="plat">{{ plat }}</th>
                <!-- <th>Total</th> -->
              </tr>
            </thead>
            <tbody>
              <tr v-for="lvl in [0, 1, 2, 3]" :key="lvl">
                <td style="display:flex;align-items:center;gap:6px;">
                  <span class="color-box" :style="{ backgroundColor: colorByLevel(lvl) }"></span>
                  {{ lvl }}
                </td>

                <!-- Platform counts -->
                <td v-for="plat in platforms" :key="plat" style="text-align:center;">
                  <a href="#" @click.prevent="zoomToLevelPlatform(plat, lvl)" :style="{
                    color: lvl === 0 ? 'black' : 'black',
                    fontWeight: 'bold'
                  }">
                    {{ countByPlatformAndLevel(plat, lvl) }}
                  </a>
                </td>

                <!-- Total column -->
                <!-- <td style="text-align:center; font-weight:bold;" :style="{ color: lvl === 0 ? 'black' : 'black' }">
                  {{ totalCountByLevel(lvl) }}
                </td> -->
                <!-- <td style="text-align:center; font-weight:bold;"
                    :style="{ color: lvl === 0 ? 'black' : colorByLevel(lvl) }">
                  {{ totalCountByLevel(lvl) }}
                </td> -->
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
 <!-- another YTD filter -->
  <!-- Below the current Contamination Summary table -->
<!-- YTD table (Machine then Bottle, with rowspan for Type label) -->
    <v-row class="mt-6">
  <!-- Left: YTD table -->
  <v-col cols="12" md="6">
    <div class="summary-table">
          <h3 class="mb-2" style="text-align: center; color: green;">Contamination Summary (Year-To-Date)</h3>

          <table border="1" cellspacing="0" cellpadding="6" style="width:100%; text-align:center;">
            <thead>
              <tr>
                <th rowspan="2">Type</th>
                <th rowspan="2">Level</th>
                <th v-for="plat in platforms" :key="'hdr-'+plat">{{ plat }}</th>
                <!-- <th rowspan="2">Total</th> -->
              </tr>
            </thead>

            <tbody>
              <!-- Machine block -->
              <tr>
                <td rowspan="4" style="vertical-align:middle; font-weight:bold;">Machine</td>
                <td style="display:flex;align-items:center;gap:6px;">
                  <span class="color-box" :style="{ backgroundColor: colorByLevel(0) }"></span>
                  0
                </td>
                <td v-for="plat in platforms" :key="'m-'+plat+'-0'">{{ getYTD(plat, 'machine', 0) }}</td>
                <!-- <td rowspan="4" style="vertical-align:middle; font-weight:bold;">
                  {{ totalYTD('machine') }}
                </td> -->
              </tr>
              <tr>
                <td style="display:flex;align-items:center;gap:6px;">
                  <span class="color-box" :style="{ backgroundColor: colorByLevel(1) }"></span>
                  1
                </td>
                <td v-for="plat in platforms" :key="'m-'+plat+'-1'" >
                  {{ getYTD(plat, 'machine', 1) }}
                </td>
              </tr>
              <tr>
                <td style="display:flex;align-items:center;gap:6px;">
                  <span class="color-box" :style="{ backgroundColor: colorByLevel(2) }"></span>
                  2
                </td>
                <td v-for="plat in platforms" :key="'m-'+plat+'-2'" >
                  {{ getYTD(plat, 'machine', 2) }}
                </td>
              </tr>
              <tr>
                <td style="display:flex;align-items:center;gap:6px;">
                  <span class="color-box" :style="{ backgroundColor: colorByLevel(3) }"></span>
                  3
                </td>
                <td v-for="plat in platforms" :key="'m-'+plat+'-3'" >
                  {{ getYTD(plat, 'machine', 3) }}
                </td>
              </tr>

              <!-- Bottle block -->
              <tr>
                <td rowspan="4" style="vertical-align:middle; font-weight:bold;">Bottle</td>
                <td style="display:flex;align-items:center;gap:6px;">
                  <span class="color-box" :style="{ backgroundColor: colorByLevel(0) }"></span>
                  0
                </td>
                <td v-for="plat in platforms" :key="'b-'+plat+'-0'">{{ getYTD(plat, 'bottle', 0) }}</td>
                <!-- <td rowspan="4" style="vertical-align:middle; font-weight:bold;">
                  {{ totalYTD('bottle') }}
                </td> -->
              </tr>
              <tr>
                <td style="display:flex;align-items:center;gap:6px;">
                  <span class="color-box" :style="{ backgroundColor: colorByLevel(1) }"></span>
                  1
                </td>
                <td v-for="plat in platforms" :key="'b-'+plat+'-1'" >
                  {{ getYTD(plat, 'bottle', 1) }}
                </td>
              </tr>
              <tr>
                <td style="display:flex;align-items:center;gap:6px;">
                  <span class="color-box" :style="{ backgroundColor: colorByLevel(2) }"></span>
                  2
                </td>
                <td v-for="plat in platforms" :key="'b-'+plat+'-2'" >
                  {{ getYTD(plat, 'bottle', 2) }}
                </td>
              </tr>
              <tr>
                <td style="display:flex;align-items:center;gap:6px;">
                  <span class="color-box" :style="{ backgroundColor: colorByLevel(3) }"></span>
                  3
                </td>
                <td v-for="plat in platforms" :key="'b-'+plat+'-3'" >
                  {{ getYTD(plat, 'bottle', 3) }}
                </td>
              </tr>

            </tbody>
          </table>
        </div>
  </v-col>

  <!-- Right: High Contamination Sites -->
  <!-- Right: High Contamination Sites -->
<!-- Right: High Contamination Sites -->
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

 <v-row class="mt-6">
    <v-col cols="12" md="7">
      <table class="styled-table" cellspacing="0" cellpadding="5" style="width: 100%; text-align: center;">
        <thead>
          <tr class="main-title-row">
            <th colspan="8" class="head-font-title-container">Water Quality Results Per Platform</th>
          </tr>

          <tr class="header-row">
            <th colspan="3">Microbiological Parameters</th>
            <th v-for="(item, index) in resultMonthlyTest" :key="index">
              {{ item.Platform }}
            </th>
          </tr>
        </thead>

        <tbody>
          <tr class="section-title-row"><td colspan="8">Monthly sampling by advisor</td></tr>

          <tr>
            <td colspan="3" class="bold-cell">Number of Sites Sampled</td>
            <td class="font-title-container" v-for="(item, index) in resultMonthlyTest" :key="'sampled-'+index">{{ item.sites }}</td>
          </tr>

          <tr>
            <td rowspan="2" colspan="2" class="bold-cell">%WHO compliance E. Coli - 0 CFU/100mL</td>
            <td class="font-title-container">Treatment system</td>
            <td
                  v-for="(item, index) in resultMonthlyTest"
                  :key="'ecoli-'+index"
                  :class="{
                    'bg-green': parseFloat(item.machine_percentage) === 100,
                    'bg-yellow': parseFloat(item.machine_percentage) >= 80.01 && parseFloat(item.machine_percentage) <= 99.95,
                    'bg-darkred': parseFloat(item.machine_percentage) >= 1 && parseFloat(item.machine_percentage) <= 80
                  }"
                >
                  {{ item.machine_percentage }}%
                </td>
          </tr>
          <tr>
            <td class="font-title-container">Bottle</td>
            <!-- <td v-for="(item, index) in resultMonthlyTest" :key="'bottle-'+index" :style="getBgColor(item.bottle_percentage)">{{ item.bottle_percentage }}%</td> -->
            <td
                  v-for="(item, index) in resultMonthlyTest"
                  :key="'ecoli-'+index"
                  :class="{
                    'bg-green': parseFloat(item.bottle_percentage) === 100,
                    'bg-yellow': parseFloat(item.bottle_percentage) >= 80.01 && parseFloat(item.bottle_percentage) <= 99.95,
                    'bg-darkred': parseFloat(item.bottle_percentage) >= 1 && parseFloat(item.bottle_percentage) <= 80
                  }"
                >
                  {{ item.bottle_percentage }}%
                </td>
          </tr>

          <tr>
            <td rowspan="2" colspan="2" class="bold-cell">%WHO compliance Coliforms & E. Coli - 0 CFU/100mL</td>
            <td class="font-title-container">Treatment system</td>
            <!-- <td v-for="(item, index) in resultMonthlyTest" :key="'ecolibottle-'+index">{{ item.machine_esch_ecoli }}%</td> -->
            <td
                  v-for="(item, index) in resultMonthlyTest"
                  :key="'ecoli-'+index"
                  :class="{
                    'bg-green': parseFloat(item.machine_esch_ecoli) === 100,
                    'bg-yellow': parseFloat(item.machine_esch_ecoli) >= 80.01 && parseFloat(item.machine_esch_ecoli) <= 99.95,
                    'bg-darkred': parseFloat(item.machine_esch_ecoli) >= 1 && parseFloat(item.machine_esch_ecoli) <= 80
                  }"
                >
                  {{ item.machine_esch_ecoli }}%
                </td>
          </tr>
          <tr>
            <td class="font-title-container">Bottle</td>
            <!-- <td v-for="(item, index) in resultMonthlyTest" :key="'bottleecoli-'+index">{{ item.bottle_esch_ecoli }}%</td> -->
            <td
                  v-for="(item, index) in resultMonthlyTest"
                  :key="'ecoli-'+index"
                  :class="{
                    'bg-green': parseFloat(item.bottle_esch_ecoli) === 100,
                    'bg-yellow': parseFloat(item.bottle_esch_ecoli) >= 80.01 && parseFloat(item.bottle_esch_ecoli) <= 99.95,
                    'bg-darkred': parseFloat(item.bottle_esch_ecoli) >= 1 && parseFloat(item.bottle_esch_ecoli) <= 80
                  }"
                >
                  {{ item.bottle_esch_ecoli }}%
                </td>
          </tr>

          <tr>
            <td colspan="2" class="bold-cell">#Level 1 Alert</td>
            <td class="font-title-container">Treatment system</td>
            <td class="font-title-container" v-for="(item, index) in resultMonthlyTest" :key="'ecolibottle1-'+index">{{ item.ma_1 }}</td>
          </tr>
          <tr>
            <td colspan="2" class="bold-cell">#Level 2 Alert</td>
            <td class="font-title-container">Treatment system</td>
            <td class="font-title-container" v-for="(item, index) in resultMonthlyTest" :key="'ecolibottle2-'+index">{{ item.ma_2 }}</td>
          </tr>
          <tr>
            <td colspan="2" class="bold-cell">#Level 3 Alert</td>
            <td class="font-title-container">Treatment system</td>
            <td class="font-title-container" v-for="(item, index) in resultMonthlyTest" :key="'ecolibottle3-'+index">{{ item.ma_3 }}</td>
          </tr>

          <tr>
            <td colspan="3" class="bold-cell">Site tested under 24h</td>
            <!-- <td v-for="(item, index) in resultMonthlyTest" :key="'delay-'+index">{{ item.delay }} %</td> -->
            <td v-for="(item, index) in resultMonthlyTest" :key="'ecoli-'+index" 
                  :class="{
                    'bg-green': parseFloat(item.delay) === 100,
                    'bg-yellow': parseFloat(item.delay) >= 80.01 && parseFloat(item.delay) <= 99.95,
                    'bg-darkred': parseFloat(item.delay) >= 1 && parseFloat(item.delay) <= 80
                          }">
                  {{ item.delay }}%
                </td>
          </tr>

          <tr class="section-title-row"><td colspan="8">Sampling after technician interventions</td></tr>

          <tr>
            <td colspan="3" class="bold-cell">#Sites re-tested after technician interventions</td>
            <td class="font-title-container" v-for="(item, index) in resultAfterIntervention" :key="'retest-'+index">{{ item.sites }}</td>
          </tr>

          <tr>
            <td rowspan="2" colspan="2" class="bold-cell">%WHO compliance E. Coli - 0 CFU/100mL</td>
            <td class="font-title-container">Treatment system</td>
            <!-- <td v-for="(item, index) in resultAfterIntervention" :key="'ecoli-'+index">{{ item.machine_percentage }}%</td> -->
            <td v-for="(item, index) in resultAfterIntervention" :key="'ecoli-'+index" 
                  :class="{
                    'bg-green': parseFloat(item.machine_percentage) === 100,
                    'bg-yellow': parseFloat(item.machine_percentage) >= 80.01 && parseFloat(item.machine_percentage) <= 99.95,
                    'bg-darkred': parseFloat(item.machine_percentage) >= 1 && parseFloat(item.machine_percentage) <= 80
                          }">
                  {{ item.machine_percentage }}%
                </td>
          </tr>
          <tr>
            <td class="font-title-container">Bottle</td>
            <!-- <td v-for="(item, index) in resultAfterIntervention" :key="'bottle-'+index">{{ item.bottle_percentage }}%</td> -->
            <td v-for="(item, index) in resultAfterIntervention" :key="'bottle-'+index" 
                  :class="{
                    'bg-green': parseFloat(item.bottle_percentage) === 100,
                    'bg-yellow': parseFloat(item.bottle_percentage) >= 80.01 && parseFloat(item.bottle_percentage) <= 99.95,
                    'bg-darkred': parseFloat(item.bottle_percentage) >= 1 && parseFloat(item.bottle_percentage) <= 80
                          }">
                  {{ item.bottle_percentage }}%
            </td>
          </tr>

          <tr>
            <td rowspan="2" colspan="2" class="bold-cell">%WHO compliance Coliforms & E. Coli - 0 CFU/100mL</td>
            <td class="font-title-container">Treatment system</td>
            <!-- <td v-for="(item, index) in resultAfterIntervention" :key="'ecolibottle-'+index">{{ item.machine_esch_ecoli }}%</td> -->
            <td v-for="(item, index) in resultAfterIntervention" :key="'ecolibottle-'+index" 
                  :class="{
                    'bg-green': parseFloat(item.machine_esch_ecoli) === 100,
                    'bg-yellow': parseFloat(item.machine_esch_ecoli) >= 80.01 && parseFloat(item.machine_esch_ecoli) <= 99.95,
                    'bg-darkred': parseFloat(item.machine_esch_ecoli) >= 1 && parseFloat(item.machine_esch_ecoli) <= 80
                          }">
                  {{ item.machine_esch_ecoli }}%
            </td>
          </tr>
          <tr>
            <td class="font-title-container">Bottle</td>
            <!-- <td v-for="(item, index) in resultAfterIntervention" :key="'bottleecoli-'+index">{{ item.bottle_esch_ecoli }}%</td> -->
            <td v-for="(item, index) in resultAfterIntervention" :key="'bottleecoli-'+index"
                  :class="{
                    'bg-green': parseFloat(item.bottle_esch_ecoli) === 100,
                    'bg-yellow': parseFloat(item.bottle_esch_ecoli) >= 80.01 && parseFloat(item.bottle_esch_ecoli) <= 99.95,
                    'bg-darkred': parseFloat(item.bottle_esch_ecoli) >= 1 && parseFloat(item.bottle_esch_ecoli) <= 80
                          }">
                  {{ item.bottle_esch_ecoli }}%
            </td>
          </tr>

          <tr class="section-title-row"><td colspan="8">Global view after technician interventions</td></tr>

          <tr>
            <td colspan="2" class="bold-cell">%WHO compliance E. Coli - 0 CFU/100mL</td>
            <td class="font-title-container">Treatment system</td>
            <!-- <td v-for="(item, index) in resultGlobalView" :key="'ecoli-'+index">{{ item.machine_percentage }}%</td> -->
            <td v-for="(item, index) in resultGlobalView" :key="'ecoli-'+index"
                  :class="{
                    'bg-green': parseFloat(item.machine_percentage) === 100,
                    'bg-yellow': parseFloat(item.machine_percentage) >= 80.01 && parseFloat(item.machine_percentage) <= 99.95,
                    'bg-darkred': parseFloat(item.machine_percentage) >= 1 && parseFloat(item.machine_percentage) <= 80
                          }">
                  {{ item.machine_percentage }}%
            </td>
          </tr>
          <tr>
            <td colspan="2" class="bold-cell">Calculated on ALL sites</td>
            <td class="font-title-container">Bottle</td>
            <!-- <td v-for="(item, index) in resultGlobalView" :key="'bottle-'+index">{{ item.bottle_percentage }}%</td> -->
            <td v-for="(item, index) in resultGlobalView" :key="'bottle-'+index"
                  :class="{
                    'bg-green': parseFloat(item.bottle_percentage) === 100,
                    'bg-yellow': parseFloat(item.bottle_percentage) >= 80.01 && parseFloat(item.bottle_percentage) <= 99.95,
                    'bg-darkred': parseFloat(item.bottle_percentage) >= 1 && parseFloat(item.bottle_percentage) <= 80
                          }">
                  {{ item.bottle_percentage }}%
            </td>
          </tr>

          <tr>
            <td colspan="2" class="bold-cell">%WHO compliance Coliforms & E. Coli - 0 CFU/100mL</td>
            <td class="font-title-container">Treatment system</td>
            <!-- <td v-for="(item, index) in resultGlobalView" :key="'ecolibottle-'+index">{{ item.machine_esch_ecoli }}%</td> -->
            <td v-for="(item, index) in resultGlobalView" :key="'ecolibottle-'+index"
                  :class="{
                    'bg-green': parseFloat(item.machine_esch_ecoli) === 100,
                    'bg-yellow': parseFloat(item.machine_esch_ecoli) >= 80.01 && parseFloat(item.machine_esch_ecoli) <= 99.95,
                    'bg-darkred': parseFloat(item.machine_esch_ecoli) >= 1 && parseFloat(item.machine_esch_ecoli) <= 80
                          }">
                  {{ item.machine_esch_ecoli }}%
            </td>
          </tr>
          <tr>
            <td colspan="2" class="bold-cell">Calculated on ALL sites</td>
            <td class="font-title-container">Bottle</td>
            <td v-for="(item, index) in resultGlobalView" :key="'bottleecoli-'+index"
                  :class="{
                    'bg-green': parseFloat(item.bottle_esch_ecoli) === 100,
                    'bg-yellow': parseFloat(item.bottle_esch_ecoli) >= 80.01 && parseFloat(item.bottle_esch_ecoli) <= 99.95,
                    'bg-darkred': parseFloat(item.bottle_esch_ecoli) >= 1 && parseFloat(item.bottle_esch_ecoli) <= 80
                          }">
                  {{ item.bottle_esch_ecoli }}%
            </td>
          </tr>
        </tbody>
      </table>
    </v-col>
  </v-row>

    <!-- Legend -->
    <!-- <div class="legend">
      <div><span class="circle" style="background-color: darkblue;"></span> Level 0 – No contamination</div>
      <div><span class="circle" style="background-color: yellow;"></span> Level 1 – Low</div>
      <div><span class="circle" style="background-color: orange;"></span> Level 2 – Medium</div>
      <div><span class="circle" style="background-color: red;"></span> Level 3 – High</div>
    </div> -->
  </v-container>
</template>

<script setup>
import { ref, computed, onMounted, watch } from "vue";
import axios from "axios";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import Swal from "sweetalert2";

// ---- Reactive variables ----
const selectedDate = ref(new Date().toISOString().slice(0, 7));
const platform = ref("All");
const contamination = ref("contamination_level_machine");
const level = ref("All");
const dataYTD = ref([]);
const allSamples = ref([]);
const map = ref(null);
const markers = ref([]);
const highSites = ref([]);
const resultMonthlyTest = ref([]); // For the new table
const resultAfterIntervention = ref([]);
const resultGlobalView = ref([]);
const platforms = ["BTB", "SR", "KSP", "PP", "KC"];

// ---- Helper functions ----
const colorByLevel = (lvl) => {
  switch (parseInt(lvl)) {
    case 0:
      return "darkblue";
    case 1:
      return "yellow";
    case 2:
      return "orange";
    case 3:
      return "red";
    default:
      return "gray";
  }
};
const colorByLevel1 = (lvl) => {
  switch (parseInt(lvl)) {
    case 0:
      return "black";
    case 1:
      return "black";
    case 2:
      return "black";
    case 3:
      return "black";
    default:
      return "black";
  }
};

const getBgColor = (value) => {
    if (value === 100) {
      return {
        backgroundColor: '#4CAF50',  // green
        color: 'white',
        fontWeight: 'bold'
      };
    } else if (value >= 81 && value <= 98) {
      return {
        backgroundColor: '#FFEB3B',  // yellow
        color: '#333',
        fontWeight: 'bold'
      };
    } else if (value >= 1 && value <= 80) {
      return {
        backgroundColor: '#B71C1C',  // dark red
        color: 'white',
        fontWeight: 'bold'
      };
    }
    // default no background
    return {};
  };

const createLabeledMarker = (idSite, siteName, color) => {
  const labelText = `${idSite ?? ""} - ${siteName ?? ""}`;
  return L.divIcon({
    className: "custom-marker",
    html: `<div style="display:flex;flex-direction:column;align-items:center;">
      <span style="background-color:${color}; width:14px; height:14px; border-radius:50%; border:2px solid white; box-shadow:0 0 3px rgba(0,0,0,0.4);"></span>
      <small style="background:white;color:black;padding:2px 4px;border-radius:4px;margin-top:2px;font-size:9px;font-weight:bold;white-space:nowrap;">
        ${labelText}
      </small>
    </div>`,
    iconSize: [40, 40],
    iconAnchor: [20, 20],
  });
};

// ---- Map init ----
const initMap = () => {
  map.value = L.map("map", {
    minZoom: 7,
    maxZoom: 14,
    zoomControl: true,
    maxBounds: [
      [9.5, 102.3],
      [15.0, 107.6],
    ],
  }).setView([12.5657, 104.991], 7);

  // ✅ English-only map (Carto Light)
  L.tileLayer("https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png", {
    attribution: "© OpenStreetMap contributors",
    subdomains: "abcd",
    maxZoom: 19,
  }).addTo(map.value);
};

// ---- Fetch data ----
const fetchMapData = async () => {
  if (!selectedDate.value) return;

  Swal.fire({
    title: "Loading map data...",
    allowOutsideClick: false,
    didOpen: () => Swal.showLoading(),
  });

  try {
    const response = await axios.get("/api/WQReport", {
      params: { month: selectedDate.value + "-01" },
    });
    allSamples.value = Array.isArray(response.data.dataThisMonth) ? response.data.dataThisMonth : [];
    // dataYTD is an object like { BTB: { machine: [..], bottle: [..] }, ... }
    dataYTD.value = (typeof response.data.dataYTD === "object" && response.data.dataYTD !== null)
      ? response.data.dataYTD
      : {};
    highSites.value = (response.data.highContaminationSites || []).map(
      (site) => ({
        Id_Site: site.Id_Site,
        platform: site.platform,
        machineLevel2: site.machine.level2 ?? 0,
        machineLevel3: site.machine.level3 ?? 0,
        bottleLevel2: site.bottle.level2 ?? 0,
        bottleLevel3: site.bottle.level3 ?? 0,
      })
    );
    resultMonthlyTest.value = Array.isArray(response.data.resultMonthlyTest) ? response.data.resultMonthlyTest : [];
    resultAfterIntervention.value = Array.isArray(response.data.resultAfterIntervention) ? response.data.resultAfterIntervention : [];
    resultGlobalView.value = Array.isArray(response.data.resultGlobalView) ? response.data.resultGlobalView : [];
    console.log("Fetched map data:", resultGlobalView.value);
    // Fetch YTD data too
   // await fetchYTDData();

    renderMarkers(filteredSamples.value);
  } catch (err) {
    console.error(err);
    Swal.fire("Error", "Failed to fetch map data", "error");
  } finally {
    Swal.close();
  }
};

// Transform API data into grouped format for table

const groupedHighSitesYTD = computed(() => {
  const map = {};

  (highSites.value || []).forEach((site) => {
    const plat = site.platform || "Unknown";

    if (!map[plat]) {
      map[plat] = {
        machineLevel2: new Set(),
        machineLevel3: new Set(),
        bottleLevel2: new Set(),
        bottleLevel3: new Set(),
      };
    }

    if (site.machineLevel2 >= 3) map[plat].machineLevel2.add(site.Id_Site);
    if (site.machineLevel3 >= 3) map[plat].machineLevel3.add(site.Id_Site);
    if (site.bottleLevel2 >= 3) map[plat].bottleLevel2.add(site.Id_Site);
    if (site.bottleLevel3 >= 3) map[plat].bottleLevel3.add(site.Id_Site);
  });

  return map;
});





//YTD Data Fetch
const fetchYTDData = async () => {
  if (!selectedDate.value) return;

  try {
    const response = await axios.get("/api/map-ytd", {
      params: { month: selectedDate.value + "-01" }, // server returns from Jan 1 to selected month
    });
    allSamplesYTD.value = Array.isArray(response.data) ? response.data : [];
  } catch (err) {
    console.error("Failed to fetch YTD data:", err);
  }
};

// ---- Count functions for YTD ----
const getYTD = (plat, type, lvl) => {
  // type is 'machine' or 'bottle'
  return dataYTD.value?.[plat]?.[type]?.[lvl] ?? 0;
};

// totals for YTD per type
const totalYTD = (type) => {
  return platforms.reduce((sum, plat) => sum + (dataYTD.value?.[plat]?.[type]?.reduce((acc, v) => acc + (parseInt(v) || 0), 0) ?? 0), 0);
};


const countByPlatformAndLevelYTD = (plat,lvl)=>{
  if(!allSamplesYTD.value[plat]) return 0;
  const type = contamination.value==="contamination_level_machine"? "machine":"bottle";
  return allSamplesYTD.value[plat][type][lvl]??0;
};
const totalCountByLevelYTD = (lvl)=> platforms.reduce((sum,plat)=>sum+countByPlatformAndLevelYTD(plat,lvl),0);

// Zoom


// ---- Filtered samples for map ----
const filteredSamples = computed(() => {
  let data = [...allSamples.value];
  if (platform.value !== "All")
    data = data.filter((s) => s.platform === platform.value);
  if (level.value !== "All") {
    data = data.filter((s) => {
      const val =
        contamination.value === "contamination_level_machine"
          ? s.machine_contamination_level
          : s.bottle_contamination;
      return parseInt(val) === parseInt(level.value);
    });
  }
  return data;
});

// ---- Render markers ----
const renderMarkers = (samples) => {
  markers.value.forEach((m) => map.value.removeLayer(m));
  markers.value = [];

  const latLngs = [];
  samples.forEach((s) => {
    if (s.latitude && s.longitude) {
      const val =
        contamination.value === "contamination_level_machine"
          ? s.machine_contamination_level
          : s.bottle_contamination;
      const color = colorByLevel(val);
      const marker = L.marker([s.latitude, s.longitude], {
        icon: createLabeledMarker(s.Id_Site, s.SiteName_En, color),
      }).addTo(map.value)
      .bindPopup(`
          <b>Site:</b> ${s.Id_Site}<br>
          <b>Machine Level:</b> ${s.machine_contamination_level}<br>
          <b>Bottle Level:</b> ${s.bottle_contamination}<br>
          <b>Platform:</b> ${s.platform ?? "-"}
        `)
        .addTo(map.value);

      markers.value.push(marker);
      latLngs.push([s.latitude, s.longitude]);
    }
  });

  if (latLngs.length > 0)
    map.value.fitBounds(L.latLngBounds(latLngs), { padding: [50, 50] });
  else map.value.setView([12.5657, 104.991], 7);
};

// ---- Count Id_Site by platform and level ----
const countByPlatformAndLevel = (plat, lvl) => {
  return allSamples.value.filter((s) => {
    if (platform.value !== "All" && s.platform !== platform.value) return false;
    if (plat !== "All" && s.platform !== plat) return false;
    const val =
      contamination.value === "contamination_level_machine"
        ? s.machine_contamination_level
        : s.bottle_contamination;
    return parseInt(val) === lvl;
  }).length;
};

// ---- Total across all platforms ----
const totalCountByLevel = (lvl) => {
  return platforms.reduce(
    (sum, plat) => sum + countByPlatformAndLevel(plat, lvl),
    0
  );
};

// ---- Zoom to selected level/platform ----
const zoomToLevelPlatform = (plat, lvl) => {
  const selected = filteredSamples.value.filter((s) => {
    if (plat !== "All" && s.platform !== plat) return false;
    const val =
      contamination.value === "contamination_level_machine"
        ? s.machine_contamination_level
        : s.bottle_contamination;
    return parseInt(val) === lvl;
  });

  const latLngs = selected
    .filter((s) => s.latitude && s.longitude)
    .map((s) => [s.latitude, s.longitude]);

  if (latLngs.length > 0)
    map.value.fitBounds(L.latLngBounds(latLngs), { padding: [50, 50] });
};

// ---- Watch filters ----
watch([platform, contamination, level], () => {
  renderMarkers(filteredSamples.value);
});

// ---- Mount ----
onMounted(() => {
  initMap();
  fetchMapData();
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
  font-size: 13px; /* smaller font */
  color: #333;
  max-width: 100%; /* keep responsive */
  margin: 0 auto; /* center horizontally */
}

.styled-table th,
.styled-table td {
  border: 1px solid #ddd;
  padding: 5px 6px; /* less padding */
  line-height: 1.2; /* tighter line height */
}

.main-title-row th {
  font-size: 16px; /* smaller main title */
  padding: 8px 10px;
}

.header-row th {
  background-color: #a5d6a7;
  color: #1b5e20;
  font-weight: bold;
  font-size: 14px; /* slightly smaller header */
  text-align: center;

}

.section-title-row td {
  font-size: 16px; /* slightly smaller section titles */
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
  font-size: 16px;
  font-weight: bold;
  text-align: center;
  margin-bottom: 12px;
  color: darkred;
}
</style>
