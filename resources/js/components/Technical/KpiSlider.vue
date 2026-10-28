<template>
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
</template>

<script setup>
import { ref, computed } from 'vue'

// ── KPI Data (fake) ───────────────────────────────────────────────────────────
const kpiCards = [
    {
        title: 'Open Issues',
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
        title: 'Resolved This Month',
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
        title: 'Avg. Resolution Time',
        subtitle: 'Mean time to resolve',
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
        title: 'Sites Visited',
        subtitle: 'Field visits this month',
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
</script>

<style scoped>
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
</style>
