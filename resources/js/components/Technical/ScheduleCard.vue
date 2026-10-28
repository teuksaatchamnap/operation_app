<template>
    <div class="px-6 pb-6">
        <v-card rounded="lg" elevation="2">

            <!-- Card header -->
            <div class="schedule-header px-5 py-4 d-flex align-center justify-space-between">
                <div class="d-flex align-center ga-3">
                    <div class="schedule-icon d-flex align-center justify-center">
                        <v-icon color="white" size="20">mdi-calendar-clock</v-icon>
                    </div>
                    <!-- Daily view: show day name + prev/next -->
                    <template v-if="!isCalendarView">
                        <v-btn icon size="x-small" variant="outlined" @click="dayOffset--">
                            <v-icon size="16">mdi-chevron-left</v-icon>
                        </v-btn>
                        <div>
                            <div class="text-subtitle-1 font-weight-bold">My Schedule – {{ scheduleDate.dayName }}
                            </div>
                            <div class="text-caption text-medium-emphasis">{{ scheduleDate.fullDate }}</div>
                        </div>
                        <v-btn icon size="x-small" variant="outlined" @click="dayOffset++">
                            <v-icon size="16">mdi-chevron-right</v-icon>
                        </v-btn>
                    </template>
                    <!-- Calendar view: static title -->
                    <template v-else>
                        <div>
                            <div class="text-subtitle-1 font-weight-bold">My Schedule</div>
                            <div class="text-caption text-medium-emphasis">{{ calendarMonthLabel }}</div>
                        </div>
                    </template>
                </div>

                <!-- Toggle button -->
                <v-btn variant="outlined" size="small" @click="isCalendarView = !isCalendarView">
                    <v-icon start size="16">{{ isCalendarView ? 'mdi-view-list' : 'mdi-calendar-month' }}</v-icon>
                    {{ isCalendarView ? 'Daily View' : 'Calendar View' }}
                </v-btn>
            </div>

            <v-divider />

            <v-card-text class="pa-5">
                <ScheduleDailyView v-if="!isCalendarView" :tasks="todayTasks" @open="openDetail" />
                <ScheduleCalendarView v-else :month-offset="calMonth" />
            </v-card-text>

            <!-- Footer progress (daily view only) -->
            <template v-if="!isCalendarView">
                <v-divider />
                <div class="px-5 py-3 d-flex align-center justify-space-between">
                    <div class="text-caption text-medium-emphasis">
                        {{ doneCount }} / {{ todayTasks.length }} completed
                    </div>
                    <v-progress-linear
                        :model-value="todayTasks.length ? (doneCount / todayTasks.length) * 100 : 0"
                        color="success" bg-color="#f0f0f0" rounded height="6" style="max-width:140px" />
                </div>
            </template>

        </v-card>

        <!-- Loaded only after the first "Open Details" click -->
        <TaskDetailDialog v-if="selectedTask" v-model="detailDialog" :task="selectedTask"
            :date="scheduleDate.fullDate" @toggle-done="selectedTask.done = !selectedTask.done" />
    </div>
</template>

<script setup>
import { ref, reactive, computed, defineAsyncComponent } from 'vue'
import ScheduleDailyView from './ScheduleDailyView.vue'

const ScheduleCalendarView = defineAsyncComponent(() => import('./ScheduleCalendarView.vue'))
const TaskDetailDialog = defineAsyncComponent(() => import('./TaskDetailDialog.vue'))

const dayOffset = ref(0)
const isCalendarView = ref(false)
const detailDialog = ref(false)
const selectedTask = ref(null)

const openDetail = (task) => { selectedTask.value = task; detailDialog.value = true }

const scheduleDate = computed(() => {
    const d = new Date(2026, 4, 6)
    d.setDate(d.getDate() + dayOffset.value)
    return {
        dayName: d.toLocaleDateString('en-US', { weekday: 'long' }),
        fullDate: d.toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' }),
        day: d.getDate(),
    }
})

// reactive so "Mark Complete" in the dialog updates the footer progress
const allTasks = reactive({
    5: [
        { code: 'A3', time: '08:00', title: 'Routine Check', type: 'RC', typeColor: 'grey-darken-1', site: 'Site A3 – Phnom Penh', note: 'Check pump pressure & filter', technician: 'Sok Dara', priority: 'Low', done: false },
        { code: 'B7', time: '10:30', title: 'Water Sample', type: 'WS', typeColor: 'cyan-darken-1', site: 'Site B7 – Kampong Cham', note: 'Collect 3 samples for lab', technician: 'Chan Piseth', priority: 'Medium', done: false },
        { code: 'C2', time: '14:00', title: 'Issue Follow-up', type: 'Issue', typeColor: 'error', site: 'Site C2 – Siem Reap', note: 'Pump motor not starting', technician: 'Rin Sophea', priority: 'High', done: false },
    ],
    6: [
        { code: 'D5', time: '07:30', title: 'Site Assessment', type: 'SA', typeColor: 'purple', site: 'Site D5 – Battambang', note: 'Annual structural review', technician: 'Sok Dara', priority: 'Medium', done: false },
        { code: 'E1', time: '09:00', title: 'Routine Check', type: 'RC', typeColor: 'grey-darken-1', site: 'Site E1 – Kandal', note: null, technician: 'Heng Vutha', priority: 'Low', done: true },
        { code: 'F4', time: '11:00', title: 'Water Sample', type: 'WS', typeColor: 'cyan-darken-1', site: 'Site F4 – Takeo', note: 'Turbidity test required', technician: 'Chan Piseth', priority: 'Medium', done: false },
        { code: 'G9', time: '15:00', title: 'Critical Issue', type: 'Issue', typeColor: 'error', site: 'Site G9 – Phnom Penh', note: 'Chlorinator failure', technician: 'Rin Sophea', priority: 'High', done: false },
    ],
    7: [
        { code: 'H2', time: '08:30', title: 'Routine Check', type: 'RC', typeColor: 'grey-darken-1', site: 'Site H2 – Prey Veng', note: null, technician: 'Heng Vutha', priority: 'Low', done: false },
    ],
    8: [
        { code: 'A8', time: '09:00', title: 'Water Sample', type: 'WS', typeColor: 'cyan-darken-1', site: 'Site A8 – Kampot', note: 'Monthly water quality check', technician: 'Chan Piseth', priority: 'Medium', done: false },
        { code: 'B3', time: '13:00', title: 'Site Assessment', type: 'SA', typeColor: 'purple', site: 'Site B3 – Kratie', note: null, technician: 'Sok Dara', priority: 'Medium', done: false },
    ],
    12: [
        { code: 'C6', time: '10:00', title: 'Routine Check', type: 'RC', typeColor: 'grey-darken-1', site: 'Site C6 – Phnom Penh', note: null, technician: 'Heng Vutha', priority: 'Low', done: false },
        { code: 'D1', time: '14:30', title: 'Issue Repair', type: 'Issue', typeColor: 'error', site: 'Site D1 – Kampong Speu', note: 'Replace broken pipe valve', technician: 'Rin Sophea', priority: 'High', done: false },
    ],
})

const todayTasks = computed(() => allTasks[scheduleDate.value.day] ?? [])
const doneCount = computed(() => todayTasks.value.filter(t => t.done).length)

// ── Calendar ──────────────────────────────────────────────────────────────────
const calMonth = ref(0) // offset from May 2026

const calendarMonthLabel = computed(() => {
    const d = new Date(2026, 4 + calMonth.value, 1)
    return d.toLocaleDateString('en-US', { month: 'long', year: 'numeric' })
})
</script>

<style scoped>
.schedule-header {
    background: linear-gradient(135deg, #f8faff 0%, #eef2ff 100%);
}

.schedule-icon {
    width: 36px;
    height: 36px;
    border-radius: 10px;
    background: linear-gradient(135deg, #1565C0, #1976D2);
}
</style>
