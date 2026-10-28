<template>
    <div class="px-6 pb-6">
        <v-card rounded="lg" elevation="2">

            <!-- Toolbar -->
            <div class="px-4 pt-4 pb-3 d-flex flex-wrap align-center justify-space-between ga-3">
                <div>
                    <div class="text-subtitle-1 font-weight-bold">Technical Issues</div>
                    <div class="text-caption text-medium-emphasis">{{ filteredIssues.length }} record{{ filteredIssues.length !== 1 ? 's' : '' }}</div>
                </div>
                <div class="d-flex flex-wrap ga-2">
                    <v-text-field
                        v-model="searchQuery"
                        placeholder="Search site code..."
                        prepend-inner-icon="mdi-magnify"
                        variant="outlined" density="compact" hide-details
                        style="max-width:220px"
                    />
                    <v-select
                        v-model="filterPlatform"
                        :items="platformOptions"
                        variant="outlined" density="compact" hide-details
                        style="max-width:180px"
                    />
                </div>
            </div>

            <v-divider />

            <v-data-table
                :headers="issueHeaders"
                :items="filteredIssues"
                :search="searchQuery"
                :items-per-page="10"
                :items-per-page-options="[5, 10, 25]"
                density="comfortable"
                class="issue-data-table"
            >
                <!-- Problem Type -->
                <template #item.problemType="{ item }">
                    <v-chip size="x-small" variant="outlined">{{ item.problemType || '–' }}</v-chip>
                </template>

                <!-- Site Status -->
                <template #item.siteStatus="{ item }">
                    <v-chip
                        size="x-small" variant="tonal"
                        :color="item.siteStatus === 'Can Produce' ? 'success' : 'error'"
                    >{{ item.siteStatus }}</v-chip>
                </template>

                <!-- Urgency -->
                <template #item.urgency="{ item }">
                    <v-chip size="x-small" variant="tonal" :color="urgencyColor(item.urgency)">
                        {{ item.urgency }}
                    </v-chip>
                </template>

                <!-- Status -->
                <template #item.status="{ item }">
                    <v-chip size="x-small" variant="outlined">{{ item.status }}</v-chip>
                </template>

                <!-- SLA -->
                <template #item.sla="{ item }">
                    <span class="text-body-2 font-weight-medium" :class="slaColor(item.sla)">{{ item.sla }}h</span>
                </template>

                <!-- Plan Date -->
                <template #item.planDate="{ item }">
                    <span class="text-body-2">{{ item.planDate || '—' }}</span>
                </template>

                <!-- Actions -->
                <template #item.actions="{ item }">
                    <v-btn
                        size="x-small" variant="tonal" color="primary"
                        @click.stop="openIssue(item)"
                    >
                        <v-icon start size="12">mdi-eye-outline</v-icon>
                        Detail
                    </v-btn>
                </template>

                <!-- Empty state -->
                <template #no-data>
                    <div class="text-center text-medium-emphasis pa-8">
                        <v-icon size="40" color="grey-lighten-2" class="mb-2">mdi-table-search</v-icon>
                        <div>No issues found</div>
                    </div>
                </template>
            </v-data-table>

        </v-card>

        <!-- Loaded only after the first "Detail" click -->
        <IssueDetailDialog v-if="selectedIssue" v-model="issueDialog" :issue="selectedIssue" />
    </div>
</template>

<script setup>
import { ref, computed, defineAsyncComponent } from 'vue'
import { urgencyColor, slaColor } from './technicalHelpers'

const IssueDetailDialog = defineAsyncComponent(() => import('./IssueDetailDialog.vue'))

const mockIssues = [
    { id: 1, kioskCode: 'A1', platform: 'Battambang',        title: 'Water pump motor failure',       problemType: 'Motor',          siteStatus: 'Cannot Produce', urgency: 'critical', status: 'open',         sla: 2,  planDate: '2026-05-08', assignedTo: 'Sok Dara',    description: 'Motor overheating and shutting down repeatedly.' },
    { id: 2, kioskCode: 'G9', platform: 'Kampong Chhnang',   title: 'UV filter replacement needed',   problemType: 'UV Filter',      siteStatus: 'Can Produce',    urgency: 'high',     status: 'scheduled',    sla: 18, planDate: '2026-05-09', assignedTo: 'Chan Piseth', description: 'UV lamp has reached end of service life.' },
    { id: 3, kioskCode: 'C3', platform: 'Phnom Penh',        title: 'Monthly routine check',          problemType: 'Filter System',  siteStatus: 'Can Produce',    urgency: 'low',      status: 'in-progress',  sla: 5,  planDate: null,          assignedTo: 'Rin Sophea',  description: 'Routine maintenance inspection scheduled.' },
    { id: 4, kioskCode: 'B5', platform: 'Siem Reap',         title: 'Pipe leak at junction point',    problemType: 'Pipe Leak',      siteStatus: 'Cannot Produce', urgency: 'high',     status: 'open',         sla: 6,  planDate: '2026-05-10', assignedTo: 'Heng Vutha',  description: 'Water leaking at main junction, pressure loss.' },
    { id: 5, kioskCode: 'D2', platform: 'Kampong Cham',      title: 'Chlorinator not dosing',         problemType: 'Chlorinator',    siteStatus: 'Can Produce',    urgency: 'medium',   status: 'scheduled',    sla: 30, planDate: '2026-05-12', assignedTo: 'Sok Dara',    description: 'Chlorine dosing pump shows zero output.' },
    { id: 6, kioskCode: 'F4', platform: 'Takeo',             title: 'Solar panel output low',         problemType: 'Solar Panel',    siteStatus: 'Can Produce',    urgency: 'medium',   status: 'open',         sla: 48, planDate: null,          assignedTo: 'Chan Piseth', description: 'Panel output dropped 40% — possible shading or fault.' },
    { id: 7, kioskCode: 'E8', platform: 'Kampong Speu',      title: 'Electricity grid outage',        problemType: 'Grid/Electricity',siteStatus: 'Cannot Produce',urgency: 'critical', status: 'open',         sla: 1,  planDate: '2026-05-08', assignedTo: 'Rin Sophea',  description: 'Site running on backup; grid not restored.' },
]

const platformOptions = [
    { title: 'All Platforms', value: 'all' },
    { title: 'Battambang',       value: 'Battambang' },
    { title: 'Siem Reap',        value: 'Siem Reap' },
    { title: 'Phnom Penh',       value: 'Phnom Penh' },
    { title: 'Kampong Cham',     value: 'Kampong Cham' },
    { title: 'Kampong Speu',     value: 'Kampong Speu' },
    { title: 'Kampong Chhnang',  value: 'Kampong Chhnang' },
    { title: 'Takeo',            value: 'Takeo' },
]

const searchQuery    = ref('')
const filterPlatform = ref('all')

const issueHeaders = [
    { title: 'Kiosk',        key: 'kioskCode',   sortable: true  },
    { title: 'Platform',     key: 'platform',    sortable: true  },
    { title: 'Title',        key: 'title',       sortable: false },
    { title: 'Problem Type', key: 'problemType', sortable: false },
    { title: 'Site Status',  key: 'siteStatus',  sortable: true  },
    { title: 'Urgency',      key: 'urgency',     sortable: true  },
    { title: 'Status',       key: 'status',      sortable: true  },
    { title: 'Open Time',    key: 'sla',         sortable: true  },
    { title: 'Plan Date',    key: 'planDate',    sortable: true  },
    { title: 'Assigned To',  key: 'assignedTo',  sortable: true  },
    { title: '',             key: 'actions',     sortable: false },
]

const filteredIssues = computed(() =>
    mockIssues.filter(i =>
        (filterPlatform.value === 'all' || i.platform === filterPlatform.value)
    )
)

const issueDialog   = ref(false)
const selectedIssue = ref(null)

const openIssue = (issue) => { selectedIssue.value = issue; issueDialog.value = true }
</script>

<style scoped>
.issue-data-table :deep(thead th) {
    font-size: 11px !important;
    font-weight: 700 !important;
    text-transform: uppercase;
    letter-spacing: .06em;
    color: #616161 !important;
    background: #f8f9fa !important;
    white-space: nowrap;
}

.issue-data-table :deep(tbody tr:hover td) {
    background: #f5f8ff;
}
</style>
