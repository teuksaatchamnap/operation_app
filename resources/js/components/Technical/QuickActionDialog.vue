<template>
    <v-dialog v-model="open" max-width="480">
        <v-card rounded="xl">
            <div class="qa-dialog-header pa-5 d-flex align-center justify-space-between"
                :style="{ background: form.gradient }">
                <div class="d-flex align-center ga-2">
                    <v-icon color="white">{{ form.icon }}</v-icon>
                    <span class="text-subtitle-1 font-weight-bold text-white">{{ form.title }}</span>
                </div>
                <v-btn icon size="small" variant="text" color="white" @click="open = false">
                    <v-icon>mdi-close</v-icon>
                </v-btn>
            </div>
            <v-card-text class="pa-5">
                <template v-for="(field, i) in form.fields" :key="`${type}-${field.label}`">
                    <v-select v-if="field.items" :label="field.label" :items="field.items" variant="outlined"
                        density="comfortable" :class="{ 'mb-3': i < form.fields.length - 1 }" />
                    <v-textarea v-else-if="field.rows" :label="field.label" :placeholder="field.placeholder"
                        variant="outlined" density="comfortable" :rows="field.rows"
                        :class="{ 'mb-3': i < form.fields.length - 1 }" />
                    <v-text-field v-else :label="field.label" :placeholder="field.placeholder" variant="outlined"
                        density="comfortable" :class="{ 'mb-3': i < form.fields.length - 1 }" />
                </template>
            </v-card-text>
            <v-card-actions class="pa-5 pt-0">
                <v-btn variant="text" @click="open = false">Cancel</v-btn>
                <v-spacer />
                <v-btn :color="form.submitColor" variant="flat" rounded="lg" @click="open = false">
                    {{ form.submitLabel }}
                </v-btn>
            </v-card-actions>
        </v-card>
    </v-dialog>
</template>

<script setup>
import { computed } from 'vue'

const open = defineModel({ type: Boolean, default: false })

const props = defineProps({
    type: { type: String, required: true }, // issue | routine | assessment | water
})

const siteCode = { label: 'Site Code', placeholder: 'e.g., A3' }

// fields: `items` → v-select, `rows` → v-textarea, otherwise v-text-field
const forms = {
    issue: {
        title: 'Create Issue',
        icon: 'mdi-wrench',
        gradient: 'linear-gradient(135deg,#1565C0,#1976D2)',
        submitLabel: 'Submit Issue',
        submitColor: 'primary',
        fields: [
            siteCode,
            { label: 'Issue Title', placeholder: 'Brief description' },
            { label: 'Description', placeholder: 'Detailed description of the issue', rows: 3 },
            { label: 'Problem Type', items: ['Pump Failure', 'Pipe Leak', 'Chlorinator Issue', 'Electrical', 'Filter Blocked', 'Other'] },
            { label: 'Site Status', items: ['Can Produce', 'Cannot Produce'] },
        ],
    },
    routine: {
        title: 'Routine Check',
        icon: 'mdi-clipboard-check',
        gradient: 'linear-gradient(135deg,#2E7D32,#43A047)',
        submitLabel: 'Submit Check',
        submitColor: 'success',
        fields: [
            siteCode,
            { label: 'Check Type', items: ['Daily Check', 'Weekly Check', 'Monthly Check'] },
            { label: 'Observations', placeholder: 'Note any observations or issues found', rows: 3 },
            { label: 'Overall Status', items: ['Pass', 'Fail', 'Needs Attention'] },
        ],
    },
    assessment: {
        title: 'Site Assessment',
        icon: 'mdi-file-document-outline',
        gradient: 'linear-gradient(135deg,#E65100,#FB8C00)',
        submitLabel: 'Submit Assessment',
        submitColor: 'warning',
        fields: [
            siteCode,
            { label: 'Assessment Type', items: ['Structural', 'Water Quality', 'Equipment', 'Safety', 'Full Assessment'] },
            { label: 'Assessor Name', placeholder: 'Your name' },
            { label: 'Findings', placeholder: 'Summarise your findings', rows: 3 },
        ],
    },
    water: {
        title: 'Water Sample',
        icon: 'mdi-water',
        gradient: 'linear-gradient(135deg,#00695C,#26A69A)',
        submitLabel: 'Submit Sample',
        submitColor: 'teal',
        fields: [
            siteCode,
            { label: 'Sample ID', placeholder: 'e.g., WS-2026-001' },
            { label: 'Test Type', items: ['Turbidity', 'Chlorine Level', 'pH', 'Bacteria', 'Full Panel'] },
            { label: 'Notes', placeholder: 'Additional notes about the sample', rows: 2 },
        ],
    },
}

const form = computed(() => forms[props.type])
</script>

<style scoped>
.qa-dialog-header {
    border-radius: 12px 12px 0 0;
}
</style>
