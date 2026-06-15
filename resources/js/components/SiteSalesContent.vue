<template>
    <v-card flat>
        <v-card-text>
            <template v-if="loading">
                <v-card variant="outlined" class="subtle-border">
                    <v-card-title
                        class="section-title d-flex align-center ga-2"
                    >
                        <v-icon size="small" color="primary"
                            >mdi-chart-line</v-icon
                        >
                        Sales by Channel
                    </v-card-title>
                    <v-card-text>
                        <div class="skeleton skeleton-table" />
                    </v-card-text>
                </v-card>
            </template>

            <v-row v-else-if="error" class="text-center">
                <v-col>
                    <div class="text-medium-emphasis">
                        Failed to load sales data
                    </div>
                </v-col>
            </v-row>

            <template v-else-if="data">
                <v-card variant="outlined" class="subtle-border">
                    <v-card-title
                        class="section-title d-flex align-center ga-2"
                    >
                        <v-icon size="small" color="primary"
                            >mdi-chart-line</v-icon
                        >
                        Sales by Channel
                        <v-spacer />
                        <div class="d-flex align-center ga-2">
                            <CurrencySwitch />
                        </div>
                        <div class="d-flex align-center ga-2 ml-2">
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
                    </v-card-title>
                    <v-card-text>
                        <v-table
                            v-if="data.sales.length"
                            density="compact"
                            class="sales-table"
                        >
                            <thead>
                                <tr class="accent-header">
                                    <th class="caption-label font-weight-bold">
                                        Date
                                    </th>
                                    <th
                                        v-for="ch in channels"
                                        :key="ch.key"
                                        class="caption-label font-weight-bold text-right"
                                    >
                                        {{ ch.label }}<br />
                                        <span class="text-medium-emphasis">
                                            {{
                                                formatCurrency(
                                                    data.prices[ch.priceKey],
                                                )
                                            }}
                                        </span>
                                    </th>
                                    <th
                                        class="caption-label font-weight-bold text-right"
                                    >
                                        Total
                                    </th>
                                    <th
                                        class="caption-label font-weight-bold text-right"
                                    >
                                        Total sales<br />
                                        <span class="text-medium-emphasis">{{
                                            currency === "usd" ? "USD" : "KHR"
                                        }}</span>
                                    </th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr v-for="sale in data.sales" :key="sale.date">
                                    <td class="font-weight-medium">
                                        {{ formatDate(sale.date) }}
                                    </td>
                                    <td
                                        v-for="ch in channels"
                                        :key="ch.key"
                                        class="text-right"
                                    >
                                        {{ sale[ch.key] }}
                                    </td>
                                    <td class="text-right font-weight-bold">
                                        {{ sale.Total_Sales }}
                                    </td>
                                    <td class="text-right font-weight-bold">
                                        {{ formatCurrency(getRowTotal(sale)) }}
                                    </td>
                                </tr>
                                <tr class="sales-total-row">
                                    <td
                                        class="font-weight-bold text-uppercase caption-label"
                                    >
                                        Total
                                    </td>
                                    <td
                                        v-for="ch in channels"
                                        :key="ch.key"
                                        class="text-right font-weight-bold"
                                    >
                                        {{ formatNumber(data.totals[ch.key]) }}
                                    </td>
                                    <td class="text-right font-weight-bold">
                                        {{
                                            formatNumber(
                                                data.totals.Total_Sales,
                                            )
                                        }}
                                    </td>
                                </tr>
                                <tr class="sales-income-row">
                                    <td
                                        class="font-weight-bold text-uppercase caption-label"
                                    >
                                        {{
                                            currency === "usd"
                                                ? "Total USD"
                                                : "Total KHR"
                                        }}
                                    </td>
                                    <td
                                        v-for="ch in channels"
                                        :key="ch.key"
                                        class="text-right font-weight-bold"
                                    >
                                        {{
                                            formatCurrency(
                                                data.income[ch.incomeKey],
                                            )
                                        }}
                                    </td>
                                    <td />
                                    <td
                                        rowspan="2"
                                        class="text-right font-weight-bold"
                                    >
                                        {{
                                            formatCurrency(
                                                data.income.Total_Income,
                                            )
                                        }}
                                    </td>
                                </tr>
                            </tbody>
                        </v-table>
                        <div
                            v-else
                            class="text-medium-emphasis text-center pa-4"
                        >
                            No sales data for this month
                        </div>
                    </v-card-text>
                </v-card>

                <div class="mt-4">
                    <MonthlyPerformanceChart
                        :site="site"
                        :month="selectedMonth"
                    />
                </div>

                <div class="mt-4">
                    <v-card variant="outlined" class="subtle-border">
                        <v-card-title
                            class="section-title d-flex align-center ga-2"
                        >
                            <v-icon size="small" color="primary"
                                >mdi-chart-line</v-icon
                            >
                            Sales Comparison: Kiosk vs Platform vs Network
                        </v-card-title>
                        <v-card-text>
                            <div
                                v-if="comparisonLoading"
                                class="text-center pa-4"
                            >
                                <v-progress-circular indeterminate />
                            </div>
                            <div
                                v-else-if="comparisonError"
                                class="text-medium-emphasis text-center pa-4"
                            >
                                Failed to load sales comparison
                            </div>
                            <ApexChart
                                v-else-if="comparisonData"
                                ref="comparisonChartRef"
                                type="line"
                                height="350"
                                :options="comparisonOptions"
                                :series="comparisonData.series"
                            />
                            <div
                                v-else
                                class="text-medium-emphasis text-center pa-4"
                            >
                                No comparison data available
                            </div>
                            <ChartExportButtons
                                v-if="comparisonData"
                                :chart="comparisonChartRef?.chart"
                                filename="sales-comparison"
                            />
                        </v-card-text>
                    </v-card>
                </div>

                <div class="mt-4">
                    <v-card variant="outlined" class="subtle-border">
                        <v-card-title
                            class="section-title d-flex align-center ga-2"
                        >
                            <v-icon size="small" color="primary"
                                >mdi-water</v-icon
                            >
                            Water Loss by Week
                        </v-card-title>
                        <v-card-text>
                            <template v-if="waterLoading">
                                <div class="skeleton skeleton-table" />
                            </template>

                            <template v-else-if="waterError">
                                <div
                                    class="text-medium-emphasis text-center pa-4"
                                >
                                    Failed to load water loss data
                                </div>
                            </template>

                            <template
                                v-else-if="waterData && waterData.weeks.length"
                            >
                                <v-table density="compact" class="sales-table">
                                    <thead>
                                        <tr class="accent-header">
                                            <th
                                                class="caption-label font-weight-bold"
                                            >
                                                Week
                                            </th>
                                            <th
                                                class="caption-label font-weight-bold text-right"
                                            >
                                                Meter Start (L)
                                            </th>
                                            <th
                                                class="caption-label font-weight-bold text-right"
                                            >
                                                Meter End (L)
                                            </th>
                                            <th
                                                class="caption-label font-weight-bold text-right"
                                            >
                                                Consumed (L)
                                            </th>
                                            <th
                                                class="caption-label font-weight-bold text-right"
                                            >
                                                Sold (L)
                                            </th>
                                            <th
                                                class="caption-label font-weight-bold text-right"
                                            >
                                                Loss (L)
                                            </th>
                                            <th
                                                class="caption-label font-weight-bold text-right"
                                            >
                                                Loss (%)
                                            </th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        <tr
                                            v-for="w in waterData.weeks"
                                            :key="w.week"
                                        >
                                            <td class="font-weight-medium">
                                                {{ w.week }}
                                            </td>
                                            <td class="text-right">
                                                {{
                                                    w.meter_start != null
                                                        ? formatNumber(
                                                              w.meter_start,
                                                          )
                                                        : "N/A"
                                                }}
                                            </td>
                                            <td class="text-right">
                                                {{
                                                    w.meter_end != null
                                                        ? formatNumber(
                                                              w.meter_end,
                                                          )
                                                        : "N/A"
                                                }}
                                            </td>
                                            <td class="text-right">
                                                {{
                                                    w.consumed != null
                                                        ? formatNumber(
                                                              w.consumed,
                                                          )
                                                        : "N/A"
                                                }}
                                            </td>
                                            <td class="text-right">
                                                {{ formatNumber(w.sold) }}
                                            </td>
                                            <td class="text-right">
                                                {{
                                                    w.loss != null
                                                        ? formatNumber(w.loss)
                                                        : "N/A"
                                                }}
                                            </td>
                                            <td class="text-right">
                                                {{
                                                    w.loss_pct != null
                                                        ? w.loss_pct + "%"
                                                        : "N/A"
                                                }}
                                            </td>
                                        </tr>
                                    </tbody>
                                </v-table>
                            </template>

                            <div
                                v-else
                                class="text-medium-emphasis text-center pa-4"
                            >
                                No water loss data for this month
                            </div>
                        </v-card-text>
                    </v-card>
                </div>
            </template>
        </v-card-text>
    </v-card>
</template>

<script setup>
import axios from "axios";
import { computed, ref, watchEffect, defineAsyncComponent } from "vue";
import { useCurrency } from "../composables/useCurrency";
import { useTheme } from "vuetify";
import CurrencySwitch from "./CurrencySwitch.vue";
import ChartExportButtons from "./ChartExportButtons.vue";
import MonthlyPerformanceChart from "./MonthlyPerformanceChart.vue";

const ApexChart = defineAsyncComponent(() => import("vue3-apexcharts"));

const props = defineProps({
    site: {
        type: Object,
        default: null,
    },
    initialMonth: {
        type: String,
        default: "",
    },
});

const now = new Date();
const loading = ref(false);
const error = ref(false);
const data = ref(null);
const waterLoading = ref(false);
const waterError = ref(false);
const waterData = ref(null);
const selectedMonth = ref(
    props.initialMonth ||
        `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, "0")}`,
);

const displayMonth = computed(() => {
    const [year, month] = selectedMonth.value.split("-").map(Number);
    return new Date(year, month - 1, 1).toLocaleDateString("en-US", {
        month: "short",
        year: "numeric",
    });
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
        month: "short",
        day: "numeric",
    });
}

function formatNumber(num) {
    if (num === null || num === undefined) return "-";
    return Number(num).toLocaleString("en-US");
}

function getRowTotal(sale) {
    if (!data.value?.prices || !sale) return 0;
    let total = 0;
    for (const ch of channels) {
        total += (sale[ch.key] || 0) * (data.value.prices[ch.priceKey] || 0);
    }
    return total;
}

const { currency, formatCurrency } = useCurrency();

const comparisonLoading = ref(false);
const comparisonError = ref(false);
const comparisonData = ref(null);
const comparisonChartRef = ref(null);

const theme = useTheme();
const isDark = computed(() => theme.global.name.value === "dark");
const textColor = computed(() => (isDark.value ? "#e0e0e0" : "#333333"));

const comparisonColors = ["#FF6384", "#36A2EB", "#4BC0C0", "#FF9F40"];

const comparisonOptions = computed(() => {
    const categories = comparisonData.value?.categories ?? [];

    return {
        chart: {
            foreColor: textColor.value,
            background: "transparent",
            zoom: { enabled: false },
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
        colors: comparisonColors,
        xaxis: {
            categories,
            labels: { style: { colors: textColor.value } },
        },
        yaxis: {
            labels: { style: { colors: textColor.value } },
            title: {
                text: "Sales Volume",
                style: { color: textColor.value },
            },
        },
        stroke: {
            curve: "smooth",
            width: 2,
            dashArray: [0, 0, 0, 5],
        },
        legend: {
            position: "bottom",
            horizontalAlign: "center",
            labels: { colors: textColor.value },
        },
        tooltip: {
            shared: true,
            theme: isDark.value ? "dark" : "light",
        },
        responsive: [
            {
                breakpoint: 600,
                options: { chart: { height: 250 } },
            },
        ],
    };
});

watchEffect(async () => {
    if (!props.site?.id) return;

    comparisonLoading.value = true;
    comparisonError.value = false;

    try {
        const res = await axios.get(
            `/api/sites/${props.site.id}/sales-comparison`,
        );
        comparisonData.value = res.data;
    } catch {
        comparisonError.value = true;
        comparisonData.value = null;
    } finally {
        comparisonLoading.value = false;
    }
});

const channels = [
    {
        key: "Free_Sales",
        label: "Free",
        priceKey: "Free_Price",
        incomeKey: "Free_Income",
    },
    {
        key: "Hod_Sales",
        label: "Home Delivery",
        priceKey: "Hod_Price",
        incomeKey: "Hod_Income",
    },
    {
        key: "WiS_Sales",
        label: "School",
        priceKey: "WiS_Price",
        incomeKey: "WiS_Income",
    },
    {
        key: "Onsite_Sales",
        label: "On-Site",
        priceKey: "Onsite_Price",
        incomeKey: "Onsite_Income",
    },
    {
        key: "Shopkeeper_Sales",
        label: "Shopkeeper",
        priceKey: "Shopkeeper_Price",
        incomeKey: "Shopkeeper_Income",
    },
    {
        key: "Bottle_Sales",
        label: "Bottle",
        priceKey: "Bottle_Price",
        incomeKey: "Bottle_Income",
    },
    {
        key: "Other_Sales",
        label: "Other",
        priceKey: "Other_Price",
        incomeKey: "Other_Income",
    },
];

watchEffect(async () => {
    if (!props.site?.id) return;

    loading.value = true;
    error.value = false;

    try {
        const res = await axios.get(`/api/sites/${props.site.id}/daily-sales`, {
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

    waterLoading.value = true;
    waterError.value = false;

    try {
        const res = await axios.get(
            `/api/sites/${props.site.id}/water-loss-by-week`,
            {
                params: { month: selectedMonth.value },
            },
        );
        waterData.value = res.data;
    } catch {
        waterError.value = true;
        waterData.value = null;
    } finally {
        waterLoading.value = false;
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

.caption-label {
    font-size: 0.75rem;
}

.subtle-border {
    border-color: rgba(var(--v-theme-on-surface), 0.12) !important;
}

.sales-table tbody tr:hover td {
    background-color: rgba(var(--v-theme-on-surface), 0.04);
}

.sales-table tbody tr:nth-child(even) td {
    background-color: rgba(var(--v-theme-on-surface), 0.02);
}

.accent-header th {
    background-color: rgba(var(--v-theme-primary), 0.1);
    border-bottom: 2px solid rgb(var(--v-theme-primary)) !important;
}

.sales-total-row td {
    font-weight: 700;
    border-top: 2px solid rgba(var(--v-theme-on-surface), 0.15);
    padding-top: 10px !important;
    padding-bottom: 10px !important;
    background-color: rgba(var(--v-theme-primary), 0.06);
}

.sales-income-row td {
    background-color: rgba(var(--v-theme-success), 0.06);
    border-top: 1px solid rgba(var(--v-theme-success), 0.25);
}

.skeleton {
    background: rgba(var(--v-theme-on-surface), 0.08);
    border-radius: 4px;
    animation: skeleton-pulse 1.5s ease-in-out infinite;
}

.skeleton-table {
    height: 350px;
    width: 100%;
}

@keyframes skeleton-pulse {
    0%,
    100% {
        opacity: 1;
    }
    50% {
        opacity: 0.35;
    }
}
</style>
