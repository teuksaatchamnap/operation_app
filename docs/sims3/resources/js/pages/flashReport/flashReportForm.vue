<template>
    <v-form v-if="!loading" class="bg-grey-lighten-1 pa-4" @submit.prevent="saveFlashReport">
      <v-container>
        <!-- Type -->
        <v-card prepend-icon="mdi-chemical-weapon" title="Flash Report" class="mb-3 rounded-lg">
          <v-card-text>
            <v-row>
              <v-col cols="12" md="3">
                <v-text-field v-model="school.Id_Site" type="text" density="compact" label="Site"
                  hide-details="auto" />
              </v-col>
              <v-col cols="12" md="3">
                <v-text-field v-model="school.Month" type="date" density="compact" label="Date"
                  hide-details="auto" />
              </v-col>
              <v-col cols="12" md="3">
                <v-text-field v-model="school.Number_jugs_village" type="text" density="compact" label="Bottle Sell In Village"
                  hide-details="auto" />
              </v-col>
              <v-col cols="12" md="3">
                <v-text-field v-model="school.Number_jugs_school" type="text" density="compact" label="Bottle At School"
                  hide-details="auto" />
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
        <v-row class="ma-2" justify="center">
          <v-btn prepend-icon="mdi-cancel" rounded="lg" color="error" class="ma-4" size="large" @click="$router.go(-1)">
            Cancel
          </v-btn>
          <!-- <v-btn prepend-icon="mdi-content-delete" rounded="lg" color="secondary" class="ma-4" size="large" @click="$router.go(-1)">
            Delete
          </v-btn> -->
          <!-- <v-btn prepend-icon="mdi-content-save" rounded="lg" color="primary" class="ma-4" size="large" type="submit">
            Save
          </v-btn> -->
        </v-row>
      </v-container>
    </v-form>
    <div v-if="loading" class="d-flex justify-center mt-10">
      <v-progress-circular indeterminate :size="60" color="primary" />
    </div>
  </template>
  
  <script>
  
  export default {
    name: 'SaleRecord',
    data: function () {
      return {
        loading: false,
        school:{
          Code_Flash_report:'',
          Id_Site:'',
          Number_jugs_village:0,
          Number_jugs_school:0,
          Month:new Date().toJSON().slice(0, 10),
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
      
    },
    unmounted() {
    
    },
    mounted() {
      if (this.$route.params.id) {
              axios.get("/api/flashReport/form/" + this.$route.params.id).then(response => {
                   this.loading = false
                   this.school = response.data;
                   
                   //this.school.academy_start= start.toISOString().slice(0, 10);
              })
          }
    },
    methods: {
      saveFlashReport(validationEvent) 
      {
        this.hasError = false;
        validationEvent.then(result => {
          if (result.valid === true) {
            this.loading = true; 
              window.axios.put("/api/flashReport/update/" + this.$route.params.id, this.school).then(response => {
                console.log(response.data)
                this.$router.go(-1)
              }).catch(() => {
                this.loading = false;
                this.hasError = true;
              })
          }
         else {
            this.hasError = true;
          }
        })
      },
    }
  }
  </script>
  
  