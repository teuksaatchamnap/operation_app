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
                    <div class="text-body-1 font-weight-medium px-4 pt-2">
                        General Details
                    </div>
                    <v-card-text>
                        <v-row density="comfortable">
                            <v-col cols="3">
                                <div class="caption-label text-medium-emphasis">
                                    Platform
                                </div>
                                <div class="text-body-1">
                                    {{ data.platform ?? "-" }}
                                </div>
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
                                <div class="text-body-1">
                                    {{ formattedDate }}
                                </div>
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
                                <div class="text-body-1">
                                    {{ data.rom_name ?? "-" }}
                                </div>
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
                                <div class="text-body-1">
                                    {{ formattedPopulation }}
                                </div>
                            </v-col>
                            <v-col cols="3">
                                <div class="caption-label text-medium-emphasis">
                                    Households
                                </div>
                                <div class="text-body-1">
                                    {{ formattedHouseholds }}
                                </div>
                            </v-col>
                        </v-row>
                    </v-card-text>
                </v-card>

                <v-card variant="outlined" class="subtle-border mt-4">
                    <div class="d-flex align-center px-4">
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
                        <v-row density="comfortable">
                            <v-col
                                v-for="(kpi, key) in data.kpis"
                                :key="key"
                                cols="3"
                            >
                                <div class="caption-label text-medium-emphasis">
                                    <v-tooltip
                                        v-if="kpi.description"
                                        location="top"
                                        max-width="300"
                                    >
                                        <template v-slot:activator="{ props: tooltipProps }">
                                            <span
                                                v-bind="tooltipProps"
                                                class="d-inline-flex align-center ga-1"
                                            >
                                                {{ kpi.label }}
                                                <v-icon
                                                    size="x-small"
                                                    color="info"
                                                >
                                                    mdi-help-circle
                                                </v-icon>
                                            </span>
                                        </template>
                                        <span>{{ kpi.description }}</span>
                                    </v-tooltip>
                                    <template v-else>{{ kpi.label }}</template>
                                </div>
                                <div class="text-body-1 d-flex align-center ga-1">
                                    <v-icon
                                        v-if="objectiveMetClass(kpi) !== null"
                                        :color="objectiveMetClass(kpi) === true ? 'success' : 'error'"
                                        size="x-small"
                                    >
                                        mdi-circle
                                    </v-icon>
                                    {{ formatKpiValue(kpi) }}
                                </div>
                            </v-col>
                        </v-row>
                    </v-card-text>
                </v-card>

                <v-card variant="outlined" class="subtle-border mt-4">
                    <div class="text-body-1 font-weight-medium px-4 pt-2">
                        Monthly Sales Performance
                    </div>
                    <v-card-text>
                        <div v-if="chartLoading" class="text-center pa-4">
                            <v-progress-circular indeterminate />
                        </div>
                        <div
                            v-else-if="chartError"
                            class="text-medium-emphasis text-center pa-4"
                        >
                            Failed to load monthly performance
                        </div>
                        <apexchart
                            v-else-if="chartData"
                            ref="chartRef"
                            type="line"
                            height="350"
                            :options="chartOptions"
                            :series="chartData.series"
                        />
                        <div
                            v-if="chartData"
                            class="d-flex justify-end ga-1 mt-1"
                        >
                            <v-btn
                                variant="text"
                                size="small"
                                prepend-icon="mdi-file-image"
                                @click="exportChart('png')"
                            >
                                PNG
                            </v-btn>
                            <v-btn
                                variant="text"
                                size="small"
                                prepend-icon="mdi-file-document"
                                @click="exportChart('svg')"
                            >
                                SVG
                            </v-btn>
                            <v-btn
                                variant="text"
                                size="small"
                                prepend-icon="mdi-file-delimited"
                                @click="exportChart('csv')"
                            >
                                CSV
                            </v-btn>
                        </div>
                    </v-card-text>
                </v-card>
            </template>
        </v-card-text>
    </v-card>
</template>

<script setup>
import axios from "axios";
import { computed, ref, watchEffect } from "vue";
import { useTheme } from "vuetify";

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
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec",
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

function objectiveMetClass(kpi) {
    const val = typeof kpi.value === "number" ? kpi.value : parseFloat(kpi.value);
    const obj = typeof kpi.objective === "number" ? kpi.objective : parseFloat(kpi.objective);
    if (isNaN(val) || isNaN(obj)) return null;
    return val >= obj;
}

function formatKpiValue(kpi) {
    const val =
        typeof kpi.value === "number"
            ? Number(kpi.value).toLocaleString("en-US")
            : (kpi.value ?? "-");
    const obj =
        typeof kpi.objective === "number"
            ? Number(kpi.objective).toLocaleString("en-US")
            : (kpi.objective ?? "-");
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

const chartData = ref(null);
const chartLoading = ref(false);
const chartError = ref(false);
const chartRef = ref(null);

function exportChart(format) {
    if (!chartRef.value) return;

    if (format === "csv") {
        chartRef.value.chart.exports.csv();
        return;
    }

    const type = format === "svg" ? "svg" : undefined;
    const filename = `monthly-sales-performance.${format}`;
    chartRef.value.chart.dataURI({ scale: 1, type }).then(({ imgURI }) => {
        const link = document.createElement("a");
        link.href = imgURI;
        link.download = filename;
        link.click();
    });
}

const theme = useTheme();
const isDark = computed(() => theme.global.name.value === "dark");

const textColor = computed(() => (isDark.value ? "#e0e0e0" : "#333333"));

const chartColors = [
    "#FF6384",
    "#36A2EB",
    "#FFCE56",
    "#4BC0C0",
    "#9966FF",
    "#FF9F40",
];

const chartOptions = computed(() => {
    const series = chartData.value?.series ?? [];
    const categories = chartData.value?.categories ?? [];

    const options = {
        chart: {
            foreColor: textColor.value,
            background: "transparent",
            zoom: {
                enabled: false,
            },
            toolbar: {
                tools: {
                    download: false,
                    selection: false,
                    zoom: false,
                    zoomin: false,
                    zoomout: false,
                    pan: false,
                    reset: false,
                },
            },
        },
        colors: chartColors,
        xaxis: {
            categories,
            labels: {
                style: {
                    colors: textColor.value,
                },
            },
        },
        yaxis: {
            labels: {
                style: {
                    colors: textColor.value,
                },
            },
            title: {
                text: "bottles/day",
                style: {
                    color: textColor.value,
                },
            },
        },
        stroke: {
            curve: "smooth",
            width: 2,
        },
        legend: {
            position: "bottom",
            horizontalAlign: "center",
            labels: {
                colors: textColor.value,
            },
        },
        tooltip: {
            shared: true,
            theme: isDark.value ? "dark" : "light",
        },
        responsive: [
            {
                breakpoint: 600,
                options: {
                    chart: { height: 250 },
                },
            },
        ],
    };

    const [selYear, selMonthNum] = selectedMonth.value.split("-");
    const selMonthIndex = parseInt(selMonthNum, 10) - 1;
    const seriesIdx = series.findIndex((s) => s.name === selYear);

    if (
        seriesIdx >= 0
        && series[seriesIdx].data[selMonthIndex] != null
    ) {
        const yVal = series[seriesIdx].data[selMonthIndex];
        const color = chartColors[seriesIdx] || chartColors[0];

        options.annotations = {
            points: [
                {
                    x: categories[selMonthIndex],
                    y: yVal,
                    seriesIndex: seriesIdx,
                    marker: {
                        size: 8,
                        fillColor: color,
                        strokeColor: "#fff",
                        strokeWidth: 2,
                        shape: "circle",
                    },
                },
            ],
        };
    }

    return options;
});

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

watchEffect(async () => {
    if (!props.site?.id) return;

    chartLoading.value = true;
    chartError.value = false;

    try {
        const res = await axios.get(
            `/api/sites/${props.site.id}/monthly-performance`,
        );
        const currentYear = String(now.getFullYear());
        const currentMonth = now.getMonth();
        const series = res.data.series.map((s) => {
            if (s.name === currentYear) {
                return { ...s, data: s.data.slice(0, currentMonth + 1) };
            }
            return s;
        });
        chartData.value = { ...res.data, series };
    } catch {
        chartError.value = true;
        chartData.value = null;
    } finally {
        chartLoading.value = false;
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
