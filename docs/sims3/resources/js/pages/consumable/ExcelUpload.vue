<template>
  <v-container class="upload-container">
    <v-card class="pa-5">
      <v-card-title class="d-flex justify-space-between align-center">
        <span class="text-h5">Order Request</span>
        <a href="/api/download-template" class="text-h5"><v-btn color="primary" >Download Template</v-btn></a>
      </v-card-title>
      <v-divider class="my-4"></v-divider>
      <!-- <v-select v-model="selectedOption" :items="['', 'Project', 'Entre_Charge', 'TS1001_Admin','Entre_Deposit']"
        label="Which option do you want to upload?" filled rounded color="primary" class="mb-4"
        prepend-icon="mdi-check-circle" :class="selectedOption ? 'success-icon' : ''"></v-select> -->
      <v-file-input label="Choose Excel File" @change="handleFileUpload" accept=".xlsx, .xls" filled rounded show-size
        prepend-icon="mdi-file-excel" color="primary" class="mb-4" ref="fileInput"
        :class="file ? 'success-icon1' : ''"></v-file-input>
      <v-btn @click="confirmUpload" :disabled="!file" color="primary" class="mt-4">Send Excel File</v-btn>
    </v-card>
  </v-container>
</template>

<script>
import axios from 'axios'; // Import Axios
import Swal from 'sweetalert2';

export default {
  name: 'ExcelUploader',
  data() {
    return {
      file: null,
      //selectedOption: null, 
    };
  },
  methods: {
    handleFileUpload(event) {
      this.file = event.target.files[0];
    },
    async confirmUpload() {
      const result = await Swal.fire({
        title: 'Are you sure?',
        text: 'You are about to upload the Excel file.',
        icon: 'warning',
        showCancelButton: true,
        confirmButtonText: 'Yes, upload it!',
        cancelButtonText: 'Cancel',
      });

      if (result.isConfirmed) {
        this.uploadFile();
      }
    },
    async uploadFile() {
      const formData = new FormData();
      formData.append('file', this.file);

      // if (!this.selectedOption) {
      //   Swal.fire('Error', 'Please select an option before uploading.', 'error');
      //   return;
      // }

      Swal.fire({
        title: 'Uploading...',
        text: 'Please wait while the file is being uploaded.',
        allowOutsideClick: false,
        didOpen: () => {
          Swal.showLoading();
        },
      });

      try {
        const response = await axios.post('/api/uploadExcel?option=1', formData, {
        //  const response = await axios.post('/api/uploadExcel', formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          },
        });

        // Check for successful response (status 200-299)
        if (response.status >= 200 && response.status < 300) {
          console.log('File uploaded:', response.data);
          Swal.fire({
            title: 'Success',
            html: `File uploaded successfully!<br> Total record insert: ${response.data.inserted_records}`,
            icon: 'success'
          });

          // Reset form
          this.file = null;
          this.$refs.fileInput.reset();
         // redirect to dashboard of request. 
          setTimeout(() => {
            window.location.href = 'https://dashboard.teuksaat1001.com/logistic';
          }, 2000);
        } else {
          throw new Error(response.data.message || 'Upload failed');
        }
      } catch (error) {
        console.error('Upload error:', error);
        let errorMessage = 'Your uploaded file has a problem. Please contact IT for support';

        if (error.response) {
          // The request was made and the server responded with a status code
          // that falls out of the range of 2xx
          errorMessage = error.response.data.message || errorMessage;
        } else if (error.request) {
          // The request was made but no response was received
          errorMessage = 'No response from server. Please check your network connection.';
        }

        Swal.fire('Error', errorMessage, 'error');
      }
    },
  },
};
</script>

<style scoped>
.upload-container {
  margin: 20px auto;
  max-width: 600px;
}

.success-icon>>>.v-icon {
  color: #4CAF50 !important;
}

.success-icon1>>>.v-icon {
  color: #4CAF50 !important;
}
</style>