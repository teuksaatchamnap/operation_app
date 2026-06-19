<template>
    <v-card flat>
        <v-card-text>
            <template v-if="loading">
                <v-card variant="outlined" class="subtle-border">
                    <v-card-title class="section-title d-flex align-center ga-2">
                        <v-icon size="small" color="primary">mdi-store-outline</v-icon>
                        General Details
                    </v-card-title>
                    <v-card-text>
                        <v-row density="comfortable">
                            <v-col v-for="i in 10" :key="i" cols="3">
                                <div class="skeleton skeleton-label" />
                                <div class="skeleton skeleton-value mt-1" />
                            </v-col>
                        </v-row>
                    </v-card-text>
                </v-card>

                <v-card variant="outlined" class="subtle-border mt-4">
                    <v-card-title class="section-title d-flex align-center ga-2">
                        <v-icon size="small" color="primary">mdi-gauge</v-icon>
                        Site KPI
                    </v-card-title>
                    <v-card-text>
                        <v-row density="comfortable">
                            <v-col v-for="i in 8" :key="i" cols="3">
                                <div class="skeleton skeleton-label" />
                                <div class="skeleton skeleton-value mt-1" />
                            </v-col>
                        </v-row>
                    </v-card-text>
                </v-card>

                <v-card variant="outlined" class="subtle-border mt-4">
                    <v-card-title class="section-title d-flex align-center ga-2">
                        <v-icon size="small" color="primary">mdi-chart-line</v-icon>
                        Monthly Sales Performance
                    </v-card-title>
                    <v-card-text>
                        <div class="skeleton skeleton-chart" />
                    </v-card-text>
                </v-card>
            </template>

            <v-row v-else-if="error" class="text-center">
                <v-col>
                    <div class="text-medium-emphasis">
                        Failed to load site analysis
                    </div>
                </v-col>
            </v-row>

            <template v-else-if="data">
                <v-card variant="outlined" class="subtle-border">
                    <v-card-title class="section-title d-flex align-center ga-2">
                        <v-icon size="small" color="primary">mdi-store-outline</v-icon>
                        General Details
                    </v-card-title>
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
                            <v-col cols="3">
                                <div class="caption-label text-medium-emphasis">
                                    Delivery Program
                                </div>
                                <div class="text-body-1">
                                    {{ data.delivery_program == 1 ? "Yes" : "No" }}
                                </div>
                            </v-col>
                            <v-col cols="3">
                                <div class="caption-label text-medium-emphasis">
                                    Treatment Process
                                </div>
                                <div class="text-body-1">
                                    {{ data.treatment_process ?? "-" }}
                                </div>
                            </v-col>
                        </v-row>
                    </v-card-text>
                </v-card>

                <v-card variant="outlined" class="subtle-border mt-4">
                    <v-card-title class="section-title d-flex align-center ga-2">
                        <v-icon size="small" color="primary">mdi-gauge</v-icon>
                        Site KPI
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
                    </v-card-title>
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
                                        <template
                                            v-slot:activator="{
                                                props: tooltipProps,
                                            }"
                                        >
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
                                <div
                                    class="text-body-1 d-flex align-center ga-1"
                                >
                                    <v-icon
                                        v-if="objectiveMetClass(kpi) !== null"
                                        :color="
                                            objectiveMetClass(kpi) === true
                                                ? 'success'
                                                : 'error'
                                        "
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

                <MonthlyPerformanceChart :site="site" :month="selectedMonth" />

                <v-row class="mt-4">
                    <v-col cols="6">
                        <v-card variant="outlined" class="subtle-border h-100">
                            <v-card-title class="section-title d-flex align-center ga-2">
                                <v-icon size="small" color="primary">mdi-chart-pie</v-icon>
                                Monthly Sales Breakdown
                            </v-card-title>
                            <v-card-text>
                                <div
                                    v-if="salesLoading"
                                    class="text-center pa-4"
                                >
                                    <v-progress-circular indeterminate />
                                </div>
                            <template v-else-if="salesBreakdown.length">
                                <ApexChart
                                    ref="salesChartRef"
                                    type="pie"
                                    height="350"
                                    :options="salesChartOptions"
                                    :series="salesSeries"
                                />
                                <ChartExportButtons
                                    :chart="salesChartRef?.chart"
                                    filename="monthly-sales-breakdown"
                                />
                            </template>
                                <div
                                    v-else
                                    class="text-medium-emphasis text-center pa-4"
                                >
                                    No sales data for this month
                                </div>
                            </v-card-text>
                        </v-card>
                    </v-col>
                    <v-col cols="6">
                        <v-card variant="outlined" class="subtle-border h-100">
                            <v-card-title class="section-title d-flex align-center ga-2">
                                <v-icon size="small" color="primary">mdi-chart-bar</v-icon>
                                Monthly Expenses Comparison
                            </v-card-title>
                            <v-card-text>
                                <div
                                    v-if="expenseLoading"
                                    class="text-center pa-4"
                                >
                                    <v-progress-circular indeterminate />
                                </div>
                                <template v-else-if="expenseData.length">
                                    <ApexChart
                                        ref="expenseChartRef"
                                        type="bar"
                                        height="350"
                                        :options="expenseChartOptions"
                                        :series="expenseChartSeries"
                                    />
                                    <ChartExportButtons
                                        :chart="expenseChartRef?.chart"
                                        filename="monthly-expenses-comparison"
                                    />
                                </template>
                                <div
                                    v-else
                                    class="text-medium-emphasis text-center pa-4"
                                >
                                    No expense data for this month
                                </div>
                            </v-card-text>
                        </v-card>
                    </v-col>
                </v-row>

                <v-card variant="outlined" class="subtle-border mt-4">
                    <v-card-title class="section-title d-flex align-center ga-2">
                        <v-icon size="small" color="primary">mdi-cash-multiple</v-icon>
                        Profit &amp; Loss Details
                        <v-spacer />
                        <CurrencySwitch />
                    </v-card-title>
                    <v-card-text>
                        <div v-if="profitLossLoading" class="text-center pa-4">
                            <v-progress-circular indeterminate />
                        </div>
                        <v-table
                            v-else-if="profitLossData"
                            density="compact"
                            class="pl-table"
                        >
                            <thead>
                                <tr class="pl-header-row">
                                    <th class="caption-label font-weight-bold text-uppercase">
                                        Category
                                    </th>
                                    <th
                                        v-for="col in profitLossColumns"
                                        :key="col.key"
                                        class="caption-label font-weight-bold text-uppercase text-right"
                                    >
                                        {{ col.label }}
                                    </th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr class="pl-section-header pl-revenue-header">
                                    <td colspan="5">
                                        <span class="font-weight-bold text-uppercase caption-label">Revenue</span>
                                    </td>
                                </tr>
                                <tr>
                                    <td class="pl-indent">
                                        Revenue from sales
                                    </td>
                                    <td
                                        v-for="col in profitLossColumns"
                                        :key="col.key"
                                        class="text-right"
                                    >
                                        {{
                                            formatCurrency(
                                                profitLossData.revenue.sales[
                                                    col.key
                                                ],
                                            )
                                        }}
                                    </td>
                                </tr>
                                <tr>
                                    <td class="pl-indent">
                                        Revenue from water in school
                                    </td>
                                    <td
                                        v-for="col in profitLossColumns"
                                        :key="col.key"
                                        class="text-right"
                                    >
                                        {{
                                            formatCurrency(
                                                profitLossData.revenue
                                                    .water_in_school[col.key],
                                            )
                                        }}
                                    </td>
                                </tr>
                                <tr class="pl-revenue-subtotal">
                                    <td class="font-weight-bold">Subtotal Revenue</td>
                                    <td
                                        v-for="col in profitLossColumns"
                                        :key="col.key"
                                        class="text-right"
                                    >
                                        {{
                                            formatCurrency(
                                                profitLossData.revenue
                                                    .sub_total[col.key],
                                            )
                                        }}
                                    </td>
                                </tr>
                                <tr class="pl-section-header pl-expenses-header">
                                    <td colspan="5">
                                        <span class="font-weight-bold text-uppercase caption-label">Expenses</span>
                                    </td>
                                </tr>
                                <tr
                                    v-for="cat in profitLossData.expenses
                                        .categories"
                                    :key="cat.category"
                                >
                                    <td class="pl-indent">
                                        {{ cat.category }}
                                    </td>
                                    <td
                                        v-for="col in profitLossColumns"
                                        :key="col.key"
                                        class="text-right"
                                    >
                                        {{ formatCurrency(cat[col.key]) }}
                                    </td>
                                </tr>
                                <tr class="pl-expenses-subtotal">
                                    <td class="font-weight-bold">Subtotal Expenses</td>
                                    <td
                                        v-for="col in profitLossColumns"
                                        :key="col.key"
                                        class="text-right"
                                    >
                                        {{
                                            formatCurrency(
                                                profitLossData.expenses
                                                    .sub_total[col.key],
                                            )
                                        }}
                                    </td>
                                </tr>
                                <tr
                                    class="pl-result"
                                    :class="
                                        profitLossData.result.current >= 0
                                            ? 'text-success'
                                            : 'text-error'
                                    "
                                >
                                    <td class="font-weight-bold">Result (Revenue &minus; Expenses)</td>
                                    <td
                                        v-for="col in profitLossColumns"
                                        :key="col.key"
                                        class="text-right"
                                    >
                                        {{
                                            formatCurrency(
                                                profitLossData.result[col.key],
                                            )
                                        }}
                                    </td>
                                </tr>
                                <tr class="pl-entrepreneur-income">
                                    <td>
                                        Entrepreneur Income (Salary + Profit)
                                    </td>
                                    <td
                                        v-for="col in profitLossColumns"
                                        :key="col.key"
                                        class="text-right"
                                    >
                                        {{
                                            formatCurrency(
                                                entrepreneurIncome[col.key],
                                            )
                                        }}
                                    </td>
                                </tr>
                            </tbody>
                        </v-table>
                    </v-card-text>
                </v-card>

                <v-row class="mt-4">
                    <v-col cols="6">
                        <v-card variant="outlined" class="subtle-border h-100">
                            <v-card-title class="section-title d-flex align-center ga-2">
                                <v-icon size="small" color="primary">mdi-tag-multiple</v-icon>
                                Average Prices by Channel
                            </v-card-title>
                            <v-card-text>
                                <div v-if="pricesLoading" class="text-center pa-4">
                                    <v-progress-circular indeterminate />
                                </div>
                                <v-table
                                    v-else-if="pricesData.length"
                                    density="compact"
                                    class="prices-table"
                                >
                                    <thead>
                                        <tr class="accent-header">
                                            <th class="caption-label font-weight-bold">
                                                Channel
                                            </th>
                                            <th class="caption-label font-weight-bold text-right">
                                                Avg Price
                                            </th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        <tr
                                            v-for="item in pricesData"
                                            :key="item.label"
                                        >
                                            <td class="font-weight-medium">{{ item.label }}</td>
                                            <td class="text-right font-weight-bold">
                                                {{ formatCurrency(item.price) }}
                                            </td>
                                        </tr>
                                    </tbody>
                                </v-table>
                                <div
                                    v-else
                                    class="text-medium-emphasis text-center pa-4"
                                >
                                    No price data for this month
                                </div>
                            </v-card-text>
                        </v-card>
                    </v-col>
                    <v-col cols="6">
                        <v-card variant="outlined" class="subtle-border h-100">
                            <v-card-title class="section-title d-flex align-center ga-2">
                                <v-icon size="small" color="primary">mdi-bottle-wine</v-icon>
                                New Bottles Bought
                            </v-card-title>
                            <v-card-text>
                                <div v-if="bottleLoading" class="text-center pa-4">
                                    <v-progress-circular indeterminate />
                                </div>
                                <v-table
                                    v-else-if="bottleData"
                                    density="compact"
                                    class="bottle-table"
                                >
                                    <thead>
                                        <tr class="accent-header">
                                            <th class="caption-label font-weight-bold">
                                                Period
                                            </th>
                                            <th class="caption-label font-weight-bold text-right">
                                                Bottles
                                            </th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        <tr>
                                            <td class="font-weight-medium">YTD</td>
                                            <td class="text-right font-weight-bold bottle-value">
                                                {{ formatBottleNumber(bottleData.ytd) }}
                                            </td>
                                        </tr>
                                        <tr>
                                            <td class="font-weight-medium">Previous Year</td>
                                            <td class="text-right font-weight-bold bottle-value">
                                                {{ formatBottleNumber(bottleData.last_year) }}
                                            </td>
                                        </tr>
                                        <tr
                                            class="bottle-diff-row"
                                            :class="bottleDiff >= 0 ? 'text-success' : 'text-error'"
                                        >
                                            <td class="font-weight-medium">YTD vs Previous Year</td>
                                            <td class="text-right font-weight-bold bottle-value">
                                                {{ bottleDiff >= 0 ? '+' : '-' }}{{ formatBottleNumber(Math.abs(bottleDiff)) }}
                                                ({{ bottleDiffPct }}%)
                                            </td>
                                        </tr>
                                    </tbody>
                                </v-table>
                                <div
                                    v-else
                                    class="text-medium-emphasis text-center pa-4"
                                >
                                    No bottle data for this period
                                </div>
                            </v-card-text>
                        </v-card>
                    </v-col>
                </v-row>
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
import MonthlyPerformanceChart from "./MonthlyPerformanceChart.vue";

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
    const val =
        typeof kpi.value === "number" ? kpi.value : parseFloat(kpi.value);
    const obj =
        typeof kpi.objective === "number"
            ? kpi.objective
            : parseFloat(kpi.objective);
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

const salesChartRef = ref(null);
const expenseChartRef = ref(null);

const salesBreakdown = ref([]);
const salesLoading = ref(false);

const expenseData = ref([]);
const expenseLoading = ref(false);

const expenseChartSeries = computed(() => [
    {
        name: "This Site",
        data: expenseData.value.map((i) => i.site_amount),
    },
    {
        name: "Network Average",
        data: expenseData.value.map((i) => i.avg_amount),
    },
]);

const expenseChartOptions = computed(() => ({
    chart: {
        type: "bar",
        foreColor: textColor.value,
        background: "transparent",
        toolbar: { show: false },
    },
    colors: ["#36A2EB", "#FFCE56"],
    plotOptions: {
        bar: {
            horizontal: false,
            columnWidth: "55%",
        },
    },
    dataLabels: { enabled: false },
    xaxis: {
        categories: expenseData.value.map((i) => i.category),
        labels: { style: { colors: textColor.value } },
    },
    yaxis: {
        labels: { style: { colors: textColor.value } },
        title: { text: "Amount ($)", style: { color: textColor.value } },
    },
    tooltip: {
        y: {
            formatter: (val) => Number(val).toLocaleString("en-US"),
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

const salesSeries = computed(() => salesBreakdown.value.map((i) => i.value));

const salesChartOptions = computed(() => ({
    labels: salesBreakdown.value.map((i) => i.label),
    chart: {
        type: "pie",
        foreColor: textColor.value,
        background: "transparent",
        toolbar: { show: false },
    },
    colors: chartColors,
    dataLabels: {
        enabled: true,
        formatter(val) {
            return val.toFixed(1) + "%";
        },
        style: {
            colors: ["#fff"],
            fontSize: "13px",
            fontWeight: 600,
        },
        dropShadow: {
            enabled: false,
        },
    },
    tooltip: {
        y: {
            formatter(val) {
                return Number(val).toLocaleString("en-US") + " bottles";
            },
        },
        theme: isDark.value ? "dark" : "light",
    },
    legend: {
        position: "bottom",
        horizontalAlign: "center",
        labels: {
            colors: textColor.value,
        },
    },
    responsive: [
        {
            breakpoint: 600,
            options: {
                chart: { height: 250 },
                legend: { position: "bottom" },
            },
        },
    ],
}));

watchEffect(async () => {
    if (!props.site?.id) return;

    expenseLoading.value = true;

    try {
        const res = await axios.get(
            `/api/sites/${props.site.id}/expense-breakdown`,
            { params: { month: selectedMonth.value } },
        );
        expenseData.value = res.data.expenses;
    } catch {
        expenseData.value = [];
    } finally {
        expenseLoading.value = false;
    }

    salesLoading.value = true;

    try {
        const res = await axios.get(
            `/api/sites/${props.site.id}/monthly-sales-breakdown`,
            { params: { month: selectedMonth.value } },
        );
        salesBreakdown.value = res.data.breakdown.filter((i) => i.value > 0);
    } catch {
        salesBreakdown.value = [];
    } finally {
        salesLoading.value = false;
    }
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

const profitLossData = ref(null);
const profitLossLoading = ref(false);
const { currency, formatCurrency, KHR_TO_USD } = useCurrency();

const profitLossColumns = computed(() => {
    if (!profitLossData.value?.labels) return [];
    return [
        { key: "current", label: profitLossData.value.labels.current },
        { key: "previous", label: profitLossData.value.labels.previous },
        { key: "ytd", label: profitLossData.value.labels.ytd },
        { key: "last_year", label: profitLossData.value.labels.last_year },
    ];
});

const entrepreneurIncome = computed(() => {
    if (!profitLossData.value) return {};
    const { result, entrepreneur_salary } = profitLossData.value;
    return {
        current: result.current + entrepreneur_salary.current,
        previous: result.previous + entrepreneur_salary.previous,
        ytd: result.ytd + entrepreneur_salary.ytd,
        last_year: result.last_year + entrepreneur_salary.last_year,
    };
});



watchEffect(async () => {
    if (!props.site?.id) return;

    profitLossLoading.value = true;

    try {
        const res = await axios.get(`/api/sites/${props.site.id}/profit-loss`, {
            params: { month: selectedMonth.value },
        });
        profitLossData.value = res.data;
    } catch {
        profitLossData.value = null;
    } finally {
        profitLossLoading.value = false;
    }
});

const pricesData = ref([]);
const pricesLoading = ref(false);

watchEffect(async () => {
    if (!props.site?.id) return;

    pricesLoading.value = true;

    try {
        const res = await axios.get(
            `/api/sites/${props.site.id}/channel-prices`,
            { params: { month: selectedMonth.value } },
        );
        pricesData.value = res.data.prices;
    } catch {
        pricesData.value = [];
    } finally {
        pricesLoading.value = false;
    }
});

const bottleData = ref(null);
const bottleLoading = ref(false);

const bottleDiff = computed(() => {
    if (!bottleData.value) return 0;
    return bottleData.value.ytd - bottleData.value.last_year;
});

const bottleDiffPct = computed(() => {
    if (!bottleData.value || !bottleData.value.last_year) return 0;
    return ((bottleDiff.value / bottleData.value.last_year) * 100).toFixed(1);
});

function formatBottleNumber(value) {
    if (value === null || value === undefined) return "-";
    return Number(value).toLocaleString("en-US");
}

watchEffect(async () => {
    if (!props.site?.id) return;

    bottleLoading.value = true;

    try {
        const res = await axios.get(
            `/api/sites/${props.site.id}/bottle-purchases`,
            { params: { month: selectedMonth.value } },
        );
        bottleData.value = res.data;
    } catch {
        bottleData.value = null;
    } finally {
        bottleLoading.value = false;
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

/* ========== P&L table ========== */

.pl-header-row th {
    font-weight: 600;
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    background-color: rgba(var(--v-theme-on-surface), 0.04);
    border-bottom: 2px solid rgb(var(--v-theme-primary));
    padding-top: 10px !important;
    padding-bottom: 10px !important;
}

/* Section headers — Revenue / Expenses */
.pl-section-header td {
    padding-top: 14px !important;
    padding-bottom: 6px !important;
    letter-spacing: 0.05em;
}

.pl-revenue-header td {
    background-color: rgba(var(--v-theme-success), 0.06);
    border-bottom: 1px solid rgba(var(--v-theme-success), 0.25);
}

.pl-revenue-subtotal td {
    background-color: rgba(var(--v-theme-success), 0.1);
    border-top: 1px solid rgba(var(--v-theme-success), 0.3);
}

.pl-expenses-header td {
    background-color: rgba(var(--v-theme-error), 0.06);
    border-bottom: 1px solid rgba(var(--v-theme-error), 0.25);
}

.pl-expenses-subtotal td {
    background-color: rgba(var(--v-theme-error), 0.1);
    border-top: 1px solid rgba(var(--v-theme-error), 0.3);
}

/* Result row */
.pl-result td {
    font-weight: 700;
    font-size: 1rem;
    border-top: 2px solid rgba(var(--v-theme-on-surface), 0.15);
    padding-top: 10px !important;
    padding-bottom: 10px !important;
}

/* Entrepreneur income */
.pl-entrepreneur-income td {
    background-color: rgba(var(--v-theme-info), 0.06);
    font-weight: 600;
}

/* Indented sub-items */
.pl-indent {
    padding-left: 36px !important;
}

/* P&L row hover — skip section headers to keep their tint */
.pl-table tbody tr:not(.pl-section-header):not(.pl-result):hover td {
    background-color: rgba(var(--v-theme-on-surface), 0.04);
}

/* ========== Small data tables (prices, bottles) ========== */

.prices-table tbody tr:hover td,
.bottle-table tbody tr:hover td {
    background-color: rgba(var(--v-theme-on-surface), 0.04);
}

.prices-table tbody tr:nth-child(even) td,
.bottle-table tbody tr:nth-child(even) td {
    background-color: rgba(var(--v-theme-on-surface), 0.02);
}

/* Accent header row on small tables */
.accent-header th {
    background-color: rgba(var(--v-theme-primary), 0.1);
    border-bottom: 2px solid rgb(var(--v-theme-primary)) !important;
}

/* Bottle diff row */
.bottle-diff-row td {
    padding-top: 12px !important;
    padding-bottom: 12px !important;
    border-top: 1px solid rgba(var(--v-theme-on-surface), 0.12);
}

.bottle-value {
    font-size: 1.1rem;
}

/* ========== Skeleton loading ========== */
.skeleton {
    background: rgba(var(--v-theme-on-surface), 0.08);
    border-radius: 4px;
    animation: skeleton-pulse 1.5s ease-in-out infinite;
}

.skeleton-label {
    height: 10px;
    width: 55%;
}

.skeleton-value {
    height: 18px;
    width: 80%;
}

.skeleton-chart {
    height: 350px;
    width: 100%;
}

@keyframes skeleton-pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.35; }
}
</style>
