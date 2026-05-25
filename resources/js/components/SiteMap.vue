<template>
    <div v-if="geojsonData" ref="containerRef" class="map-container">
        <l-map
            :zoom="7"
            :center="[12.5, 104.9]"
            style="height: 500px; width: 100%"
            @ready="onMapReady"
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
                @ready="($event) => bindHoverTooltip($event, site)"
                @click="emit('site-click', site)"
            />
        </l-map>
        <v-btn
            class="fullscreen-btn"
            variant="flat"
            density="compact"
            icon
            @click="toggleFullscreen"
        >
            <v-icon>{{ isFullscreen ? "mdi-fullscreen-exit" : "mdi-fullscreen" }}</v-icon>
        </v-btn>
    </div>
    <v-progress-linear
        v-else
        indeterminate
        color="primary"
        class="mb-2"
    />
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from "vue";
import { useTheme } from "vuetify";
import "leaflet/dist/leaflet.css";
import L from "leaflet";
import {
    LMap,
    LTileLayer,
    LGeoJson,
    LCircleMarker,
} from "@vue-leaflet/vue-leaflet";

import markerIcon from "leaflet/dist/images/marker-icon.png";
import markerShadow from "leaflet/dist/images/marker-shadow.png";

delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
    iconUrl: markerIcon,
    shadowUrl: markerShadow,
});

const emit = defineEmits(["site-click"]);

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
    hoverData: {
        type: Object,
        default: () => ({}),
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
const mapInstance = ref(null);
const containerRef = ref(null);
const isFullscreen = ref(false);

const theme = useTheme();
const isDark = computed(() => theme.global.current.value.dark);
const maskColor = computed(() => (isDark.value ? "#0f0f1a" : "#ffffff"));
const maskPolygon = ref(null);

function toggleFullscreen() {
    if (!containerRef.value) return;
    if (document.fullscreenElement) {
        document.exitFullscreen();
    } else {
        containerRef.value.requestFullscreen();
    }
}

function onFullscreenChange() {
    isFullscreen.value = !!document.fullscreenElement;
    if (mapInstance.value) {
        mapInstance.value.invalidateSize();
    }
}

watch(maskColor, (color) => {
    if (maskPolygon.value) {
        maskPolygon.value.setStyle({ fillColor: color, color });
    }
});

onMounted(() => {
    document.addEventListener("fullscreenchange", onFullscreenChange);
});

onUnmounted(() => {
    document.removeEventListener("fullscreenchange", onFullscreenChange);
});

function onMapReady(map) {
    mapInstance.value = map;
    if (geojsonData.value) {
        applyCanvasMask();
        clampMapView();
    }
}

function applyCanvasMask() {
    if (!mapInstance.value || !geojsonData.value) return;

    const map = mapInstance.value;

    map.createPane("maskPane");
    map.getPane("maskPane").style.zIndex = 300;

    const holes = [];

    for (const feature of geojsonData.value.features) {
        const geom = feature.geometry;
        if (geom.type === "Polygon") {
            const ring = geom.coordinates[0].map((c) => [c[1], c[0]]);
            holes.push(ring);
        } else if (geom.type === "MultiPolygon") {
            for (const polyCoords of geom.coordinates) {
                const ring = polyCoords[0].map((c) => [c[1], c[0]]);
                holes.push(ring);
            }
        }
    }

    const worldRing = [
        [-90, -180],
        [90, -180],
        [90, 180],
        [-90, 180],
        [-90, -180],
    ];

    const renderer = L.canvas({ pane: "maskPane", padding: 0.5 });

    maskPolygon.value = L.polygon([worldRing, ...holes], {
        renderer,
        fillColor: maskColor.value,
        fillOpacity: 0.95,
        color: maskColor.value,
        weight: 0,
        interactive: false,
    }).addTo(map);
}

function clampMapView() {
    if (!mapInstance.value || !geojsonData.value) return;
    const bounds = L.geoJSON(geojsonData.value).getBounds();
    mapInstance.value.setMaxBounds(bounds.pad(0.1));
}

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
    if (props.dataMode === "water_source") {
        return site.water_source || "N/A";
    }
    if (props.dataMode === "treatment_process") {
        return site.treatment_process || "N/A";
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

function bindHoverTooltip(marker, site) {
    const h = props.hoverData[site.id];
    if (!h) {
        marker.bindTooltip(site.name, { sticky: true });
        return;
    }

    function row(label, value) {
        return value
            ? `<div class="hover-row"><span>${label}</span><span class="hover-value">${value}</span></div>`
            : "";
    }

    const html = `
        <div class="site-hover-tooltip">
            <div class="hover-title">${h.site_name || site.name}</div>
            ${row("Site Status:", h.status)}
            ${row("Platform:", h.platform)}
            ${row("Entrepreneur:", h.entrepreneur)}
            ${row("Advisor:", h.advisor)}
            ${row("Technician:", h.technician)}
            ${row("Tier:", h.tier)}
            ${row("Year of Construction/Last Rehab:", h.year_construction)}
        </div>
    `;

    marker.bindTooltip(html, { sticky: true, className: "site-hover-tooltip" });
}

async function fetchGeoJson() {
    try {
        const res = await fetch("/CambodiaCommuneBoundaries.geojson");
        geojsonData.value = await res.json();
        if (mapInstance.value) {
            applyCanvasMask();
            clampMapView();
        }
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
    position: relative;
}

.map-container:fullscreen {
    padding: 0;
    border-radius: 0;
    width: 100vw;
    height: 100vh;
}

.map-container:fullscreen :deep(.leaflet-container) {
    height: 100% !important;
}

.fullscreen-btn {
    position: absolute;
    top: 8px;
    right: 8px;
    z-index: 1000;
}

:deep(.leaflet-tooltip.site-hover-tooltip) {
    background: #fff;
    color: #212121;
    border: none;
    border-radius: 8px;
    padding: 0;
    font-size: 12px;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.15);
    min-width: 200px;
    max-width: 260px;
}

:deep(.site-hover-tooltip .hover-title) {
    font-weight: 600;
    font-size: 13px;
    padding: 8px 10px 4px;
    border-bottom: 1px solid #e0e0e0;
    margin-bottom: 4px;
}

:deep(.site-hover-tooltip .hover-row) {
    display: flex;
    justify-content: space-between;
    gap: 8px;
    padding: 1px 10px;
    line-height: 1.7;
}

:deep(.site-hover-tooltip .hover-row span:first-child) {
    color: #757575;
    white-space: nowrap;
}

:deep(.site-hover-tooltip .hover-row .hover-value) {
    font-weight: 500;
    text-align: right;
}

:deep(.leaflet-tooltip.site-hover-tooltip.leaflet-tooltip-top:before),
:deep(.leaflet-tooltip.site-hover-tooltip.leaflet-tooltip-bottom:before) {
    border-top-color: #fff;
    border-bottom-color: #fff;
}

:deep(.leaflet-tooltip.site-hover-tooltip.leaflet-tooltip-left:before),
:deep(.leaflet-tooltip.site-hover-tooltip.leaflet-tooltip-right:before) {
    border-left-color: #fff;
    border-right-color: #fff;
}
</style>
