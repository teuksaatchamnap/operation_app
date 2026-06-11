<template>
  <v-form @submit.prevent="saveSite">
    <v-tabs v-model="tab" class="rounded-t-xl" bg-color="white" align-tabs="center">
      <v-tab v-for="category in Object.keys(columnsMapping)" :key="category" :value="category">
        {{ category }}
      </v-tab>
    </v-tabs>
    <!-- Form -->
    <v-card v-if="editedSite" height="650px" :loading="loading" class="rounded-t-0 rounded-b-xl">
      <v-card-text class="d-flex flex-column justify-start">
        <v-row class="flex-grow-0">
          <v-col cols="12" md="2">
            <v-text-field v-model="editedSite.Id_Site" density="compact" :readonly="!!site.Id_Site" label="Site"
              hide-details="auto" :rules="required" />
          </v-col>
          <v-col cols="12" md="2">
            <v-select v-model="editedSite.Platform" :items="['', 'BTB', 'SR', 'KSP', 'PP', 'KC', 'Dead']" density="compact"
              label="Platform" hide-details="auto" :rules="required" />
          </v-col>
          <v-col cols="12" md="2">
            <v-select v-model="editedSite.Last_Tier" :items="tiers" density="compact" label="Last tier"
              hide-details="auto" />
          </v-col>
          <v-col cols="12" md="3">
            <v-select v-model="editedSite.technician_site" label="Technician" density="compact" hide-details="auto"
              :items="['veasna.r@teuksaat1001.com', 'phalla.p@teuksaat1001.com', 'phanith.m@teuksaat1001.com', 'odom.p@teuksaat1001.com', 'bros.t@teuksaat1001.com'
                , 'vuthy.n@teuksaat1001.com', 'pisak.m@teuksaat1001.com', 'dara.s@teuksaat1001.com', 'darith.s@teuksaat1001.com', 'sak.s@teuksaat1001.com',
                'theary.m@teuksaat1001.com','chanthan.m@teuksaat1001.com','sopheap.k@teuksaat1001.com','vichet.h@teuksaat1001.com','leab.l@teuksaat1001.com']" />
          </v-col>
          <v-col cols="12" md="3">
            <v-select v-model="editedSite.Advisor_email" label="Advisor" density="compact" hide-details="auto" 
            :items="advisorList" />
          </v-col>

        </v-row>
        <v-row class="flex-grow-0">
          
          <!-- <v-col cols="12" md="2">
            <v-text-field v-model="editedSite.Project_Date" type="date" density="compact" label="Project Start Date"
              hide-details="auto" />
          </v-col>
          <v-col cols="12" md="2">
            <v-text-field v-model="editedSite.Platform_Date" type="date" density="compact" label="Project End Date"
              hide-details="auto" readonly="" />
          </v-col>
          <v-col cols="12" md="2">
            <v-select v-model="editedSite.Move_Site" label="Move Site" density="compact" hide-details="auto"
              :items="move_site" />
          </v-col> -->
          <v-col v-for="property in columnsMapping[tab]" :key="property" cols="12" md="3">
            <v-text-field v-model="editedSite[property]" density="compact" :key="item" :label="property"
              :type="property.toLowerCase().includes('date') || property.includes('ProjectAgreement') || property.includes('Date_of_birth') ? 'date' : 'text'"
              hide-details="auto" />
          </v-col>
        </v-row>
        <div class="mt-auto align-end w-100 d-flex justify-center">
          <v-btn prepend-icon="mdi-cancel" rounded="lg" color="error" class="ma-4" @click="$emit('cancel-modal')">
            Cancel
          </v-btn>
          <v-btn v-if="$store.state.user.permissions.includes('site_edit')" prepend-icon="mdi-content-save" rounded="lg"
            color="primary" class="ma-4" type="submit">
            Save
          </v-btn>
        </div>
      </v-card-text>
    </v-card>
  </v-form>
</template>

<script>

export default {
  name: 'SiteForm',
  props: {
    site: {
      type: Object,
      required: true,
    },
  },
  emits: ['site-saved', 'cancel-modal'],
  data: function () {
    return {
      editedSite: {
        Project_Date: new Date().toJSON().slice(0, 10),
      },
      loading: false,
      advisorList: [],
      platforms: [],
      files: [],
      tab: "id",
      hasError: false,
      move_site: ['Project', 'Operation'],
      tiers: ["ST1", "1", "2", "3", "New", "Reopen", "Closed", "Dead"],
      columnsMapping: {
        "id": ["Advisor", "Khmer_advisor", "Old_Platform"],
        // "address": ["Code_Village", "Village", "Village_khmer", "Code_Commune", "Commune", "Commune_khmer", "Code_District", "District", "District_khmer", "Code_Province", "Province", "Province_khmer", "Latitude", "Longitude"],
        "address": ["Code_Village", "Village", "Village_khmer", "Commune", "Commune_khmer", "District", "District_khmer", "Code_Province", "Province", "Province_khmer", "Latitude", "Longitude"],
        //"project": ["ProjectAgreement", "Wave", "Sale_Starting_Date", "Funder_1", "Funder_2", "Funder_3", "Building_cost"],
        "project": ["ProjectAgreement", "Wave", "Funder_1", "Funder_2", "Funder_3"],
        // "demography": [
        //   "Number_Village", "Number_Family", "Number_Households", "Number_Population", "Number_Women", "Number_Migration",
        //   "Number_Village_5km", "Number_Family_5km", "Number_Households_5km", "Number_Population_5km", "Number_Women_5km", "Number_Migration_5km",

        // ],
        "demography": [
          "Number_Village", "Number_Family", "Number_Population", "Number_Population_5km"
        ],
        "infrastructure": ["Number_Pagoda", "Number_Primary_School", "Land_of_kiosk", "Road_Leading_to_Kiosk", "Paved_Asphalt_Road", "Concrete_Road", "Laterite_Road", "White_Soiled_Road"],
        //"economic": ["Monthly_Income_Average_per_Person", "Labour_Market", "Monthly_Income_Average_per_Worker"],
        "technical": [
          "Water_Source", "Well_Pond_Ownership", "Depth_Well_Pond", "Water_Source_Distance_From_Kiosk",
          "Second_Water_Source", "Well_Pond_Ownership_Second_Source", "Depth_Well_Pond_Second_Source", "Water_Source_Distance_From_Kiosk_Second_Source",
          "Main_Power_Source", "Second_Power_Source", "Type_of_Water_Tank"
        ],
        // "entrepreneur": ["Entrepreneur_English_Name", "Entrepreneur_Khmer_Name", "Sex", "Commune_Entrepreneur", "Province_Entrepreneur", "Date_of_birth", "Date_start_working", "Phone_Number",
        //   "Education", "Previous_Job", "Resignation", "Generation", "Education_Background", "Part_Time_Job", "ID_Number", "Reading", "Writing", "Calculating", "Why_working_as_entrepreneur"],
        "entrepreneur": ["Entrepreneur_English_Name", "Entrepreneur_Khmer_Name", "Sex", "Commune_Entrepreneur", "Province_Entrepreneur", "Date_of_birth", "Date_start_working", "Phone_Number",
          "Education", "Previous_Job", "Resignation", "Education_Background", "Part_Time_Job", "ID_Number", "Reading", "Writing", "Calculating", "Why_working_as_entrepreneur"],
      },
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
    "editedSite.Project_Date": function () {
      if (this.editedSite.Project_Date) {
        const newDate = new Date(this.editedSite.Project_Date);
        newDate.setDate(newDate.getDate() + 90);
        this.editedSite.Platform_Date = newDate.toISOString().substring(0, 10);
      }
    },
  },
  unmounted() {
  },
  mounted() {
    this.editedSite = { ...this.site };
    for (const col of Object.keys(this.columnsMapping)) {
      for (const property of this.columnsMapping[col]) {
        if ((property.toLowerCase().includes('date') || property.includes('ProjectAgreement') || property.includes('Date_of_birth')) && this.editedSite[property]) {
          this.editedSite[property] = this.editedSite[property].substring(0, 10);
        }
      }
    }

    window.axios.get("/api/configurations?app=site").then(response => {
      this.platforms = JSON.parse(response.data.find(c => c.name == 'platform').value)
    });
    window.axios.get("/api/advisorsEmail").then(response => {
      this.advisorList = response.data.map(advisor => advisor.email);
      console.log("user :", this.advisorList);
      // Update the v-select items dynamically if needed
    });
  },
  methods: {
    handleFileChange(event) {
      this.files = Array.from(event.target.files);
    },
    saveSite(validationEvent) {
      this.hasError = false;
      validationEvent.then(result => {
        if (result.valid === true) {
          this.loading = true;
          if (!this.site.Id_Site) {
            let formData = new FormData();
            formData.append('data', JSON.stringify(this.editedSite));
            window.axios.post("/api/sites", formData, {
              headers: {
                'Content-Type': 'multipart/form-data'
              }
            }).then(() => {
              this.$emit('site-saved');
            }).catch(() => {
              this.loading = false;
              this.hasError = true;
            })
          }
          else {
            let formData = new FormData();
            formData.append('_method', 'PUT');
            formData.append('data', JSON.stringify(this.editedSite));
            window.axios.post("/api/sites/update/" + this.editedSite.Id_Site, formData, {
              headers: {
                'Content-Type': 'multipart/form-data'
              }
            }).then(() => {
              this.$emit('site-saved');
            }).catch(() => {
              this.loading = false;
              this.hasError = true;
            })
          }
        } else {
          this.hasError = true;
        }
      })
    },
  }
}
</script>
