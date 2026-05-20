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
                    {{ getSiteValue(site) || "N/A" }}</l-tooltip
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

const props = defineProps({
    sites: {
        type: Array,
        required: true,
    },
    dataMode: {
        type: String,
        required: true,
    },
    legend: {
        type: Array,
        default: () => [],
    },
});

const legendMap = computed(() => {
    const map = {};
    for (const entry of props.legend) {
        map[entry.value] = entry.color;
    }
    return map;
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

function getSiteValue(site) {
    if (props.dataMode === "active") {
        return site.active ? "Active" : "Inactive";
    }
    if (props.dataMode === "is_profitable") {
        return site.is_profitable ? "Profitable" : "Not Profitable";
    }
    if (props.dataMode === "contamination_level") {
        return site.contamination_level === 0
            ? "Safe"
            : site.contamination_level == null
              ? "N/A"
              : String(site.contamination_level);
    }
    if (props.dataMode === "is_water_loss_ok") {
        return site.is_water_loss_ok === 0
            ? "OK"
            : site.is_water_loss_ok == null
              ? "N/A"
              : "Not OK";
    }
    if (props.dataMode === "data_collection") {
        return site.data_collection === 2
            ? "Complete"
            : site.data_collection === 1
              ? "Partial"
              : site.data_collection == null
                ? "N/A"
                : "None";
    }
    return site.tier;
}

function getColor(value) {
    return legendMap.value[value] || "#E0E0E0";
}

function darkenColor(hex, amount = 0.4) {
    const num = parseInt(hex.slice(1), 16);
    const r = Math.max(0, Math.floor(((num >> 16) & 0xff) * (1 - amount)));
    const g = Math.max(0, Math.floor(((num >> 8) & 0xff) * (1 - amount)));
    const b = Math.max(0, Math.floor((num & 0xff) * (1 - amount)));
    return `#${((r << 16) | (g << 8) | b).toString(16).padStart(6, "0")}`;
}

function markerColor(site, part) {
    const key = getSiteValue(site);
    const fill = getColor(key);
    return part === "fill" ? fill : darkenColor(fill, 0.4);
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
