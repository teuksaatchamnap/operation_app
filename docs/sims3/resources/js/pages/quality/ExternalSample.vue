<template>
    <v-form v-if="!loading" class="bg-grey-lighten-1 pa-4" @submit.prevent="saveSaleRecord">
      <v-container>
        <v-card prepend-icon="mdi-chemical-weapon" title="External Sample Test" class="mb-3 rounded-lg">
          <v-card-text>
            <v-row>
              <v-col cols="12" md="3">
                <v-autocomplete v-model="sample.site" label="Site" density="compact" :items="Object.keys(sites)"
                persistent-hint :rules="required" />
              </v-col>
              <v-col cols="12" md="3">
                <v-text-field v-model="sample.test_date" type="date" density="compact" label="Sample Date"
                  hide-details="auto" />
              </v-col>
              <v-col cols="12" md="6">
                <!-- <v-file-input label="Select picture or file to upload"
                v-model="file" variant="outlined" @change="onFileChange"></v-file-input> -->
                <v-file-input v-model="file" variant="outlined" label="Upload File" accept=".jpg,.png,.pdf,.docx,.xlsx"></v-file-input>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
        
        <v-row class="ma-2" justify="center">
          <v-btn prepend-icon="mdi-cancel" rounded="lg" color="error" class="ma-4" size="large" @click="$router.go(-1)">
            Cancel
          </v-btn>
          <v-btn prepend-icon="mdi-content-save" rounded="lg" color="primary" class="ma-4" size="large"  type="submit">
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
    name: 'ExternalSample',
    data: function () {
      return {
        sites: [],
        loading: false,
        sample:{
          site:'',
          test_date:new Date().toJSON().slice(0, 10),
          upload_path:'',
        },
        file: null,
        hasError: false,
        required: [
          value => {
            if (value) return true
            return 'This field is required.'
          },
        ]
      }
    },
    mounted() {
          window.axios.get("/api/sites").then(response => {
            this.sites = response.data.reduce(function (map, obj) {
             map[obj.Id_Site] = obj.Advisor;
            return map;
      }, {});
    })
    },
    methods: {
      // onFileChange(file) {
      //       this.file = file[0];
      //   },
        saveSaleRecord() 
      {
        this.hasError = false;
            let formData = new FormData();
            let fileToUpload = Array.isArray(this.file) ? this.file[0] : this.file;
            formData.append('site', this.sample.site);
            formData.append('test_date', this.sample.test_date);
            formData.append('file', fileToUpload);
            axios.post("/api/samplesExternal", formData, {
              headers: {
                'Content-Type': 'multipart/form-data'
              }
            }).then(() => {
              this.$router.go(-1)
            }).catch(() => {
              this.loading = false;
              this.hasError = true;
            })
         
      },
    }
  }
  </script>
  
  