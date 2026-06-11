<template>
  <div v-if="!loading" class="d-flex flex-row pa-4">
    <v-select v-model="selectedPlatform" class="flex-grow-0 mr-5" label="Platform" :items="platformFilterItems" />
    <v-select v-model="report_type" class="flex-grow-0 mr-5" label="Report Type" :items="['Monthly_report','Mid_Flash_Report','Weekly_Flash_report']" />
    <v-select v-if="this.report_type=='Weekly_Flash_report'" v-model="weekly" class="flex-grow-0 mr-5" label="Week" :items="[1,2,3,4]" />
    <v-text-field v-model="selectedDate" class="flex-grow-0 mr-5" label="Month" type="month" />
    
    <v-text-field v-model="search" class="flex-grow-0 mr-5 search" label="Search site" type="text" />
    <v-btn class="ml-5 mt-2 me-auto" color="primary" 
    @click="$router.push({ path: '/flashReportDashboard', query:{report_type:this.report_type, date:selectedDate } })" > Dashboard</v-btn>
    <!-- <v-btn class="ml-5 mt-2 mr-5" color="secondary" icon="mdi-microsoft-excel" @click="exportExcel()" />  -->
  </div>

  <v-table v-if="!loading">
    <thead>
      <tr>
        <th />
        <th v-for="(platformSites, platform) in platformsToDisplay" :key="platform" class="text-center">
          <h4>{{ platform }}</h4>
          <h5>
            {{ Object.keys(samples).filter(site => sites[platform].find(s => site === s.Id_Site)).length }} sites 
          </h5>
          
        </th>
      </tr>
    </thead>
    <tbody>
      <tr class="ma-0 pa-0">
        <th class="text-subtitle-2 text-center">
          Submitted
        </th>
        <td v-for="(platformSites, platform) in platformsToDisplay" :key="platform">
          <div class="d-flex justify-center flex-wrap my-4">
            <v-chip v-for="site in platformSites.filter(s => samples[s.Id_Site] && samples[s.Id_Site].length > 0)"
              :key="site.Id_Site" size="small" :class="{
                'site': 1,
                ['level-' + 0]: 1,
                'highlighted': search != '' && site.Id_Site.includes(search)
              }" >
              {{ site.Id_Site }}
              <span v-if="samples[site.Id_Site].length > 1" class="badge">{{ samples[site.Id_Site].length }}</span>
              <!-- <v-icon color="green" class="ml-0 ">mdi-arrow-up</v-icon> -->
            </v-chip>
          </div>
        </td>
      </tr>
      <tr>
        <td class="text-subtitle-2 text-center">
          Not Submit
        </td>
        <td v-for="(platformSites, platform) in platformsToDisplay" :key="platform">
          <div class="d-flex justify-center flex-wrap my-4">
            <v-chip v-for="site in platformSites.filter(s => !samples[s.Id_Site] || samples[s.Id_Site].length == 0)"
              :key="site.Id_Site" size="small" :class="{
                'site': 1,
                'highlighted': search != '' && site.Id_Site.includes(search)
              }" >
              {{ site.Id_Site }}
              <!-- <v-icon color="red" class="ml-1 ">mdi-arrow-down</v-icon> -->
            </v-chip>
          </div>
        </td>
      </tr>
    </tbody>
  </v-table>

  <!-- <qualitychart v-if="!loading && Object.keys(samples).length > 0" :samples="filteredSamples" /> -->

  <div v-if="loading" class="d-flex justify-center mt-10 pt-10">
    <v-progress-circular indeterminate :size="60" color="primary" />
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
      loading: true,
      selectedDate: '',
      search: '',
      selectedPlatform: 'All',
      samples: [],
      sites: [],
      report_type:'Monthly_report',
      weekly:1,
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
    weekly() {
      this.getSamples()
    },
    report_type() {
      this.getSamples()
    }
  },
  mounted() {
    this.selectedDate = new Date().toISOString().slice(0, 7)
  },
  methods: {
    exportExcel() {
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
    },
    getSamples() {
      this.loading = true
      console.log(this.report_type)
      let date = this.selectedDate.split("-")
      let year = parseInt(date[0])
      let month = parseInt(date[1])
      window.axios.get('/api/flashReport?year=' + year + '&month=' + month+'&report_type='+ this.report_type +'&week='+this.weekly).then(response => {
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
  background-color:lightblue;
}

.level-1 {
  background-color: lightblue;

}

.level-2 {
  background-color: green
}

.level-3 {
  background-color: green
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

@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(5px); }
}

.bouncing {
  animation: bounce 1s infinite ease-in-out;
}
</style>