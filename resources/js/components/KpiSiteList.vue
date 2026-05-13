<template>
    <v-card class="mb-6 pa-4">
        <div class="d-flex align-center mb-4">
            <div class="text-subtitle-1 font-weight-bold">Sites</div>
            <v-spacer />
            <v-select
                v-model="dataMode"
                :items="dataModeOptions"
                item-title="title"
                item-value="value"
                density="compact"
                hide-details
                class="mr-4"
                style="max-width: 160px"
            />
            <v-btn-toggle
                v-model="viewMode"
                mandatory
                density="comfortable"
                color="primary"
            >
                <v-btn value="table" size="small">
                    <v-icon start size="small">mdi-table</v-icon>
                    Table
                </v-btn>
                <v-btn value="kanban" size="small">
                    <v-icon start size="small">mdi-view-column</v-icon>
                    Kanban
                </v-btn>
                <v-btn value="map" size="small">
                    <v-icon start size="small">mdi-map</v-icon>
                    Map
                </v-btn>
            </v-btn-toggle>
        </div>

        <v-progress-linear
            v-if="loading"
            indeterminate
            color="primary"
            class="mb-2"
        />

        <template v-if="viewMode === 'table' && !loading">
            <v-data-table
                v-if="mergedSites.length > 0"
                :items="mergedSites"
                :headers="tableHeaders"
                :items-per-page="-1"
                density="comfortable"
                class="elevation-1 rounded"
            >
                <template #item.active="{ item }">
                    <v-chip
                        :color="item.active ? 'success' : 'grey'"
                        size="small"
                        variant="flat"
                    >
                        {{ item.active ? "Active" : "Inactive" }}
                    </v-chip>
                </template>
                <template #item.tier="{ item }">
                    <v-chip
                        :color="getTierColor(item.tier)"
                        size="small"
                        variant="flat"
                    >
                        {{ item.tier }}
                    </v-chip>
                </template>
            </v-data-table>
        </template>

        <SiteKanban
            v-if="viewMode === 'kanban' && !loading"
            :sites="mergedSites"
            :data-mode="dataMode"
        />

        <SiteMap
            v-if="viewMode === 'map' && !loading"
            :sites="mergedSites"
            :data-mode="dataMode"
        />

        <div
            v-if="!loading && mergedSites.length === 0"
            class="text-center text-medium-emphasis pa-6"
        >
            No sites found for the selected filters.
        </div>

        <template v-if="mergedSites.length > 0">
            <v-divider class="my-3" />
            <div class="d-flex flex-wrap ga-4">
                <div
                    v-for="entry in legendItems"
                    :key="entry.label"
                    class="d-flex align-center"
                >
                    <div
                        class="legend-swatch"
                        :style="{ backgroundColor: entry.color }"
                    />
                    <span class="text-caption ml-1">{{ entry.label }}</span>
                </div>
            </div>
        </template>
    </v-card>
</template>

<script setup>
import { ref, computed, watch, onMounted } from "vue";
import axios from "axios";
import SiteKanban from "./SiteKanban.vue";
import SiteMap from "./SiteMap.vue";

const TIER_COLORS = {
    Dead: "#616161",
    Closed: "#795548",
    Inactive: "#BDBDBD",
    New: "#00BCD4",
    Reopen: "#FF9800",
    ST1: "#1B5E20",
    "1": "#4CAF50",
    "2": "#FFC107",
    "3": "#F44336",
};

const TIER_ORDER = ["Dead", "Closed", "Inactive", "New", "Reopen", "ST1", "1", "2", "3"];

const props = defineProps({
    filters: {
        type: Object,
        required: true,
    },
    sites: {
        type: Array,
        default: () => [],
    },
    platforms: {
        type: Array,
        default: () => [],
    },
    advisors: {
        type: Array,
        default: () => [],
    },
});

const dataModeOptions = [
    { title: "Active Site", value: "active" },
    { title: "Tier", value: "tier" },
];

const factRows = ref([]);
const loading = ref(false);
const viewMode = ref("table");
const dataMode = ref("active");

const platformMap = computed(() => {
    const map = {};
    for (const p of props.platforms) {
        map[p.id] = p.name;
    }
    return map;
});

const advisorMap = computed(() => {
    const map = {};
    for (const a of props.advisors) {
        map[a.id] = a.name;
    }
    return map;
});

const siteMap = computed(() => {
    const map = {};
    for (const s of props.sites) {
        map[s.id] = s;
    }
    return map;
});

const tableHeaders = computed(() => {
    const headers = [
        { title: "Site", key: "name" },
        { title: "Platform", key: "platform_name" },
        { title: "Advisor", key: "advisor_name" },
    ];
    if (dataMode.value === "active") {
        headers.push({ title: "Active", key: "active", align: "center" });
    } else {
        headers.push({ title: "Tier", key: "tier", align: "center" });
    }
    return headers;
});

const mergedSites = computed(() => {
    const seen = new Set();
    const result = [];

    for (const row of factRows.value) {
        if (seen.has(row.site_id)) continue;
        seen.add(row.site_id);

        const site = siteMap.value[row.site_id];
        if (!site) continue;

        result.push({
            id: row.site_id,
            name: site.name,
            latitude: site.latitude,
            longitude: site.longitude,
            platform_name: platformMap.value[row.platform_id] || "Unassigned",
            advisor_name: advisorMap.value[row.advisor_id] || "Unassigned",
            active: !!row.active,
            tier: row.tier,
        });
    }

    return result;
});

const legendItems = computed(() => {
    if (dataMode.value === "active") {
        return [
            { label: "Active", color: "#4CAF50" },
            { label: "Inactive", color: "#E0E0E0" },
        ];
    }
    const tiers = [
        ...new Set(mergedSites.value.map((s) => s.tier).filter((t) => t != null && t !== "")),
    ];
    tiers.sort((a, b) => {
        const ia = TIER_ORDER.indexOf(a);
        const ib = TIER_ORDER.indexOf(b);
        return (ia === -1 ? 999 : ia) - (ib === -1 ? 999 : ib);
    });
    return tiers.map((tier) => ({
        label: tier,
        color: getTierColor(tier),
    }));
});

function getTierColor(tier) {
    return TIER_COLORS[tier] || "#E0E0E0";
}

async function fetchFactMonthly() {
    loading.value = true;
    try {
        const params = {
            month: props.filters.month,
            kpis: dataMode.value,
        };
        if (props.filters.site_ids?.length) {
            params.site_ids = props.filters.site_ids;
        }
        if (props.filters.advisor_ids?.length) {
            params.advisor_ids = props.filters.advisor_ids;
        }
        if (props.filters.platform_ids?.length) {
            params.platform_ids = props.filters.platform_ids;
        }
        const res = await axios.get("/api/fact-monthly", { params });
        factRows.value = res.data;
    } catch (error) {
        console.error("Failed to load fact monthly data:", error);
        factRows.value = [];
    } finally {
        loading.value = false;
    }
}

watch(
    () => props.filters,
    () => {
        fetchFactMonthly();
    },
    { deep: true },
);

watch(dataMode, () => {
    fetchFactMonthly();
});

onMounted(() => {
    fetchFactMonthly();
});
</script>

<style scoped>
.legend-swatch {
    width: 14px;
    height: 14px;
    border-radius: 3px;
    flex-shrink: 0;
}
</style>
