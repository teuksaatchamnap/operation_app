<template>
  <v-container fluid fill-height>
    <v-row align="center" justify="center" class="ma-0 pa-0" style="min-height: 100vh;">
      <v-col cols="12" sm="8" md="6" lg="4">
        <v-card class="pa-6">
          <h3 class="mb-4 text-center">Import Invoice & Balance</h3>

          <v-file-input v-model="file" label="Choose Excel File"
            accept="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet, application/vnd.ms-excel"
            outlined :disabled="uploading"></v-file-input>

          <v-btn class="mt-4" color="blue" block @click="uploadFile"
            :disabled="!file || file.length === 0 || uploading">
            Upload
          </v-btn>

          <v-snackbar v-model="snackbar.show" :color="snackbar.color" timeout="4000" top right>
            {{ snackbar.message }}
          </v-snackbar>

          <!-- Upload progress dialog -->
          <v-dialog v-model="uploading" persistent max-width="300">
            <v-card class="pa-4" outlined>
              <div class="text-center mb-4" style="font-size: 1.8rem; font-weight: bold;">
                {{ uploadProgress }}%
              </div>
              <v-progress-linear :value="uploadProgress" height="20" color="blue" striped rounded></v-progress-linear>
            </v-card>
          </v-dialog>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>


<script>
import axios from "axios";

export default {
  data() {
    return {
      file: null,
      snackbar: {
        show: false,
        message: "",
        color: "",
      },
      uploading: false,
      uploadProgress: 0,
      smoothProgressInterval: null,
      targetProgress: 0,
    };
  },

  computed: {
        isAuthenticated() {
            return this.$store.state.isAuthenticated;
        },
        user() {
            return this.$store.state.user;
        },
  },
  mounted() {
    if (!this.isAuthenticated || !this.user.permissions.includes('import_invoices')) {
      this.$router.push('/cashier');
    }
  },

  methods: {
    async uploadFile() {
      if (!this.file || this.file.length === 0) {
        this.showSnackbar("Please select a file first.", "error");
        return;
      }

      const form = new FormData();
      let fileToUpload = Array.isArray(this.file) ? this.file[0] : this.file;
      if (!fileToUpload) {
        console.error("No file selected");
        this.importing = false;
        return;
    }
      form.append("file", fileToUpload);

      this.uploading = true;
      this.uploadProgress = 1;
      this.targetProgress = 1;

      if (this.smoothProgressInterval) {
        clearInterval(this.smoothProgressInterval);
        this.smoothProgressInterval = null;
      }

      this.smoothProgressInterval = setInterval(() => {
        if (this.uploadProgress < this.targetProgress) {
          this.uploadProgress++;
        }
      }, 100);

      try {
        const response = await axios.post("/api/upload-excel", form, {
          headers: { "Content-Type": "multipart/form-data" },
          onUploadProgress: (progressEvent) => {
            if (progressEvent.lengthComputable) {
              const percent = Math.round(
                (progressEvent.loaded * 100) / progressEvent.total
              );
              if (percent > this.targetProgress) {
                this.targetProgress = percent;
              }
            }
          },
        });

        this.targetProgress = 100;
        this.uploadProgress = 100;

        this.showSnackbar(response.data.message || "Upload successful!", "success");
        this.file = null;
        setTimeout(() => this.$router.push('/cashier'), 1500);
      } catch (error) {
        console.error(error);

        const msg =
          error.response?.data?.message ||
          error.message ||
          "Upload failed!";

        this.showSnackbar(msg, "error");
        this.file = null;
      } finally {
        clearInterval(this.smoothProgressInterval);
        this.smoothProgressInterval = null;
        this.uploading = false;
        this.uploadProgress = 0;
        this.targetProgress = 0;
      }
    },

    showSnackbar(message, color) {
      this.snackbar.message = message;
      this.snackbar.color = color === "error" ? "red darken-2" : "green darken-2";
      this.snackbar.show = true;
    },
  },
};
</script>
