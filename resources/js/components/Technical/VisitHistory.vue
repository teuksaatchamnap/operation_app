<template>
    <div class="px-6 pb-6">
        <v-card rounded="lg" elevation="2">

            <!-- Toolbar -->
            <div class="px-4 pt-4 pb-3 d-flex flex-wrap align-center justify-space-between ga-3">
                <div class="d-flex align-center ga-3">
                    <div class="schedule-icon d-flex align-center justify-center">
                        <v-icon color="white" size="20">mdi-calendar-check-outline</v-icon>
                    </div>
                    <div>
                        <div class="text-subtitle-1 font-weight-bold">Visit History – {{ visitMonthLabel }}</div>
                        <div class="text-caption text-medium-emphasis">View past site visits</div>
                    </div>
                </div>
                <div class="d-flex ga-2">
                    <v-btn variant="outlined" size="small" @click="prevVisitMonth">
                        <v-icon start size="16">mdi-chevron-left</v-icon>
                        Previous Month
                    </v-btn>
                    <v-btn variant="outlined" size="small" @click="nextVisitMonth">
                        Next Month
                        <v-icon end size="16">mdi-chevron-right</v-icon>
                    </v-btn>
                </div>
            </div>

            <v-divider />

            <v-table class="visit-history-table">
                <thead>
                    <tr>
                        <th class="text-left">Date</th>
                        <th class="text-left">Site Code</th>
                        <th class="text-left">Site Name</th>
                        <th class="text-left">Actions Performed</th>
                        <th class="text-left">Comments</th>
                        <th class="text-left">Status</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="visit in visitRecords" :key="visit.date + visit.siteCode">
                        <td>{{ visit.date }}</td>
                        <td>{{ visit.siteCode }}</td>
                        <td>{{ visit.siteName }}</td>
                        <td>{{ visit.actions }}</td>
                        <td>{{ visit.comments }}</td>
                        <td>
                            <v-chip size="small" color="success" variant="tonal">{{ visit.status }}</v-chip>
                        </td>
                    </tr>
                    <tr v-if="visitRecords.length === 0">
                        <td colspan="6" class="text-center text-medium-emphasis py-8">
                            <v-icon size="40" color="grey-lighten-2" class="mb-2">mdi-calendar-remove-outline</v-icon>
                            <div>No visits recorded for this month</div>
                        </td>
                    </tr>
                </tbody>
            </v-table>

        </v-card>
    </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const visitMonthOffset = ref(0)

const visitHistoryData = {
    '2026-01': [
        { date: '2026-01-15', siteCode: 'A2', siteName: 'Kiosk A2', actions: 'Routine inspection, Quality control', comments: 'Site in excellent condition. Entrepreneur very motivated.', status: 'completed' },
        { date: '2026-01-16', siteCode: 'D4', siteName: 'Kiosk D4', actions: 'Technical issue follow-up, Water sampling', comments: 'Technical issue resolved successfully.', status: 'completed' },
        { date: '2026-01-20', siteCode: 'E7', siteName: 'Kiosk E7', actions: 'Monthly review, Entrepreneur coaching', comments: 'Need to improve record keeping.', status: 'completed' },
    ],
    '2026-05': [
        { date: '2026-05-04', siteCode: 'A3', siteName: 'Kiosk A3', actions: 'Routine inspection', comments: 'Pump running normally.', status: 'completed' },
        { date: '2026-05-06', siteCode: 'D5', siteName: 'Kiosk D5', actions: 'Site assessment', comments: 'Annual structural review passed.', status: 'completed' },
    ],
}

const visitMonthDate = computed(() => new Date(2026, 0 + visitMonthOffset.value, 1))
const visitMonthLabel = computed(() => visitMonthDate.value.toLocaleDateString('en-US', { month: 'long', year: 'numeric' }))
const visitMonthKey = computed(() => `${visitMonthDate.value.getFullYear()}-${String(visitMonthDate.value.getMonth() + 1).padStart(2, '0')}`)
const visitRecords = computed(() => visitHistoryData[visitMonthKey.value] ?? [])

const prevVisitMonth = () => { visitMonthOffset.value-- }
const nextVisitMonth = () => { visitMonthOffset.value++ }
</script>

<style scoped>
.schedule-icon {
    width: 36px;
    height: 36px;
    border-radius: 10px;
    background: linear-gradient(135deg, #1565C0, #1976D2);
}

.visit-history-table :deep(thead th) {
    font-size: 11px !important;
    font-weight: 700 !important;
    text-transform: uppercase;
    letter-spacing: .06em;
    color: #616161 !important;
    background: #f8f9fa !important;
    white-space: nowrap;
}

.visit-history-table :deep(tbody tr:hover td) {
    background: #f5f8ff;
}
</style>
