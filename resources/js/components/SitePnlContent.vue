<template>
    <v-card flat>
        <v-card-text>
            <v-card variant="outlined" class="subtle-border">
                <v-card-title class="section-title d-flex align-center ga-2">
                    <v-icon size="small" color="primary">mdi-cash-plus</v-icon>
                    Income &amp; Expenses
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
                    <v-card v-if="loading || incomeLoading" variant="outlined" class="subtle-border">
                        <v-card-text>
                            <div class="skeleton skeleton-table" />
                        </v-card-text>
                    </v-card>
                    <v-row v-else-if="error || incomeError" class="text-center">
                        <v-col>
                            <div class="text-medium-emphasis">
                                Failed to load data
                            </div>
                        </v-col>
                    </v-row>
                    <template v-else-if="data && incomeData">
                        <v-table density="compact" class="pnl-table">
                            <thead>
                                <tr class="accent-header income-header">
                                    <th class="caption-label font-weight-bold">Revenue</th>
                                    <th class="caption-label font-weight-bold text-right">Amount</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr
                                    v-for="ch in incomeChannels"
                                    :key="ch.key"
                                >
                                    <td>{{ ch.label }}</td>
                                    <td class="text-right font-weight-medium">{{ formatCurrency(incomeIncome[ch.incomeKey] ?? 0) }}</td>
                                </tr>
                                <tr class="pl-grand-total">
                                    <td class="font-weight-bold text-uppercase">Total Revenue</td>
                                    <td class="text-right font-weight-bold">{{ formatCurrency(incomeIncome.Total_Income ?? 0) }}</td>
                                </tr>

                                <tr class="pl-spacer-row">
                                    <td colspan="2" />
                                </tr>

                                <template v-if="data.categories.length">
                                    <tr class="accent-header expenses-header">
                                        <th class="caption-label font-weight-bold" colspan="2">Expenses</th>
                                    </tr>

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

                                    <tr class="pl-expenses-total">
                                        <td class="font-weight-bold text-uppercase">Total Expenses</td>
                                        <td class="text-right font-weight-bold">
                                            {{ formatCurrency(data.grand_total) }}
                                        </td>
                                    </tr>
                                </template>

                                <tr class="pl-net-result" :class="netResult >= 0 ? 'text-success' : 'text-error'">
                                    <td class="font-weight-bold text-uppercase">NET RESULT</td>
                                    <td class="text-right font-weight-bold">
                                        {{ formatCurrency(netResult) }}
                                    </td>
                                </tr>
                            </tbody>
                        </v-table>
                        <div
                            v-if="!data.categories.length"
                            class="text-medium-emphasis text-center pa-4"
                        >
                            No expenses for this month
                        </div>
                    </template>
                    <div
                        v-else
                        class="text-medium-emphasis text-center pa-4"
                    >
                        No data for this month
                    </div>
                </v-card-text>
            </v-card>

            <template v-if="data">
                <v-card variant="outlined" class="subtle-border mt-4">
                    <v-card-title class="section-title d-flex align-center ga-2">
                        <v-icon size="small" color="primary">mdi-chart-bar</v-icon>
                        Monthly Expenses by Category
                    </v-card-title>
                    <v-card-text>
                        <div v-if="chartLoading" class="text-center pa-4">
                            <v-progress-circular indeterminate />
                        </div>
                        <template v-else-if="chartData">
                            <ApexChart
                                ref="chartRef"
                                type="bar"
                                height="350"
                                :options="chartOptions"
                                :series="chartSeries"
                            />
                            <ChartExportButtons
                                :chart="chartRef?.chart"
                                filename="monthly-expenses-by-category"
                            />
                        </template>
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
                        <template v-else-if="profitData">
                            <ApexChart
                                ref="profitChartRef"
                                type="line"
                                height="350"
                                :options="profitOptions"
                                :series="profitSeries"
                            />
                            <ChartExportButtons
                                :chart="profitChartRef?.chart"
                                filename="monthly-profit-loss"
                            />
                        </template>
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
import ChartExportButtons from "./ChartExportButtons.vue";

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
const incomeLoading = ref(false);
const incomeError = ref(false);
const incomeData = ref(null);
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

const incomeChannels = [
    { key: "Hod_Sales", label: "Home Delivery", priceKey: "Hod_Price", incomeKey: "Hod_Income" },
    { key: "Shopkeeper_Sales", label: "Shopkeeper", priceKey: "Shopkeeper_Price", incomeKey: "Shopkeeper_Income" },
    { key: "Onsite_Sales", label: "On-Site", priceKey: "Onsite_Price", incomeKey: "Onsite_Income" },
    { key: "WiS_Sales", label: "Water in School", priceKey: "WiS_Price", incomeKey: "WiS_Income" },
    { key: "Bottle_Sales", label: "Bottle", priceKey: "Bottle_Price", incomeKey: "Bottle_Income" },
    { key: "Emergency_Sales", label: "Emergency", priceKey: "Emergency_Price", incomeKey: "Emergency_Income" },
    { key: "Other_Sales", label: "Other", priceKey: "Other_Price", incomeKey: "Other_Income" },
    { key: "Free_Sales", label: "Free", priceKey: "Free_Price", incomeKey: "Free_Income" },
];

const incomeIncome = computed(() => incomeData.value?.income ?? {});

const netResult = computed(() => {
    const totalIncome = incomeIncome.value?.Total_Income ?? 0;
    const totalExpenses = data.value?.grand_total ?? 0;
    return totalIncome - totalExpenses;
});

const theme = useTheme();
const isDark = computed(() => theme.global.name.value === "dark");
const textColor = computed(() => (isDark.value ? "#e0e0e0" : "#333333"));

const chartRef = ref(null);
const profitChartRef = ref(null);

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

    incomeLoading.value = true;
    incomeError.value = false;

    try {
        const res = await axios.get(`/api/sites/${props.site.id}/daily-sales`, {
            params: { month: selectedMonth.value },
        });
        incomeData.value = res.data;
    } catch {
        incomeError.value = true;
        incomeData.value = null;
    } finally {
        incomeLoading.value = false;
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

.income-header th {
    background-color: rgba(var(--v-theme-success), 0.08);
    border-bottom: 2px solid rgb(var(--v-theme-success)) !important;
}

.pl-spacer-row td {
    height: 12px;
    padding: 0 !important;
    border: none !important;
    background: transparent !important;
}

.expenses-header th {
    background-color: rgba(var(--v-theme-error), 0.08);
    border-bottom: 2px solid rgb(var(--v-theme-error)) !important;
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

.pl-expenses-total td {
    font-weight: 700;
    font-size: 1rem;
    border-top: 2px solid rgb(var(--v-theme-error));
    padding-top: 10px !important;
    padding-bottom: 10px !important;
    background-color: rgba(var(--v-theme-error), 0.1);
}

.pl-net-result td {
    font-weight: 800;
    font-size: 1.05rem;
    border-top: 3px double rgba(var(--v-theme-on-surface), 0.25);
    padding-top: 12px !important;
    padding-bottom: 12px !important;
    background-color: rgba(var(--v-theme-primary), 0.04);
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
