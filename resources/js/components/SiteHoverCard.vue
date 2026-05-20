<template>
    <v-card class="site-hover-card" elevation="4" min-width="220" max-width="280">
        <v-card-title class="text-subtitle-2 font-weight-bold pa-2 pb-0">
            {{ site.site_name }}
        </v-card-title>
        <v-divider class="mx-2" />
        <v-card-text class="text-caption pa-2">
            <div v-if="site.status" class="hover-row">
                <span class="text-medium-emphasis">Site Status:</span>
                <span class="font-weight-medium">{{ site.status }}</span>
            </div>
            <div v-if="site.platform" class="hover-row">
                <span class="text-medium-emphasis">Platform:</span>
                <span class="font-weight-medium">{{ site.platform }}</span>
            </div>
            <div v-if="site.entrepreneur" class="hover-row">
                <span class="text-medium-emphasis">Entrepreneur:</span>
                <span class="font-weight-medium">{{ site.entrepreneur }}</span>
            </div>
            <div v-if="site.advisor" class="hover-row">
                <span class="text-medium-emphasis">Advisor:</span>
                <span class="font-weight-medium">{{ site.advisor }}</span>
            </div>
            <div v-if="site.technician" class="hover-row">
                <span class="text-medium-emphasis">Technician:</span>
                <span class="font-weight-medium">{{ site.technician }}</span>
            </div>
            <div v-if="site.tier" class="hover-row">
                <span class="text-medium-emphasis">Tier:</span>
                <span class="font-weight-medium">{{ site.tier }}</span>
            </div>
            <div v-if="site.year_construction" class="hover-row">
                <span class="text-medium-emphasis">Year of Construction/Last Rehab:</span>
                <span class="font-weight-medium">{{ site.year_construction }}</span>
            </div>
        </v-card-text>
    </v-card>
</template>

<script setup>
defineProps({
    site: {
        type: Object,
        required: true,
    },
});
</script>

<style scoped>
.site-hover-card {
    pointer-events: none;
}

.hover-row {
    display: flex;
    justify-content: space-between;
    gap: 8px;
    line-height: 1.6;
}

.hover-row span:first-child {
    white-space: nowrap;
}
</style>
