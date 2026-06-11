<template>
    <v-form @submit.prevent="submitForm">
      <v-text-field v-model="site" label="Site" type="text"></v-text-field>
      <v-text-field v-model="test_date" type="date" label="Test Date"></v-text-field>
      <v-file-input 
        v-model="file" 
        label="Upload File" 
        accept=".jpg,.png,.pdf,.docx"
        required
      ></v-file-input>
      <v-btn type="submit">Submit</v-btn>
    </v-form>
  </template>
  
  <script>
  import axios from 'axios';
  
  export default {
    data() {
      return {
        site: '',
        test_date: '',
        file: null
      };
    },
    methods: {
      submitForm() {
        const formData = new FormData();
        formData.append('site', this.site);
        formData.append('test_date', this.test_date);
        formData.append('file', this.file[0]);
        axios.post('/api/samplesExternal', formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        })
        .then(response => {
          // Handle success, e.g., show a success message
          console.log(response.data);
        })
        .catch(error => {
          // Handle errors, e.g., show an error message
          console.error(error);
        });
      }
    }
  };
  </script>
  