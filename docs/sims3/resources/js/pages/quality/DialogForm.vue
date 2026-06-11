<template>
    <v-form v-if="!loading" class="bg-grey-lighten-1 pa-4" @submit.prevent="saveSample">
      <v-container>
        <!-- Type -->
        <v-card prepend-icon="mdi-chemical-weapon" title="Type" class="mb-3 rounded-lg">
          <v-card-text>
            <v-row>
              <v-col cols="12" md="3">
                
                <v-select v-model="sample.type" label="Type" density="compact" hide-details="auto"
                  :items="['Monthly Test', 'WQ Alert', 'Site_Opening', 'Site_Selection', 'Site_Intervention','Raw_Water']" />
              </v-col>
              <v-col v-if="sample.type === 'WQ Alert'" cols="12" md="2">
                <v-select v-model="sample.test_number" label="Test Number" density="compact" hide-details="auto"
                  :items="(sample.type === 'Monthly Test') ? ['first'] : ['second', 'third', 'corrective action']" />
              </v-col>
              <v-col v-if="sample.type === 'Raw_Water'" cols="12" md="2">
              <v-select v-model="sample.raw_water_type" label="Raw Water Type" density="compact" hide-details="auto"
                :items="['','Arsenic', 'Zmag', 'RO Inlet','UF Inlet','UF Outlet']" /> </v-col>
              <v-col cols="12" md="2">
                <v-text-field v-model="sample.response_date" type="date" density="compact" label="Response date"
                  hide-details="auto" />
              </v-col>
              <v-col cols="12" md="5">
                <v-file-input v-if="sample.type == 'Site_Selection'" label="Select picture or file to upload"
                  v-model="sample.picture" multiple variant="outlined" @change="handleFileChange"></v-file-input>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
        <!-- Site selection -->
        <v-card v-if="sample.type === 'Site_Selection'" prepend-icon="mdi-card-account-details-outline"
          title="Sample Site Selection" class="mb-3 rounded-lg">
          <v-card-text>
            <v-row>
              <v-col cols="12" md="2">
                <v-text-field v-model="sample.sample_code" type="text" density="compact" label="Sample Code"
                  hide-details="auto" :readonly="checkCode" />
              </v-col>
              <v-col cols="12" md="5">
                <v-text-field v-model="sample.sample_en_location" type="text" density="compact" label="English Location"
                  hide-details="auto" />
              </v-col>
              <v-col cols="12" md="5">
                <v-text-field v-model="sample.sample_kh_location" type="text" density="compact" label="Khmer Location"
                  hide-details="auto" />
              </v-col>
            </v-row>
            <v-row>
              <v-col cols="12" md="5">
                <v-text-field v-model="sample.latitude" type="text" density="compact" label="Latitude"
                  hide-details="auto" />
              </v-col>
              <v-col cols="12" md="5">
                <v-text-field v-model="sample.longtitude" type="text" density="compact" label="Longtitude"
                  hide-details="auto" />
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
        <!-- info new site Site_Opening -->
        <v-card
          v-if="sample.type === 'Site_Opening' || sample.type === 'Site_Selection' || sample.type === 'Site_Intervention' || sample.type === 'Raw_Water'"
          prepend-icon="mdi-card-account-details-outline" title="Sample Info" class="mb-3 rounded-lg">
          <v-card-text>
            <v-row>
              <v-col cols="12" md="4">
                <v-text-field v-model="sample.site_open_sample_date" type="date" density="compact"
                  label="Sample Date Pick Up" hide-details="auto" />
              </v-col>
              <v-col cols="12" md="4">
                <v-select v-model="sample.site_open_sample_type" label="Sample Type" density="compact" hide-details="auto"
                  :items="['', 'Pond', 'River', 'Well', 'Utility', 'Clean_Water', 'Drinking_Water', 'Canal', 'Water_Truck']" />
              </v-col>
              <v-col cols="12" md="4">
                <v-select v-model="sample.site_open_project_type" label="Project / Description" density="compact"
                  hide-details="auto"
                  :items="['', 'Rehabilitation', 'Change RWS', 'Before Deepcleaning', 
                  'Change water source', 'Operation', 'Scarcity', 'Community pond', 
                  '2025-01', '2025-02', '2025-03', '2026-01', '2026-02', '2026-03','2027-01','2027-02','2027-03']" />
              </v-col>
            </v-row>
            <v-row>
              <v-col cols="12" md="6">
                <v-text-field v-model="sample.site_open_description" type="text" density="compact"
                  label="Description Detail" hide-details="auto" />
              </v-col>
              <v-col cols="12" md="3">
                <v-text-field v-model="sample.site_open_sample_by" type="text" density="compact" label="Take Sample By"
                  hide-details="auto" />
              </v-col>
              <v-col cols="12" md="3">
                <v-select v-model="sample.laboratory" label="Laboratory" density="compact" hide-details="auto"
                  :items="['', 'SR', 'PP', 'KC', 'BTB']" :rules="required" />
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
        <!-- Identification -->
        <v-card v-if="sample.type !== 'Site_Selection'" prepend-icon="mdi-card-account-details-outline"
          title="Identification" class="mb-3 rounded-lg">
          <v-card-text>
            <v-row>
              <v-col cols="12" md="3">
                <v-autocomplete v-model="sample.site" label="Site" density="compact"
                  :hint="sites[sample.site] ? 'Advisor in charge: ' + sites[sample.site] : ''" :items="Object.keys(sites)"
                  persistent-hint :rules="required" />
              </v-col>
              <v-col cols="12" md="3">
                <v-text-field v-model="sample.sample_date" type="date" density="compact" label="Sample date"
                  hide-details="auto" />
              </v-col>
              <v-col cols="12" md="3">
                <v-text-field v-model="sample.received_date" type="date" density="compact" label="Received date"
                  hide-details="auto" persistent-hint>
                  <template #details>
                    <v-chip size="small" variant="elevated" :color="delay >= 5 || delay < 0 ? 'error' : 'success'">
                      <v-icon v-if="delay >= 5 || delay < 0" start icon="mdi-alert-circle" />
                      Delay = {{ delay }}
                    </v-chip>
                  </template>
                </v-text-field>
              </v-col>
              <v-col cols="12" md="3">
                <v-text-field v-model="sample.analysis_date" type="date" density="compact" label="Analysis date"
                  hide-details="auto" />
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
        <!-- Microbio -->
        <v-card prepend-icon="mdi-bacteria" title="Microbiological Analysis" class="mb-3 rounded-lg" v-if="sample.type !== 'Raw_Water'">
          <v-card-text>
            <v-row>
              <v-col cols="12" md="3" align-self="center" class="text-right">
                Machine
              </v-col>
              <v-col cols="12" md="3">
                <v-text-field v-model="sample.total_coliform" density="compact" label="Coliform - 24h" hint="N ≤ 0"
                  persistent-hint />
              </v-col>
              <v-col cols="12" md="3">
                <v-text-field v-model="sample.escherichia" density="compact" label="Escherichia Coli - 24h" hint="N = 0"
                  persistent-hint />
              </v-col>
              <v-col cols="12" md="3">
                <v-text-field v-model="sample.contamination_level_machine" readonly type="number" density="compact"
                  label="Contamination level" hide-details="auto">
                  <template #append-inner>
                    <v-icon
                      :color="sample.contamination_level_machine == 3 ? 'red' : (sample.contamination_level_machine == 2 ? 'orange' : (sample.contamination_level_machine == 1 ? 'yellow' : undefined))"
                      :icon="sample.contamination_level_machine == 3 ? 'mdi-alert-circle' : (sample.contamination_level_machine > 0 ? 'mdi-alert-circle-outline' : undefined)" />
                  </template>
                </v-text-field>
              </v-col>
            </v-row>
            <v-row>
              <v-col cols="12" md="3" align-self="center" class="text-right">
                Bottle
              </v-col>
              <v-col cols="12" md="3">
                <v-text-field v-model="sample.total_coliform_bottle" density="compact" label="Coliform - 24h" hint="N ≤ 0"
                  persistent-hint />
              </v-col>
              <v-col cols="12" md="3">
                <v-text-field v-model="sample.escherichia_bottle" density="compact" label="Escherichia Coli - 24h"
                  hint="N = 0" persistent-hint />
              </v-col>
              <v-col cols="12" md="3">
                <v-text-field v-model="sample.contamination_level_bottle" readonly type="number" density="compact"
                  label="Contamination level" hide-details="auto">
                  <template #append-inner>
                    <v-icon
                      :color="sample.contamination_level_bottle == 3 ? 'red' : (sample.contamination_level_bottle == 2 ? 'orange' : (sample.contamination_level_bottle == 1 ? 'yellow' : undefined))"
                      :icon="sample.contamination_level_bottle == 3 ? 'mdi-alert-circle' : (sample.contamination_level_bottle > 0 ? 'mdi-alert-circle-outline' : undefined)" />
                  </template>
                </v-text-field>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
        <!-- Physico-chemical -->
        <v-card
          v-if="sample.type === 'Monthly Test' || sample.type == 'Site_Opening' || sample.type === 'Site_Intervention' || sample.type === 'Site_Selection' || sample.type === 'Raw_Water'"
          prepend-icon="mdi-terrain" title="Physico-chemical analysis" class="mb-3 rounded-lg">
          <v-card-text>
            <v-row>
              <v-col v-for="param in physicos" :key="param" cols="12" md="3">
                <v-text-field v-model="sample[param.code]" density="compact" :label="param.label" :hint="param.interval"
                  persistent-hint>
                  <template #append-inner>
                    <v-chip v-if="param.pt != ''" size="small" label>
                      {{ param.pt }}
                    </v-chip>
                  </template>
                </v-text-field>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
        <!-- Sanitary inspection -->
        <v-card v-if="sample.type === 'Monthly Test'" prepend-icon="mdi-magnify" title="Sanitary inspection"
          class="mb-3 rounded-lg">
          <v-card-text>
            <v-row>
              <v-col cols="12" md="4">
                <v-text-field v-model="sample.pretreatment" density="compact" label="Pretreatment" hide-details="auto" />
              </v-col>
              <v-col cols="12" md="4">
                <v-text-field v-model="sample.production" density="compact" label="Production" hide-details="auto" />
              </v-col>
              <v-col cols="12" md="4">
                <v-text-field v-model="sample.desinfection" density="compact" label="Desinfection" hide-details="auto" />
              </v-col>
            </v-row>
            <v-row class="pt-0 mt-0">
              <v-col cols="12" md="3">
                <v-text-field v-model="sample.taste" density="compact" label="Taste" hide-details="auto" />
              </v-col>
              <v-col cols="12" md="3">
                <v-text-field v-model="sample.smell" density="compact" label="Smell" hide-details="auto" />
              </v-col>
              <v-col cols="12" md="3">
                <v-text-field v-model="sample.color" density="compact" label="Color" hide-details="auto" />
              </v-col>
              <v-col cols="12" md="3">
                <v-text-field v-model="sample.temperature" density="compact" label="Temperature" hide-details="auto" />
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
        <!-- Conclusion -->
        <v-card v-if="sample.type === 'Monthly Test' || sample.type === 'WQ Alert'" prepend-icon="mdi-dna"
          title="Conclusion" class="mb-3 rounded-lg">
          <v-card-text>
            <v-row>
              <v-col cols="12" md="3">
                <v-select v-model="sample.safe" :items="['yes', 'no']" density="compact" label="Safe drinking water"
                  hide-details="auto" required />
              </v-col>
              <v-col cols="12" md="3">
                <!-- <v-text-field v-model="sample.root_cause" density="compact" label="Root cause" hide-details="auto" /> -->
                <v-select v-model="sample.root_cause" label="Root cause" density="compact" hide-details="auto"
                  :items="['Water Pretreatment to be improved', 'Entrepreneur Operating procedure', 'Technical issues', 'Chlorine managment', 'Sampling methodology and transportation', 'Others']" />
              </v-col>
              <v-col cols="12" md="3">
                <!-- <v-text-field v-model="sample.action_done" density="compact" label="Action done" hide-details="auto" /> -->
                <v-select v-model="sample.action_done" label="Action done" density="compact" hide-details="auto"
                  :items="['Yes', 'No']" />
              </v-col>
              <v-col cols="12" md="3">
                <v-select v-model="sample.email_alert"
                  :items="[{ title: 'yes', value: true }, { title: 'no', value: false }]" density="compact"
                  label="Email alert" hide-details="auto" />
              </v-col>
            </v-row>
            <v-row class="mt-0 pt-0">
              <v-col cols="12" md="12">
                <v-textarea v-model="sample.comment" density="compact" rows="2" label="Notes / Comments"
                  hide-details="auto" required />
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
        <!-- Sokha judgement -->
        <v-card v-if="(sample.type === 'Site_Selection' || sample.type == 'Site_Opening' || sample.type === 'Site_Intervention') &&
      (email == 'borin.t@teuksaat1001.com' || email == 'chamnap.keo@teuksaat1001.com' || email == 'amandine.chaussinand@teuksaat1001.com'
      || email == 'amandine.chaussinand@1001fontaines.com')"
          prepend-icon="mdi-card-account-details-outline" title="Final Judgement" class="mb-3 rounded-lg">
          <v-card-text>
            <v-row>
              <v-col cols="12" md="6">
                <v-text-field v-model="sample.site_open_comment" type="text" density="compact" label="Comment"
                  hide-details="auto" />
              </v-col>
              <v-col cols="12" md="6">
                <v-text-field v-model="sample.site_open_judgement" type="text" density="compact" label="Judgement"
                  hide-details="auto" />
              </v-col>
            </v-row>
            <v-row>
              <v-col cols="12" md="9">
                <v-text-field v-model="sample.site_open_solution" type="text" density="compact" label="Solution"
                  hide-details="auto" />
              </v-col>
              <v-col cols="12" md="3">
                <v-select v-model="sample.site_open_final_judgement" label="Final Judgement" density="compact"
                  hide-details="auto" :items="['', 'Acceptable', 'Reject', 'Optional']" />
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
        <!-- Save and cancel-->
        <v-row v-if="hasError" justify="center" class="my-0">
          <v-alert density="compact" type="error" title="Missing data" text="There is missing data in your form" />
        </v-row>
        <v-row class="ma-2" justify="center">
          <v-btn prepend-icon="mdi-cancel" rounded="lg" color="error" class="ma-4" size="large" @click="$emit('cancel-modal')">
            Cancel
          </v-btn>
          <v-btn prepend-icon="mdi-content-save" rounded="lg" color="primary" class="ma-4" size="large" type="submit">
            Save
          </v-btn>
        </v-row>
      </v-container>
    </v-form>
    <div v-if="loading" class="d-flex justify-center mt-10">
      <v-progress-circular indeterminate :size="80" color="primary" />
    </div>
  </template>
  
  <script>
  
  export default {
    name: 'SampleForm',
    props: {
      getData: {
      type: Number,
      default: 0 // Or any default value you prefer
    } 
  },
  emits: ['site-saved', 'cancel-modal'],
    data: function () {
      return {
        loading: true,
        sites: [],
        dialog: false,
        checkCode: false,
        email: '',
        physicos: [
          { code: 'ph', label: 'pH', interval: '6.5 < N < 9', pt: '' },
          { code: 'turbidity', label: 'Turbidity', interval: 'N ≤ 2', pt: '' },
          { code: 'conductivity', label: 'Conductivity', interval: '', pt: '' },
          { code: 'tds', label: 'TDS', interval: '', pt: '' },
          { code: 'chlorine', label: 'Free Chlorine', interval: 'N ≤ 0.1', pt: 'Cl' },
          { code: 'total_chlore', label: 'Total Chlorine', interval: 'N ≤ 0.5', pt: 'Cl' },
          { code: 'chloride', label: 'Chloride', interval: 'N ≤ 250', pt: 'Cl-' },
          { code: 'nitrate', label: 'Nitrate', interval: 'N ≤ 50', pt: 'NO3' },
          { code: 'alkalinity', label: 'Alkalinity', interval: 'N ≤ 3', pt: '' },
          { code: 'nitrite', label: 'Nitrite', interval: '', pt: 'NO2' },
          { code: 'amonia', label: 'Amonia', interval: 'N ≤ 0.5', pt: 'NH3' },
          { code: 'silver', label: 'Silver', interval: 'N ≤ 0.1', pt: 'Ag' },
          { code: 'aluminium', label: 'Aluminium', interval: 'N ≤ 0.2', pt: 'Al' },
          { code: 'iron', label: 'Iron', interval: 'N ≤ 0.3', pt: 'Fe' },
          { code: 'sulfates', label: 'Sulfates', interval: '', pt: '' },
          { code: 'manganese', label: 'Manganese', interval: 'N ≤ 0.1', pt: 'Mn' },
          { code: 'arsenic', label: 'Arsenic', interval: 'N ≤ 0.05', pt: 'As' },
          { code: 'fluoride', label: 'Fluorides', interval: 'N ≤ 1.5', pt: 'F' },
          { code: 'calcium', label: 'Calcium', interval: '', pt: 'Ca' },
          { code: 'hardness', label: 'Total hardness', interval: 'N ≤ 300', pt: '' }
        ],
        sample: {
          id: undefined,
          site: undefined,
          site_open_sample_type: "",
          site_open_description: "",
          site_open_sample_by: "",
          site_open_final_judgement: "",
          site_open_comment: "",
          site_open_judgement: "",
          site_open_solution: "",
          site_open_sample_date: new Date().toJSON().slice(0, 10),
          sample_date: new Date().toJSON().slice(0, 10),
          received_date: new Date().toJSON().slice(0, 10),
          analysis_date: new Date().toJSON().slice(0, 10),
          sample_code: 0,
          delay: 0,
          type: 'Monthly Test',
          test_number: 'first',
          response_date: new Date().toJSON().slice(0, 10),
          total_coliform: "",
          escherichia: "",
          contamination_level_machine: null,
          escherichia_bottle: "",
          total_coliform_bottle: "",
          contamination_level_bottle: null,
          picture: []
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
      delay() {
        let ms = new Date(this.sample.received_date).getTime() - new Date(this.sample.sample_date).getTime()
        return Math.ceil(ms / (1000 * 3600 * 24));
      }
    },
    watch: {
      "sample.escherichia": function () {
        this.sample.contamination_level_machine = this.calculateContamination(this.sample.escherichia, this.sample.total_coliform)
      },
      "sample.total_coliform": function () {
        this.sample.contamination_level_machine = this.calculateContamination(this.sample.escherichia, this.sample.total_coliform)
      },
      "sample.escherichia_bottle": function () {
        this.sample.contamination_level_bottle = this.calculateContamination(this.sample.escherichia_bottle, this.sample.total_coliform_bottle)
      },
      "sample.total_coliform_bottle": function () {
        this.sample.contamination_level_bottle = this.calculateContamination(this.sample.escherichia_bottle, this.sample.total_coliform_bottle)
      },
      "sample.contamination_level_bottle": function () {
        this.updateSafeAndComment()
      },
      "sample.contamination_level_machine": function () {
        this.updateSafeAndComment()
      },
      delay: function (newval) {
        this.sample.delay = newval
      },
      "sample.type": function (newval) {
        if (newval == 'Monthly Test') {
          this.sample.test_number = 'first'
        }
        else if (newval == 'Site_Opening') {
          this.sample.test_number = 'Site_Opening'
        }
        else if (newval == 'Site_Selection') {
          this.sample.test_number = 'Site_Selection'
          // if (!this.$route.params.id) {
          //   window.axios.get("/api/getSampleCode").then(response => {
          //     // console.log(response.data[0].sample_code)
          //     if (response.data[0].sample_code != undefined) {
          //       this.sample.sample_code = response.data[0].sample_code + 1
          //       this.checkCode = true;
          //     }
          //     else {
          //       this.sample.sample_code = 1;
          //       this.checkCode = false;
          //     }
  
          //   })
          // }
        }
        else {
          this.sample.test_number = 'second'
        }
        //this.sample.test_number = (newval === 'Monthly Test') ? 'first' : 'second'
      },
    },
    unmounted() {
      document.body.classList.remove('bg-grey-lighten-1')
    },
    closeDialog() {
    this.dialog = false;
      },
    mounted() {
       
          
      document.body.classList.add('bg-grey-lighten-1')
      const requests = []
      if (this.$route.params.id ) {
        requests.push(window.axios.get("/api/samples/" + this.$route.params.id).then(response => {
          this.sample = response.data.samples;
          //this.sample_code = response.data.samples.id
          this.email = response.data.email;
          console.log("email is update :" +this.email)
          // this.sample.type = ['second', 'third', 'corrective action','site_opening'].includes(response.data.test_number) ? 'WQ Alert' : 'Monthly Test';
          this.sample.email_alert = response.data.samples.email_alert === "yes" ? true : false;
        }))
      }
      else{
        requests.push(window.axios.get("/api/samples/" + this.getData).then(response => {
          this.sample = response.data.samples;
          //this.sample_code = response.data.samples.id
          this.email = response.data.email;
          console.log("email is add :" +this.email)
          // this.sample.type = ['second', 'third', 'corrective action','site_opening'].includes(response.data.test_number) ? 'WQ Alert' : 'Monthly Test';
          this.sample.email_alert = response.data.samples.email_alert === "yes" ? true : false;
        }))
      }
      requests.push(window.axios.get("/api/sites").then(response => {
        this.sites = response.data.reduce(function (map, obj) {
          map[obj.Id_Site] = obj.Advisor;
          return map;
        }, {});
      }))
      window.axios.all(requests).then(() => this.loading = false)
    },
    methods: {
      handleFileChange(event) {
        const files = event.target.files;
        this.sample.picture = Array.from(files);
      },
      saveSample(validationEvent) {
        this.hasError = false;
        validationEvent.then(result => {
          if (result.valid === true) {
            this.loading = true;
            if (!this.sample.id) {
              let formData = new FormData();
              formData.append('sample', JSON.stringify(this.sample));
              this.sample.picture.forEach((image) => formData.append('images[]', image));
              window.axios.post("/api/samples", formData, {
                headers: {
                  'Content-Type': 'multipart/form-data'
                }
              }).then(() => {
                this.$router.go(-1)
              }).catch(() => {
                this.loading = false;
                this.hasError = true;
              })
            }
            else {
              window.axios.put("/api/samples/" + this.sample.id, this.sample).then(() => {
                this.$emit('cancel-modal');
                this.dialog =false;
                if (this.sample.type == "Monthly Test" || this.sample.type == "WQ Alert") {
                  this.$router.push({ path: '/quality' })
                }
                else {
                  this.$router.push({ path: '/quality/siteOpening' })
                }
                this.loading = false;
                this.dialog= false;
                //this.$router.go(-1)
              }).catch(() => {
                this.loading = false;
                this.hasError = true;
              })
            }
          }
          else {
            this.hasError = true;
          }
        })
      },
      calculateContamination(escherichia, coliform) {
        if (escherichia == "TNTC" || parseInt(escherichia) > 0) {
          return "3";
        }
        else if (coliform == "TNTC" || parseInt(coliform) >= 20) {
          return "2";
        }
        else if (parseInt(coliform) > 0) {
          return "1";
        }
        else if (coliform == "" || escherichia == "") {
          return null
        }
        return "0";
      },
      updateSafeAndComment() {
        if (this.sample.contamination_level_bottle == "" || this.sample.contamination_level_machine == "") {
          this.sample.safe = ""
          this.sample.comment = "";
        }
        else if (this.sample.contamination_level_bottle > 0 || this.sample.contamination_level_machine > 0) {
          this.sample.safe = "no";
          this.sample.comment = "(ទឹកមិនមានសុវត្ថិភាព (សូមរៀនរៀបចំសម្លាប់មេរោគម៉ាស៊ីន និង ប៊ីដុងសាជាថ្មី)";
        }
        else {
          this.sample.safe = "yes";
          this.sample.comment = "ទឹកមានសុវត្ថិភាព";
        }
      }
    }
  }
  </script>
  