<template>
    <v-dialog v-model="open" max-width="760" scrollable>
        <v-card rounded="xl">
            <div class="issue-dialog-header px-6 py-5 d-flex align-start justify-space-between">
                <div>
                    <div class="d-flex align-center ga-2 mb-1">
                        <v-chip :color="urgencyColor(issue.urgency)" size="small" variant="flat" class="font-weight-bold">
                            {{ issue.urgency }}
                        </v-chip>
                        <span class="text-h6 font-weight-bold text-white">{{ issue.kioskCode }}</span>
                    </div>
                    <div class="text-body-2 text-white" style="opacity:.85">{{ issue.title }}</div>
                </div>
                <v-btn icon size="small" variant="text" color="white" @click="open = false">
                    <v-icon>mdi-close</v-icon>
                </v-btn>
            </div>

            <v-tabs v-model="issueTab" bg-color="grey-lighten-4">
                <v-tab value="info">Issue Info</v-tab>
                <v-tab value="technical">Technical Analysis</v-tab>
                <v-tab value="water">Water Quality</v-tab>
                <v-tab value="history">History</v-tab>
                <v-tab value="assessment">Site Assessments</v-tab>
                <v-tab value="routine">Routine Check</v-tab>
            </v-tabs>

            <v-card-text class="pa-5">
                <v-tabs-window v-model="issueTab">

                    <!-- Issue Info -->
                    <v-tabs-window-item value="info">
                        <v-card variant="outlined" rounded="lg">
                            <v-card-text>
                                <v-row dense>
                                    <v-col cols="6">
                                        <div class="text-caption text-medium-emphasis">Problem Type</div>
                                        <div class="text-body-2 font-weight-bold mt-1">{{ issue.problemType || 'Not specified' }}</div>
                                    </v-col>
                                    <v-col cols="6">
                                        <div class="text-caption text-medium-emphasis">Site Status</div>
                                        <v-chip class="mt-1" size="small" :color="issue.siteStatus === 'Can Produce' ? 'success' : 'error'" variant="tonal">
                                            {{ issue.siteStatus || 'Unknown' }}
                                        </v-chip>
                                    </v-col>
                                    <v-col cols="6">
                                        <div class="text-caption text-medium-emphasis">Urgency</div>
                                        <v-chip class="mt-1" size="small" :color="urgencyColor(issue.urgency)" variant="tonal">{{ issue.urgency }}</v-chip>
                                    </v-col>
                                    <v-col cols="6">
                                        <div class="text-caption text-medium-emphasis">Open Time</div>
                                        <div class="text-body-2 font-weight-bold mt-1" :class="slaColor(issue.sla)">{{ issue.sla }}h</div>
                                    </v-col>
                                    <v-col cols="6">
                                        <div class="text-caption text-medium-emphasis mb-1">Issue Status</div>
                                        <v-select :items="statusOptions" density="compact" variant="outlined" hide-details :model-value="issue.status" style="max-width:200px" />
                                    </v-col>
                                    <v-col cols="6">
                                        <div class="text-caption text-medium-emphasis">Plan Date</div>
                                        <div class="text-body-2 font-weight-bold mt-1">{{ issue.planDate || 'Not scheduled' }}</div>
                                    </v-col>
                                    <v-col cols="6">
                                        <div class="text-caption text-medium-emphasis">Assigned To</div>
                                        <div class="text-body-2 font-weight-bold mt-1">{{ issue.assignedTo }}</div>
                                    </v-col>
                                    <v-col cols="6">
                                        <div class="text-caption text-medium-emphasis">Platform</div>
                                        <div class="text-body-2 font-weight-bold mt-1">{{ issue.platform }}</div>
                                    </v-col>
                                    <v-col cols="12">
                                        <div class="text-caption text-medium-emphasis">Description</div>
                                        <div class="text-body-2 mt-1">{{ issue.description }}</div>
                                    </v-col>
                                </v-row>
                            </v-card-text>
                        </v-card>
                    </v-tabs-window-item>

                    <!-- Placeholder tabs -->
                    <v-tabs-window-item
                        v-for="tab in ['technical','water','history','assessment','routine']"
                        :key="tab" :value="tab"
                    >
                        <v-card variant="outlined" rounded="lg">
                            <v-card-text class="text-center text-medium-emphasis py-12">
                                <v-icon size="40" color="grey-lighten-2" class="mb-3">mdi-file-document-outline</v-icon>
                                <div>No data available for this section yet.</div>
                            </v-card-text>
                        </v-card>
                    </v-tabs-window-item>

                </v-tabs-window>
            </v-card-text>

            <v-divider />
            <v-card-actions class="pa-4">
                <v-btn variant="text" @click="open = false">Close</v-btn>
            </v-card-actions>
        </v-card>
    </v-dialog>
</template>

<script setup>
import { ref, watch } from 'vue'
import { urgencyColor, slaColor } from './technicalHelpers'

const open = defineModel({ type: Boolean, default: false })

const props = defineProps({
    issue: { type: Object, required: true },
})

const statusOptions = ['open','scheduled','in-progress','pending-validation','ready-for-intervention','resolved']

const issueTab = ref('info')

// Always start on the Info tab when a different issue is opened
watch(() => props.issue, () => { issueTab.value = 'info' })
</script>

<style scoped>
.issue-dialog-header {
    background: linear-gradient(135deg, #0D47A1 0%, #1976D2 100%);
    border-radius: 12px 12px 0 0;
}
</style>
