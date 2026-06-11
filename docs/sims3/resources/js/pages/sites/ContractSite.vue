<template>
    <v-container class="d-flex justify-center align-center fill-height">
        <v-card class="pa-6" max-width="600" elevation="4">
            <v-row align="center" justify="space-between" class="mb-4">
                <v-col cols="auto">
                    <v-card-title>Upload Commune & Training Contracts</v-card-title>
                </v-col>
                <v-col cols="auto">
                    <v-btn color="secondary" @click="$router.back()">Back</v-btn>
                </v-col>
            </v-row>

            <v-form ref="formRef" @submit.prevent="confirmUpload">
                <v-select v-model="form.site_id" :items="siteOptions" item-value="Id_Site" item-title="label"
                    label="Select Site" :loading="loadingSites" :error="showValidation && !form.site_id"
                    :error-messages="showValidation && !form.site_id ? 'Site selection is required' : ''"
                    required></v-select>

                <v-file-input v-model="form.commune_contract" label="Commune Contract" accept=".pdf,.zip" show-size
                    return-object prepend-icon="mdi-file-upload"></v-file-input>
                <!-- <div v-if="form.commune_contract" class="d-flex justify-space-between mb-2">
          <span class="text-caption">Selected: {{ form.commune_contract.name }}</span>
          <v-btn small color="red" @click="form.commune_contract = null">Remove</v-btn>
        </div> -->

                <v-file-input v-model="form.training_contract" label="Training Contract" accept=".pdf,.zip" show-size
                    return-object prepend-icon="mdi-file-upload"></v-file-input>
                <!-- <div v-if="form.training_contract" class="d-flex justify-space-between mb-2">
          <span class="text-caption">Selected: {{ form.training_contract.name }}</span>
          <v-btn small color="red" @click="form.training_contract = null">Remove</v-btn>
        </div> -->

                <v-progress-linear v-if="uploadProgress > 0" :value="uploadProgress" height="6" color="green"
                    class="my-3" striped rounded></v-progress-linear>

                <v-btn color="primary" type="submit" class="mt-4" :loading="submitting"
                    :disabled="!form.site_id || (!form.commune_contract && !form.training_contract)">
                    Submit
                </v-btn>
            </v-form>
        </v-card>

        <!-- Confirm Dialog -->
        <v-dialog v-model="confirmDialog" max-width="400">
            <v-card>
                <v-card-title class="text-h6">Confirm Upload</v-card-title>
                <v-card-text>Are you sure you want to upload the selected file(s)?</v-card-text>
                <v-card-actions>
                    <v-spacer></v-spacer>
                    <v-btn color="grey" @click="confirmDialog = false">Cancel</v-btn>
                    <v-btn color="primary" @click="submitForm">Yes, Upload</v-btn>
                </v-card-actions>
            </v-card>
        </v-dialog>

        <!-- Result Dialog -->
        <v-dialog v-model="resultDialog.visible" max-width="400">
            <v-card>
                <v-card-title class="text-h6">{{ resultDialog.title }}</v-card-title>
                <v-card-text>{{ resultDialog.message }}</v-card-text>
                <v-card-actions>
                    <v-spacer></v-spacer>
                    <v-btn color="primary" @click="resultDialog.visible = false">OK</v-btn>
                </v-card-actions>
            </v-card>
        </v-dialog>
    </v-container>
</template>

<script>
import axios from 'axios'

export default {
    name: 'SiteContractForm',
    data() {
        return {
            form: {
                site_id: null,
                commune_contract: null,
                training_contract: null
            },
            showValidation: false,
            siteOptions: [],
            loadingSites: false,
            submitting: false,
            uploadProgress: 0,
            confirmDialog: false,
            resultDialog: {
                visible: false,
                title: '',
                message: ''
            }
        }
    },
    watch: {
        'form.site_id'(val) {
            if (val) this.showValidation = false
        }
    },
    mounted() {
        this.loadSites()
    },
    methods: {
        async loadSites() {
            this.loadingSites = true
            try {
                const res = await axios.get('/api/sites')

                this.siteOptions = [
                    { Id_Site: '', label: '' },
                    ...res.data.map(site => ({
                        ...site,
                        label: site.Id_Site  // to make sure item-title can use 'label'
                    }))
                ]
            } catch (err) {
                console.error('Failed to load sites', err)
            } finally {
                this.loadingSites = false
            }
        },
        confirmUpload() {
            this.showValidation = true

            if (!this.form.site_id) {
                return // error will show
            }

            if (!this.form.commune_contract && !this.form.training_contract) {
                this.showResult('Validation Error', 'Please select at least one file.')
                return
            }

            // All valid → reset validation flags
            this.showValidation = false
            this.confirmDialog = true
        },
        async submitForm() {
    this.confirmDialog = false
    this.submitting = true
    this.uploadProgress = 0

    const formData = new FormData()
    formData.append('site_id', this.form.site_id)

    // Commune contract
    if (this.form.commune_contract) {
        const communeFile = Array.isArray(this.form.commune_contract)
            ? this.form.commune_contract[0]
            : this.form.commune_contract

        console.log('Commune contract file:', communeFile)
        console.log('Commune contract name:', communeFile?.name)
        formData.append('commune_contract', communeFile)
    }

    // Training contract
    if (this.form.training_contract) {
        const trainingFile = Array.isArray(this.form.training_contract)
            ? this.form.training_contract[0]
            : this.form.training_contract

        console.log('Training contract file:', trainingFile)
        console.log('Training contract name:', trainingFile?.name)
        formData.append('training_contract', trainingFile)
    }

    console.log('Site ID:', this.form.site_id)
    console.log('FormData entries:')
    for (let [key, value] of formData.entries()) {
        console.log(key, value)
    }

    try {
        await axios.post('/api/site-contract', formData, {
            headers: { 'Content-Type': 'multipart/form-data' },
            onUploadProgress: (progressEvent) => {
                this.uploadProgress = Math.round((progressEvent.loaded * 100) / progressEvent.total)
            }
        })

        this.showResult('Upload Successful', 'Files have been uploaded successfully.')
        this.resetForm()
    } catch (err) {
        console.error('Upload failed', err)
        this.showResult('Upload Failed', 'An error occurred while uploading. Please try again.')
    } finally {
        this.submitting = false
        this.uploadProgress = 0
    }
}
,
        resetForm() {
            this.form.commune_contract = null
            this.form.training_contract = null
        },
        showResult(title, message) {
            this.resultDialog.title = title
            this.resultDialog.message = message
            this.resultDialog.visible = true
        }
    }
}
</script>

<style scoped>
.text-caption {
    font-size: 0.85rem;
}
</style>
