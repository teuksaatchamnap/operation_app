<template>
    <v-card class="kpi-card rounded-xl" :loading="loading">
        <v-card-item>
            <div class="d-flex justify-space-between align-start">
                <div>
                    <v-card-title>
                        <span class="text-lg">{{
                            kpi?.name || kpi?.col_name || ""
                        }}</span>
                    </v-card-title>

                    <v-card-subtitle
                        v-if="latestAvailable"
                        class="text-caption text-medium-emphasis"
                    >
                        Latest Available in
                        {{ filters.month.slice(0, 4) ?? "" }}
                    </v-card-subtitle>
                    <v-card-subtitle
                        v-else-if="yearToDate"
                        class="text-caption text-medium-emphasis"
                    >
                        YTD ⇒ {{ filters.month ?? "" }}
                    </v-card-subtitle>
                    <v-card-subtitle
                        v-else
                        class="text-caption text-medium-emphasis"
                    >
                        {{ kpi?.periodicity || "Monthly" }}
                        {{ filters.month ?? "" }}
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

        <v-card-text class="text-center py-1">
            <div class="text-h1 font-weight-bold text-primary kpi-value">
                {{ formatValue(displayValue) }}
            </div>
            <div class="text-subtitle-1 text-medium-emphasis mt-0 mb-3">
                {{ kpi?.unit || "" }}
            </div>
            <div v-if="matchingObjective" class="text-left">
                <v-chip
                    v-if="objectiveReached"
                    size="small"
                    color="success"
                    variant="tonal"
                    class="ma-0"
                >
                    <v-icon start size="x-small"> mdi-check-circle </v-icon>
                    Objective : {{ formatValue(matchingObjective.value) }}
                </v-chip>
                <v-chip
                    v-else
                    size="small"
                    color="error"
                    variant="tonal"
                    class="ma-0"
                >
                    <v-icon start size="x-small"> mdi-close-circle </v-icon>
                    Objective : {{ formatValue(matchingObjective.value) }}
                </v-chip>
                <div class="text-caption text-medium-emphasis pa-0 ma-0 ml-2">
                    <v-icon size="x-small">mdi-delta</v-icon>
                    {{ objectiveDelta >= 0 ? "+" : ""
                    }}{{ formatValue(Math.abs(objectiveDelta)) }}
                </div>
            </div>
        </v-card-text>
    </v-card>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from "vue";
import axios from "axios";

const props = defineProps({
    kpi: {
        type: Object,
        default: null,
    },
    yearToDate: {
        type: Number,
        default: () => 0,
    },
    latestAvailable: {
        type: Number,
        default: () => 0,
    },
    filters: {
        type: Object,
        default: () => ({}),
    },
});

const computedValue = ref(0);
const loading = ref(false);
const displayValue = ref(0);
const randomInterval = ref(null);

const matchingObjective = computed(() => {
    if (!props.kpi?.objectives?.length || !props.filters.month) return null;

    return (
        props.kpi.objectives.find((obj) => {
            return (
                obj.type === "global" &&
                props.filters.month >= obj.start_date &&
                (props.filters.month <= obj.end_date || obj.end_date == null)
            );
        }) || null
    );
});

const objectiveDelta = computed(() => {
    if (!matchingObjective.value) return null;
    return computedValue.value - parseFloat(matchingObjective.value.value);
});

const objectiveReached = computed(() => {
    if (!matchingObjective.value) return null;
    return computedValue.value >= parseFloat(matchingObjective.value.value);
});

function formatValue(value) {
    if (value === null || value === undefined) return "-";

    const numValue = typeof value === "string" ? parseFloat(value) : value;

    if (!isNaN(numValue)) {
        return numValue.toLocaleString("en-US", {
            maximumFractionDigits: 2,
            minimumFractionDigits: 0,
        });
    }
    return value;
}

async function fetchComputedValue() {
    if (
        !props.kpi ||
        !props.filters ||
        Object.keys(props.filters).length === 0
    ) {
        computedValue.value = 0;
        return;
    }

    loading.value = true;

    try {
        const params = {
            kpis: props.kpi.col_name,
            year_to_date: props.yearToDate,
            latest_available: props.latestAvailable,
        };

        if (props.kpi.aggregate) {
            params.aggregate = props.kpi.aggregate;
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
            computedValue.value = data[0][props.kpi.col_name] || 0;
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
    await fetchComputedValue();
});

watch(
    () => props.kpi,
    async (newKpi) => {
        if (newKpi) {
            await fetchComputedValue();
        }
    },
);

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

.kpi-card {
    min-width: 210px;
    flex-shrink: 0;
}
</style>
