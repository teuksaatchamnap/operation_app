<template>
    <v-card class="kpi-card rounded-xl" :loading="loading">
        <v-card-item>
            <div class="d-flex justify-space-between align-start">
                <div>
                    <v-card-title class="text-h6 font-weight-medium">
                        {{ kpi?.name || kpiColName }}
                    </v-card-title>

                    <v-card-subtitle
                        v-if="yearToDate == 1"
                        class="text-caption text-medium-emphasis"
                    >
                        YTD
                    </v-card-subtitle>
                    <v-card-subtitle
                        v-else
                        class="text-caption text-medium-emphasis"
                    >
                        {{ kpi?.periodicity || "Monthly" }}
                    </v-card-subtitle>
                </div>
                <v-tooltip
                    v-if="kpi?.description"
                    location="top"
                    max-width="300"
                >
                    <template v-slot:activator="{ props: tooltipProps }">
                        <v-btn
                            icon="mdi-help-circle"
                            variant="text"
                            density="comfortable"
                            size="small"
                            color="info"
                            v-bind="tooltipProps"
                        ></v-btn>
                    </template>
                    <span>{{ kpi.description }}</span>
                </v-tooltip>
            </div>
        </v-card-item>

        <v-card-text class="text-center py-6">
            <div class="text-h1 font-weight-bold text-primary kpi-value">
                {{ formatValue(displayValue) }}
            </div>
            <div class="text-subtitle-1 text-medium-emphasis mt-2">
                {{ kpi?.unit || "" }}
            </div>
        </v-card-text>
    </v-card>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted } from "vue";
import axios from "axios";

const props = defineProps({
    kpiColName: {
        type: String,
        required: true,
    },
    yearToDate: {
        type: Boolean,
        required: false,
        default: () => 0,
    },
    filters: {
        type: Object,
        default: () => ({}),
    },
});

const kpi = ref(null);
const computedValue = ref(0);
const loading = ref(false);
const displayValue = ref(0);
const randomInterval = ref(null);

function formatValue(value) {
    if (value === null || value === undefined) return "-";

    // Convert string to number if necessary
    const numValue = typeof value === "string" ? parseFloat(value) : value;

    if (!isNaN(numValue)) {
        return numValue.toLocaleString("en-US", {
            maximumFractionDigits: 2,
            minimumFractionDigits: 0,
        });
    }
    return value;
}

async function fetchKpiDetails() {
    try {
        const response = await axios.get("/api/kpis");
        const kpis = response.data;
        kpi.value = kpis.find((k) => k.col_name === props.kpiColName) || null;
    } catch (error) {
        console.error("Failed to fetch KPI details:", error);
    }
}

async function fetchComputedValue() {
    if (!props.filters || Object.keys(props.filters).length === 0) {
        computedValue.value = 0;
        return;
    }

    loading.value = true;

    try {
        const params = {
            kpis: props.kpiColName,
            year_to_date: props.yearToDate,
        };

        if (kpi.value?.aggregate) {
            params.aggregate = kpi.value.aggregate;
        }

        if (props.filters.site_ids?.length > 0) {
            params.site_ids = props.filters.site_ids;
        }

        if (props.filters.advisor_ids?.length > 0) {
            params.advisor_ids = props.filters.advisor_ids;
        }

        if (props.filters.platform_ids?.length > 0) {
            params.platform_ids = props.filters.platform_ids;
        }

        if (props.filters.month) {
            params.month = props.filters.month;
        }

        const response = await axios.get("/api/fact-monthly", { params });
        const data = response.data;

        if (data && data.length > 0) {
            computedValue.value = data[0][props.kpiColName] || 0;
        } else {
            computedValue.value = 0;
        }
    } catch (error) {
        console.error("Failed to fetch computed value:", error);
        computedValue.value = 0;
    } finally {
        loading.value = false;
    }
}

onMounted(async () => {
    await fetchKpiDetails();
    await fetchComputedValue();
});

onUnmounted(() => {
    if (randomInterval.value) {
        clearInterval(randomInterval.value);
    }
});

watch(
    () => props.filters,
    async () => {
        await fetchComputedValue();
    },
    { deep: true },
);

watch(
    () => loading.value,
    (isLoading) => {
        if (isLoading) {
            randomInterval.value = setInterval(() => {
                displayValue.value = Math.floor(Math.random() * 999999);
            }, 50);
        } else {
            if (randomInterval.value) {
                clearInterval(randomInterval.value);
                randomInterval.value = null;
            }
            displayValue.value = computedValue.value;
        }
    },
    { immediate: true },
);

watch(
    () => computedValue.value,
    (newValue) => {
        if (!loading.value) {
            displayValue.value = newValue;
        }
    },
);
</script>

<style scoped>
.kpi-value {
    font-size: 2rem !important;
    line-height: 1;
}

@media (min-width: 960px) {
    .kpi-value {
        font-size: 3rem !important;
    }
}
</style>
