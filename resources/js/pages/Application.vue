<template>
    <v-card class="pa-4">
        <v-row align="center">
            <v-col>
                <MonthPicker v-model="selectedMonth" />
            </v-col>
            <v-col>
                <v-autocomplete
                    v-model="selectedSites"
                    :items="availableSites"
                    item-title="name"
                    item-value="id"
                    label="Sites"
                    multiple
                    clearable
                    chips
                    closable-chips
                    hide-details
                    auto-select-first
                    autocomplete="off"
                />
            </v-col>
            <v-col>
                <v-autocomplete
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
                    auto-select-first
                    autocomplete="off"
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

    <ScrollPanel class="my-2">
        <KpiCard :kpi="findKpi('active')" :filters="kpiFilters" />
        <KpiCard
            :kpi="findKpi('super_tier_1')"
            :latest-available="1"
            :filters="kpiFilters"
        />
        <KpiCard
            :kpi="findKpi('bottles_per_day')"
            :year-to-date="1"
            :filters="kpiFilters"
        />
        <KpiCard
            :kpi="findKpi('sales_volume')"
            :year-to-date="1"
            :filters="kpiFilters"
        />
        <KpiCard
            :kpi="findKpi('sales_volume_lfl')"
            :year-to-date="1"
            :filters="kpiFilters"
        />
        <KpiCard :kpi="findKpi('sales_volume_lfl')" :filters="kpiFilters" />
        <KpiCard :kpi="findKpi('has_3_workers')" :filters="kpiFilters" />
        <KpiCard :kpi="findKpi('consumers')" :filters="kpiFilters" />
        <KpiCard
            :kpi="findKpi('who_compliance')"
            :filters="kpiFilters"
            :latest-available="1"
        />
        <KpiCard :kpi="findKpi('is_profitable')" :filters="kpiFilters" />
        <KpiCard
            :kpi="findKpi('ec_collection')"
            :filters="kpiFilters"
            :year-to-date="1"
        />
    </ScrollPanel>

    <KpiSiteList
        :filters="kpiFilters"
        :sites="sites"
        :platforms="platforms"
        :advisors="advisors"
        :kpis="kpis"
    />
</template>

<script setup>
import { ref, computed, onMounted, watch } from "vue";
import axios from "axios";
import KpiCard from "../components/KpiCard.vue";
import MonthPicker from "../components/MonthPicker.vue";
import ScrollPanel from "../components/ScrollPanel.vue";
import KpiSiteList from "../components/KpiSiteList.vue";

const now = new Date();
const currentMonth = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, "0")}`;

const kpis = ref([]);
const sites = ref([]);
const advisors = ref([]);
const platforms = ref([]);
const selectedSites = ref([]);
const selectedAdvisors = ref([]);
const selectedPlatforms = ref([]);
const selectedMonth = ref(currentMonth);
const factSiteIds = ref(null);

const STORAGE_KEY = "application_filters";

function loadFilters() {
    try {
        const saved = localStorage.getItem(STORAGE_KEY);
        if (saved) {
            const parsed = JSON.parse(saved);
            selectedMonth.value = parsed.month ?? currentMonth;
            selectedSites.value = parsed.sites ?? [];
            selectedAdvisors.value = parsed.advisors ?? [];
            selectedPlatforms.value = parsed.platforms ?? [];
        }
    } catch {}
}

function saveFilters() {
    localStorage.setItem(
        STORAGE_KEY,
        JSON.stringify({
            month: selectedMonth.value,
            sites: selectedSites.value,
            advisors: selectedAdvisors.value,
            platforms: selectedPlatforms.value,
        }),
    );
}

watch(
    [selectedMonth, selectedSites, selectedAdvisors, selectedPlatforms],
    saveFilters,
    { deep: true },
);

const kpiFilters = computed(() => ({
    site_ids: selectedSites.value,
    advisor_ids: selectedAdvisors.value,
    platform_ids: selectedPlatforms.value,
    month: selectedMonth.value,
}));

const availableSites = computed(() => {
    if (factSiteIds.value === null) return sites.value;
    const ids = factSiteIds.value;
    return sites.value.filter((s) => ids.has(s.id));
});

function findKpi(colName) {
    return kpis.value.find((k) => k.col_name === colName) || null;
}

async function fetchFactSiteIds() {
    try {
        const res = await axios.get("/api/fact-monthly", {
            params: { month: selectedMonth.value, kpis: "active" },
        });
        factSiteIds.value = new Set(res.data.map((r) => r.site_id));
    } catch {
        factSiteIds.value = null;
    }
}

watch(selectedMonth, fetchFactSiteIds);

onMounted(async () => {
    loadFilters();

    try {
        const [kpisRes, sitesRes, advisorsRes, platformsRes] =
            await Promise.all([
                axios.get("/api/kpis"),
                axios.get("/api/sites"),
                axios.get("/api/advisors"),
                axios.get("/api/platforms"),
            ]);
        kpis.value = kpisRes.data;
        sites.value = sitesRes.data;
        advisors.value = advisorsRes.data;
        platforms.value = platformsRes.data;
    } catch (error) {
        console.error("Failed to load dimensions:", error);
    }

    fetchFactSiteIds();
});
</script>
