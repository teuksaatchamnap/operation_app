<template>
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

    <ScrollPanel class="mb-6">
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

    <ActiveSitesList
        :filters="kpiFilters"
        :sites="sites"
        :platforms="platforms"
        :advisors="advisors"
    />
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import axios from "axios";
import KpiCard from "../components/KpiCard.vue";
import MonthPicker from "../components/MonthPicker.vue";
import ScrollPanel from "../components/ScrollPanel.vue";
import ActiveSitesList from "../components/ActiveSitesList.vue";

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

const kpiFilters = computed(() => ({
    site_ids: selectedSites.value,
    advisor_ids: selectedAdvisors.value,
    platform_ids: selectedPlatforms.value,
    month: selectedMonth.value,
}));

function findKpi(colName) {
    return kpis.value.find((k) => k.col_name === colName) || null;
}

onMounted(async () => {
    try {
        const [kpisRes, sitesRes, advisorsRes, platformsRes] = await Promise.all([
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
});
</script>
