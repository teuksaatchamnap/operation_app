<template>
  <v-form v-if="!loading" class="bg-grey-lighten-1 pa-4" @submit.prevent="downlonadReport">
    <v-container>
      <!-- Type -->
      <v-card prepend-icon="mdi-chemical-weapon" title="Site Analysis" class="mb-3 rounded-lg"> <br>
        <v-card-text>
          <v-row>
            <v-col cols="12" md="3">
              <v-select v-model="analysis.advisor" label="Choose Advisor" density="compact" hide-details="auto"
                :items="advisors" item-title="Advisor" :rules="required" />
            </v-col>
            <v-col cols="12" md="3">
              <v-select v-model="analysis.site" label="Choose site" density="compact" hide-details="auto" :items="sites"
                item-title="Id_Site" :rules="required" />
            </v-col>
          </v-row>
        </v-card-text>
      </v-card>
      <v-row class="ma-2" justify="center">
        <v-btn prepend-icon="mdi-file-excel" rounded="lg" color="green" class="ma-4" size="large" type="submit">
          Report
        </v-btn>
      </v-row>
    </v-container>
  </v-form>
  <div v-if="loading" class="d-flex justify-center mt-10">
    <v-progress-circular indeterminate :size="60" color="primary" />
  </div>
</template>
  
<script>

export default {
  name: 'SiteAnalysis',
  data: function () {
    return {
      month: new Date().toJSON().slice(0, 7),
      loading: false,
      sites: [],
      advisors: [],
      analysis: {
        advisor: '',
        site: ''
      },
      hasError: false,
      required: [
        value => {
          if (value) return true
          return 'This field is required.'
        },
      ]
    }
  },
  computed: {

  },
  watch: {
    "analysis.advisor": function () {
      axios.defaults.headers.get['Access-Control-Allow-Origin'] = '*';
      axios.post("https://dashboard.teuksaat1001.com/SiteofAdvisor?advisor=" + this.analysis.advisor, {}, { withCredentials: false }).then(response => {
        this.loading = false
        this.sites = response.data.site;
        this.sites.push({ Id_Site: 'All sites' })
        console.log(this.sites)
      })
    }
  },
  unmounted() {

  },
  mounted() {
    axios.defaults.headers.get['Access-Control-Allow-Origin'] = '*';
    axios.post("https://dashboard.teuksaat1001.com/Advisor", {}, { withCredentials: false }).then(response => {
      this.loading = false
      this.advisors = response.data.advisor;


    })

  },
  methods: 
  {
    downlonadReport() {
      var win = window.open("https://dashboard.teuksaat1001.com/SiteAnalysis?site=" + this.analysis.site + "&advisor=" + this.analysis.advisor, "_blank");
      if (win) {
        console.log('Your file will be downloaded shortly');
        win.focus();
      } else {
        //alert('No file download');
        console.log("your file can't download");
      }
    }
  },

}
</script>
  
  