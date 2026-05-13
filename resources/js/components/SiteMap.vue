<template>
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
                :color="markerColor(site, 'stroke')"
                :fill-color="markerColor(site, 'fill')"
                :fill-opacity="0.85"
                :weight="2"
            >
                <l-tooltip
                    >{{ site.name }} :
                    {{ props.dataMode === "active" ? (site.active ? "Active" : "Inactive") : site.tier || "N/A" }}</l-tooltip
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

<script setup>
import { ref, computed, onMounted } from "vue";
import "leaflet/dist/leaflet.css";
import L from "leaflet";
import {
    LMap,
    LTileLayer,
    LGeoJson,
    LCircleMarker,
    LTooltip,
} from "@vue-leaflet/vue-leaflet";

import markerIcon from "leaflet/dist/images/marker-icon.png";
import markerShadow from "leaflet/dist/images/marker-shadow.png";

delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
    iconUrl: markerIcon,
    shadowUrl: markerShadow,
});

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

const props = defineProps({
    sites: {
        type: Array,
        required: true,
    },
    dataMode: {
        type: String,
        required: true,
    },
});

const geojsonData = ref(null);

const sitesWithCoords = computed(() =>
    props.sites.filter((s) => s.latitude && s.longitude),
);

const geoJsonStyleFn = () => ({
    fillColor: "#e0e0e0",
    fillOpacity: 0.25,
    color: "#bdbdbd",
    weight: 1,
});

const geoJsonOptions = computed(() => ({
    onEachFeature: (feature, layer) => {
        const name =
            feature.properties?.ADM1_EN +
            " > " +
            feature.properties?.ADM2_EN +
            " > " +
            feature.properties?.ADM3_EN;
        layer.bindTooltip(name, {
            sticky: true,
            className: "commune-tooltip",
        });
        layer.on("mouseover", () => {
            layer.setStyle({
                fillColor: "#64B5F6",
                fillOpacity: 0.5,
                color: "#1565C0",
                weight: 2,
            });
        });
        layer.on("mouseout", () => {
            layer.setStyle({
                fillColor: "#e0e0e0",
                fillOpacity: 0.25,
                color: "#bdbdbd",
                weight: 1,
            });
        });
    },
}));

function getTierColor(tier) {
    return TIER_COLORS[tier] || "#E0E0E0";
}

function markerColor(site, part) {
    if (props.dataMode === "active") {
        if (site.active) {
            return part === "fill" ? "#4CAF50" : "#2E7D32";
        }
        return part === "fill" ? "#9E9E9E" : "#757575";
    }
    return getTierColor(site.tier);
}

async function fetchGeoJson() {
    try {
        const res = await fetch("/CambodiaCommuneBoundaries.geojson");
        geojsonData.value = await res.json();
    } catch (error) {
        console.error("Failed to load map boundaries:", error);
    }
}

onMounted(() => {
    fetchGeoJson();
});
</script>

<style scoped>
.map-container {
    border-radius: 8px;
    overflow: hidden;
}

.map-container :deep(.leaflet-tooltip) {
    background-color: #424242;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 4px 8px;
    font-size: 12px;
}

.map-container :deep(.leaflet-tooltip-left:before),
.map-container :deep(.leaflet-tooltip-right:before) {
    border-left-color: #424242;
    border-right-color: #424242;
}

.map-container :deep(.leaflet-tooltip-top:before),
.map-container :deep(.leaflet-tooltip-bottom:before) {
    border-top-color: #424242;
    border-bottom-color: #424242;
}

.map-container :deep(.commune-tooltip) {
    background-color: #1565c0;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 4px 8px;
    font-size: 12px;
}

.map-container :deep(.commune-tooltip.leaflet-tooltip-left:before),
.map-container :deep(.commune-tooltip.leaflet-tooltip-right:before) {
    border-left-color: #1565c0;
    border-right-color: #1565c0;
}

.map-container :deep(.commune-tooltip.leaflet-tooltip-top:before),
.map-container :deep(.commune-tooltip.leaflet-tooltip-bottom:before) {
    border-top-color: #1565c0;
    border-bottom-color: #1565c0;
}
</style>
