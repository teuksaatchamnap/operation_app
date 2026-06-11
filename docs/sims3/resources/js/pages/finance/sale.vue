<template>
  <v-container class="pa-6" style="max-width: 500px;">
    <v-card elevation="3" class="pa-6">

      <v-card-title class="text-h6 mb-4">
        Step By Step Form
      </v-card-title>

      <!-- STEP 1 - DATE -->
      <div v-if="step === 1">
        <v-text-field
          v-model="form.date"
          label="Select Date"
          type="date"
          variant="outlined"
        ></v-text-field>

        <v-btn color="primary" class="mt-4" @click="nextStep">
          Next
        </v-btn>
      </div>

      <!-- STEP 2 - NUMBER OF SCHOOL -->
      <div v-if="step === 2">
        <v-text-field
          v-model.number="form.numberOfSchool"
          label="Number of School"
          type="number"
          variant="outlined"
          @keypress="onlyNumber"
        ></v-text-field>

        <div class="mt-4">
          <v-btn variant="outlined" @click="prevStep">
            Back
          </v-btn>

          <v-btn color="primary" class="ml-2" @click="nextStep">
            Next
          </v-btn>
        </div>
      </div>

      <!-- STEP 3 -->
      <div v-if="step === 3">
        <v-text-field
          v-model="form.field1"
          label="Field 1"
          variant="outlined"
        ></v-text-field>

        <div class="mt-4">
          <v-btn variant="outlined" @click="prevStep">Back</v-btn>
          <v-btn color="primary" class="ml-2" @click="nextStep">Next</v-btn>
        </div>
      </div>

      <!-- STEP 4 -->
      <div v-if="step === 4">
        <v-text-field
          v-model="form.field2"
          label="Field 2"
          variant="outlined"
        ></v-text-field>

        <div class="mt-4">
          <v-btn variant="outlined" @click="prevStep">Back</v-btn>
          <v-btn color="primary" class="ml-2" @click="nextStep">Next</v-btn>
        </div>
      </div>

      <!-- STEP 5 -->
      <div v-if="step === 5">
        <v-text-field
          v-model="form.field3"
          label="Field 3"
          variant="outlined"
        ></v-text-field>

        <div class="mt-4">
          <v-btn variant="outlined" @click="prevStep">Back</v-btn>
          <v-btn color="primary" class="ml-2" @click="nextStep">Next</v-btn>
        </div>
      </div>

      <!-- STEP 6 -->
      <div v-if="step === 6">
        <v-text-field
          v-model="form.field4"
          label="Field 4"
          variant="outlined"
        ></v-text-field>

        <div class="mt-4">
          <v-btn variant="outlined" @click="prevStep">Back</v-btn>
          <v-btn color="primary" class="ml-2" @click="nextStep">Next</v-btn>
        </div>
      </div>

      <!-- STEP 7 -->
      <div v-if="step === 7">
        <v-text-field
          v-model="form.field5"
          label="Field 5"
          variant="outlined"
        ></v-text-field>

        <div class="mt-4">
          <v-btn variant="outlined" @click="prevStep">Back</v-btn>
          <v-btn color="success" class="ml-2" @click="finishForm">Finish</v-btn>
        </div>
      </div>

    </v-card>
  </v-container>
</template>

<script>
export default {
  name: "StepByStepForm",

  data() {
    return {
      step: 1,
      form: {
        date: "",
        numberOfSchool: null,
        field1: "",
        field2: "",
        field3: "",
        field4: "",
        field5: "",
      }
    }
  },

  mounted() {
    // Set today date automatically
    const today = new Date().toISOString().split('T')[0]
    this.form.date = today
  },

  methods: {
    nextStep() {
      this.step++
    },

    prevStep() {
      this.step--
    },

    finishForm() {
      console.log("Submitted Data:", this.form)

      alert("Form Submitted Successfully!")

      this.resetForm()
    },

    resetForm() {
      this.step = 1
      this.form = {
        date: new Date().toISOString().split('T')[0],
        numberOfSchool: null,
        field1: "",
        field2: "",
        field3: "",
        field4: "",
        field5: "",
      }
    },

    onlyNumber(e) {
      const char = String.fromCharCode(e.keyCode)
      if (!/[0-9]/.test(char)) {
        e.preventDefault()
      }
    }
  }
}
</script>
