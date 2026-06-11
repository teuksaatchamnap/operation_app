<template>
  <div v-if="!loading" class="d-flex flex-row pa-4">
    <v-select v-model="selectedPlatform" class="flex-grow-0 mr-5" label="Platform" :items="platformFilterItems" />
    <v-text-field v-model="selectedDate" class="flex-grow-0 mr-5" label="Month" type="month" />
    <v-text-field v-model="search" class="flex-grow-0 mr-5 search" label="Search site" type="text" />
    <v-btn class="ml-5 mt-2 me-auto" color="primary" icon="mdi-eyedropper-plus"
      @click="$router.push({ path: '/quality/sample' })" />
    <!-- <v-btn class="ml-5 mt-2 me-auto" color="yellow" icon="mdi-cloud-print"
    @click="$router.push({ path: '/labCertificate', query:{platform:selectedPlatform, date:selectedDate } })" /> -->

    <v-btn class="ml-5 mt-2 me-auto" color="yellow" icon="mdi-cloud-print"
    @click="ShowPrintCertificate()" />
    <v-btn class="ml-5 mt-2 me-auto" color="primary" @click="$router.push({ path: '/quality/siteOpening' })"> Site
      Opening/ Site Selection</v-btn>
    <v-tooltip text="Data export">
      <template #activator="{ props }">
        <v-btn v-bind="props" class="ml-5 mt-2 mr-2" color="green" icon="mdi-microsoft-excel" @click="exportExcelModal()" />
      </template>
    </v-tooltip>
    <v-tooltip text="Excel dashboard">
      <template #activator="{ props }">
        <v-btn v-bind="props" :disabled="isExportingDashboard" :class="{ 'rotate-icon': isExportingDashboard }" class="ml-5 mt-2 mr-5 text-white" color="red" :icon="isExportingDashboard ? 'mdi-loading' : 'mdi-file-chart-outline'"
          @click="exportExcelDashboard()" />
      </template>
    </v-tooltip>
  </div>

  <v-table v-if="!loading">
    <thead>
      <tr>
        <th />
        <th v-for="(platformSites, platform) in platformsToDisplay" :key="platform" class="text-center">
          <h4>{{ platform }}</h4>
          <h5>
            {{ Object.keys(samples).filter(site => sites[platform].find(s => site === s.Id_Site)).length }} sites tested
          </h5>
          <h5>
            {{ sites[platform] ? sites[platform].length : 0 }} active sites
          </h5>
        </th>
      </tr>
    </thead>
    <tbody>
      <tr class="ma-0 pa-0">
        <th class="text-subtitle-2 text-center">
          Tested
        </th>
        <td v-for="(platformSites, platform) in platformsToDisplay" :key="platform">
          <div class="d-flex justify-center flex-wrap my-4">
            <v-chip v-for="site in platformSites.filter(s => samples[s.Id_Site] && samples[s.Id_Site].length > 0)"
              :key="site.Id_Site" size="small" :class="{
    'site': 1,
    ['level-' + Math.max(samples[site.Id_Site][0].contamination_level_bottle, samples[site.Id_Site][0].contamination_level_machine)]: 1,
    'highlighted': search != '' && site.Id_Site.includes(search)
  }" @click="$router.push({ path: '/quality/' + site.Id_Site })">
              {{ site.Id_Site }}
              <span v-if="samples[site.Id_Site].length > 1" class="badge">{{ samples[site.Id_Site].length }}</span>
            </v-chip>
          </div>
        </td>
      </tr>
      <tr>
        <td class="text-subtitle-2 text-center">
          Not tested
        </td>
        <td v-for="(platformSites, platform) in platformsToDisplay" :key="platform">
          <div class="d-flex justify-center flex-wrap my-4">
            <v-chip v-for="site in platformSites.filter(s => !samples[s.Id_Site] || samples[s.Id_Site].length == 0)"
              :key="site.Id_Site" size="small" :class="{
    'site': 1,
    'highlighted': search != '' && site.Id_Site.includes(search)
  }" @click="$router.push({ path: '/quality/' + site.Id_Site })">
              {{ site.Id_Site }}
            </v-chip>
          </div>
        </td>
      </tr>
    </tbody>
  </v-table>

  <!-- <qualitychart v-if="!loading && Object.keys(samples).length > 0" :samples="filteredSamples" /> -->
  <div id="map" class="map-container"></div>

  <div v-if="loading" class="d-flex justify-center mt-10 pt-10">
    <v-progress-circular indeterminate :size="60" color="primary" />
  </div>
  <div class="text-center">
    <v-dialog v-model="dialog" activator="parent" max-width="500">
      <v-card prepend-icon="" title="Do you want to download all site or one site ?">
        <v-card-text>
          <v-select v-model="reportType" label="Type" density="compact" hide-details="auto"
            :items="['Monthly Report', 'One_Site', 'Range_Date','Panalty_Site']" />
            <v-spacer> </v-spacer>
            <v-autocomplete v-model="reportSite" label="Site" density="compact"
                 :items="Object.keys(resultsites)" v-if="reportType =='One_Site'" :rules="required"
                persistent-hint  />
                <v-spacer> </v-spacer>
                <v-text-field v-model="rangeStart"  label="Start" type="date" hide-details="auto" v-if="reportType =='Range_Date'" />
                <v-text-field v-model="rangeEnd"  label="End" type="date" hide-details="auto"  v-if="reportType =='Range_Date'"/>
        </v-card-text>
        <v-card>
          <template v-slot:actions>
            <v-spacer></v-spacer>
            <v-btn @click="dialog = false; exportExcel()" >
              Download
            </v-btn>

          </template>
        </v-card>
      </v-card>
    </v-dialog>
  </div>
  <!--Dialog for lap to print-->
  <div class="text-center">
    <v-dialog v-model="labdialog" activator="parent" max-width="500">
      <v-card prepend-icon="" title="Which template do you want to print ?">
        <v-card-text>
          <div class="mb-4">
            <v-select v-model="labName" label="Select Lab Name" density="compact" hide-details="auto"
              :items="['','chakriya.v@teuksaat1001.com', 'sreymao.b@teuksaat1001.com', 'chanmonida.h@teuksaat1001.com','champey.p@teuksaat1001.com']" />
          </div>
          <div class="mb-4">
            <v-select v-model="labreportType" label="Type" density="compact" hide-details="auto"
              :items="['Monthly Test', 'WQ Alert']" />
          </div>
          <div class="mb-4" v-if="labreportType =='WQ Alert'">
            <v-select v-model="testNumber" label="Type" density="compact" hide-details="auto"
              :items="['second', 'third', 'corrective action']" />
          </div>

        </v-card-text>

        <v-card>
          <template v-slot:actions>
            <v-spacer></v-spacer>
            <v-btn @click="labdialog = false; PrintCertificate(selectedPlatform,selectedDate,labreportType,testNumber,labName)" >
              Print
            </v-btn>

          </template>
        </v-card>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>

import QualityChart from "../../components/QualityCharts.vue"

export default {
  name: 'QualityHome',
  components: {
    qualitychart: QualityChart,
  },
  data: function () {
    return {
      reportType: '',
      labreportType:'',
      testNumber:'',
      labName:'',
      reportSite:'',
      loading: true,
      isExportingDashboard: false,
      selectedDate: '',
      search: '',
      selectedPlatform: 'All',
      samples: [],
      dialog: false,
      labdialog:false,
      sites: [],
      resultsites:[],
      required: [
        value => {
          if (value) return true
          return 'This field is required.'
        },
      ]
    }
  },
  computed: {
    platformsToDisplay() {
      if (this.selectedPlatform === 'All') {
        return this.sites
      } else {
        return {
          [this.selectedPlatform]: this.sites[this.selectedPlatform]
        }
      }
    },
    platformFilterItems() {
      let p = Object.keys(this.sites)
      p.unshift("All");
      return p
    },
    filteredSamples() {
      if (this.selectedPlatform === 'All') {
        return this.samples
      } else {
        return Object.fromEntries(Object.entries(this.samples).filter(([key,]) => {
          return this.sites[this.selectedPlatform].find(s => s.Id_Site === key)
        }));
      }
    }
  },
  watch: {
    selectedDate() {
      this.getSamples()
    },

  },
  mounted() {
    this.selectedDate = new Date().toISOString().slice(0, 7)
    window.axios.get("/api/sites").then(response => {
      this.resultsites = response.data.reduce(function (map, obj) {
        map[obj.Id_Site] = obj.Advisor;
        return map;
      }, {});
    })
  },
  methods: {
    exportExcel() {
      if(this.reportType=='Monthly Report')
      {
      window.axios.get('/api/samplesExport?month=' + this.selectedDate, { responseType: 'blob' }).then(response => {
        const url = URL.createObjectURL(new Blob([response.data], {
          type: 'application/vnd.ms-excel'
        }))
        const link = document.createElement('a')
        link.href = url
        link.setAttribute('download', "export_quality_" + this.selectedDate + ".xlsx")
        document.body.appendChild(link)
        link.click()
        link.remove()
      });

      }
      else if (this.reportType=='One_Site')
      {
        if(this.reportSite !='')
        {
          window.axios.get('/api/sampleExcelSite?site=' + this.reportSite, { responseType: 'blob' }).then(response => {
          const url = URL.createObjectURL(new Blob([response.data], {
          type: 'application/vnd.ms-excel'
        }))
        const link = document.createElement('a')
        link.href = url
        link.setAttribute('download', "export_quality_" + this.selectedDate + ".xlsx")
        document.body.appendChild(link)
        link.click()
        link.remove()
        });

        }
      }
      else if (this.reportType=='Range_Date')
      {
          window.axios.get('/api/sampleExcelRangDate?start=' + this.rangeStart +'&end='+this.rangeEnd, { responseType: 'blob' }).then(response => {
          const url = URL.createObjectURL(new Blob([response.data], {
          type: 'application/vnd.ms-excel'
        }))
        const link = document.createElement('a')
        link.href = url
        link.setAttribute('download', "export_quality" + ".xlsx")
        document.body.appendChild(link)
        link.click()
        link.remove()
        });
      }
      else if (this.reportType=='Panalty_Site')
      {
        window.axios.get('/api/panaltySite?month=' + this.selectedDate, { responseType: 'blob' }).then(response => {
          const url = URL.createObjectURL(new Blob([response.data], {
          type: 'application/vnd.ms-excel'
        }))
        const link = document.createElement('a')
        link.href = url
        link.setAttribute('download', "panaltySite_" +this.selectedDate + ".xlsx")
        document.body.appendChild(link)
        link.click()
        link.remove()
        });
      }
    },
    exportExcelModal() {
      this.dialog = true
    },
    ShowPrintCertificate(){

      if(this.selectedPlatform == "All")
          {
              alert("Please select platform")
          }
      else{
        this.labdialog=true
      }

    },
    PrintCertificate(platform1,dateSelect,reportType,testNumber,labName)
    {

         if(platform1 == "All")
          {
              alert("Please select platform")
          }
        else if(labName == "")
          {
              alert("Please select lab name")
          }
        else if(reportType == "")
          {
              alert("Please select report type")
          }
        else
        {
            this.$router.push({
            path: '/labCertificate',
            query:{
            platform:platform1,
            date:dateSelect,
            labreportType:reportType,
            testNumber:testNumber,
            labName:labName
            }
          });
    }
    },
    exportExcelDashboard() {
      this.isExportingDashboard = true;
      const month = this.selectedDate.slice(0, 7)
      window.axios.defaults.headers.get['Access-Control-Allow-Origin'] = '*';
      window.axios.get("https://dashboard.teuksaat1001.com/QualityDashboard?month=" + month + "&ts=" + (new Date()).toISOString(), {
        withCredentials: false,
        responseType: 'blob'
      }).then(response => {
        const url = URL.createObjectURL(new Blob([response.data], {
          type: 'application/vnd.ms-excel'
        }))
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', 'Quality_dashboard_' + month + '.xlsx');
        document.body.appendChild(link);
        link.click();
        link.remove();
        this.isExportingDashboard = false;
      }).catch(err => {
        window.alert(err)
        this.isExportingDashboard = false;
      })
    },
    getSamples() {
      this.loading = true
      let date = this.selectedDate.split("-")
      let year = parseInt(date[0])
      let month = parseInt(date[1])
      window.axios.get('/api/samples?year=' + year + '&month=' + month).then(response => {
        this.samples = response.data.samples
        this.sites = response.data.sites
        this.loading = false
      });
    },
  }
}
</script>

<style scoped>
.site {
  margin: 1px;
  overflow: visible;
}

.level-0 {
  background-color: #B3E5FC;
}

.level-1 {
  background-color: #FFEB3B;
}

.level-2 {
  background-color: #FF9800
}

.level-3 {
  background-color: #F44336
}

.badge {
  z-index: 100;
  box-sizing: border-box;
  font-size: 0.7em;
  color: white;
  background: #0094c7;
  width: 15px;
  height: 15px;
  margin: 0;
  border-radius: 50%;
  position: absolute;
  top: -3px;
  right: -6px;
  text-align: center;
  padding-top: 2px;
}

.search {
  min-width: 200px;
}

.highlighted {
  animation: blinking ease 0.5s infinite alternate;
}

@keyframes blinking {
  0% {
    box-shadow: 0px 0px 1px 1px #2196F3;
  }

  100% {
    box-shadow: 0px 0px 8px 8px #03A9F4;
  }
}
.rotate-icon {
  animation: rotate 1s infinite linear;
}

@keyframes rotate {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style>
