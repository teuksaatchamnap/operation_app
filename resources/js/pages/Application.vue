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
    <div class="d-flex flex-row mb-6" style="gap: 16px">
        <div class="flex-1-1">
            <KpiCard
                kpi-col-name="sales_volume"
                :year-to-date="1"
                :filters="kpiFilters"
            />
        </div>
        <div class="flex-1-1">
            <KpiCard kpi-col-name="days_open" :filters="kpiFilters" />
        </div>
        <div class="flex-1-1">
            <KpiCard kpi-col-name="active" :filters="kpiFilters" />
        </div>
        <div class="flex-1-1">
            <KpiCard kpi-col-name="super_tier_1" :filters="kpiFilters" />
        </div>
        <div class="flex-1-1">
            <KpiCard
                kpi-col-name="bottles_per_day"
                :year-to-date="1"
                :filters="kpiFilters"
            />
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted, computed } from "vue";
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

const kpiFilters = computed(() => ({
    site_ids: selectedSites.value,
    advisor_ids: selectedAdvisors.value,
    platform_ids: selectedPlatforms.value,
    month: selectedMonth.value,
}));

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
});
</script>
