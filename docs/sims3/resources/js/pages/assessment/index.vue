<template>
  <!-- <v-btn icon="mdi-arrow-left-bold-circle" color="blue" size="small" @click="$router.push({ path: '/quality' })"></v-btn> -->
  <v-card class="ma-3">
    <v-tabs v-model="tab" bg-color="blue">
      <v-tab value="assessment">
        Assessment
      </v-tab>
      <v-tab value="routine">
        Routine
      </v-tab>
    </v-tabs>
    <v-card-text v-if="loading" class="d-flex justify-center mt-10">
      <v-progress-circular indeterminate :size="60" color="primary" />
    </v-card-text>
    <v-card-text v-else>
      <div v-if="tab == 'assessment'">
        <div class="d-flex flex-row align-center mb-3">
          <v-row>
            <v-col cols="12" md="2">
              <v-btn class="ml-5 mt-2 mr-5" color="secondary" icon="mdi-microsoft-excel" @click="excelDownloadAll()" />
            </v-col>
            <!-- <v-col cols="12" md="2">
                                <v-btn class="mr-5" color="blue" icon="mdi-hospital" @click="$router.push({ path: '/FormRoutine' })" />
                            </v-col> -->
          </v-row>
          <v-text-field v-model="search" density="compact" label="Search" hide-details clearable class="shrink"
            prepend-inner-icon="mdi-clipboard-text-search" />
        </div>
        <!-- show data -->
        <v-data-table v-model:items-per-page="itemsPerPage" :headers="headersAssessment" :items="filterPA"
          density="compact" class="pa-4">
          <!-- <template #item.excel="{ item }">
                        <v-chip size="small" color="Blue" v-if="item.site_open_final_judgement == '' || item.site_open_final_judgement == null"
                        @click="excelDownload(item.site)">
                            <v-icon start size="x-small" icon="mdi-apple-keyboard-shift" />Detail
                        </v-chip>
                    </template> -->
          <template #item.detail="{ item }">
            <v-chip size="small" color="Blue" @click.prevent="
              $router.push({
                path: '/FormAssessment/' + item.id,
              })
              ">
              <v-icon start size="x-small" icon="mdi-apple-keyboard-shift" color="green" />Detail
            </v-chip>
          </template>
        </v-data-table>
      </div>
      <div v-else>
        <div class="d-flex flex-row align-center mb-3">
          <v-row>
            <v-col cols="12" md="2">
              <v-btn class="ml-5 mt-2 mr-5" color="secondary" icon="mdi-microsoft-excel" @click="excelDownloadAll()" />
            </v-col>
          </v-row>
          <v-text-field v-model="search" density="compact" label="Search" hide-details clearable class="shrink"
            prepend-inner-icon="mdi-clipboard-text-search" />
        </div>
        <!-- show data -->
        <v-data-table v-model:items-per-page="itemsPerPage" :headers="headersRoutine" :items="filterPA"
          density="compact" class="pa-4">
          <!-- <template #item.excel="{ item }">
                        <v-chip size="small" color="Blue" v-if="item.site_open_final_judgement == '' || item.site_open_final_judgement == null"
                        @click="excelDownload(item.site)">
                            <v-icon start size="x-small" icon="mdi-apple-keyboard-shift" />Detail
                        </v-chip>
                    </template> -->
          <template #item.detail="{ item }">
            <v-chip size="small" color="Blue" @click.prevent="
              $router.push({
                path: '/FormRoutine/' + item.id,
              })
              ">
              <v-icon start size="x-small" icon="mdi-apple-keyboard-shift" color="green" />Detail
            </v-chip>
          </template>
        </v-data-table>
      </div>
    </v-card-text>
  </v-card>

  <div class="text-center">
    <v-dialog v-model="dialog" activator="parent" width="auto">
      <v-card>
        <v-card-text>
          Excel download is in construction. Please be patient !!!
        </v-card-text>
        <v-card-actions>
          <v-btn color="primary" block @click="dialog = false">
            Close
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
// import { VDataTable } from 'vuetify/labs/VDataTable'
export default {
  name: "HomePage",
  data: function () {
    return {
      open: false,
      startdate: new Date().toJSON().slice(0, 10),
      enddate: new Date().toJSON().slice(0, 10),
      position: "",
      positionData: [],
      dialog: false,
      loading: true,
      PA: [],
      itemsPerPage: 15,
      search: "",
      tab: "assessment",
      throttleTimer: -1,
      headersAssessment: [
        {
          title: "Detail",
          align: "start",
          key: "detail",
          width: 20,
          sortable: true,
        },
        {
          title: "Site",
          align: "start",
          key: "site",
          width: 10,
          sortable: true,
        },
        {
          title: "Date",
          align: "start",
          key: "date_form",
          width: 20,
          sortable: true,
        },
        {
          title: "Technician",
          align: "start",
          key: "technician",
          width: 20,
          sortable: true,
        },
        {
          title: "First Assessment",
          align: "start",
          key: "first_site_assessment",
          width: 30,
          sortable: true,
        },
        {
          title: "Main_water_source",
          align: "start",
          key: "main_source_of_water",
          width: 30,
          sortable: true,
        },
        {
          title: "Electricity_source",
          align: "start",
          key: "main_source_of_electricity",
          width: 40,
          sortable: true,
        },
        {
          title: "Solar_panel",
          align: "start",
          key: "solar_panel",
          width: 40,
          sortable: true,
        },
        {
          title: "Battery",
          align: "start",
          key: "condition_batteries",
          width: 40,
          sortable: true,
        },
        {
          title: "Invertor",
          align: "start",
          key: "condition_inverter_dc_to_ac",
          width: 40,
          sortable: true,
        },
        {
          title: "Water_tank",
          align: "start",
          key: "type_of_raw_water_tank",
          width: 40,
          sortable: true,
        },
        {
          title: "Sand_filter",
          align: "start",
          key: "type_of_sand_filter_tank",
          width: 40,
          sortable: true,
        },
        {
          title: "Ac_filter",
          align: "start",
          key: "type_of_ac_filter_tank",
          width: 40,
          sortable: true,
        },
        // { title: 'Excel', align: 'start', key: 'excel', width: 40,sortable: true },
      ],
      headersRoutine: [
        {
          title: "Detail",
          align: "start",
          key: "detail",
          width: 40,
          sortable: true,
        },
        {
          title: "Site",
          align: "start",
          key: "site",
          width: 40,
          sortable: true,
        },
        {
          title: "Date",
          align: "start",
          key: "date",
          width: 60,
          sortable: true,
        },
        {
          title: "Name",
          align: "start",
          key: "technician",
          width: 50,
          sortable: true,
        },
        {
          title: "Main_Person",
          align: "start",
          key: "main_person_the_water_kiosk_with_you",
          width: 40,
          sortable: true,
        },
        {
          title: "Water_Tank",
          align: "start",
          key: "condition_of_raw_water_tank",
          width: 40,
          sortable: true,
        },
        {
          title: "Sand_Filter",
          align: "start",
          key: "condition_of_sand_filter_tank",
          width: 40,
          sortable: true,
        },
        {
          title: "Ac_Filter",
          align: "start",
          key: "condition_of_ac_filter_tank",
          width: 40,
          sortable: true,
        },
        {
          title: "Resin_Filter",
          align: "start",
          key: "condition_of_resin_filter_tank",
          width: 40,
          sortable: true,
        },
        {
          title: "RO",
          align: "start",
          key: "condition_of_ro",
          width: 40,
          sortable: true,
        },
        {
          title: "Ultrafiltration",
          align: "start",
          key: "condition_of_ultrafiltration",
          width: 40,
          sortable: true,
        },
        {
          title: "Leak_Pipe",
          align: "start",
          key: "are_pre_treatment_pipes_leaking",
          width: 20,
          sortable: true,
        },
        {
          title: "Pretreatment",
          align: "start",
          key: "is_the_pre_treatment_clean",
          width: 40,
          sortable: true,
        },
        // { title: 'Excel', align: 'start', key: 'excel', width: 40,sortable: true },
      ],
    };
  },
  computed: {
    filterPA() {
      if (this.tab == "assessment" || this.tab == "routine") {
        if (this.search == "") {
          return this.PA;
        } else {
          // return this.PA.filter(m => (m.site).includes(this.search))

          // return this.PA.filter(item => {
          //   return item.site.includes(this.search.toLocaleUpperCase()) || item.technician.includes(this.search.toLocaleUpperCase()) ;
          //             });
          const search = this.search.toLocaleUpperCase();
          return this.PA.filter((item) => {
            return (
              item.site.toUpperCase().includes(search) ||
              item.technician.toUpperCase().includes(search)
            );
          });
        }
      }
    },
  },
  watch: {
    tab() {
      // we throttle the call in case people click too much
      if (this.throttleTimer) {
        clearTimeout(this.throttleTimer);
      }
      this.throttleTimer = setTimeout(() => {
        this.getData();
      });
    },
  },
  mounted() {
    this.getData();
  },
  methods: {
    getData() {
      this.loading = true;
      window.axios
        .get("/api/assessment/?" + this.tab + "=1")
        .then((response) => {
          console.log(response.data);
          this.PA = response.data;
          this.loading = false;
        });
    },
    showExcelDownloadMessage() {
      // alert ("Download excel is in construction !!! Thank you for your patient")
      setTimeout(() => {
        this.dialog = true;
      }, 50);
    },
    excelDownload(s) {
      window.axios
        .get("/api/assessmentDownload?tab=" + this.tab + "&site=" + s, {
          responseType: "blob",
        })
        .then((response) => {
          const url = URL.createObjectURL(
            new Blob([response.data], {
              type: "application/vnd.ms-excel",
            })
          );
          const link = document.createElement("a");
          link.href = url;
          link.setAttribute("download", this.tab + ".xlsx");
          document.body.appendChild(link);
          link.click();
          link.remove();
        });
    },
    excelDownloadAll() {
      window.axios
        .get("/api/assessmentDownloadAll?tab=" + this.tab, {
          responseType: "blob",
        })
        .then((response) => {
          const url = URL.createObjectURL(
            new Blob([response.data], {
              type: "application/vnd.ms-excel",
            })
          );
          const link = document.createElement("a");
          link.href = url;
          link.setAttribute("download", this.tab + ".xlsx");
          document.body.appendChild(link);
          link.click();
          link.remove();
        });
    },
  },
};
</script>

<style>
.waiting {
  color: red;
  font-weight: bold;
}

.validated {
  color: orange;
  font-weight: bold;
}

.advanced {
  color: green;
  font-weight: bold;
}

.expense_validated {
  color: #666666;
  font-weight: bold;
}
</style>
