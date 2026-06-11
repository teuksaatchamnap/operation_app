<template>
    <v-form v-if="!loading" class="bg-grey-lighten-1 pa-4" @submit.prevent="saveSaleRecord">
      <v-container>
        <!-- Type -->
        <v-card prepend-icon="mdi-chemical-weapon" title="Entrepreneur Information" class="mb-3 rounded-lg">
          <v-card-text>
            <v-row>
              <v-col cols="12" md="3">
                <v-text-field v-model="school.Id_Site" type="text" density="compact" label="Site"
                  hide-details="auto" />
              </v-col>
              <v-col cols="12" md="3">
                <v-text-field v-model="school.en_name_english" type="text" density="compact" label="Entrepreneur Name English"
                  hide-details="auto" />
              </v-col>
              <v-col cols="12" md="3">
                <v-text-field v-model="school.en_name_khmer" type="text" density="compact" label="Entrepreneur Name Khmer"
                  hide-details="auto" />
              </v-col>
              <v-col cols="12" md="3">
                <v-text-field v-model="school.en_phone_number" type="text" density="compact" label="Phone"
                  hide-details="auto" />
              </v-col>
            </v-row>
            <v-row>
              <v-col cols="12" md="3">
                <v-text-field v-model="school.village_english" type="text" density="compact" label="Village English"
                  hide-details="auto" />
              </v-col>
              <v-col cols="12" md="3">
                <v-text-field v-model="school.village_khmer" type="text" density="compact" label="Village Khmer"
                  hide-details="auto" />
              </v-col>
              <v-col cols="12" md="3">
                <v-text-field v-model="school.commune_english" type="text" density="compact" label="Commune English"
                  hide-details="auto" />
              </v-col>
              <v-col cols="12" md="3">
                <v-text-field v-model="school.commune_khmer" type="text" density="compact" label="Commune Khmer"
                  hide-details="auto" />
              </v-col>
            </v-row>
            <v-row>
              <v-col cols="12" md="12">
                <v-text-field v-model="school.province" type="text" density="compact" label="Province"
                  hide-details="auto" />
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
            <v-card prepend-icon="mdi-chemical-weapon" title="Bottle Provided" class="mb-3 rounded-lg">
              <v-card-text>
            <v-row>
              <v-col cols="12" md="3">
                <v-text-field v-model="school.number_of_classes" type="number" density="compact" label="Number of Classes"
                  hide-details="auto" />
              </v-col>
              <v-col cols="12" md="2">
                <v-text-field v-model="school.bottle_requested_by_school" type="number" density="compact" label="Bottle School Request"
                  hide-details="auto" />
              </v-col>
              <v-col cols="12" md="2">
                <v-text-field v-model="school.bottle_approved" type="number" density="compact" label="Bottle ROM approved"
                  hide-details="auto" />
              </v-col>
              <div v-if="$store.state.user.permissions.includes('md_validatd')" >
                <v-col cols="12" md="3">
                  <!-- <v-select v-model="school.status_bottle" label="Status ROM Approved" density="compact" hide-details="auto" :items="['Ok','Over']"> -->
                  <v-select v-model="school.status" label="MD Approved" density="compact" hide-details="auto" :items="['waiting_validation','validation']" />
                </v-col>
              </div>
            </v-row>
          </v-card-text>
        </v-card>
         <!-- Info about Sell Record -->
        <v-card prepend-icon="mdi-chemical-weapon" title="School Information" class="mb-3 rounded-lg">
          <v-card-text>
            <v-row>
              <v-col cols="12" md="4">
                <v-text-field v-model="school.school_code" type="text" density="compact" label="School Code"
                  hide-details="auto" />
              </v-col>
              <v-col cols="12" md="4">
                <v-text-field v-model="school.school_name_english" type="text" density="compact" label="English School Name"
                  hide-details="auto" />
              </v-col>
              <v-col cols="12" md="4">
                <v-text-field v-model="school.school_name_khmer" type="text" density="compact" label="Khmer School Name"
                  hide-details="auto" />
              </v-col>
              </v-row>
              <v-row>
              <v-col cols="12" md="4">
                <v-text-field v-model="school.school_director_name_english" type="text" density="compact" label="English School Director Name"
                  hide-details="auto" />
              </v-col>
              <v-col cols="12" md="4">
                <v-text-field v-model="school.school_director_name_khmer" type="text" density="compact" label="Khmer School Director Name"
                  hide-details="auto" />
              </v-col>
              <v-col cols="12" md="4">
                <v-text-field v-model="school.school_director_phone_number" type="text" density="compact" label="school_director_phone_number"
                  hide-details="auto" />
              </v-col>
            </v-row>
            <v-row>
              <v-col cols="12" md="3">
                <v-text-field v-model="school.academy_start" type="date" density="compact" label="Academy Start"
                  hide-details="auto" />
              </v-col>
              <v-col cols="12" md="3">
                <v-text-field v-model="school.academy_end" type="date" density="compact" label="Academy End"
                  hide-details="auto" />
              </v-col>
              
              <v-col cols="12" md="3">
                <v-text-field v-model="school.start_grade" type="text" density="compact" label="Start Grade"
                  hide-details="auto" />
              </v-col>
              <v-col cols="12" md="3">
                <v-text-field v-model="school.end_grade" type="number" density="compact" label="End Grade"
                  hide-details="auto" />
              </v-col>
            </v-row>
            <v-row>
              
              <v-col cols="12" md="3">
                <v-text-field v-model="school.number_of_boys" type="number" density="compact" label="number_of_boys"
                  hide-details="auto" />
              </v-col>
              <v-col cols="12" md="3">
                <v-text-field v-model="school.number_of_girls" type="number" density="compact" label="number_of_girls"
                  hide-details="auto" />
              </v-col>
              <v-col cols="12" md="3">
                <v-text-field v-model="school.number_of_children" type="number" density="compact" label="number_of_children"
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
    name: 'SaleRecord',
    data: function () {
      return {
        loading: false,
        school:{
          id:'',
          Id_Site:'',
          en_name_english:'',
          en_name_khmer:'',
          commune_english:'',
          commune_khmer:'',
          school_director_name_english:'',
          school_director_name_khmer:'',
          school_name_english:'',
          school_name_khmer:'',
          number_of_children:0,
          number_of_girls:0,
          number_of_classes:0,
          bottle_requested_by_school:0,
          bottle_number_by_entre:0,
          number_of_children:0,
          number_of_boys:0,
          school_grade:'',
          academy_start:new Date().toJSON().slice(0, 10),
          academy_end:new Date().toJSON().slice(0, 10),
          village_english:'',
          village_khmer:'',
          school_director_phone_number:'',
          school_code:'',
          province:'',
          status:'',
          status_bottle:'',
          bottle_approved:0,
          en_phone_number:'',

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
              axios.get("/api/schoolProgram/search/" + this.$route.params.id).then(response => {
                   this.loading = false
                   this.school = response.data;
                   let end= new Date(response.data.academy_end);
                   let start= new Date(response.data.academy_start);
                   this.school.academy_end= end.toISOString().slice(0, 10);
                   this.school.academy_start= start.toISOString().slice(0, 10);
                  
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
            console.log(this.school)
              window.axios.put("/api/schoolProgram/update/" + this.$route.params.id, this.school).then(response => {
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
  
  