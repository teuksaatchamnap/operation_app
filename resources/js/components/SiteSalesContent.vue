<template>
    <v-card flat>
        <v-card-text>
            <template v-if="loading">
                <v-card variant="outlined" class="subtle-border">
                    <v-card-title class="section-title d-flex align-center ga-2">
                        <v-icon size="small" color="primary">mdi-chart-line</v-icon>
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
                    <v-card-title class="section-title d-flex align-center ga-2">
                        <v-icon size="small" color="primary">mdi-chart-line</v-icon>
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
                                    <th class="caption-label font-weight-bold">Date</th>
                                    <th
                                        v-for="ch in channels"
                                        :key="ch.key"
                                        class="caption-label font-weight-bold text-right"
                                    >
                                        {{ ch.label }}<br />
                                        <span class="text-medium-emphasis">
                                            {{ formatCurrency(data.prices[ch.priceKey]) }}
                                        </span>
                                    </th>
                                    <th class="caption-label font-weight-bold text-right">Total</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr
                                    v-for="sale in data.sales"
                                    :key="sale.date"
                                >
                                    <td class="font-weight-medium">{{ formatDate(sale.date) }}</td>
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
                                </tr>
                                <tr class="sales-total-row">
                                    <td class="font-weight-bold text-uppercase caption-label">Total</td>
                                    <td
                                        v-for="ch in channels"
                                        :key="ch.key"
                                        class="text-right font-weight-bold"
                                    >
                                        {{ formatNumber(data.totals[ch.key]) }}
                                    </td>
                                    <td class="text-right font-weight-bold">
                                        {{ formatNumber(data.totals.Total_Sales) }}
                                    </td>
                                </tr>
                                <tr class="sales-income-row">
                                    <td class="font-weight-bold text-uppercase caption-label">{{ currency === 'usd' ? 'Total USD' : 'Total KHR' }}</td>
                                    <td
                                        v-for="ch in channels"
                                        :key="ch.key"
                                        class="text-right font-weight-bold"
                                    >
                                        {{ formatCurrency(data.income[ch.incomeKey]) }}
                                    </td>
                                    <td class="text-right font-weight-bold">
                                        {{ formatCurrency(data.income.Total_Income) }}
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
            </template>
        </v-card-text>
    </v-card>
</template>

<script setup>
import axios from "axios";
import { computed, ref, watchEffect } from "vue";
import { useCurrency } from "../composables/useCurrency";
import CurrencySwitch from "./CurrencySwitch.vue";

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
        month: "short",
        day: "numeric",
    });
}

function formatNumber(num) {
    if (num === null || num === undefined) return "-";
    return Number(num).toLocaleString("en-US");
}

const { currency, formatCurrency } = useCurrency();

const channels = [
    { key: "Free_Sales", label: "Free", priceKey: "Free_Price", incomeKey: "Free_Income" },
    { key: "Hod_Sales", label: "Home Delivery", priceKey: "Hod_Price", incomeKey: "Hod_Income" },
    { key: "WiS_Sales", label: "School", priceKey: "WiS_Price", incomeKey: "WiS_Income" },
    { key: "Onsite_Sales", label: "On-Site", priceKey: "Onsite_Price", incomeKey: "Onsite_Income" },
    { key: "Shopkeeper_Sales", label: "Shopkeeper", priceKey: "Shopkeeper_Price", incomeKey: "Shopkeeper_Income" },
    { key: "Bottle_Sales", label: "Bottle", priceKey: "Bottle_Price", incomeKey: "Bottle_Income" },
    { key: "Other_Sales", label: "Other", priceKey: "Other_Price", incomeKey: "Other_Income" },
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
    0%, 100% { opacity: 1; }
    50% { opacity: 0.35; }
}
</style>
