<template>
    <div v-if="kanbanGroups.length > 0" class="kanban-container">
        <div
            v-for="group in kanbanGroups"
            :key="group.platform"
            class="kanban-column"
        >
            <div class="text-subtitle-2 font-weight-bold">
                {{ group.platform }}
            </div>
            <div class="d-flex flex-wrap ga-1 mb-3">
                <v-chip size="x-small" variant="tonal">
                    {{ group.sites.length }}
                </v-chip>
                <v-chip
                    v-for="(count, value) in groupCounts(group.sites)"
                    :key="value"
                    size="x-small"
                    variant="flat"
                    :color="getDataColor(value)"
                >
                    {{ count }}
                </v-chip>
            </div>
            <div class="kanban-cards">
                <div
                    v-for="site in group.sites"
                    :key="site.id"
                    class="kanban-circle"
                    :style="circleStyle(site)"
                >
                    {{ site.name }}
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { computed } from "vue";

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

const legendOrder = computed(() => props.legend.map((entry) => entry.value));

const kanbanGroups = computed(() => {
    const groups = {};
    for (const site of props.sites) {
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

function getColor(value) {
    return legendMap.value[value] || "#E0E0E0";
}

function isLightColor(hex) {
    const r = parseInt(hex.slice(1, 3), 16);
    const g = parseInt(hex.slice(3, 5), 16);
    const b = parseInt(hex.slice(5, 7), 16);
    return r * 0.299 + g * 0.587 + b * 0.114 > 186;
}

function getDataColor(value) {
    return getColor(value);
}

function groupCounts(sites) {
    const counts = {};
    for (const site of sites) {
        const value =
            props.dataMode === "active"
                ? site.active
                    ? "Active"
                    : "Inactive"
                : site.tier;
        counts[value] = (counts[value] || 0) + 1;
    }
    const sorted = Object.entries(counts);
    if (props.dataMode === "tier") {
        sorted.sort((a, b) => legendOrder.value.indexOf(a[0]) - legendOrder.value.indexOf(b[0]));
    }
    return Object.fromEntries(sorted);
}

function circleStyle(site) {
    const key = props.dataMode === "active" ? (site.active ? "Active" : "Inactive") : site.tier;
    const bg = getColor(key);
    return {
        backgroundColor: bg,
        color: isLightColor(bg) ? "#616161" : "#FFFFFF",
    };
}
</script>

<style scoped>
.kanban-container {
    display: flex;
    gap: 0;
    overflow-x: auto;
    padding-bottom: 8px;
}

.kanban-column {
    border-right: 1px solid #e0e0e0;
    padding: 0 16px;
    min-width: 160px;
    text-align: center;
}

.kanban-column:last-child {
    border-right: none;
}

.kanban-cards {
    display: flex;
    flex-direction: row;
    flex-wrap: wrap;
    gap: 12px;
    align-items: center;
    justify-content: center;
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
</style>
