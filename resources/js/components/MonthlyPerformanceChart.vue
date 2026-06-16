<template>
    <v-card variant="outlined" class="subtle-border">
        <v-card-title class="section-title d-flex align-center ga-2">
            <v-icon size="small" color="primary">mdi-chart-line</v-icon>
            Monthly Sales Performance
        </v-card-title>
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
            <ApexChart
                v-else-if="chartData"
                ref="chartRef"
                type="line"
                height="350"
                :options="chartOptions"
                :series="chartData.series"
            />
            <div v-else class="text-medium-emphasis text-center pa-4">
                No performance data available
            </div>
            <ChartExportButtons
                v-if="chartData"
                :chart="chartRef?.chart"
                filename="monthly-sales-performance"
            />
        </v-card-text>
    </v-card>
</template>

<script setup>
import axios from "axios";
import { computed, ref, watchEffect, defineAsyncComponent } from "vue";
import { useTheme } from "vuetify";

import ChartExportButtons from "./ChartExportButtons.vue";

const ApexChart = defineAsyncComponent(() => import("vue3-apexcharts"));

const props = defineProps({
    site: {
        type: Object,
        default: null,
    },
    month: {
        type: String,
        default: "",
    },
});

const now = new Date();
const chartData = ref(null);
const chartLoading = ref(false);
const chartError = ref(false);
const chartRef = ref(null);

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

    const colors = series.map((s) => {
        if (s.name === "Objectives") return "#FF0000";
        return chartColors[series.indexOf(s) % chartColors.length];
    });

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
        colors,
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
            width: series.map((s) =>
                s.name === String(now.getFullYear()) ? 6 : 2,
            ),
            dashArray: series.map((s) => (s.name === "Objectives" ? 6 : 0)),
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

    const selMonth =
        props.month ||
        `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, "0")}`;

    const [selYear, selMonthNum] = selMonth.split("-");
    const selMonthIndex = parseInt(selMonthNum, 10) - 1;
    const seriesIdx = series.findIndex((s) => s.name === selYear);

    if (seriesIdx >= 0 && series[seriesIdx].data[selMonthIndex] != null) {
        const yVal = series[seriesIdx].data[selMonthIndex];
        const color = colors[seriesIdx] || colors[0];

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
.section-title {
    font-size: 1rem;
    font-weight: 600;
    letter-spacing: 0.0125em;
    padding-block: 14px;
    line-height: 1.5rem;
}

.subtle-border {
    border-color: rgba(var(--v-theme-on-surface), 0.12) !important;
}
</style>
