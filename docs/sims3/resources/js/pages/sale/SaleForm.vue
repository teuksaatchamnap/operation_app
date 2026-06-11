<template>
    <v-form v-if="!loading" class="bg-grey-lighten-1 pa-4" @submit.prevent="saveSaleRecord">
      <v-container>
        <!-- Type -->
        <v-card prepend-icon="mdi-chemical-weapon" title="ពត័មានការលក់" class="mb-3 rounded-lg">
          <v-card-text>
            <v-row>
              <v-col cols="12" md="3">
                <v-text-field v-model="sale.site" type="text" density="compact" label="ទីតាំង"
                  hide-details="auto" />
              </v-col>
              <v-col cols="12" md="3">
                <v-text-field v-model="sale.sale_date" type="date" density="compact" label="កាលបរិច្ឆេទ"
                  hide-details="auto" />
              </v-col>
              <v-col cols="12" md="3">
                <v-text-field v-model="sale.customer" type="text" density="compact" label="ឈ្មោះអតិថិជន"
                  hide-details="auto" />
              </v-col>
              <v-col cols="12" md="3">
                <v-select v-model="sale.sex" label="ភេទ" density="compact" hide-details="auto"
                    :items="['male','female']" />
              </v-col>
            </v-row>
  
            <v-row>
              <v-col cols="12" md="3">
                <v-select v-model="sale.customer_type" label="ប្រភេទអតិថិជន" density="compact" hide-details="auto"
                    :items="['home_usage','shopkeeper','kisok']" />
              </v-col>
              <v-col cols="12" md="3">
                <v-text-field v-model="sale.village" type="text" density="compact" label="ឈ្មោះភូមិ"
                  hide-details="auto" />
              </v-col>
              <v-col cols="12" md="3">
                <v-text-field v-model="sale.contact" type="text" density="compact" label="លេខទំនាក់ទំនង"
                  hide-details="auto" />
                  
              </v-col>
              <v-col cols="12" md="3">
                <v-select v-model="sale.delivery_status" label="បានដឹកដល់ផ្ទះអតិថិជន" density="compact" hide-details="auto"
                    :items="['Yes','No']" />
              </v-col>
            </v-row>
            <v-row>
              <v-col cols="12" md="3">
                <v-select v-model="sale.payment_type" label="ប្រភេទការទូទាត់លុយ" density="compact" hide-details="auto"
                    :items="['pay_by_cash','ជំបាក់']" />
              </v-col>
              <v-col cols="12" md="3">
                <v-select v-model="sale.sale_type" label="ប្រភេទលក់" density="compact" hide-details="auto"
                    :items="['sale_intervention','opening_site']" />
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
         <!-- Info about Sell Record -->
        <v-card prepend-icon="mdi-chemical-weapon" title="របាយការណ័លក់" class="mb-3 rounded-lg">
          <v-card-text>
            <v-row>
              <v-col cols="12" md="3">
                <v-select v-model="sale.sale_officer1" label="អ្នកលក់ទី១" density="compact" hide-details="auto"
                    :items="['Phann Sophea','Touch Chanly','Dok Keun','Kul Chandet','Chey Simon','Kao Dolla','Chee Rathana','Ly Eang']" />
              </v-col>
              <v-col cols="12" md="3">
                <v-select v-model="sale.sale_officer2" label="អ្នកលក់ទី២" density="compact" hide-details="auto"
                :items="['Phann Sophea','Touch Chanly','Dok Keun','Kul Chandet','Chey Simon','Kao Dolla','Chee Rathana','Ly Eang']" />
              </v-col>
              <v-col cols="12" md="3">
                <v-select v-model="sale.sale_officer3" label="អ្នកលក់ទី៣" density="compact" hide-details="auto"
                    :items="['Phann Sophea','Touch Chanly','Dok Keun','Kul Chandet','Chey Simon','Kao Dolla','Chee Rathana','Ly Eang']" />
              </v-col>
              <v-col cols="12" md="3">
                <v-select v-model="sale.sale_officer4" label="អ្នកលក់ទី៤" density="compact" hide-details="auto"
                :items="['Phann Sophea','Touch Chanly','Dok Keun','Kul Chandet','Chey Simon','Kao Dolla','Chee Rathana','Ly Eang']" />
              </v-col>
            </v-row>
            <v-row>
              <v-col cols="12" md="2">
                <v-text-field v-model="sale.free" type="number" density="compact" label="ចំនួនចែកទទេ"
                  hide-details="auto" />
              </v-col>
              <v-col cols="12" md="2">
                <v-text-field v-model="sale.new_bottle" type="number" density="compact" label="អតិថិជនថ្មីទិញទឹក"
                  hide-details="auto" />
              </v-col>
              <v-col cols="12" md="2">
                <v-text-field v-model="sale.lending_bottle" type="number" density="compact" label="ប៊ីដុងខ្ចី"
                  hide-details="auto" />
              </v-col>
              <v-col cols="12" md="2">
                <v-text-field v-model="sale.refill" type="number" density="compact" label="អតិថិជនប្តូរទឹក"
                  hide-details="auto" />
              </v-col>
              <v-col cols="12" md="2">
                <v-text-field v-model="sale.total_bottle_sell" type="number" density="compact" label="សរុបតំលៃលក់ប៊ីដុង"
                  hide-details="auto" />
              </v-col>
            </v-row>
            <v-row>
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
        sale:{
          id:'',
          site:'',
          sale_date:new Date().toJSON().slice(0, 10),
          customer:'',
          sex:'',
          customer_type:'',
          village:'',
          contact:'',
          sale_officer1:'',
          sale_officer2:'',
           delivery_status:'',
           payment_type:'',
           free:0,
           new_bottle:0,
           refill:0,
           price_refill:0,
           price_new_bottle:0,
           total_bottle_sell:0,
           total_revenue:0,
           total_refill_sell:0,
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
              axios.get("/api/saleRecord/search/" + this.$route.params.id).then(response => {
                   this.loading = false
                   this.sale = response.data;
                  console.log("ID :" + response.data)
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
              window.axios.put("/api/saleRecord/update/" + this.$route.params.id, this.sale).then(response => {
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
  
  