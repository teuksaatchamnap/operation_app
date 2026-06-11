<template>
    <v-form v-if="!loading" class="bg-grey-lighten-1 pa-4" @submit.prevent="saveSaleRecord">
      <v-container>
        <!-- Type -->
        <v-card prepend-icon="mdi-chemical-weapon" title="ពត័មានការលក់" class="mb-3 rounded-lg">
          <v-card-text>
            <v-row>
              <v-col cols="12" md="3">
                <v-text-field v-model="entrepreneur.Id_Site" type="text" density="compact" label="Site"
                  hide-details="auto" />
              </v-col>
               <v-col cols="12" md="3">
                <v-text-field v-model="entrepreneur.Entrepreneur_English_name" type="text" density="compact" label="Entrepreneur_English_name"
                  hide-details="auto" />
              </v-col>
               <v-col cols="12" md="3">
                <v-text-field v-model="entrepreneur.Entrepreneur_Khmer_name" type="text" density="compact" label="Entrepreneur_Khmer_name"
                  hide-details="auto" />
              </v-col>
               <v-col cols="12" md="3">
                <v-select v-model="entrepreneur.Sex" label="Sex" density="compact" hide-details="auto"
                    :items="['male','female']" />
              </v-col>
            </v-row>
  
            <v-row>
              <v-col cols="12" md="2">
                <v-text-field v-model="entrepreneur.Working_Date" type="date" density="compact" label="Working_Date"
                  hide-details="auto" />
              </v-col>
              <v-col cols="12" md="2">
                <v-text-field v-model="entrepreneur.Entrepreneur_Phone" type="text" density="compact" label="Entrepreneur_Phone"
                  hide-details="auto" />
              </v-col>
              <v-col cols="12" md="2">
                <v-text-field v-model="entrepreneur.Education" type="text" density="compact" label="Education"
                  hide-details="auto" />
              </v-col>
              <v-col cols="12" md="2">
                <v-text-field v-model="entrepreneur.Previous_Job" type="text" density="compact" label="Previous_Job"
                  hide-details="auto" />
              </v-col>
              <v-col cols="12" md="3">
                  <v-select v-model="entrepreneur.Status_Entrepreneur" label="Status_Entrepreneur" density="compact" hide-details="auto"
                    :items="['active','not active']" />
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
         <!-- Info about Sell Record -->
        <v-row class="ma-2" justify="center">
          <v-btn prepend-icon="mdi-cancel" rounded="lg" color="error" class="ma-4" size="large" @click="$router.go(-1)">
            Cancel
          </v-btn>
          <!-- <v-btn prepend-icon="mdi-content-delete" rounded="lg" color="secondary" class="ma-4" size="large" @click="$router.go(-1)">
            Delete
          </v-btn> -->
          <v-btn prepend-icon="mdi-content-save" rounded="lg" color="primary" class="ma-4" size="large" type="submit">
            Save
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
    name: 'EnForm',
    data: function () {
      return {
        loading: false,
        entrepreneur:{
          id:'',
          Id_Site:'',
          Working_Date:new Date().toJSON().slice(0, 10),
          Platform:'',
          Sex:'',
          Entrepreneur_English_name:'',
          Entrepreneur_Khmer_name:'',
          Entrepreneur_Phone:'',
          Education:'',
          Previous_Job:'',
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
              axios.get("/api/entrepreneurForm/" + this.$route.params.id).then(response => {
                   this.loading = false
                   this.entrepreneur = response.data.data;
                   console.log(this.entrepreneur)
              }).catch(() => {
                  this.loading = false;
                  this.hasError = true;
              })
          }
    },
    methods: {
      saveSaleRecord(validationEvent) 
      {
        this.hasError = false;
        validationEvent.then(result => {
          if (result.valid === true) {
            this.loading = true; 
              window.axios.put("/api/entrepreneur/update/" + this.$route.params.id, this.entrepreneur).then(response => {
                
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
  
  