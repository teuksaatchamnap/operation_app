<template>
    <v-card class="mb-6 pa-4">
        <div class="d-flex align-center mb-4">
            <div class="text-subtitle-1 font-weight-bold">Sites</div>
            <v-spacer />
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
            </v-data-table>
        </template>

        <template v-if="viewMode === 'kanban' && !loading">
            <div v-if="kanbanGroups.length > 0" class="kanban-container">
                <div
                    v-for="group in kanbanGroups"
                    :key="group.platform"
                    class="kanban-column"
                >
                    <div class="text-subtitle-2 font-weight-bold mb-3">
                        {{ group.platform }}
                        <v-chip size="x-small" variant="tonal" class="ml-2">
                            {{ group.sites.length }}
                        </v-chip>
                    </div>
                    <div class="kanban-cards">
                        <div
                            v-for="site in group.sites"
                            :key="site.id"
                            class="kanban-circle"
                            :class="{
                                'kanban-circle--active': site.active,
                                'kanban-circle--inactive': !site.active,
                            }"
                        >
                            {{ site.name }}
                        </div>
                    </div>
                </div>
            </div>
        </template>

        <template v-if="viewMode === 'map' && !loading">
            <div v-if="geojsonData" class="map-container">
                <l-map
                    :zoom="7"
                    :center="[12.5, 104.9]"
                    style="height: 500px; width: 100%"
                >
                    <l-tile-layer
                        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                        attribution="&copy; OpenStreetMap contributors"
                    />
                    <l-geo-json
                        v-if="geojsonData"
                        :geojson="geojsonData"
                        :options-style="geoJsonStyleFn"
                        :options="geoJsonOptions"
                    />
                    <l-circle-marker
                        v-for="site in sitesWithCoords"
                        :key="site.id"
                        :lat-lng="[site.latitude, site.longitude]"
                        :radius="5"
                        :color="site.active ? '#2E7D32' : '#757575'"
                        :fill-color="site.active ? '#4CAF50' : '#9E9E9E'"
                        :fill-opacity="0.85"
                        :weight="2"
                    >
                        <l-tooltip
                            >{{ site.name }} :
                            {{ site.active ? "Active" : "Inactive" }}</l-tooltip
                        >
                    </l-circle-marker>
                </l-map>
            </div>
            <v-progress-linear
                v-else
                indeterminate
                color="primary"
                class="mb-2"
            />
        </template>

        <div
            v-if="!loading && mergedSites.length === 0"
            class="text-center text-medium-emphasis pa-6"
        >
            No sites found for the selected filters.
        </div>
    </v-card>
</template>

<script setup>
import { ref, computed, watch, onMounted } from "vue";
import axios from "axios";
import "leaflet/dist/leaflet.css";
import L from "leaflet";
import {
    LMap,
    LTileLayer,
    LGeoJson,
    LCircleMarker,
    LTooltip,
} from "@vue-leaflet/vue-leaflet";

// Fix Leaflet default icon paths for Vite
import markerIcon from "leaflet/dist/images/marker-icon.png";
import markerShadow from "leaflet/dist/images/marker-shadow.png";

delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
    iconUrl: markerIcon,
    shadowUrl: markerShadow,
});

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

const factRows = ref([]);
const loading = ref(false);
const viewMode = ref("table");
const geojsonData = ref(null);

const tableHeaders = [
    { title: "Site", key: "name" },
    { title: "Platform", key: "platform_name" },
    { title: "Advisor", key: "advisor_name" },
    { title: "Active", key: "active", align: "center" },
];

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
        });
    }

    return result;
});

const sitesWithCoords = computed(() =>
    mergedSites.value.filter((s) => s.latitude && s.longitude),
);

const kanbanGroups = computed(() => {
    const groups = {};
    for (const site of mergedSites.value) {
        const platform = site.platform_name || "Unassigned";
        if (!groups[platform]) {
            groups[platform] = { platform, sites: [] };
        }
        groups[platform].sites.push(site);
    }
    return Object.values(groups).sort((a, b) =>
        a.platform.localeCompare(b.platform),
    );
});

const geoJsonStyleFn = () => ({
    fillColor: "#e0e0e0",
    fillOpacity: 0.25,
    color: "#bdbdbd",
    weight: 1,
});

const geoJsonOptions = computed(() => ({
    onEachFeature: (feature, layer) => {
        const name =
            feature.properties?.ADM0_EN +
            " > " +
            feature.properties?.ADM1_EN +
            " > " +
            feature.properties?.ADM2_EN +
            " > " +
            feature.properties?.ADM3_EN;
        layer.bindTooltip(name, { sticky: true });
    },
}));

async function fetchFactMonthly() {
    loading.value = true;
    try {
        const params = {
            month: props.filters.month,
            kpis: "active",
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

async function fetchGeoJson() {
    try {
        const res = await fetch("/CambodiaCommuneBoundaries.geojson");
        geojsonData.value = await res.json();
    } catch (error) {
        console.error("Failed to load map boundaries:", error);
    }
}

watch(
    () => props.filters,
    () => {
        fetchFactMonthly();
    },
    { deep: true },
);

watch(viewMode, (mode) => {
    if (mode === "map" && !geojsonData.value) {
        fetchGeoJson();
    }
});

onMounted(() => {
    fetchFactMonthly();
});
</script>

<style scoped>
.kanban-container {
    display: flex;
    gap: 16px;
    overflow-x: auto;
    padding-bottom: 8px;
}

.kanban-cards {
    display: flex;
    flex-direction: row;
    flex-wrap: wrap;
    gap: 12px;
    align-items: center;
    overflow-y: auto;
}

.kanban-circle {
    width: 35px;
    height: 35px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    text-align: center;
    font-size: 11px;
    font-weight: 500;
    padding: 8px;
    word-break: keep-all;
    overflow: hidden;
    transition: transform 0.15s ease;
}

.kanban-circle:hover {
    transform: scale(1.08);
}

.kanban-circle--active {
    background-color: #4caf50;
    color: white;
}

.kanban-circle--inactive {
    background-color: #e0e0e0;
    color: #616161;
}

.map-container {
    border-radius: 8px;
    overflow: hidden;
}
</style>
