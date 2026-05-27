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

            <template v-else-if="data">
                <v-card variant="outlined" class="subtle-border">
                    <div class="text-body-1 font-weight-medium px-4 pt-4 pb-2">
                        General Details
                    </div>
                    <v-card-text>
                        <v-row dense>
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

                <v-card variant="outlined" class="subtle-border mt-4">
                    <div class="d-flex align-center px-4 pt-4 pb-2">
                        <div class="text-body-1 font-weight-medium">
                            Site KPI
                        </div>
                        <v-spacer />
                        <div class="d-flex align-center ga-2">
                            <v-btn
                                icon
                                variant="text"
                                size="small"
                                @click="prevMonth"
                            >
                                <v-icon>mdi-chevron-left</v-icon>
                            </v-btn>
                            <span class="text-body-2">{{ displayMonth }}</span>
                            <v-btn
                                icon
                                variant="text"
                                size="small"
                                @click="nextMonth"
                            >
                                <v-icon>mdi-chevron-right</v-icon>
                            </v-btn>
                        </div>
                    </div>
                    <v-card-text>
                        <v-row dense>
                            <v-col
                                v-for="(kpi, key) in data.kpis"
                                :key="key"
                                cols="3"
                            >
                                <div class="caption-label text-medium-emphasis">
                                    {{ kpi.label }}
                                </div>
                                <div class="text-body-1">
                                    {{ formatKpiValue(kpi) }}
                                </div>
                            </v-col>
                        </v-row>
                    </v-card-text>
                </v-card>
            </template>
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

const now = new Date();
const loading = ref(false);
const error = ref(false);
const data = ref(null);
const selectedMonth = ref(
    `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, "0")}`,
);

const monthNames = [
    "Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
];

const displayMonth = computed(() => {
    const [year, month] = selectedMonth.value.split("-");
    return `${monthNames[parseInt(month) - 1]} ${year}`;
});

function parseMonth(value) {
    const [y, m] = value.split("-").map(Number);
    return { year: y, month: m };
}

function prevMonth() {
    const { year, month } = parseMonth(selectedMonth.value);
    const d = new Date(year, month - 2, 1);
    selectedMonth.value = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}`;
}

function nextMonth() {
    const { year, month } = parseMonth(selectedMonth.value);
    const d = new Date(year, month, 1);
    selectedMonth.value = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}`;
}

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

function formatKpiValue(kpi) {
    const val =
        typeof kpi.value === "number"
            ? Number(kpi.value).toLocaleString("en-US")
            : kpi.value ?? "-";
    const obj =
        typeof kpi.objective === "number"
            ? Number(kpi.objective).toLocaleString("en-US")
            : kpi.objective ?? "-";
    return `${val} / ${obj}`;
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
        const res = await axios.get(`/api/sites/${props.site.id}/analysis`, {
            params: { month: selectedMonth.value },
        });
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
