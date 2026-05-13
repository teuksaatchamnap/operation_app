<template>
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

function getTierColor(tier) {
    return TIER_COLORS[tier] || "#E0E0E0";
}

function isLightColor(hex) {
    const r = parseInt(hex.slice(1, 3), 16);
    const g = parseInt(hex.slice(3, 5), 16);
    const b = parseInt(hex.slice(5, 7), 16);
    return r * 0.299 + g * 0.587 + b * 0.114 > 186;
}

function circleStyle(site) {
    if (props.dataMode === "active") {
        return {
            backgroundColor: site.active ? "#4CAF50" : "#E0E0E0",
            color: site.active ? "#FFFFFF" : "#616161",
        };
    }
    const bg = getTierColor(site.tier);
    return {
        backgroundColor: bg,
        color: isLightColor(bg) ? "#616161" : "#FFFFFF",
    };
}
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
</style>
