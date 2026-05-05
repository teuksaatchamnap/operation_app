<template>
    <!-- Filter Form -->
    <v-card class="mb-6 pa-4">
        <v-row align="center">
            <v-col>
                <MonthPicker v-model="selectedMonth" />
            </v-col>
            <v-col>
                <v-select
                    v-model="selectedSites"
                    :items="sites"
                    item-title="name"
                    item-value="id"
                    label="Sites"
                    multiple
                    clearable
                    chips
                    closable-chips
                    hide-details
                />
            </v-col>
            <v-col>
                <v-select
                    v-model="selectedAdvisors"
                    :items="advisors"
                    item-title="name"
                    item-value="id"
                    label="Advisors"
                    multiple
                    clearable
                    chips
                    closable-chips
                    hide-details
                />
            </v-col>
            <v-col>
                <v-select
                    v-model="selectedPlatforms"
                    :items="platforms"
                    item-title="name"
                    item-value="id"
                    label="Platforms"
                    multiple
                    clearable
                    chips
                    closable-chips
                    hide-details
                />
            </v-col>
        </v-row>
    </v-card>

    <!-- KPI Cards -->
    <div class="kpi-scroll-wrapper mb-6">
        <v-btn
            v-show="canScrollLeft"
            icon="mdi-chevron-left"
            class="kpi-scroll-btn kpi-scroll-btn-left"
            density="comfortable"
            size="large"
            variant="tonal"
            @click="scrollKpis('left')"
        />
        <div
            ref="kpiScroller"
            class="kpi-scroller"
            :class="{ 'kpi-scroller--dragging': isDragging }"
            @scroll="updateScrollState"
            @mousedown="onDragStart"
            @mousemove="onDragMove"
            @mouseup="onDragEnd"
            @mouseleave="onDragEnd"
        >
            <KpiCard
                kpi-col-name="sales_volume"
                :year-to-date="1"
                :filters="kpiFilters"
            />
            <KpiCard
                kpi-col-name="sales_volume_lfl"
                :year-to-date="1"
                :filters="kpiFilters"
            />
            <KpiCard kpi-col-name="sales_volume_lfl" :filters="kpiFilters" />
            <KpiCard kpi-col-name="active" :filters="kpiFilters" />
            <KpiCard
                kpi-col-name="super_tier_1"
                :latest-available="1"
                :filters="kpiFilters"
            />
            <KpiCard
                kpi-col-name="bottles_per_day"
                :year-to-date="1"
                :filters="kpiFilters"
            />
            <KpiCard kpi-col-name="has_3_workers" :filters="kpiFilters" />
            <KpiCard kpi-col-name="consumers" :filters="kpiFilters" />
        </div>
        <v-btn
            v-show="canScrollRight"
            icon="mdi-chevron-right"
            class="kpi-scroll-btn kpi-scroll-btn-right"
            density="comfortable"
            size="large"
            variant="tonal"
            @click="scrollKpis('right')"
        />
    </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed, nextTick } from "vue";
import axios from "axios";
import KpiCard from "../components/KpiCard.vue";
import MonthPicker from "../components/MonthPicker.vue";

const now = new Date();
const currentMonth = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, "0")}`;

const sites = ref([]);
const advisors = ref([]);
const platforms = ref([]);
const selectedSites = ref([]);
const selectedAdvisors = ref([]);
const selectedPlatforms = ref([]);
const selectedMonth = ref(currentMonth);

const kpiScroller = ref(null);
const canScrollLeft = ref(false);
const canScrollRight = ref(false);
let resizeObserver = null;
let isDragging = ref(false);
let dragStartX = 0;
let dragScrollLeft = 0;

function onDragStart(e) {
    isDragging.value = true;
    dragStartX = e.pageX - kpiScroller.value.offsetLeft;
    dragScrollLeft = kpiScroller.value.scrollLeft;
}

function onDragMove(e) {
    if (!isDragging.value) return;
    e.preventDefault();
    const x = e.pageX - kpiScroller.value.offsetLeft;
    const walk = (x - dragStartX) * 1.5;
    kpiScroller.value.scrollLeft = dragScrollLeft - walk;
}

function onDragEnd() {
    isDragging.value = false;
}

const kpiFilters = computed(() => ({
    site_ids: selectedSites.value,
    advisor_ids: selectedAdvisors.value,
    platform_ids: selectedPlatforms.value,
    month: selectedMonth.value,
}));

function updateScrollState() {
    const el = kpiScroller.value;
    if (!el) return;
    canScrollLeft.value = el.scrollLeft > 0;
    canScrollRight.value = el.scrollLeft + el.clientWidth < el.scrollWidth - 1;
}

function scrollKpis(direction) {
    const el = kpiScroller.value;
    if (!el) return;
    el.scrollBy({
        left: direction === "left" ? -300 : 300,
        behavior: "smooth",
    });
}

onMounted(async () => {
    try {
        const [sitesRes, advisorsRes, platformsRes] = await Promise.all([
            axios.get("/api/sites"),
            axios.get("/api/advisors"),
            axios.get("/api/platforms"),
        ]);
        sites.value = sitesRes.data;
        advisors.value = advisorsRes.data;
        platforms.value = platformsRes.data;
    } catch (error) {
        console.error("Failed to load dimensions:", error);
    }

    await nextTick();
    updateScrollState();
    if (kpiScroller.value) {
        resizeObserver = new ResizeObserver(updateScrollState);
        resizeObserver.observe(kpiScroller.value);
    }
});

onUnmounted(() => {
    if (resizeObserver) {
        resizeObserver.disconnect();
    }
});
</script>

<style scoped>
.kpi-scroll-wrapper {
    position: relative;
}

.kpi-scroller {
    display: flex;
    gap: 16px;
    overflow-x: auto;
    scroll-behavior: smooth;
    padding: 10px 10px 10px 10px;
    cursor: grab;
    user-select: none;
}

.kpi-scroller--dragging {
    cursor: grabbing;
    scroll-behavior: auto;
}

.kpi-scroller::-webkit-scrollbar {
    display: none;
}

.kpi-scroller {
    -ms-overflow-style: none;
    scrollbar-width: none;
}

.kpi-scroll-btn {
    position: absolute;
    top: 50%;
    transform: translateY(-50%);
    z-index: 1;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.kpi-scroll-btn-left {
    left: 4px;
}

.kpi-scroll-btn-right {
    right: 4px;
}
</style>
