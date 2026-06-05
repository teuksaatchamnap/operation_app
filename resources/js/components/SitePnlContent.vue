<template>
    <v-card flat>
        <v-card-text>
            <template v-if="loading">
                <v-card variant="outlined" class="subtle-border">
                    <v-card-title class="section-title d-flex align-center ga-2">
                        <v-icon size="small" color="primary">mdi-cash-multiple</v-icon>
                        Expense Breakdown
                    </v-card-title>
                    <v-card-text>
                        <div class="skeleton skeleton-table" />
                    </v-card-text>
                </v-card>
            </template>

            <v-row v-else-if="error" class="text-center">
                <v-col>
                    <div class="text-medium-emphasis">
                        Failed to load expense data
                    </div>
                </v-col>
            </v-row>

            <template v-else-if="data">
                <v-card variant="outlined" class="subtle-border">
                    <v-card-title class="section-title d-flex align-center ga-2">
                        <v-icon size="small" color="primary">mdi-cash-multiple</v-icon>
                        Expense Breakdown
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
                            v-if="data.categories.length"
                            density="compact"
                            class="pnl-table"
                        >
                            <thead>
                                <tr class="accent-header">
                                    <th class="caption-label font-weight-bold">
                                        Category / Item
                                    </th>
                                    <th
                                        class="caption-label font-weight-bold text-right"
                                    >
                                        Amount
                                    </th>
                                </tr>
                            </thead>
                            <tbody>
                                <template
                                    v-for="cat in data.categories"
                                    :key="cat.category"
                                >
                                    <tr class="pl-section-header pl-expenses-header">
                                        <td colspan="2">
                                            <span class="font-weight-bold text-uppercase caption-label">{{ cat.category }}</span>
                                        </td>
                                    </tr>
                                    <tr
                                        v-for="item in cat.items"
                                        :key="item.ref"
                                    >
                                        <td class="pl-indent">
                                            {{ item.label }}
                                        </td>
                                        <td class="text-right font-weight-medium">
                                            {{ formatCurrency(item.amount) }}
                                        </td>
                                    </tr>
                                    <tr class="pl-expenses-subtotal">
                                        <td class="font-weight-bold">Subtotal {{ cat.category }}</td>
                                        <td class="text-right font-weight-bold">
                                            {{ formatCurrency(cat.sub_total) }}
                                        </td>
                                    </tr>
                                </template>
                                <tr class="pl-grand-total">
                                    <td class="font-weight-bold text-uppercase">Grand Total</td>
                                    <td class="text-right font-weight-bold">
                                        {{ formatCurrency(data.grand_total) }}
                                    </td>
                                </tr>
                            </tbody>
                        </v-table>
                        <div
                            v-else
                            class="text-medium-emphasis text-center pa-4"
                        >
                            No expense data for this month
                        </div>
                    </v-card-text>
                </v-card>

                <v-card variant="outlined" class="subtle-border mt-4">
                    <v-card-title class="section-title d-flex align-center ga-2">
                        <v-icon size="small" color="primary">mdi-chart-bar</v-icon>
                        Monthly Expenses by Category
                    </v-card-title>
                    <v-card-text>
                        <div v-if="chartLoading" class="text-center pa-4">
                            <v-progress-circular indeterminate />
                        </div>
                        <ApexChart
                            v-else-if="chartData"
                            type="bar"
                            height="350"
                            :options="chartOptions"
                            :series="chartSeries"
                        />
                        <div
                            v-else
                            class="text-medium-emphasis text-center pa-4"
                        >
                            No expense data available
                        </div>
                    </v-card-text>
                </v-card>

                <v-card variant="outlined" class="subtle-border mt-4">
                    <v-card-title class="section-title d-flex align-center ga-2">
                        <v-icon size="small" color="primary">mdi-chart-timeline-variant</v-icon>
                        Monthly Profit &amp; Loss
                    </v-card-title>
                    <v-card-text>
                        <div v-if="profitChartLoading" class="text-center pa-4">
                            <v-progress-circular indeterminate />
                        </div>
                        <ApexChart
                            v-else-if="profitData"
                            type="line"
                            height="350"
                            :options="profitOptions"
                            :series="profitSeries"
                        />
                        <div
                            v-else
                            class="text-medium-emphasis text-center pa-4"
                        >
                            No profit &amp; loss data available
                        </div>
                    </v-card-text>
                </v-card>
            </template>
        </v-card-text>
    </v-card>
</template>

<script setup>
import axios from "axios";
import { computed, ref, watchEffect, defineAsyncComponent } from "vue";
import { useTheme } from "vuetify";
import { useCurrency } from "../composables/useCurrency";
import CurrencySwitch from "./CurrencySwitch.vue";

const ApexChart = defineAsyncComponent(() =>
    import("vue3-apexcharts"),
);

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

const { currency, formatCurrency } = useCurrency();

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

const chartLoading = ref(false);
const chartData = ref(null);

const chartSeries = computed(() => chartData.value?.series ?? []);

const chartOptions = computed(() => ({
    chart: {
        type: "bar",
        stacked: true,
        foreColor: textColor.value,
        background: "transparent",
        toolbar: { show: false },
    },
    colors: chartColors,
    plotOptions: {
        bar: {
            horizontal: false,
            columnWidth: "55%",
        },
    },
    dataLabels: { enabled: false },
    xaxis: {
        categories: chartData.value?.months ?? [],
        labels: { style: { colors: textColor.value } },
    },
    yaxis: {
        labels: { style: { colors: textColor.value } },
        title: {
            text: currency.value === "usd" ? "Amount ($)" : "Amount (KHR)",
            style: { color: textColor.value },
        },
    },
    tooltip: {
        y: {
            formatter: (val) => formatCurrency(val),
        },
        theme: isDark.value ? "dark" : "light",
    },
    legend: {
        position: "bottom",
        horizontalAlign: "center",
        labels: { colors: textColor.value },
    },
    responsive: [
        {
            breakpoint: 600,
            options: { chart: { height: 250 } },
        },
    ],
}));

watchEffect(async () => {
    if (!props.site?.id) return;

    chartLoading.value = true;

    try {
        const res = await axios.get(`/api/sites/${props.site.id}/monthly-expense-by-category`, {
            params: { month: selectedMonth.value },
        });
        chartData.value = res.data;
    } catch {
        chartData.value = null;
    } finally {
        chartLoading.value = false;
    }
});

const profitChartLoading = ref(false);
const profitData = ref(null);

const profitSeries = computed(() => {
    if (!profitData.value) return [];
    return [
        { name: "Revenue", type: "column", data: profitData.value.revenue },
        { name: "Expenses", type: "column", data: profitData.value.expenses.map((v) => -Math.abs(v)) },
        { name: "Net Profit", type: "line", data: profitData.value.net_profit },
    ];
});

const profitOptions = computed(() => ({
    chart: {
        type: "line",
        foreColor: textColor.value,
        background: "transparent",
        toolbar: { show: false },
        zoom: { enabled: false },
    },
    colors: ["#4CAF50", "#F44336", "#2196F3"],
    stroke: {
        width: [0, 0, 2],
    },
    plotOptions: {
        bar: {
            columnWidth: "55%",
        },
    },
    dataLabels: { enabled: false },
    xaxis: {
        categories: profitData.value?.months ?? [],
        labels: { style: { colors: textColor.value } },
    },
    yaxis: {
        labels: {
            style: { colors: textColor.value },
            formatter: (val) => formatCurrency(Math.abs(val)),
        },
        title: {
            text: currency.value === "usd" ? "Amount ($)" : "Amount (KHR)",
            style: { color: textColor.value },
        },
    },
    tooltip: {
        y: {
            formatter: (val, { seriesIndex }) => {
                const displayVal = seriesIndex === 1 ? Math.abs(val) : val;
                return formatCurrency(displayVal);
            },
        },
        theme: isDark.value ? "dark" : "light",
    },
    legend: {
        position: "bottom",
        horizontalAlign: "center",
        labels: { colors: textColor.value },
    },
    responsive: [
        {
            breakpoint: 600,
            options: { chart: { height: 250 } },
        },
    ],
}));

watchEffect(async () => {
    if (!props.site?.id) return;

    profitChartLoading.value = true;

    try {
        const res = await axios.get(`/api/sites/${props.site.id}/monthly-profit-loss`, {
            params: { month: selectedMonth.value },
        });
        profitData.value = res.data;
    } catch {
        profitData.value = null;
    } finally {
        profitChartLoading.value = false;
    }
});

watchEffect(async () => {
    if (!props.site?.id) return;

    loading.value = true;
    error.value = false;

    try {
        const res = await axios.get(`/api/sites/${props.site.id}/pnl-expenses`, {
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

.pnl-table tbody tr:hover td {
    background-color: rgba(var(--v-theme-on-surface), 0.04);
}

.pnl-table tbody tr:nth-child(even) td {
    background-color: rgba(var(--v-theme-on-surface), 0.02);
}

.accent-header th {
    background-color: rgba(var(--v-theme-primary), 0.1);
    border-bottom: 2px solid rgb(var(--v-theme-primary)) !important;
}

.pl-section-header td {
    padding-top: 14px !important;
    padding-bottom: 6px !important;
    letter-spacing: 0.05em;
}

.pl-expenses-header td {
    background-color: rgba(var(--v-theme-error), 0.06);
    border-bottom: 1px solid rgba(var(--v-theme-error), 0.25);
}

.pl-expenses-subtotal td {
    background-color: rgba(var(--v-theme-error), 0.1);
    border-top: 1px solid rgba(var(--v-theme-error), 0.3);
}

.pl-indent {
    padding-left: 36px !important;
}

.pl-grand-total td {
    font-weight: 700;
    font-size: 1rem;
    border-top: 2px solid rgba(var(--v-theme-on-surface), 0.15);
    padding-top: 10px !important;
    padding-bottom: 10px !important;
    background-color: rgba(var(--v-theme-primary), 0.06);
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
    0%, 100% { opacity: 1; }
    50% { opacity: 0.35; }
}
</style>
