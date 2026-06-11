<template>
    <v-container fluid class="pa-6 report-container" :class="{ 'khmer-mode': currentLanguage === 'km' }">
        <!-- Site Select -->
        <div class="d-flex justify-space-between align-center mb-2 no-print">
            <v-text-field v-model="selectedDate" class="flex-grow-0 mr-5" label="Month" type="month" />
            <v-autocomplete v-model="selectedSite" :items="sites" label="Select Site" item-title="Id_Site"
                item-value="Id_Site" density="compact" outlined
                style="max-width: 180px; font-size: 0.9rem;"></v-autocomplete>

            <v-select v-model="selectedLanguage" :items="languages" item-title="text" item-value="value"
                density="compact" style="max-width: 150px; margin-bottom: 10px;" label="Language"></v-select>
            <v-btn color="primary" @click="printReport" small>
                <v-icon left small>mdi-printer</v-icon>
                Print
            </v-btn>
        </div>

        <!-- SECTION 2: Site Info -->
        <v-row justify="center" dense>
            <v-col cols="12" md="10" lg="10"> <!-- put md='12' if want table full screen -->
                <v-card class="pa-2 mb-2" style="border-radius: 12px; box-shadow: 0 3px 6px rgba(0,0,0,0.1);">
                    <h3 class="mb-3 text-center " style="font-size: 1.2rem; color: blue;">{{ currentText.siteAnalysis }}
                    </h3>

                    <v-table density="compact"
                        style="width: 100%; border-radius: 8px; overflow: hidden; text-align: left; ">
                        <tbody>
                            <tr style="background-color: #f5f5f5;text-align: left;">
                                <td> <span class="font-title-container"> {{ currentText.site }} : </span> {{report.siteDetails.Id_Site }}</td>
                                <td> <span class="font-title-container"> {{ currentText.platform }} : </span> {{report.siteDetails.Platform }}</td>
                                <td><span class="font-title-container">{{ currentText.month }} : </span>
                                    <strong>{{ selectedDate }}</strong>
                                </td>
                                <td><span class="font-title-container">{{ currentText.entrepreneurName }} : </span>
                                    <strong>{{ report.siteDetails.Entrepreneur_English_Name }}</strong>
                                </td>
                                <td><span class="font-title-container">{{ currentText.workingDate }} : </span>
                                    <strong>{{ report.siteDetails.Date_start_working }}</strong>
                                </td>
                                <td><span class="font-title-container">{{ currentText.technician }} : </span>
                                    <strong>{{ report.assessment.technician }}</strong>
                                </td>

                            </tr>

                            <tr style="background-color: #e3f2fd;">
                                <td colspan="2" class="rowTable">Monthly Info</td>
                                <td colspan="2" class="rowTable">YTD Info</td>
                                <td colspan="2" class="rowTable">Raw Water Qual</td>
                                <td colspan="2" class="rowTable">Drinking Water Qual</td>
                            </tr>

                            <tr style="background-color: #fce4ec;">
                                <td colspan="2" class="rowTable">Bot /Day : {{ report.sales.monthly_avg_non_wis_sales_per_day?.toFixed(0) || 0}}</td>
                                <td colspan="2" class="rowTable">Bot/day : {{ report.salesYtd.avg_sales_per_day?.toFixed(0) || 0}}</td>
                                <td colspan="2" class="rowTable">pH : {{ report.routine.pH_raw_water }}</td>
                                <td colspan="2" class="rowTable">pH : {{ report.routine.pH_drinking_water }}</td>

                            </tr>

                            <tr style="background-color: #fce4ec;">
                                <td colspan="2" class="rowTable">Ecoli Alert : {{ report.sampleRecord.ecoli_alert }} </td>
                                <td colspan="2" class="rowTable">Ecoli Alert : {{ report.sampleYtdRecord.ecoli_alert_ytd }}</td>
                                <td colspan="2" class="rowTable">Turbidity : {{ report.routine.Turbidity_raw_water }}
                                </td>
                                <td colspan="2" class="rowTable">Turbidity : {{ report.routine.Turbidity_drinking_water }}</td>

                            </tr>

                            <tr style="background-color: #fce4ec;">
                                <td colspan="2" class="rowTable">Coliform Alert : {{ report.sampleRecord.coliform_alert }}</td>
                                <td colspan="2" class="rowTable">Coliform Alert : {{ report.sampleYtdRecord.coliform_alert_ytd }}</td>
                                <td colspan="2" class="rowTable">Conductivity : {{ report.routine.conductivity_raw_water }}</td>
                                <td colspan="2" class="rowTable">Conductivity : {{ report.routine.conductivity_drinking_water }}</td>

                            </tr>

                            <tr style="background-color: #fce4ec;">
                                <td colspan="2" class="rowTable">Unplanned Int : </td>
                                <td colspan="2" class="rowTable">Unplanned Int : </td>
                                <td colspan="2" class="rowTable">TDS : {{ report.routine.TDS_raw_water }}</td>
                                <td colspan="2" class="rowTable">TDS : {{ report.routine.TDS_drinking_water }}</td>
                            </tr>
                        </tbody>
                    </v-table>
                </v-card>
            </v-col>
        </v-row>

        <!-- Summary Assessment & Routine -->
        <v-row justify="center" dense class="print-row">
            <v-col cols="12" md="10">
                <v-row dense>
                    <v-col cols="12" md="6" class="print-half">
                        <v-card class="pa-2 mb-2" style="border-radius: 12px; box-shadow: 0 3px 6px rgba(0,0,0,0.1);">
                            <h3 class="mb-3 text-center" style="font-size: 1.2rem; color: blue;">
                                Total assessment by technician:
                                <span style="position: relative; display: inline-flex; align-items: center;">
                                    <span @click="showAssessmentPopup(report.siteDetails.Id_Site,'assessment')"
                                        style="cursor: pointer; text-decoration: underline; color: #1976d2;">{{ report.assessmentCountYTD }}</span>
                                    <v-badge color="red" content="click" location="end"
                                        style="margin-left: 15px;"></v-badge>
                                </span>
                            </h3>
                        </v-card>
                    </v-col>
                    <v-col cols="12" md="6" class="print-half">
                        <v-card class="pa-2 mb-2" style="border-radius: 12px; box-shadow: 0 3px 6px rgba(0,0,0,0.1);">
                            <h3 class="mb-3 text-center" style="font-size: 1.2rem; color: blue;">
                                Total routine check by technician :
                                <span style="position: relative; display: inline-flex; align-items: center;">
                                    <span @click="showAssessmentPopup(report.siteDetails.Id_Site,'routine')"
                                        style="cursor: pointer; text-decoration: underline; color: #1976d2;">5</span>
                                    <v-badge color="red" content="click" location="end"
                                        style="margin-left: 15px;"></v-badge>
                                </span>
                            </h3>
                        </v-card>
                    </v-col>
                </v-row>
            </v-col>
        </v-row>

        <!--Show Site Assessment-->
        <!-- Water Treatment -->
        <v-row justify="center" dense class="print-row">
            <v-col cols="12" md="10">
                <v-row dense>
                    <v-col cols="12" md="12">
                        <v-card class="pa-2 mb-2" style="border-radius: 12px; box-shadow: 0 3px 6px rgba(0,0,0,0.1);">
                            <h3 class="mb-3 text-center" style="font-size: 1.2rem; color: blue;">Site Assessment
                            </h3>
                            <v-table density="compact"
                                style="width: 100%; border-radius: 8px; overflow: hidden; border-collapse: separate; border-spacing: 0 15px;">
                                <tbody>
                                    <tr style="background-color: white;">
                                        <td class="rowTable">Last assess : {{ report.assessment.date_form }}</td>
                                        <td class="rowTable">Electricity : {{report.assessment.main_source_of_electricity }}</td>
                                        <td class="rowTable">Water Source : {{ report.assessment.main_source_of_water }}
                                        </td>
                                        <td class="rowTable">2nd Water Source : {{report.assessment.second_source_of_water }}</td>
                                        <td class="rowTable">UV Controller : {{ report.assessment.uv_controller }}</td>
                                    </tr>
                                    <tr style="height: 0.5rem; font-size: 0;">
                                        <td colspan="6"
                                            style="border: none; padding: 0; background-color: transparent; height: 0.5rem;">
                                        </td>
                                    </tr>

                                    <tr style="background-color: white;">
                                        <td class="rowTable">UV Lamp : {{ report.assessment.uv_lamp_condition }}</td>
                                        <td class="rowTable">UV Ballast : {{ report.assessment.uv_ballast }}</td>
                                        <td class="rowTable">UV Lamp : {{ report.assessment.uv_lamp }}</td>
                                        <td class="rowTable">RO : {{ report.assessment.reverse_osmose }}</td>
                                        <td class="rowTable">Flocculation : {{ report.assessment.flocculation_and_coagulation_process }}</td>
                                        <td class="rowTable">UF : {{ report.assessment.ultrafiltration }}</td>
                                    </tr>
                                    <tr style="height: 0.5rem; font-size: 0;">
                                        <td colspan="6"
                                            style="border: none; padding: 0; background-color: transparent; height: 0.5rem;">
                                        </td>
                                    </tr>
                                    <tr style="background-color: white;">
                                        <td class="rowTable">Raw Water Pump : {{ report.assessment.raw_water_pump }}
                                        </td>
                                        <td class="rowTable">Back Wash Pump : {{ report.assessment.back_wash_pump }}
                                        </td>
                                        <td class="rowTable">Micro Filter Pump : {{ report.assessment.micro_filter_pump}}</td>
                                        <td colspan="3" class="rowTable"></td> <!-- Empty cells to fill the row -->
                                    </tr>
                                </tbody>
                            </v-table>
                        </v-card>
                    </v-col>

                </v-row>
            </v-col>
        </v-row>

        <!-- Water Treatment -->
        <v-row justify="center" dense class="print-row">
            <v-col cols="12" md="10">
                <v-row dense>
                    <v-col cols="12" md="8" class="print-half">
                        <v-card class="pa-2 mb-2" style="border-radius: 12px; box-shadow: 0 3px 6px rgba(0,0,0,0.1);">
                            <h3 class="mb-3 text-center" style="font-size: 1.2rem; color: blue;">Water Treatment Process
                            </h3>

                            <v-table density="compact" style="width: 100%; border-radius: 8px; overflow: hidden;">
                                <thead>
                                    <tr style="background-color: #f5f5f5;">
                                        <th>Step</th>
                                        <th style="text-align: center;">Process</th>
                                        <th style="text-align: center;">Type</th>
                                        <th>Volume (L)</th>
                                        <th>Height (cm)</th>
                                        <th>Diameter (cm)</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr v-for="item in report.assessmentProcess" :key="item.step"
                                        style="background-color: #fce4ec;">
                                        <td>{{ item.step }}</td>
                                        <td>{{ item.process }}</td>
                                        <td>{{ item.fields?.Type || '-' }}</td>
                                        <td>{{ (item.fields?.Volume && parseInt(item.fields.Volume)) || '-' }}</td>
                                        <td>{{ (item.fields?.Height && parseInt(item.fields.Height)) || '-' }}</td>
                                        <td>{{ (item.fields?.Diameter && parseInt(item.fields.Diameter)) || '-' }}</td>
                                    </tr>
                                </tbody>
                            </v-table>
                        </v-card>
                    </v-col>
                    <!-- Routine Check -->
                    <v-col cols="12" md="4" class="print-half">
                        <v-card class="pa-3 mb-3"
                            style="width: 100%; border-radius: 12px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
                            <h3 class="mb-2" style="font-size: 1rem; text-align: center; color: #2e7d32;">
                                Routine Check
                            </h3>
                            <v-table density="compact" style="width: 100%; border-radius: 8px; overflow: hidden;">
                                <tbody>
                                    <tr>
                                        <td class="rowTable">Last Check</td>
                                        <td style="border: 1px solid #ccc; padding: 8px; text-align: center;">{{report.routine.date }}
                                        </td>
                                    </tr>
                                    <tr>
                                        <td class="rowTable">Flow Measured</td>
                                        <td style="border: 1px solid #ccc; padding: 8px; text-align: center;">need data
                                            display</td>
                                    </tr>
                                    <tr>
                                        <td class="rowTable">Sand Filter</td>
                                        <td style="border: 1px solid #ccc; padding: 8px; text-align: center;">{{report.routine.condition_of_sand_filter_tank }}</td>
                                    </tr>
                                    <tr>
                                        <td class="rowTable">Ac Filter</td>
                                        <td style="border: 1px solid #ccc; padding: 8px; text-align: center;">{{report.routine.condition_of_ac_filter_tank }}</td>
                                    </tr>
                                    <tr>
                                        <td class="rowTable">CIP</td>
                                        <td style="border: 1px solid #ccc; padding: 8px; text-align: center;">{{report.routine.frequency_of_the_cip_on_pipes }}</td>
                                    </tr>
                                </tbody>
                            </v-table>
                        </v-card>
                    </v-col>
                </v-row>
            </v-col>
        </v-row>

        <v-row justify="center" dense class="print-row">
            <v-col cols="12" md="10">
                <v-row dense>
                    <v-col cols="12" md="6" class="print-half">
                        <v-card class="pa-3 mb-3"
                            style="width: 100%; border-radius: 12px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
                            <h3 class="mb-2" style="font-size: 1rem; text-align: center; color: #2e7d32;">
                                Aluminium and Turbidity
                            </h3>
                            <div style="display: flex; justify-content: center; align-items: center; height: 230px; width: 100%;">
                                <canvas ref="tubiLineChart" width="300" height="200"
                                    style="max-width: 100%; max-height: 100%;"></canvas>
                            </div>
                        </v-card>
                    </v-col>

                    <v-col cols="12" md="6" class="print-half">
                       <v-card class="pa-3 mb-3"
                            style="width: 100%; border-radius: 12px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
                            <h3 class="mb-2" style="font-size: 1rem; text-align: center; color: #2e7d32;">
                                Contamination Level
                            </h3>
                            <div style="display: flex; justify-content: center; align-items: center; height: 230px; width: 100%;">
                                <canvas ref="contaminationChart" width="300" height="200"
                                    style="max-width: 100%; max-height: 100%;"></canvas>
                            </div>
                        </v-card>
                    </v-col>    
                </v-row>
            </v-col>
        </v-row>

    <div class="text-center">
            <v-dialog v-model="popUpAssessmentDetail" persistent max-width="1400px" content-class="custom-dialog">
                <v-card>
                    <!-- Use the component with v-if to ensure proper mounting -->
                    <AssessmentDetail 
                        v-if="popUpAssessmentDetail"
                        :getDataToForm="Id_Site" :type ="type"
                        @cancel-modal="popUpAssessmentDetail = false" 
                        @site-saved="popUpAssessmentDetail = false"
                    />
                </v-card>
            </v-dialog>
        </div>  
    <!-- <div class="text-center">
        <v-card class="pa-3 mb-3"
                            style="width: 100%; border-radius: 12px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
                            <h3 class="mb-2" style="font-size: 1rem; text-align: center; color: #2e7d32;">
                                Aluminium and Turbidity
                            </h3>
                            
                            <div
                                style="display: flex; justify-content: center; align-items: center; height: 300px; width: 100%;">
                                <canvas ref="tubiLineChart" width="400" height="300"
                                    style="max-width: 50%; max-height: 100%;"></canvas>
                            </div>
                        </v-card>
    </div>      -->
    </v-container>
</template>

<script>
import { Chart, registerables } from "chart.js";
import axios from "axios";
import Swal from "sweetalert2";
import AssessmentDetail from './assessmentDetail.vue';
Chart.register(...registerables);

export default {
    components: {
        AssessmentDetail
    },
    data() {
        return {
            Id_Site:'',
            type: '',
            sites: [],
            popUpAssessmentDetail: false,
            selectedSite: null,
            currentLanguage: 'en',
            report: {
                siteDetails: {},
                sales: {},
                salesYtd: {},
                assessment: {},
                assessmentProcess: [],
                routine: {},
                sampleRecord: {},
                sampleYtdRecord: {},
                assessmentCountYTD: 0,
                assessmentYTD: [],
                tubiData: {},
                contamination: {},
            },
            languages: [
                { text: 'English', value: 'en' },
                { text: 'French', value: 'fr' },
                { text: 'Khmer', value: 'km' },
            ],
            selectedLanguage: 'en',
            translations: {
                en: {
                    site: 'Site',
                    month: 'Month',
                    platform: 'Platform',
                    entrepreneurName: 'Ent.Name',
                    workingDate: 'Working Date',
                    siteAnalysis: 'Technical Analysis',
                    bottleDayExcWinS: 'Bottle/day exc WinS',
                    bottleDayExcWinSYTD: 'Bottle/day exc WinS YTD',
                    totalSalesBottle: 'Total Sales(Bottle)',
                    overWaste: 'Over Waste',
                    penetration: 'Penetration',
                    tier: 'Tier',
                    nbOfOperator: 'Nb of operator',
                    popCommune: 'Pop Commune',
                    bottleDay: 'Bottle/day',
                    dayOpen: 'Day Open',
                    beneficiaries: 'Beneficiaries',
                    houseHold: 'HouseHold',
                    technician: 'Technician',
                },
                fr: {
                    site: 'Site',
                    month: 'Mois',
                    platform: 'Plateforme',
                    entrepreneurName: 'Nom Ent.',
                    workingDate: 'Date de travail',
                    siteAnalysis: 'Analyse technique',
                    bottleDayExcWinS: 'Bouteille/jour exc WinS',
                    bottleDayExcWinSYTD: 'Bouteille/jour exc WinS YTD',
                    totalSalesBottle: 'Ventes totales (Bouteille)',
                    overWaste: 'Sur gaspillage',
                    penetration: 'Pénétration',
                    tier: 'Niveau',
                    nbOfOperator: 'Nb d\'opérateur',
                    popCommune: 'Pop Commune',
                    bottleDay: 'Bouteille/jour',
                    dayOpen: 'Jour ouvert',
                    beneficiaries: 'Bénéficiaires',
                    houseHold: 'Ménage',
                    technician: 'Technicien',
                },
                km: {
                    site: 'ទីតាំង',
                    month: 'ខែ',
                    platform: 'ភូមិភាគ',
                    entrepreneurName: 'ឈ្មោះសហគ្រិន',
                    workingDate: 'កាលបរិច្ឆេទធ្វើការ',
                    siteAnalysis: 'ការវិភាគបច្ចេកទេស',
                    bottleDayExcWinS: 'ប៊ីដុង/ថ្ងៃ អត់គិត WinS',
                    bottleDayExcWinSYTD: 'ប៊ីដុង/ថ្ងៃ អត់គិត WinS YTD',
                    totalSalesBottle: 'ការលក់សរុប(ប៊ីដុង)',
                    overWaste: 'បាត់ទឹក',
                    penetration: 'ការជ្រាបចូលទីផ្សារ',
                    tier: 'កម្រិត',
                    nbOfOperator: 'ចំនួនប្រតិបត្តិករ',
                    popCommune: 'ប្រជាជនក្នុងឃុំ',
                    bottleDay: 'ប៊ីដុង/ថ្ងៃ',
                    dayOpen: 'ចំនួនថ្ងៃបើក',
                    beneficiaries: 'អ្នកទទួលផល',
                    houseHold: 'ចំនួនគ្រួសារ',
                    technician: 'អ្នកបច្ចេកទេស',
                }
            },
            selectedDate: null,
        };
    },
    computed: {
        currentText() {
            return this.translations[this.selectedLanguage];
        }
    },
    watch: {
        selectedSite(newSite) {
            if (newSite) {
                this.fetchReport(newSite);

            }
        },
    },

    mounted() {
        this.fetchSites();
        const currentDate = new Date();
        currentDate.setMonth(currentDate.getMonth() - 1);
        this.selectedDate = currentDate.toISOString().slice(0, 7); // "YYYY-MM"
    },

    methods: {
        async showAssessmentPopup(site, type) {
            if (!site) {
                Swal.fire('Error', 'Invalid site data.', 'error');
                return;
            }
            
            console.log('Opening assessment for site:', site);
            
            // Use nextTick to ensure DOM is updated
            await this.$nextTick();
            this.type = type;
            this.Id_Site = site;
            this.popUpAssessmentDetail = true;
            
            console.log('Dialog should open now, popUpAssessmentDetail:', this.popUpAssessmentDetail);
        },
        popupDetailEntre() {
            alert("show total assessment!");
        },
        printReport() {
            window.print();
        },

        async fetchSites() {
            try {
                const { data } = await axios.get("/api/sites");
                this.sites = data;
            } catch (err) {
                console.error("Failed to fetch sites", err);
                this.sites = [];
            }
        },
        arrayToObject(arr) {
            const obj = {};
            let totalSelected = 0; // total of selected categories

            if (Array.isArray(arr)) {
                arr.forEach(e => {
                    const key = e.expense_category?.toLowerCase() || 'unknown';
                    const value = e.total_expenses || 0;

                    obj[key] = (obj[key] || 0) + value;

                    // sum only specific categories
                    if (['salary total', 'production', 'contribution', 'delivery'].includes(key)) {
                        totalSelected += value;
                    }
                });
            }
            // attach the total to the object
            obj.total_selected = totalSelected;

            return obj;
        },
        async fetchReport(siteId) {

            try {
                Swal.fire({
                    title: "Loading data...",
                    allowOutsideClick: false,
                    didOpen: () => Swal.showLoading(),
                });
                // const { data } = await axios.get(`/api/reports/${siteId}?month=${this.selectedDate}`);
                const { data } = await axios.get(`/api/assessmentAnalysis/${siteId}?month=${this.selectedDate}`);
                Swal.close();
                console.log("return Data:", data);
                if (!data || typeof data !== 'object' || Object.keys(data).length === 0) {
                    Swal.fire("No data", "No report data available for this site", "info");
                    return;
                }

                this.report = {
                    siteDetails: data.siteDetails || {},
                    sales: data.sales || {},
                    salesYtd: data.salesYtd || {},
                    assessment: data.assessment || {},
                    assessmentProcess: Array.isArray(data.assessmentProcess) ? data.assessmentProcess : [],
                    routine: data.routine || {},
                    sampleRecord: data.sample || {},
                    sampleYtdRecord: data.sampleYTD || {},
                    assessmentCountYTD: data.assessmentCountYTD || 0,
                    assessmentYTD: Array.isArray(data.assessmentYTD) ? data.assessmentYTD : [],
                    tubiData: data.alumiTubi || {},
                    contamination: data.contamination || {},
                };
                this.drawTubiLineChart(this.report.tubiData);
                this.drawContaminationPillarChart(this.report.contamination);
            } catch (err) {
                Swal.close();
                Swal.fire("Warning", "No data from this site", "warning");
                console.error("Failed to fetch report:", err);
            }
        },
        drawTubiLineChart(rawData) {
    const ctx = this.$refs.tubiLineChart;

    if (!ctx) return;

    if (this.tubiChart) {
      this.tubiChart.destroy();
    }

    // Example: rawData = { Nov: [ { aluminium: "...", turbidity: "..." }, ... ] }
    const monthKey = Object.keys(rawData)[0];   // "Nov"
    const samples = rawData[monthKey];          // array of objects

    const labels = samples.map((_, i) => "M" + (i + 1));  // S1, S2, S3...

    const aluminiumData = samples.map(s => {
      if (!s.aluminium || s.aluminium === null) return null;
      return Number(String(s.aluminium).replace(/<|>/g, ""));
    });

    const turbidityData = samples.map(s => Number(s.turbidity));

    this.tubiChart = new Chart(ctx, {
      type: "line",
      data: {
        labels: labels,
        datasets: [
          {
            label: "Aluminium",
            data: aluminiumData,
            borderColor: "red",
            borderWidth: 2,
            fill: false,
            tension: 0.3
          },
          {
            label: "Turbidity",
            data: turbidityData,
            borderColor: "blue",
            borderWidth: 2,
            fill: false,
            tension: 0.3
          }
        ]
      },
      options: {
        responsive: true,
        scales: {
          y: {
            beginAtZero: true
          }
        }
      }
    });
        },
        drawContaminationPillarChart(data) {
  const ctx = this.$refs.contaminationChart;
  if (!ctx) return;

  if (this.contamChart) this.contamChart.destroy();

  const months = Object.keys(data);
  const machineLevels = months.map(m => data[m].machine);
  const bottleLevels = months.map(m => data[m].bottle);

  this.contamChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: months,
      datasets: [
        {
          label: 'Machine Contamination Level',
          data: machineLevels,
          backgroundColor: 'rgba(54, 162, 235, 0.7)',
        },
        {
          label: 'Bottle Contamination Level',
          data: bottleLevels,
          backgroundColor: 'rgba(255, 206, 86, 0.7)',
        },
      ],
    },
    options: {
      responsive: true,
      scales: {
        y: {
          beginAtZero: true,
          max: 3,       // max contamination level
          ticks: { stepSize: 1 }
        },
        x: {
          stacked: false,  // side by side bars, not stacked
        }
      }
    }
  });
}


    }
};
</script>

<style scoped>
/* ==============================
   General Table and Layout Styles
   ============================== */
.pl-table th,
.pl-table td,
.v-table th,
.v-table td {
    padding: 2px 4px !important;
    text-align: center;
    font-size: 9pt;

}

.report-container {
    padding: 8px !important;
}

.rowTable {
    border: 1px solid #ccc;
    padding: 8px;
}

.report-container canvas {
    max-width: 100%;
    height: auto;
}

.khmer-mode {
    font-size: 105%;
    line-height: 1.4;
}

.khmer-mode .v-table,
.khmer-mode .v-card,
.khmer-mode .v-btn {
    font-size: 1.05em;
}

.khmer-mode h3 {
    font-size: 1.25rem;
}

.font-title-container {
    font-size: 12.5px;
    font-weight: bold;
    text-align: center;
    margin-bottom: 12px;
    color: #333;
    font-family: 'Arial', sans-serif;
    border: 0px solid #ccc;
    padding: 8px;
}

.khmer-mode .pl-table th,
.khmer-mode .pl-table td,
.khmer-mode .v-table th,
.khmer-mode .v-table td {
    font-size: 9.5pt;
    /* Slightly larger for Khmer */
}

/* ==============================
   Print Styling
   ============================== */
@media print {

    /* -------- Page Setup -------- */
    @page {
        size: A4 portrait;
        margin: 0.5cm;
    }

    html,
    body {
        margin: 0 !important;
        padding: 0 !important;
        zoom: 0.85;
        /* Scales everything to fit one page */
    }

    /* -------- Container -------- */
    .report-container {
        padding: 2mm !important;
        font-size: 7pt !important;
        transform: scale(0.95);
        transform-origin: top left;
    }

    /* -------- No-print elements -------- */
    .no-print {
        display: none !important;
    }

    /* -------- Cards -------- */
    .v-card {
        margin-bottom: 1mm !important;
        padding: 1mm !important;
        page-break-inside: avoid !important;
        box-shadow: none !important;
        border: 0.2mm solid #ccc !important;
    }

    /* -------- Headings -------- */
    h3 {
        font-size: 7pt !important;
        margin-bottom: 1mm !important;
        text-align: center !important;
    }

    /* -------- Layout (columns) -------- */
    .v-row {
        display: flex !important;
        flex-wrap: nowrap !important;
        justify-content: space-between !important;
        align-items: flex-start !important;
    }

    /* Equal column layout */
    .print-half {
        flex: 1 0 50% !important;
        max-width: 50% !important;
        box-sizing: border-box;
        padding: 0 1mm !important;
    }

    /* 70-30 split layout */
    .print-half1 {
        flex: 0 0 70% !important;
        max-width: 70% !important;
        box-sizing: border-box;
        padding: 0 1mm !important;
    }

    .print-half2 {
        flex: 0 0 30% !important;
        max-width: 30% !important;
        box-sizing: border-box;
        padding: 0 1mm !important;
    }

    /* -------- Tables -------- */
    .v-table {
        font-size: 6pt !important;
        width: 100% !important;
        border-collapse: collapse !important;
    }

    .v-table td,
    .v-table th {
        padding: 1px !important;
    }

    /* -------- Charts -------- */
    canvas {
        max-height: 60mm !important;
        /* reduced to ensure fits in one page */
        width: 100% !important;
        height: auto !important;
    }

    .historic-chart-canvas {
        max-height: 55mm !important;
        width: 100% !important;
        height: auto !important;
    }

    /* -------- Prevent breaks -------- */
    .v-card,
    .v-table,
    .v-row {
        page-break-before: avoid !important;
        page-break-after: avoid !important;
        page-break-inside: avoid !important;
        box-shadow: none !important;
        border: none !important;
    }

    /* -------- Scale all content to one page -------- */
    body {
        transform: scale(0.9);
        transform-origin: top center;
    }
}
</style>
