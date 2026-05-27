<template>
    <v-card flat>
        <v-card-text>
            <v-row v-if="loading">
                <v-col class="text-center">
                    <v-progress-circular indeterminate />
                </v-col>
            </v-row>

            <v-row v-else-if="error" class="text-center">
                <v-col>
                    <div class="text-medium-emphasis">
                        Failed to load site analysis
                    </div>
                </v-col>
            </v-row>

            <v-card v-else-if="data" variant="outlined" class="subtle-border">
                <div class="text-body-1 font-weight-medium px-4 pt-4 pb-2">
                    General Details
                </div>
                <v-card-text>
                    <v-row>
                        <v-col cols="3">
                            <div class="caption-label text-medium-emphasis">
                                Platform
                            </div>
                            <div class="text-body-1">{{ data.platform ?? "-" }}</div>
                        </v-col>
                        <v-col cols="3">
                            <div class="caption-label text-medium-emphasis">
                                Entrepreneur Name
                            </div>
                            <div class="text-body-1">
                                {{ data.entrepreneur_name ?? "-" }}
                            </div>
                        </v-col>
                        <v-col cols="3">
                            <div class="caption-label text-medium-emphasis">
                                Start Working Date
                            </div>
                            <div class="text-body-1">{{ formattedDate }}</div>
                        </v-col>
                        <v-col cols="3">
                            <div class="caption-label text-medium-emphasis">
                                Advisor Name
                            </div>
                            <div class="text-body-1">
                                {{ data.advisor_name ?? "-" }}
                            </div>
                        </v-col>
                        <v-col cols="3">
                            <div class="caption-label text-medium-emphasis">
                                ROM Name
                            </div>
                            <div class="text-body-1">{{ data.rom_name ?? "-" }}</div>
                        </v-col>
                        <v-col cols="3">
                            <div class="caption-label text-medium-emphasis">
                                Commune Name
                            </div>
                            <div class="text-body-1">
                                {{ data.commune_name ?? "-" }}
                            </div>
                        </v-col>
                        <v-col cols="3">
                            <div class="caption-label text-medium-emphasis">
                                Population Commune
                            </div>
                            <div class="text-body-1">{{ formattedPopulation }}</div>
                        </v-col>
                        <v-col cols="3">
                            <div class="caption-label text-medium-emphasis">
                                Households
                            </div>
                            <div class="text-body-1">{{ formattedHouseholds }}</div>
                        </v-col>
                    </v-row>
                </v-card-text>
            </v-card>
        </v-card-text>
    </v-card>
</template>

<script setup>
import axios from "axios";
import { computed, ref, watchEffect } from "vue";

const props = defineProps({
    site: {
        type: Object,
        default: null,
    },
});

const loading = ref(false);
const error = ref(false);
const data = ref(null);

function formatDate(dateStr) {
    if (!dateStr) return "-";
    const date = new Date(dateStr);
    if (isNaN(date.getTime())) return dateStr;
    return date.toLocaleDateString("en-US", {
        year: "numeric",
        month: "short",
        day: "numeric",
    });
}

function formatNumber(num) {
    if (num === null || num === undefined) return "-";
    return Number(num).toLocaleString("en-US");
}

const formattedDate = computed(() =>
    formatDate(data.value?.start_working_date),
);
const formattedPopulation = computed(() =>
    formatNumber(data.value?.population_commune),
);
const formattedHouseholds = computed(() =>
    formatNumber(data.value?.households),
);
watchEffect(async () => {
    if (!props.site?.id) return;

    loading.value = true;
    error.value = false;

    try {
        const res = await axios.get(`/api/sites/${props.site.id}/analysis`);
        data.value = res.data;
    } catch {
        error.value = true;
        data.value = null;
    } finally {
        loading.value = false;
    }
});
</script>

<style scoped>
.caption-label {
    font-size: 0.65rem;
}

.subtle-border {
    border-color: rgba(var(--v-theme-on-surface), 0.12) !important;
}
</style>
