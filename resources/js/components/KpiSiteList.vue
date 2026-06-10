<template>
    <v-card class="mb-6 pa-4">
        <div class="d-flex align-center mb-4">
            <div class="text-subtitle-1 font-weight-bold">Sites</div>
            <v-spacer />
            <v-text-field
                v-model="siteFilter"
                density="compact"
                hide-details
                clearable
                prepend-inner-icon="mdi-magnify"
                placeholder="Search sites..."
                class="mr-4"
                style="max-width: 200px"
            />
            <v-select
                v-model="dataMode"
                :items="dataModeOptions"
                item-title="title"
                item-value="value"
                density="compact"
                hide-details
                class="mr-4"
                style="max-width: 260px"
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

        <template v-if="loading">
            <div class="skeleton-table-wrapper">
                <div class="skeleton skeleton-table-header" />
                <div
                    v-for="i in 6"
                    :key="i"
                    class="skeleton skeleton-table-row"
                />
            </div>
        </template>

        <template v-if="viewMode === 'table' && !loading">
            <v-data-table
                v-if="mergedSites.length > 0"
                :items="mergedSites"
                :headers="tableHeaders"
                :items-per-page="-1"
                density="comfortable"
                class="elevation-1 rounded"
                hover
                @click:row="onRowClick"
            >
                <template #item.active="{ item }">
                    <v-chip
                        :color="
                            getTierColor(item.active ? 'Active' : 'Inactive')
                        "
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
                <template #item.is_profitable="{ item }">
                    <v-chip
                        :color="
                            getTierColor(
                                item.is_profitable
                                    ? 'Profitable'
                                    : 'Not Profitable',
                            )
                        "
                        size="small"
                        variant="flat"
                    >
                        {{
                            item.is_profitable == null
                                ? "N/A"
                                : item.is_profitable
                                  ? "Profitable"
                                  : "Not Profitable"
                        }}
                    </v-chip>
                </template>
                <template #item.contamination_level="{ item }">
                    <v-chip
                        :color="
                            getTierColor(
                                item.contamination_level === 0
                                    ? 'Safe'
                                    : String(item.contamination_level ?? 'N/A'),
                            )
                        "
                        size="small"
                        variant="flat"
                    >
                        {{
                            item.contamination_level == null
                                ? "N/A"
                                : item.contamination_level === 0
                                  ? "Safe"
                                  : item.contamination_level
                        }}
                    </v-chip>
                </template>
                <template #item.is_water_loss_ok="{ item }">
                    <v-chip
                        :color="
                            getTierColor(
                                item.is_water_loss_ok === 0
                                    ? 'OK'
                                    : item.is_water_loss_ok == null
                                      ? 'N/A'
                                      : 'Not OK',
                            )
                        "
                        size="small"
                        variant="flat"
                    >
                        {{
                            item.is_water_loss_ok == null
                                ? "N/A"
                                : item.is_water_loss_ok === 0
                                  ? "OK"
                                  : "Not OK"
                        }}
                    </v-chip>
                </template>
                <template #item.data_collection="{ item }">
                    <v-chip
                        :color="
                            getTierColor(
                                item.data_collection === 2
                                    ? 'Complete'
                                    : item.data_collection === 1
                                      ? 'Partial'
                                      : item.data_collection == null
                                        ? 'N/A'
                                        : 'None',
                            )
                        "
                        size="small"
                        variant="flat"
                    >
                        {{
                            item.data_collection == null
                                ? "N/A"
                                : item.data_collection === 2
                                  ? "Complete"
                                  : item.data_collection === 1
                                    ? "Partial"
                                    : "None"
                        }}
                    </v-chip>
                </template>
            </v-data-table>
        </template>

        <SiteKanban
            v-if="viewMode === 'kanban' && !loading"
            :sites="mergedSites"
            :data-mode="dataMode"
            :legend="currentLegend"
            :hover-data="hoverData"
            @site-click="openSiteDetail"
        />

        <SiteMap
            v-if="viewMode === 'map' && !loading"
            :sites="mergedSites"
            :data-mode="dataMode"
            :legend="currentLegend"
            :hover-data="hoverData"
            @site-click="openSiteDetail"
        />

        <div
            v-if="!loading && mergedSites.length === 0"
            class="text-center text-medium-emphasis pa-6"
        >
            No sites found for the selected filters.
        </div>

        <template v-if="viewMode !== 'map' && mergedSites.length > 0">
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

        <SiteDetail
            v-model="siteDetailDialog"
            :site="selectedSite"
            :initial-month="filters.month"
        />
    </v-card>
</template>

<script setup>
import { ref, computed, watch, onMounted } from "vue";
import axios from "axios";
import SiteKanban from "./SiteKanban.vue";
import SiteMap from "./SiteMap.vue";
import SiteHoverCard from "./SiteHoverCard.vue";
import SiteDetail from "./SiteDetail.vue";

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
    kpis: {
        type: Array,
        default: () => [],
    },
});

const dataModeOptions = [
    { title: "Active Site", value: "active" },
    { title: "Tier", value: "tier" },
    { title: "Financial Sustainability", value: "is_profitable" },
    { title: "Water Quality", value: "contamination_level" },
    { title: "Water Loss", value: "is_water_loss_ok" },
    { title: "Data collection status", value: "data_collection" },
    { title: "Water Source", value: "water_source" },
    { title: "Treatment Process", value: "treatment_process" },
];

const factRows = ref([]);
const hoverData = ref({});
const loading = ref(false);
const viewMode = ref("kanban");
const dataMode = ref("active");
const siteFilter = ref("");
const selectedSite = ref(null);
const siteDetailDialog = ref(false);

function openSiteDetail(site) {
    selectedSite.value = site;
    siteDetailDialog.value = true;
}

function onRowClick(event, { item }) {
    openSiteDetail(item);
}

const currentLegend = computed(() => {
    const kpi = props.kpis.find((k) => k.col_name === dataMode.value);
    return kpi?.legend || [];
});

const legendMap = computed(() => {
    const map = {};
    for (const entry of currentLegend.value) {
        map[entry.value] = entry.color;
    }
    return map;
});

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
    } else if (dataMode.value === "is_profitable") {
        headers.push({
            title: "Profitable",
            key: "is_profitable",
            align: "center",
        });
    } else if (dataMode.value === "contamination_level") {
        headers.push({
            title: "Water Quality",
            key: "contamination_level",
            align: "center",
        });
    } else if (dataMode.value === "is_water_loss_ok") {
        headers.push({
            title: "Water Loss",
            key: "is_water_loss_ok",
            align: "center",
        });
    } else if (dataMode.value === "data_collection") {
        headers.push({
            title: "Data Collection",
            key: "data_collection",
            align: "center",
        });
    } else if (dataMode.value === "water_source") {
        headers.push({
            title: "Water Source",
            key: "water_source",
            align: "center",
        });
    } else if (dataMode.value === "treatment_process") {
        headers.push({
            title: "Treatment Process",
            key: "treatment_process",
            align: "center",
        });
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
        if (
            siteFilter.value &&
            !site.name.toLowerCase().includes(siteFilter.value.toLowerCase())
        )
            continue;

        result.push({
            id: row.site_id,
            name: site.name,
            latitude: site.latitude,
            longitude: site.longitude,
            platform_name: platformMap.value[row.platform_id] || "Unassigned",
            advisor_name: advisorMap.value[row.advisor_id] || "Unassigned",
            active: !!row.active,
            tier: row.tier,
            is_profitable: row.is_profitable,
            contamination_level: row.contamination_level,
            is_water_loss_ok: row.is_water_loss_ok,
            data_collection: row.data_collection,
            water_source: row.water_source,
            treatment_process: row.treatment_process,
        });
    }

    return result;
});

const legendItems = computed(() => {
    return currentLegend.value.map((entry) => ({
        label: entry.value,
        color: entry.color,
    }));
});

function getTierColor(tier) {
    return legendMap.value[tier] || "#E0E0E0";
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

async function fetchHoverData() {
    try {
        const params = { month: props.filters.month };
        if (props.filters.site_ids?.length) {
            params.site_ids = props.filters.site_ids;
        }
        if (props.filters.advisor_ids?.length) {
            params.advisor_ids = props.filters.advisor_ids;
        }
        if (props.filters.platform_ids?.length) {
            params.platform_ids = props.filters.platform_ids;
        }
        const res = await axios.get("/api/sites/hover-data", { params });
        const map = {};
        for (const item of res.data) {
            map[item.site_id] = item;
        }
        hoverData.value = map;
    } catch (error) {
        console.error("Failed to load hover data:", error);
        hoverData.value = {};
    }
}

watch(
    () => props.filters,
    () => {
        fetchFactMonthly();
        fetchHoverData();
    },
    { deep: true },
);

watch(dataMode, () => {
    fetchFactMonthly();
});

onMounted(() => {
    fetchFactMonthly();
    fetchHoverData();
});
</script>

<style scoped>
:deep(.v-data-table tr) {
    cursor: pointer;
}

.legend-swatch {
    width: 14px;
    height: 14px;
    border-radius: 3px;
    flex-shrink: 0;
}

/* ========== Skeleton loading ========== */
.skeleton-table-wrapper {
    padding: 4px 0;
}

.skeleton {
    background: rgba(var(--v-theme-on-surface), 0.08);
    border-radius: 4px;
    animation: skeleton-pulse 1.5s ease-in-out infinite;
}

.skeleton-table-header {
    height: 56px;
    width: 100%;
    margin-bottom: 8px;
}

.skeleton-table-row {
    height: 48px;
    width: 100%;
    margin-bottom: 4px;
}

@keyframes skeleton-pulse {
    0%,
    100% {
        opacity: 1;
    }
    50% {
        opacity: 0.35;
    }
}
</style>
