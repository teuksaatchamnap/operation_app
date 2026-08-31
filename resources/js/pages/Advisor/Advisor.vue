<template>
    <div class="page-wrapper">

        <!-- ── Layout 1: Header / Logo ─────────────────────────────────────────── -->
        <div class="header-bar px-6 py-3 d-flex align-center justify-space-between">
            <div class="d-flex align-center ga-3">
                <!-- Logo mark -->
                <div class="logo-mark d-flex align-center justify-center">
                    <v-icon color="white" size="28">mdi-water-pump</v-icon>
                </div>
                <div>
                    <div class="text-h6 font-weight-bold text-white">TeukSaat 1001</div>

                </div>
            </div>

            <div class="d-flex align-center ga-2">
                <v-chip color="white" variant="outlined" size="small" prepend-icon="mdi-circle" class="status-chip">
                    Live
                </v-chip>
                <v-btn icon variant="text" color="white" size="small">
                    <v-icon>mdi-bell-outline</v-icon>
                </v-btn>
                <v-avatar color="white" size="34">
                    <v-icon color="primary">mdi-account</v-icon>
                </v-avatar>
            </div>
        </div>

        <!-- ── Layout 2: KPI Slider ────────────────────────────────────────────── -->
        <div class="pa-6">
            <div class="d-flex align-center justify-space-between mb-4">
                <div>
                    <div class="text-h6 font-weight-bold">Key Performance Indicators</div>
                    <div class="text-caption text-medium-emphasis">Updated today — May 2026</div>
                </div>
                <div class="d-flex align-center ga-2">
                    <v-btn icon size="small" variant="outlined" :disabled="slideIndex === 0" @click="prev">
                        <v-icon>mdi-chevron-left</v-icon>
                    </v-btn>
                    <v-btn icon size="small" variant="outlined" :disabled="slideIndex >= maxSlide" @click="next">
                        <v-icon>mdi-chevron-right</v-icon>
                    </v-btn>
                </div>
            </div>

            <!-- Slider track -->
            <div class="slider-viewport">
                <div class="slider-track" :style="trackStyle">
                    <div v-for="(kpi, i) in kpiCards" :key="i" class="slider-item">
                        <v-card class="kpi-card h-100" elevation="2" rounded="lg">
                            <!-- Top accent bar -->
                            <div class="kpi-accent" :style="{ background: kpi.color }"></div>

                            <v-card-text class="pa-5">
                                <!-- Icon + title row -->
                                <div class="d-flex align-center justify-space-between mb-3">
                                    <div class="kpi-icon-wrap d-flex align-center justify-center"
                                        :style="{ background: kpi.color + '20' }">
                                        <v-icon :color="kpi.color" size="22">{{ kpi.icon }}</v-icon>
                                    </div>
                                    <v-chip :color="kpi.trendColor" size="x-small" variant="tonal">
                                        <v-icon start size="12">{{ kpi.trendIcon }}</v-icon>
                                        {{ kpi.trendLabel }}
                                    </v-chip>
                                </div>

                                <!-- Value -->
                                <div class="text-h4 font-weight-bold mb-1">{{ kpi.value }}</div>
                                <div class="text-caption text-medium-emphasis mb-3">{{ kpi.unit }}</div>

                                <!-- Title -->
                                <div class="text-body-2 font-weight-semibold mb-1">{{ kpi.title }}</div>
                                <div class="text-caption text-medium-emphasis">{{ kpi.subtitle }}</div>

                                <!-- Progress bar -->
                                <div class="mt-4">
                                    <div class="d-flex justify-space-between mb-1">
                                        <span class="text-caption text-medium-emphasis">Progress</span>
                                        <span class="text-caption font-weight-bold">{{ kpi.progress }}%</span>
                                    </div>
                                    <v-progress-linear :model-value="kpi.progress" :color="kpi.color" bg-color="#f0f0f0"
                                        rounded height="6" />
                                </div>
                            </v-card-text>
                        </v-card>
                    </div>
                </div>
            </div>

            <!-- Dot indicators -->
            <div class="d-flex justify-center ga-1 mt-4">
                <button v-for="n in dotCount" :key="n" class="kpi-dot"
                    :class="{ 'kpi-dot-active': slideIndex === n - 1 }" @click="slideIndex = n - 1" />
            </div>
        </div>

        <!-- ── Layout 3: My Schedule ─────────────────────────────────────────── -->
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

                    <!-- ── Daily View ── -->
                    <template v-if="!isCalendarView">
                        <div v-if="todayTasks.length === 0" class="text-center text-medium-emphasis py-10">
                            <v-icon size="44" color="grey-lighten-1">mdi-calendar-blank-outline</v-icon>
                            <div class="mt-2 text-body-2">No activities scheduled for this day</div>
                        </div>

                        <v-row density="comfortable">
                            <v-col v-for="(task, i) in todayTasks" :key="i" cols="12" md="4">
                                <div class="task-row pa-4 rounded-lg h-100 d-flex flex-column">
                                    <!-- Header: time + type chip -->
                                    <div class="d-flex align-center justify-space-between mb-3">
                                        <div class="d-flex align-center ga-2">
                                            <div class="time-dot" :style="{ background: task.typeColor }"></div>
                                            <span class="text-caption font-weight-bold text-blue-darken-2">{{ task.time
                                                }}</span>
                                        </div>
                                        <v-chip size="x-small" :color="task.typeColor" variant="tonal">{{ task.type
                                            }}</v-chip>
                                    </div>

                                    <!-- Code + title -->
                                    <div class="mb-2">
                                        <div class="text-body-2 font-weight-bold">{{ task.code }} – {{ task.title }}
                                        </div>
                                    </div>

                                    <!-- Site -->
                                    <div class="text-caption text-medium-emphasis mb-1">
                                        <v-icon size="12" class="mr-1">mdi-map-marker-outline</v-icon>{{ task.site }}
                                    </div>

                                    <!-- Note -->
                                    <div v-if="task.note" class="text-caption text-medium-emphasis mb-3">
                                        <v-icon size="12" class="mr-1">mdi-note-outline</v-icon>{{ task.note }}
                                    </div>

                                    <v-spacer />

                                    <!-- Open Details buttons -->
                                    <div class="mt-4 d-flex justify-space-between">
                                        <v-btn variant="outlined" size="x-small" @click="openDetail(task)">
                                            <v-icon start size="12">mdi-open-in-new</v-icon>
                                            Open Details
                                        </v-btn>
                                        <v-btn variant="outlined" size="x-small" @click="siteAnalysis(task)">
                                            <v-icon start size="12">mdi-open-in-new</v-icon>
                                            Site Analysis
                                        </v-btn>
                                    </div>
                                </div>
                            </v-col>
                        </v-row>
                    </template>

                    <!-- ── Calendar View ── -->
                    <template v-else>
                        <div class="cal-grid mb-1">
                            <div v-for="d in ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']" :key="d"
                                class="text-center text-caption font-weight-bold text-medium-emphasis py-1">{{ d }}
                            </div>
                        </div>

                        <div class="cal-grid">
                            <div v-for="(cell, idx) in calendarGrid" :key="idx" class="cal-cell rounded" :class="[
                                cell.isWeekend ? 'cal-weekend' : '',
                                cell.isToday ? 'cal-today' : '',
                                cell.isSelected ? 'cal-selected' : '',
                                cell.day ? 'cal-clickable' : '',
                            ]" @click="cell.day && selectDay(cell.day)">
                                <template v-if="cell.day">
                                    <div class="cal-day-num" :class="cell.isToday ? 'cal-today-num' : ''">{{ cell.day }}
                                    </div>
                                    <div class="cal-events">
                                        <div v-for="(ev, ei) in cell.events.slice(0, 2)" :key="ei" class="cal-pill"
                                            :class="ev.colorClass">{{ ev.label }}</div>
                                        <div v-if="cell.events.length > 2" class="cal-pill cal-more">+{{
                                            cell.events.length - 2 }}</div>
                                    </div>
                                </template>
                            </div>
                        </div>

                        <!-- Legend -->
                        <div class="mt-4 pt-3 d-flex flex-wrap ga-3" style="border-top:1px solid #e0e0e0">
                            <div v-for="leg in legend" :key="leg.label" class="d-flex align-center ga-1">
                                <div class="legend-swatch" :class="leg.colorClass"></div>
                                <span class="text-caption text-medium-emphasis">{{ leg.label }}</span>
                            </div>
                        </div>
                    </template>

                </v-card-text>

                <!-- Footer progress (daily view only) -->
                <template v-if="!isCalendarView">
                    <v-divider />
                    <div class="px-5 py-3 d-flex align-center justify-space-between">
                        <div class="text-caption text-medium-emphasis">
                            {{todayTasks.filter(t => t.done).length}} / {{ todayTasks.length }} completed
                        </div>
                        <v-progress-linear
                            :model-value="todayTasks.length ? (todayTasks.filter(t => t.done).length / todayTasks.length) * 100 : 0"
                            color="success" bg-color="#f0f0f0" rounded height="6" style="max-width:140px" />
                    </div>
                </template>

            </v-card>
        </div>

        <!-- ── Layout 4: Quick Actions ───────────────────────────────────────── -->
        <div class="px-6 pb-6">
            <div class="d-flex align-center justify-space-between mb-3">
                <span class="text-subtitle-2 font-weight-bold text-medium-emphasis text-uppercase"
                    style="letter-spacing:.08em">Quick Actions</span>
                <v-divider class="ml-3 flex-1" />
            </div>
            <v-card elevation="1" rounded="lg" class="pa-3">
                <div class="d-flex align-center flex-wrap ga-2">
                    <v-btn variant="tonal" color="blue-darken-2" size="small" class="erp-btn"
                        @click="createIssueDialog = true">
                        <v-icon start size="15">mdi-wrench</v-icon>
                        Request Consumable
                    </v-btn>

                    <v-divider vertical class="mx-1" style="height:24px" />

                    <v-btn variant="tonal" color="green-darken-2" size="small" class="erp-btn"
                        @click="routineCheckDialog = true">
                        <v-icon start size="15">mdi-clipboard-check</v-icon>
                        Manage Entrepreneur
                    </v-btn>

                    <v-divider vertical class="mx-1" style="height:24px" />

                    <v-btn variant="tonal" color="orange-darken-2" size="small" class="erp-btn"
                        @click="siteAssessmentDialog = true">
                        <v-icon start size="15">mdi-file-document-outline</v-icon>
                        School Program
                    </v-btn>

                    <v-divider vertical class="mx-1" style="height:24px" />

                    <v-btn variant="tonal" color="teal-darken-1" size="small" class="erp-btn"
                        @click="waterSampleDialog = true">
                        <v-icon start size="15">mdi-water</v-icon>
                        Technical Issue
                    </v-btn>
                </div>
            </v-card>
        </div>

        <!-- Request Consumable Dialog -->
        <v-dialog v-model="createIssueDialog" max-width="800" scrollable>
            <div style="position:relative">
                <v-btn icon size="small" variant="flat" color="white"
                    style="position:absolute; top:12px; right:12px; z-index:10;"
                    @click="createIssueDialog = false">
                    <v-icon>mdi-close</v-icon>
                </v-btn>
                <RequestConsumable @close="createIssueDialog = false" />
            </div>
        </v-dialog>

        <!-- Manage Entrepreneur Dialog -->
        <v-dialog v-model="routineCheckDialog" max-width="900" scrollable>
            <div style="position:relative">
                <v-btn icon size="small" variant="flat" color="white"
                    style="position:absolute; top:12px; right:12px; z-index:10;"
                    @click="routineCheckDialog = false">
                    <v-icon>mdi-close</v-icon>
                </v-btn>
                <EntrepreneurForm />
            </div>
        </v-dialog>

        <!-- Site Assessment Dialog -->
        <v-dialog v-model="siteAssessmentDialog" max-width="480">
            <v-card rounded="xl">
                <div class="qa-dialog-header pa-5 d-flex align-center justify-space-between"
                    style="background:linear-gradient(135deg,#E65100,#FB8C00)">
                    <div class="d-flex align-center ga-2">
                        <v-icon color="white">mdi-file-document-outline</v-icon>
                        <span class="text-subtitle-1 font-weight-bold text-white">Site Assessment</span>
                    </div>
                    <v-btn icon size="small" variant="text" color="white" @click="siteAssessmentDialog = false">
                        <v-icon>mdi-close</v-icon>
                    </v-btn>
                </div>
                <v-card-text class="pa-5">
                    <v-text-field label="Site Code" placeholder="e.g., A3" variant="outlined" density="comfortable"
                        class="mb-3" />
                    <v-select label="Assessment Type"
                        :items="['Structural', 'Water Quality', 'Equipment', 'Safety', 'Full Assessment']"
                        variant="outlined" density="comfortable" class="mb-3" />
                    <v-text-field label="Assessor Name" placeholder="Your name" variant="outlined" density="comfortable"
                        class="mb-3" />
                    <v-textarea label="Findings" placeholder="Summarise your findings" variant="outlined"
                        density="comfortable" rows="3" />
                </v-card-text>
                <v-card-actions class="pa-5 pt-0">
                    <v-btn variant="text" @click="siteAssessmentDialog = false">Cancel</v-btn>
                    <v-spacer />
                    <v-btn color="warning" variant="flat" rounded="lg" @click="siteAssessmentDialog = false">Submit
                        Assessment</v-btn>
                </v-card-actions>
            </v-card>
        </v-dialog>

        <!-- Water Sample Dialog -->
        <v-dialog v-model="waterSampleDialog" max-width="480">
            <v-card rounded="xl">
                <div class="qa-dialog-header pa-5 d-flex align-center justify-space-between"
                    style="background:linear-gradient(135deg,#00695C,#26A69A)">
                    <div class="d-flex align-center ga-2">
                        <v-icon color="white">mdi-water</v-icon>
                        <span class="text-subtitle-1 font-weight-bold text-white">Water Sample</span>
                    </div>
                    <v-btn icon size="small" variant="text" color="white" @click="waterSampleDialog = false">
                        <v-icon>mdi-close</v-icon>
                    </v-btn>
                </div>
                <v-card-text class="pa-5">
                    <v-text-field label="Site Code" placeholder="e.g., A3" variant="outlined" density="comfortable"
                        class="mb-3" />
                    <v-text-field label="Sample ID" placeholder="e.g., WS-2026-001" variant="outlined"
                        density="comfortable" class="mb-3" />
                    <v-select label="Test Type" :items="['Turbidity', 'Chlorine Level', 'pH', 'Bacteria', 'Full Panel']"
                        variant="outlined" density="comfortable" class="mb-3" />
                    <v-textarea label="Notes" placeholder="Additional notes about the sample" variant="outlined"
                        density="comfortable" rows="2" />
                </v-card-text>
                <v-card-actions class="pa-5 pt-0">
                    <v-btn variant="text" @click="waterSampleDialog = false">Cancel</v-btn>
                    <v-spacer />
                    <v-btn color="teal" variant="flat" rounded="lg" @click="waterSampleDialog = false">Submit
                        Sample</v-btn>
                </v-card-actions>
            </v-card>
        </v-dialog>

        <!-- ── Layout 5: Issues Table ────────────────────────────────────────── -->
        <!-- <div class="px-6 pb-6">
            <v-card rounded="lg" elevation="2">


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

                    <template #item.problemType="{ item }">
                        <v-chip size="x-small" variant="outlined">{{ item.problemType || '–' }}</v-chip>
                    </template>


                    <template #item.siteStatus="{ item }">
                        <v-chip
                            size="x-small" variant="tonal"
                            :color="item.siteStatus === 'Can Produce' ? 'success' : 'error'"
                        >{{ item.siteStatus }}</v-chip>
                    </template>


                    <template #item.urgency="{ item }">
                        <v-chip size="x-small" variant="tonal" :color="urgencyColor(item.urgency)">
                            {{ item.urgency }}
                        </v-chip>
                    </template>


                    <template #item.status="{ item }">
                        <v-chip size="x-small" variant="outlined">{{ item.status }}</v-chip>
                    </template>


                    <template #item.sla="{ item }">
                        <span class="text-body-2 font-weight-medium" :class="slaColor(item.sla)">{{ item.sla }}h</span>
                    </template>


                    <template #item.planDate="{ item }">
                        <span class="text-body-2">{{ item.planDate || '—' }}</span>
                    </template>


                    <template #item.actions="{ item }">
                        <v-btn
                            size="x-small" variant="tonal" color="primary"
                            @click.stop="openIssue(item)"
                        >
                            <v-icon start size="12">mdi-eye-outline</v-icon>
                            Detail
                        </v-btn>
                    </template>


                    <template #no-data>
                        <div class="text-center text-medium-emphasis pa-8">
                            <v-icon size="40" color="grey-lighten-2" class="mb-2">mdi-table-search</v-icon>
                            <div>No issues found</div>
                        </div>
                    </template>
                </v-data-table>

            </v-card>
        </div> -->

        <!-- ── Layout 6: Visit History ───────────────────────────────────────── -->
        <div class="px-6 pb-6">
            <v-card rounded="lg" elevation="2">
                <div class="px-5 pt-4 pb-3">
                    <div class="d-flex align-center ga-2">
                        <v-icon size="20">mdi-calendar-search</v-icon>
                        <span class="text-subtitle-1 font-weight-bold">Visit History – {{ visitMonthLabel }}</span>
                    </div>
                    <div class="text-caption text-medium-emphasis mt-1">View past site visits</div>
                </div>

                <div class="px-5 pb-4 d-flex justify-space-between">
                    <v-btn variant="outlined" size="small" rounded="lg" @click="prevVisitMonth">
                        <v-icon start size="16">mdi-chevron-left</v-icon>
                        Previous Month
                    </v-btn>
                    <v-btn variant="outlined" size="small" rounded="lg" @click="nextVisitMonth">
                        Next Month
                        <v-icon end size="16">mdi-chevron-right</v-icon>
                    </v-btn>
                </div>

                <v-divider />

                <v-table v-if="visitHistory.length" density="comfortable" class="visit-history-table">
                    <thead>
                        <tr>
                            <th>Date</th>
                            <th>Site Code</th>
                            <th>Site Name</th>
                            <th>Actions Performed</th>
                            <th>Comments</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="visit in visitHistory" :key="visit.date + visit.siteCode">
                            <td>{{ visit.date }}</td>
                            <td class="font-weight-bold">{{ visit.siteCode }}</td>
                            <td>{{ visit.siteName }}</td>
                            <td>{{ visit.actions }}</td>
                            <td>{{ visit.comments }}</td>
                            <td>
                                <v-chip size="small" color="success" variant="tonal">{{ visit.status }}</v-chip>
                            </td>
                        </tr>
                    </tbody>
                </v-table>

                <div v-else class="text-center text-medium-emphasis pa-8">
                    <v-icon size="40" color="grey-lighten-2" class="mb-2">mdi-calendar-remove-outline</v-icon>
                    <div>No visits recorded for this month</div>
                </div>
            </v-card>
        </div>

        <!-- Issue Detail Dialog -->
        <v-dialog v-model="issueDialog" max-width="760" scrollable>
            <v-card v-if="selectedIssue" rounded="xl">
                <div class="issue-dialog-header px-6 py-5 d-flex align-start justify-space-between">
                    <div>
                        <div class="d-flex align-center ga-2 mb-1">
                            <v-chip :color="urgencyColor(selectedIssue.urgency)" size="small" variant="flat" class="font-weight-bold">
                                {{ selectedIssue.urgency }}
                            </v-chip>
                            <span class="text-h6 font-weight-bold text-white">{{ selectedIssue.kioskCode }}</span>
                        </div>
                        <div class="text-body-2 text-white" style="opacity:.85">{{ selectedIssue.title }}</div>
                    </div>
                    <v-btn icon size="small" variant="text" color="white" @click="issueDialog = false">
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
                                    <v-row density="comfortable">
                                        <v-col cols="6">
                                            <div class="text-caption text-medium-emphasis">Problem Type</div>
                                            <div class="text-body-2 font-weight-bold mt-1">{{ selectedIssue.problemType || 'Not specified' }}</div>
                                        </v-col>
                                        <v-col cols="6">
                                            <div class="text-caption text-medium-emphasis">Site Status</div>
                                            <v-chip class="mt-1" size="small" :color="selectedIssue.siteStatus === 'Can Produce' ? 'success' : 'error'" variant="tonal">
                                                {{ selectedIssue.siteStatus || 'Unknown' }}
                                            </v-chip>
                                        </v-col>
                                        <v-col cols="6">
                                            <div class="text-caption text-medium-emphasis">Urgency</div>
                                            <v-chip class="mt-1" size="small" :color="urgencyColor(selectedIssue.urgency)" variant="tonal">{{ selectedIssue.urgency }}</v-chip>
                                        </v-col>
                                        <v-col cols="6">
                                            <div class="text-caption text-medium-emphasis">Open Time</div>
                                            <div class="text-body-2 font-weight-bold mt-1" :class="slaColor(selectedIssue.sla)">{{ selectedIssue.sla }}h</div>
                                        </v-col>
                                        <v-col cols="6">
                                            <div class="text-caption text-medium-emphasis mb-1">Issue Status</div>
                                            <v-select :items="statusOptions" density="compact" variant="outlined" hide-details :model-value="selectedIssue.status" style="max-width:200px" />
                                        </v-col>
                                        <v-col cols="6">
                                            <div class="text-caption text-medium-emphasis">Plan Date</div>
                                            <div class="text-body-2 font-weight-bold mt-1">{{ selectedIssue.planDate || 'Not scheduled' }}</div>
                                        </v-col>
                                        <v-col cols="6">
                                            <div class="text-caption text-medium-emphasis">Assigned To</div>
                                            <div class="text-body-2 font-weight-bold mt-1">{{ selectedIssue.assignedTo }}</div>
                                        </v-col>
                                        <v-col cols="6">
                                            <div class="text-caption text-medium-emphasis">Platform</div>
                                            <div class="text-body-2 font-weight-bold mt-1">{{ selectedIssue.platform }}</div>
                                        </v-col>
                                        <v-col cols="12">
                                            <div class="text-caption text-medium-emphasis">Description</div>
                                            <div class="text-body-2 mt-1">{{ selectedIssue.description }}</div>
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
                    <v-btn variant="text" @click="issueDialog = false">Close</v-btn>
                </v-card-actions>
            </v-card>
        </v-dialog>

        <!-- ── Task Detail Dialog ──────────────────────────────────────────────── -->
        <v-dialog v-model="detailDialog" max-width="520">
            <v-card rounded="xl" v-if="selectedTask">
                <!-- Header -->
                <div class="detail-dialog-header px-6 py-5 d-flex align-start justify-space-between">
                    <div>
                        <div class="d-flex align-center ga-2 mb-1">
                            <v-chip :color="selectedTask.typeColor" size="small" variant="flat"
                                class="text-white font-weight-bold">
                                {{ selectedTask.type }}
                            </v-chip>
                            <span class="text-h6 font-weight-bold text-white">{{ selectedTask.code }}</span>
                        </div>
                        <div class="text-body-2 text-white" style="opacity:.85">{{ selectedTask.title }}</div>
                    </div>
                    <v-btn icon size="small" variant="text" color="white" @click="detailDialog = false">
                        <v-icon>mdi-close</v-icon>
                    </v-btn>
                </div>

                <v-card-text class="pa-6">
                    <!-- Info rows -->
                    <v-row density="comfortable">
                        <v-col cols="6">
                            <div class="detail-info-block pa-3 rounded-lg">
                                <div class="text-caption text-medium-emphasis mb-1">
                                    <v-icon size="12" class="mr-1">mdi-clock-outline</v-icon>Scheduled Time
                                </div>
                                <div class="text-body-2 font-weight-bold">{{ selectedTask.time }}</div>
                            </div>
                        </v-col>
                        <v-col cols="6">
                            <div class="detail-info-block pa-3 rounded-lg">
                                <div class="text-caption text-medium-emphasis mb-1">
                                    <v-icon size="12" class="mr-1">mdi-calendar-outline</v-icon>Date
                                </div>
                                <div class="text-body-2 font-weight-bold">{{ scheduleDate.fullDate }}</div>
                            </div>
                        </v-col>
                        <v-col cols="12">
                            <div class="detail-info-block pa-3 rounded-lg">
                                <div class="text-caption text-medium-emphasis mb-1">
                                    <v-icon size="12" class="mr-1">mdi-map-marker-outline</v-icon>Site Location
                                </div>
                                <div class="text-body-2 font-weight-bold">{{ selectedTask.site }}</div>
                            </div>
                        </v-col>
                        <v-col cols="12" v-if="selectedTask.note">
                            <div class="detail-info-block pa-3 rounded-lg">
                                <div class="text-caption text-medium-emphasis mb-1">
                                    <v-icon size="12" class="mr-1">mdi-note-text-outline</v-icon>Notes
                                </div>
                                <div class="text-body-2">{{ selectedTask.note }}</div>
                            </div>
                        </v-col>
                        <v-col cols="12">
                            <div class="detail-info-block pa-3 rounded-lg">
                                <div class="text-caption text-medium-emphasis mb-1">
                                    <v-icon size="12" class="mr-1">mdi-account-outline</v-icon>Assigned Technician
                                </div>
                                <div class="text-body-2 font-weight-bold">{{ selectedTask.technician }}</div>
                            </div>
                        </v-col>
                        <v-col cols="6">
                            <div class="detail-info-block pa-3 rounded-lg">
                                <div class="text-caption text-medium-emphasis mb-1">
                                    <v-icon size="12" class="mr-1">mdi-flag-outline</v-icon>Priority
                                </div>
                                <v-chip
                                    :color="selectedTask.priority === 'High' ? 'error' : selectedTask.priority === 'Medium' ? 'warning' : 'success'"
                                    size="x-small" variant="tonal">
                                    {{ selectedTask.priority }}
                                </v-chip>
                            </div>
                        </v-col>
                        <v-col cols="6">
                            <div class="detail-info-block pa-3 rounded-lg">
                                <div class="text-caption text-medium-emphasis mb-1">
                                    <v-icon size="12" class="mr-1">mdi-check-circle-outline</v-icon>Status
                                </div>
                                <v-chip :color="selectedTask.done ? 'success' : 'warning'" size="x-small"
                                    variant="tonal">
                                    {{ selectedTask.done ? 'Completed' : 'Pending' }}
                                </v-chip>
                            </div>
                        </v-col>
                    </v-row>
                </v-card-text>

                <v-divider />
                <v-card-actions class="pa-4 ga-2">
                    <v-btn variant="outlined" rounded="lg" @click="detailDialog = false">Close</v-btn>
                    <v-spacer />
                    <v-btn :color="selectedTask.done ? 'grey' : 'success'" variant="flat" rounded="lg"
                        @click="selectedTask.done = !selectedTask.done">
                        <v-icon start>{{ selectedTask.done ? 'mdi-refresh' : 'mdi-check' }}</v-icon>
                        {{ selectedTask.done ? 'Mark Pending' : 'Mark Complete' }}
                    </v-btn>
                </v-card-actions>
            </v-card>
        </v-dialog>

        <!-- ── Site Analysis Dialog ────────────────────────────────────────────── -->
        <v-dialog v-model="siteAnalysisDialog" max-width="1400" scrollable>
            <v-card rounded="xl" v-if="selectedSiteTask && siteMockData">
                <div class="detail-dialog-header px-6 py-5 d-flex align-start justify-space-between">
                    <div>
                        <div class="d-flex align-center ga-2 mb-1">
                            <v-icon color="white">mdi-chart-box-outline</v-icon>
                            <span class="text-h6 font-weight-bold text-white">{{ selectedSiteTask.code }} — Site Analysis</span>
                        </div>
                        <div class="text-body-2 text-white" style="opacity:.85">{{ selectedSiteTask.site }}</div>
                    </div>
                    <v-btn icon size="small" variant="text" color="white" @click="siteAnalysisDialog = false">
                        <v-icon>mdi-close</v-icon>
                    </v-btn>
                </div>

                <v-tabs v-model="siteAnalysisTab" bg-color="grey-lighten-4">
                    <v-tab value="analysis">Site Analysis</v-tab>
                    <v-tab value="sales">Sales</v-tab>
                    <v-tab value="pnl">P&amp;L</v-tab>
                    <v-tab value="technical">Technical</v-tab>
                    <v-tab value="site">Site</v-tab>
                </v-tabs>

                <v-divider />

                <v-card-text class="pa-5">
                    <v-tabs-window v-model="siteAnalysisTab">

                        <!-- Site Analysis -->
                        <v-tabs-window-item value="analysis">
                            <v-card variant="outlined" rounded="lg" class="mb-4">
                                <v-card-title class="text-subtitle-2 font-weight-bold">General Details</v-card-title>
                                <v-card-text>
                                    <v-row density="comfortable">
                                        <v-col cols="4">
                                            <div class="text-caption text-medium-emphasis">Platform</div>
                                            <div class="text-body-2 font-weight-bold">{{ siteMockData.profile.platform }}</div>
                                        </v-col>
                                        <v-col cols="4">
                                            <div class="text-caption text-medium-emphasis">Entrepreneur</div>
                                            <div class="text-body-2 font-weight-bold">{{ siteMockData.profile.entrepreneur }}</div>
                                        </v-col>
                                        <v-col cols="4">
                                            <div class="text-caption text-medium-emphasis">Advisor</div>
                                            <div class="text-body-2 font-weight-bold">{{ siteMockData.profile.advisor }}</div>
                                        </v-col>
                                        <v-col cols="4">
                                            <div class="text-caption text-medium-emphasis">Start Working Date</div>
                                            <div class="text-body-2 font-weight-bold">{{ siteMockData.profile.startDate }}</div>
                                        </v-col>
                                        <v-col cols="4">
                                            <div class="text-caption text-medium-emphasis">Population (Commune)</div>
                                            <div class="text-body-2 font-weight-bold">{{ siteMockData.profile.population.toLocaleString() }}</div>
                                        </v-col>
                                        <v-col cols="4">
                                            <div class="text-caption text-medium-emphasis">Treatment Process</div>
                                            <div class="text-body-2 font-weight-bold">{{ siteMockData.profile.treatment }}</div>
                                        </v-col>
                                    </v-row>
                                </v-card-text>
                            </v-card>

                            <v-card variant="outlined" rounded="lg">
                                <v-card-title class="text-subtitle-2 font-weight-bold">Site KPI</v-card-title>
                                <v-card-text>
                                    <v-row density="comfortable">
                                        <v-col v-for="kpi in siteMockData.kpis" :key="kpi.label" cols="3">
                                            <div class="text-caption text-medium-emphasis">{{ kpi.label }}</div>
                                            <div class="text-body-2 font-weight-bold d-flex align-center ga-1">
                                                <v-icon size="x-small" :color="kpi.value >= kpi.objective ? 'success' : 'error'">mdi-circle</v-icon>
                                                {{ kpi.value }} / {{ kpi.objective }}
                                            </div>
                                        </v-col>
                                    </v-row>
                                </v-card-text>
                            </v-card>
                        </v-tabs-window-item>

                        <!-- Sales -->
                        <v-tabs-window-item value="sales">
                            <v-card variant="outlined" rounded="lg">
                                <v-card-title class="text-subtitle-2 font-weight-bold">Sales by Channel — Last 5 Days</v-card-title>
                                <v-card-text>
                                    <v-table density="compact">
                                        <thead>
                                            <tr>
                                                <th>Date</th>
                                                <th v-for="ch in siteMockData.sales.channels" :key="ch" class="text-right">{{ ch }}</th>
                                                <th class="text-right">Total</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            <tr v-for="row in siteMockData.sales.rows" :key="row.date">
                                                <td class="font-weight-medium">{{ row.date }}</td>
                                                <td v-for="(v, i) in row.values" :key="i" class="text-right">{{ v }}</td>
                                                <td class="text-right font-weight-bold">{{ row.total }}</td>
                                            </tr>
                                        </tbody>
                                    </v-table>
                                </v-card-text>
                            </v-card>
                        </v-tabs-window-item>

                        <!-- P&L -->
                        <v-tabs-window-item value="pnl">
                            <v-card variant="outlined" rounded="lg">
                                <v-card-title class="text-subtitle-2 font-weight-bold">Income &amp; Expenses (MTD)</v-card-title>
                                <v-card-text>
                                    <v-table density="compact">
                                        <thead><tr><th>Revenue</th><th class="text-right">Amount ($)</th></tr></thead>
                                        <tbody>
                                            <tr v-for="r in siteMockData.pnl.revenue" :key="r.label">
                                                <td>{{ r.label }}</td>
                                                <td class="text-right">{{ r.amount }}</td>
                                            </tr>
                                            <tr class="font-weight-bold">
                                                <td>Total Revenue</td>
                                                <td class="text-right">{{ siteMockData.pnl.revenueTotal }}</td>
                                            </tr>
                                        </tbody>
                                    </v-table>
                                    <v-table density="compact" class="mt-4">
                                        <thead><tr><th>Expenses</th><th class="text-right">Amount ($)</th></tr></thead>
                                        <tbody>
                                            <tr v-for="e in siteMockData.pnl.expenses" :key="e.label">
                                                <td>{{ e.label }}</td>
                                                <td class="text-right">{{ e.amount }}</td>
                                            </tr>
                                            <tr class="font-weight-bold">
                                                <td>Total Expenses</td>
                                                <td class="text-right">{{ siteMockData.pnl.expensesTotal }}</td>
                                            </tr>
                                        </tbody>
                                    </v-table>
                                    <div class="mt-4 d-flex justify-space-between align-center pa-3 rounded-lg"
                                        :class="siteMockData.pnl.net >= 0 ? 'bg-green-lighten-5' : 'bg-red-lighten-5'">
                                        <span class="font-weight-bold text-uppercase">Net Result</span>
                                        <span class="font-weight-bold" :class="siteMockData.pnl.net >= 0 ? 'text-success' : 'text-error'">
                                            ${{ siteMockData.pnl.net }}
                                        </span>
                                    </div>
                                </v-card-text>
                            </v-card>
                        </v-tabs-window-item>

                        <!-- Technical -->
                        <v-tabs-window-item value="technical">
                            <v-card variant="outlined" rounded="lg" class="mb-4">
                                <v-card-title class="text-subtitle-2 font-weight-bold">Equipment Status</v-card-title>
                                <v-card-text>
                                    <v-table density="compact">
                                        <thead><tr><th>Equipment</th><th>Status</th><th>Last Service</th></tr></thead>
                                        <tbody>
                                            <tr v-for="eq in siteMockData.technical.equipment" :key="eq.name">
                                                <td>{{ eq.name }}</td>
                                                <td>
                                                    <v-chip size="x-small" :color="eq.status === 'Operational' ? 'success' : 'warning'" variant="tonal">
                                                        {{ eq.status }}
                                                    </v-chip>
                                                </td>
                                                <td>{{ eq.lastService }}</td>
                                            </tr>
                                        </tbody>
                                    </v-table>
                                </v-card-text>
                            </v-card>
                            <div class="d-flex ga-6">
                                <div class="text-caption text-medium-emphasis">
                                    Last Routine Check:
                                    <span class="font-weight-bold text-body-2">{{ siteMockData.technical.lastCheck }}</span>
                                </div>
                                <div class="text-caption text-medium-emphasis">
                                    Open Technical Issues:
                                    <span class="font-weight-bold text-body-2">{{ siteMockData.technical.openIssues }}</span>
                                </div>
                            </div>
                        </v-tabs-window-item>

                        <!-- Site -->
                        <v-tabs-window-item value="site">
                            <v-card variant="outlined" rounded="lg">
                                <v-card-title class="text-subtitle-2 font-weight-bold">Location &amp; Demographics</v-card-title>
                                <v-card-text>
                                    <v-row density="comfortable">
                                        <v-col cols="4">
                                            <div class="text-caption text-medium-emphasis">Village</div>
                                            <div class="text-body-2 font-weight-bold">{{ siteMockData.site.village }}</div>
                                        </v-col>
                                        <v-col cols="4">
                                            <div class="text-caption text-medium-emphasis">Commune</div>
                                            <div class="text-body-2 font-weight-bold">{{ siteMockData.site.commune }}</div>
                                        </v-col>
                                        <v-col cols="4">
                                            <div class="text-caption text-medium-emphasis">District</div>
                                            <div class="text-body-2 font-weight-bold">{{ siteMockData.site.district }}</div>
                                        </v-col>
                                        <v-col cols="4">
                                            <div class="text-caption text-medium-emphasis">Province</div>
                                            <div class="text-body-2 font-weight-bold">{{ siteMockData.site.province }}</div>
                                        </v-col>
                                        <v-col cols="4">
                                            <div class="text-caption text-medium-emphasis">Villages in Commune</div>
                                            <div class="text-body-2 font-weight-bold">{{ siteMockData.site.villagesInCommune }}</div>
                                        </v-col>
                                        <v-col cols="4">
                                            <div class="text-caption text-medium-emphasis">Coordinates</div>
                                            <div class="text-body-2 font-weight-bold">{{ siteMockData.site.lat }}°N, {{ siteMockData.site.lng }}°E</div>
                                        </v-col>
                                    </v-row>
                                </v-card-text>
                            </v-card>
                        </v-tabs-window-item>

                    </v-tabs-window>
                </v-card-text>

                <v-divider />
                <v-card-actions class="pa-4">
                    <v-btn variant="text" @click="siteAnalysisDialog = false">Close</v-btn>
                </v-card-actions>
            </v-card>
        </v-dialog>

    </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import RequestConsumable from './RequestConsumable.vue'
import EntrepreneurForm from './EntrepreneurForm.vue'

// ── KPI Data (fake) ───────────────────────────────────────────────────────────
const kpiCards = [
    {
        title: 'Active Site',
        subtitle: 'Active technical problems',
        value: '24',
        unit: 'issues pending',
        icon: 'mdi-alert-circle-outline',
        color: '#EF5350',
        progress: 60,
        trendLabel: '+3 this week',
        trendColor: 'error',
        trendIcon: 'mdi-trending-up',
    },
    {
        title: 'Super Tier 1',
        subtitle: 'Issues closed in May 2026',
        value: '47',
        unit: 'issues resolved',
        icon: 'mdi-check-circle-outline',
        color: '#66BB6A',
        progress: 78,
        trendLabel: '+12 vs last month',
        trendColor: 'success',
        trendIcon: 'mdi-trending-up',
    },
    {
        title: 'Bottle Per day',
        subtitle: 'Total sale ',
        value: '18h',
        unit: 'hours average',
        icon: 'mdi-timer-outline',
        color: '#42A5F5',
        progress: 55,
        trendLabel: '-2h improved',
        trendColor: 'success',
        trendIcon: 'mdi-trending-down',
    },
    {
        title: 'Sale Volume',
        subtitle: 'Sale',
        value: '31',
        unit: 'sites',
        icon: 'mdi-map-marker-outline',
        color: '#AB47BC',
        progress: 82,
        trendLabel: 'On track',
        trendColor: 'secondary',
        trendIcon: 'mdi-minus',
    },
    {
        title: 'Routine Checks Done',
        subtitle: 'Scheduled checks completed',
        value: '68%',
        unit: 'completion rate',
        icon: 'mdi-clipboard-check-outline',
        color: '#FFA726',
        progress: 68,
        trendLabel: '-5% vs target',
        trendColor: 'warning',
        trendIcon: 'mdi-trending-down',
    },
    {
        title: 'Water Samples Taken',
        subtitle: 'Lab samples this month',
        value: '19',
        unit: 'samples',
        icon: 'mdi-water-outline',
        color: '#26C6DA',
        progress: 90,
        trendLabel: '+4 vs last month',
        trendColor: 'info',
        trendIcon: 'mdi-trending-up',
    },
    {
        title: 'Critical SLA Breaches',
        subtitle: 'Overdue critical tickets',
        value: '3',
        unit: 'breached SLA',
        icon: 'mdi-alert-outline',
        color: '#EC407A',
        progress: 25,
        trendLabel: '-1 vs last week',
        trendColor: 'success',
        trendIcon: 'mdi-trending-down',
    },
    {
        title: 'Technicians Active',
        subtitle: 'On-field this week',
        value: '8',
        unit: 'technicians',
        icon: 'mdi-account-hard-hat-outline',
        color: '#8D6E63',
        progress: 100,
        trendLabel: 'Full team',
        trendColor: 'success',
        trendIcon: 'mdi-check',
    },
]

// ── Slider logic ──────────────────────────────────────────────────────────────
const visibleCount = 4   // cards visible at once
const slideIndex = ref(0)
const maxSlide = computed(() => kpiCards.length - visibleCount)
const dotCount = computed(() => Math.max(1, kpiCards.length - visibleCount + 1))

const trackStyle = computed(() => ({
    transform: `translateX(-${slideIndex.value * (100 / visibleCount)}%)`,
    transition: 'transform 0.45s cubic-bezier(0.25, 0.46, 0.45, 0.94)',
}))

const prev = () => { if (slideIndex.value > 0) slideIndex.value-- }
const next = () => { if (slideIndex.value < maxSlide.value) slideIndex.value++ }

// ── Schedule ──────────────────────────────────────────────────────────────────
const dayOffset = ref(0)
const isCalendarView = ref(false)
const detailDialog = ref(false)
const selectedTask = ref(null)

const openDetail = (task) => { selectedTask.value = task; detailDialog.value = true }

// ── Site Analysis (mock) ───────────────────────────────────────────────────
const siteAnalysisDialog = ref(false)
const siteAnalysisTab = ref('analysis')
const selectedSiteTask = ref(null)

const siteAnalysis = (task) => {
    selectedSiteTask.value = task
    siteAnalysisTab.value = 'analysis'
    siteAnalysisDialog.value = true
}

const rnd = (min, max) => Math.floor(min + Math.random() * (max - min))
const rndf = (min, max, dp = 1) => (min + Math.random() * (max - min)).toFixed(dp)
const pick = (arr) => arr[Math.floor(Math.random() * arr.length)]

const siteMockData = computed(() => {
    const task = selectedSiteTask.value
    if (!task) return null

    const revenue = [
        { label: 'Home Delivery', amount: rnd(150, 400) },
        { label: 'Shopkeeper', amount: rnd(80, 200) },
        { label: 'On-Site', amount: rnd(60, 150) },
        { label: 'Water in School', amount: rnd(30, 90) },
    ]
    const expenses = [
        { label: 'Electricity', amount: rnd(40, 100) },
        { label: 'Filter & Chemicals', amount: rnd(30, 80) },
        { label: 'Salary', amount: rnd(120, 220) },
        { label: 'Maintenance', amount: rnd(10, 60) },
    ]
    const revenueTotal = revenue.reduce((s, r) => s + r.amount, 0)
    const expensesTotal = expenses.reduce((s, e) => s + e.amount, 0)

    const channels = ['Home Delivery', 'Shopkeeper', 'On-Site', 'School', 'Bottle']

    return {
        profile: {
            platform: task.platform ?? pick(['Phnom Penh', 'Battambang', 'Siem Reap', 'Kampong Cham', 'Takeo']),
            entrepreneur: task.technician ?? pick(['Sok Dara', 'Chan Piseth', 'Rin Sophea', 'Heng Vutha']),
            advisor: pick(['Heng Vutha', 'Chan Piseth', 'Rin Sophea']),
            startDate: `20${rnd(16, 23)}-${String(rnd(1, 12)).padStart(2, '0')}-${String(rnd(1, 28)).padStart(2, '0')}`,
            population: rnd(2000, 6000),
            treatment: pick(['UF + UV Disinfection', 'RO + UV Disinfection', 'Sand Filter + Chlorination']),
        },
        kpis: [
            { label: 'Bottles Sold (MTD)', value: rnd(800, 2000), objective: 1500 },
            { label: 'Revenue (MTD, $)', value: rnd(400, 1000), objective: 700 },
            { label: 'Water Loss (%)', value: rndf(2, 10), objective: 5 },
            { label: 'Active Customers', value: rnd(150, 400), objective: 300 },
        ],
        sales: {
            channels,
            rows: [1, 2, 3, 4, 5].map((d) => {
                const values = channels.map(() => rnd(2, 25))
                return { date: `May ${d}`, values, total: values.reduce((a, b) => a + b, 0) }
            }),
        },
        pnl: { revenue, expenses, revenueTotal, expensesTotal, net: revenueTotal - expensesTotal },
        technical: {
            equipment: [
                { name: 'Pump Motor', status: pick(['Operational', 'Operational', 'Needs Attention']), lastService: '2026-04-02' },
                { name: 'UV Filter', status: pick(['Operational', 'Operational', 'Needs Attention']), lastService: '2026-03-18' },
                { name: 'Chlorinator', status: 'Operational', lastService: '2026-04-15' },
                { name: 'Solar Panels', status: 'Operational', lastService: '2026-02-27' },
            ],
            lastCheck: '2026-05-01',
            openIssues: rnd(0, 3),
        },
        site: {
            village: pick(['Trapaing Sab', 'Prek Ampil', 'Boeng Kok', 'Sre Ampov']),
            commune: pick(['Krang Skear', 'Ta Khmau', 'Prek Anchan']),
            district: pick(['Sangkae', 'Kandal Stueng', 'Bavel']),
            province: task.platform ?? 'Battambang',
            villagesInCommune: rnd(6, 14),
            lat: rndf(11, 13, 4),
            lng: rndf(103, 105, 4),
        },
    }
})

const scheduleDate = computed(() => {
    const d = new Date(2026, 4, 6)
    d.setDate(d.getDate() + dayOffset.value)
    return {
        dayName: d.toLocaleDateString('en-US', { weekday: 'long' }),
        fullDate: d.toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' }),
        day: d.getDate(),
    }
})

const allTasks = {
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
}

const todayTasks = computed(() => allTasks[scheduleDate.value.day] ?? [])

// ── Calendar ──────────────────────────────────────────────────────────────────
const calMonth = ref(0) // offset from May 2026
const TODAY_DAY = 6

const calendarMonthLabel = computed(() => {
    const d = new Date(2026, 4 + calMonth.value, 1)
    return d.toLocaleDateString('en-US', { month: 'long', year: 'numeric' })
})

const selectedDay = ref(TODAY_DAY)
const selectDay = (d) => { selectedDay.value = d }

const calendarEvents = {
    5: [{ label: 'RC', colorClass: 'pill-grey' }, { label: 'WS', colorClass: 'pill-cyan' }],
    6: [{ label: 'SA', colorClass: 'pill-purple' }, { label: 'Issue', colorClass: 'pill-red' }, { label: 'RC', colorClass: 'pill-grey' }],
    7: [{ label: 'RC', colorClass: 'pill-grey' }],
    8: [{ label: 'WS', colorClass: 'pill-cyan' }, { label: 'SA', colorClass: 'pill-purple' }],
    12: [{ label: 'RC', colorClass: 'pill-grey' }, { label: 'Issue', colorClass: 'pill-red' }],
    15: [{ label: 'WS', colorClass: 'pill-cyan' }],
    19: [{ label: 'SA', colorClass: 'pill-purple' }],
    21: [{ label: 'RC', colorClass: 'pill-grey' }, { label: 'WS', colorClass: 'pill-cyan' }],
    26: [{ label: 'Issue', colorClass: 'pill-red' }],
    28: [{ label: 'RC', colorClass: 'pill-grey' }],
}

const calendarGrid = computed(() => {
    const base = new Date(2026, 4 + calMonth.value, 1)
    const year = base.getFullYear()
    const month = base.getMonth()
    const daysInMonth = new Date(year, month + 1, 0).getDate()
    const firstDow = new Date(year, month, 1).getDay()

    const isCurrentMonth = calMonth.value === 0

    const cells = []
    for (let i = 0; i < firstDow; i++) cells.push({ day: null })
    for (let d = 1; d <= daysInMonth; d++) {
        const dow = new Date(year, month, d).getDay()
        cells.push({
            day: d,
            isWeekend: dow === 0 || dow === 6,
            isToday: isCurrentMonth && d === TODAY_DAY,
            isSelected: isCurrentMonth && d === selectedDay.value,
            events: (isCurrentMonth ? calendarEvents[d] : []) ?? [],
        })
    }
    return cells
})

const legend = [
    { label: 'Issue', colorClass: 'pill-red' },
    { label: 'Routine Check', colorClass: 'pill-grey' },
    { label: 'Water Sample', colorClass: 'pill-cyan' },
    { label: 'Site Assessment', colorClass: 'pill-purple' },
]

// ── Quick Actions ─────────────────────────────────────────────────────────────
const createIssueDialog    = ref(false)
const routineCheckDialog   = ref(false)
const siteAssessmentDialog = ref(false)
const waterSampleDialog    = ref(false)

// ── Issues Table ──────────────────────────────────────────────────────────────
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

const statusOptions = ['open','scheduled','in-progress','pending-validation','ready-for-intervention','resolved']

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
const issueTab      = ref('info')

const openIssue = (issue) => { selectedIssue.value = issue; issueTab.value = 'info'; issueDialog.value = true }

const urgencyColor = (u) => ({ critical: 'error', high: 'orange-darken-1', medium: 'warning', low: 'success' }[u] || 'default')
const slaColor     = (s) => s <= 4 ? 'text-green-darken-2' : s < 24 ? 'text-amber-darken-2' : 'text-red-darken-2'

// ── Visit History (mock) ─────────────────────────────────────────────────────
const VISIT_BASE_YEAR = 2026
const VISIT_BASE_MONTH = 0 // January
const visitMonthOffset = ref(0)

const visitMonthLabel = computed(() => {
    const d = new Date(VISIT_BASE_YEAR, VISIT_BASE_MONTH + visitMonthOffset.value, 1)
    return d.toLocaleDateString('en-US', { month: 'long', year: 'numeric' })
})

const prevVisitMonth = () => { visitMonthOffset.value-- }
const nextVisitMonth = () => { visitMonthOffset.value++ }

const visitHistoryByMonth = {
    '-1': [
        { date: '2025-12-10', siteCode: 'F4', siteName: 'Kiosk F4', actions: 'Water sample collection', comments: 'Sample sent to lab for analysis.', status: 'completed' },
        { date: '2025-12-22', siteCode: 'B3', siteName: 'Kiosk B3', actions: 'Routine inspection', comments: 'No issues found.', status: 'completed' },
    ],
    0: [
        { date: '2026-01-15', siteCode: 'A2', siteName: 'Kiosk A2', actions: 'Routine inspection, Quality control', comments: 'Site in excellent condition. Entrepreneur very motivated.', status: 'completed' },
        { date: '2026-01-16', siteCode: 'D4', siteName: 'Kiosk D4', actions: 'Technical issue follow-up, Water sampling', comments: 'Technical issue resolved successfully.', status: 'completed' },
        { date: '2026-01-20', siteCode: 'E7', siteName: 'Kiosk E7', actions: 'Monthly review, Entrepreneur coaching', comments: 'Need to improve record keeping.', status: 'completed' },
    ],
    1: [
        { date: '2026-02-05', siteCode: 'B3', siteName: 'Kiosk B3', actions: 'Routine inspection', comments: 'All good.', status: 'completed' },
        { date: '2026-02-18', siteCode: 'C6', siteName: 'Kiosk C6', actions: 'Pump repair follow-up', comments: 'Pump running normally now.', status: 'completed' },
    ],
}

const visitHistory = computed(() => visitHistoryByMonth[visitMonthOffset.value] ?? [])

</script>

<style scoped>
.page-wrapper {
    min-height: 100vh;
    background: #f4f6f9;
}

/* ── Header ── */
.header-bar {
    background: linear-gradient(135deg, #1565C0 0%, #0D47A1 60%, #1976D2 100%);
    box-shadow: 0 2px 12px rgba(21, 101, 192, 0.3);
}

.logo-mark {
    width: 46px;
    height: 46px;
    border-radius: 12px;
    background: rgba(255, 255, 255, 0.2);
    backdrop-filter: blur(4px);
}

.status-chip {
    animation: pulse-dot 2s infinite;
}

@keyframes pulse-dot {

    0%,
    100% {
        opacity: 1;
    }

    50% {
        opacity: 0.6;
    }
}

/* ── KPI Slider ── */
.slider-viewport {
    overflow: hidden;
    border-radius: 12px;
}

.slider-track {
    display: flex;
    width: 100%;
}

.slider-item {
    min-width: calc(100% / 4);
    flex-shrink: 0;
    padding: 0 8px;
    box-sizing: border-box;
}

.kpi-card {
    position: relative;
    overflow: hidden;
    transition: box-shadow 0.2s, transform 0.2s;
}

.kpi-card:hover {
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12) !important;
    transform: translateY(-2px);
}

.kpi-accent {
    height: 4px;
    width: 100%;
}

.kpi-icon-wrap {
    width: 44px;
    height: 44px;
    border-radius: 10px;
}

/* ── Dots ── */
.kpi-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #ccc;
    border: none;
    cursor: pointer;
    transition: background 0.2s, width 0.2s;
    padding: 0;
}

.kpi-dot-active {
    background: #1565C0;
    width: 22px;
    border-radius: 4px;
}

/* ── Schedule ── */
.schedule-header {
    background: linear-gradient(135deg, #f8faff 0%, #eef2ff 100%);
}

.schedule-icon {
    width: 36px;
    height: 36px;
    border-radius: 10px;
    background: linear-gradient(135deg, #1565C0, #1976D2);
}

.task-row {
    background: #fafafa;
    border: 1px solid #f0f0f0;
    transition: background 0.15s, border-color 0.15s;
}

.task-row:hover {
    background: #f0f4ff;
    border-color: #bbdefb;
}

.task-done {
    background: #f9f9f9;
    opacity: 0.65;
}

.task-time {
    min-width: 44px;
}

.time-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    margin: 0 auto;
}

/* ── Calendar ── */
.cal-grid {
    display: grid;
    grid-template-columns: repeat(7, 1fr);
    gap: 3px;
}

.cal-cell {
    min-height: 72px;
    padding: 4px 5px;
    background: #fff;
    border: 1px solid #f0f0f0;
    transition: background 0.15s;
}

.cal-clickable {
    cursor: pointer;
}

.cal-clickable:hover {
    background: #f5f8ff;
}

.cal-weekend {
    background: #fafafa;
}

.cal-today {
    border-color: #1976D2 !important;
    background: #e3f2fd !important;
}

.cal-selected {
    border-color: #1565C0 !important;
    background: #dce8fc !important;
}

.cal-day-num {
    font-weight: 600;
    font-size: 12px;
    color: #424242;
    line-height: 1.4;
}

.cal-today-num {
    color: #1565C0;
}

.cal-events {
    margin-top: 3px;
}

.cal-pill {
    display: block;
    font-size: 10px;
    padding: 1px 4px;
    border-radius: 3px;
    margin-top: 2px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.pill-red {
    background: #ffebee;
    color: #c62828;
}

.pill-grey {
    background: #f5f5f5;
    color: #424242;
}

.pill-cyan {
    background: #e0f7fa;
    color: #00695c;
}

.pill-purple {
    background: #f3e5f5;
    color: #6a1b9a;
}

.cal-more {
    background: #eeeeee;
    color: #757575;
}

.legend-swatch {
    width: 14px;
    height: 14px;
    border-radius: 3px;
    flex-shrink: 0;
}

/* ── Quick Actions ── */
.erp-btn {
    font-size: 12px !important;
    font-weight: 600 !important;
    letter-spacing: 0.02em !important;
    text-transform: none !important;
    border-radius: 6px !important;
}

.qa-dialog-header {
    border-radius: 12px 12px 0 0;
}

/* ── Issues Table ── */
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

.issue-dialog-header {
    background: linear-gradient(135deg, #0D47A1 0%, #1976D2 100%);
    border-radius: 12px 12px 0 0;
}

/* ── Task Detail Dialog ── */
.detail-dialog-header {
    background: linear-gradient(135deg, #1565C0 0%, #1976D2 100%);
    border-radius: 12px 12px 0 0;
}

.detail-info-block {
    background: #f8faff;
    border: 1px solid #e8eef8;
}
</style>
