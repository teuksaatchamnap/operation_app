<template>
  <v-form v-if="!loading" class="bg-grey-lighten-1 pa-4" @submit.prevent="saveKOL">
    <v-container>
      <!-- Type -->
      <v-card prepend-icon="mdi-chemical-weapon" title="ការរៀបចំការប្រជុំ KOL​ មុនបើកស្ថានីយផលិតទឹក" class="mb-3 rounded-lg">
        <v-card-text>
          <v-row>
            <v-col cols="12" md="3">
              <v-text-field v-model="kol.site" type="text" density="compact" label="ទីតាំង"
                hide-details="auto" />
            </v-col>
            <v-col cols="12" md="3">
              <v-text-field v-model="kol.record_date" type="date" density="compact" label="កាលបរិច្ឆេទ"
                hide-details="auto" />
            </v-col>
            <v-col cols="12" md="3">
              <v-text-field v-model="kol.village" type="text" density="compact" label="ឈ្មោះភូមិ"
                hide-details="auto" />
            </v-col>
            <v-col cols="12" md="3">
              <v-text-field v-model="kol.chief_village" type="text" density="compact" label="ឈ្មោះរបស់មេភូមិ"
                hide-details="auto" />
            </v-col>
          </v-row>

          <v-row>
            <v-col cols="12" md="3">
              <v-text-field v-model="kol.chief_village_contact" type="text" density="compact" label="លេខទំនាក់ទំនងរបស់មេភូមិ"
                hide-details="auto" />
            </v-col>
            <v-col cols="12" md="3">
              <v-text-field v-model="kol.total_houses" type="number" density="compact" label="ចំនួនខ្នងផ្ទះ"
                hide-details="auto" />
            </v-col>
            <v-col cols="12" md="3">
              <v-text-field v-model="kol.total_household" type="number" density="compact" label="ចំនួនគ្រួសារ"
                hide-details="auto" />
            </v-col>
            <v-col cols="12" md="3">
              <v-text-field v-model="kol.distance" type="number" density="compact" label="រយៈចំងាយនៃភូមិពីសាលាឃុំ"
                hide-details="auto" />
            </v-col>
          </v-row>
          <v-row>
            <v-col cols="12" md="3">
              <v-text-field v-model="kol.expectation" type="text" density="compact" label="ការរំពឹងទុកនៃចំណែកទីផ្សារ"
                hide-details="auto" />
            </v-col>
            <v-col cols="12" md="3">
              <v-text-field v-model="kol.actual_market" type="text" density="compact" label="ចំណែទីផ្សារជាក់ស្តែង"
                hide-details="auto" />
            </v-col>
            <v-col cols="12" md="3">
              <v-text-field v-model="kol.market_comparison" type="text" density="compact" label="ការប្រៀបធៀបចំណែកទីផ្សារ"
                hide-details="auto" />
            </v-col>
            <v-col cols="12" md="3">
              <v-text-field v-model="kol.penentration" type="number" density="compact" label="ចំណែកទីផ្សារ/Penetration"
                hide-details="auto" />
            </v-col>
          </v-row>
          <v-row>
            <v-col cols="12" md="12">
              <v-text-field v-model="kol.remark" type="text" density="compact" label="កំណត់សំគាល់​ រឺ សំណើរ"
                hide-details="auto" />
            </v-col>
          </v-row>
        </v-card-text>
      </v-card>
      <v-row class="ma-2" justify="center">
        <v-btn prepend-icon="mdi-cancel" rounded="lg" color="error" class="ma-4" size="large" @click="$router.go(-1)">
          Cancel
        </v-btn>
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
  name: 'KolForm',
  data: function () {
    return {
      loading: false,
      kol:{
        id:'',
        site:'',
        record_date:new Date().toJSON().slice(0, 10),
        village:'',
        chief_village:'',
        chief_village_contact:'',
        total_houses:0,
        total_household:0,
        distance:0,
        expectation:'',
        actual_market:'',
        market_comparison:'',
        remark:'',
        penentration:0
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
    "kol.site":function() {
      return this.kol.site= this.kol.site.toUpperCase();
    }
  },
  unmounted() {
  
  },
  mounted() {
   
    if (this.$route.params.id) {
            axios.get("/api/kol/" + this.$route.params.id).then(response => {
                this.loading = false
                this.kol = response.data;
            })
        }
  },
  methods: {
    saveKOL(validationEvent) {
      this.hasError = false;
      validationEvent.then(result => {
        if (result.valid === true) {
          this.loading = true;
          if (!this.kol.id) {
            window.axios.post("/api/kol", this.kol).then(() => {
              this.$router.go(-1)
            }).catch(() => {
              this.loading = false;
              this.hasError = true;
            })
          } else {
            window.axios.put("/api/kol/" + this.$route.params.id, this.kol).then(() => {
              this.$router.go(-1)
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
  }
}
</script>

