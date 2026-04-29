<template>
    <v-container>
        <div class="flex justify-between items-center mb-6">
            <h1 class="text-2xl font-bold">📡 Command Center</h1>
            <div class="flex gap-2">
                <v-tooltip location="bottom" text="Toggle dark mode">
                    <template v-slot:activator="{ props }">
                        <v-btn
                            :icon="isDark ? 'mdi-weather-night' : 'mdi-weather-sunny'"
                            variant="text"
                            v-bind="props"
                            @click="toggleDarkMode"
                        ></v-btn>
                    </template>
                </v-tooltip>
                <v-tooltip location="bottom" text="Logout">
                    <template v-slot:activator="{ props }">
                        <v-btn
                            icon="mdi-logout"
                            color="error"
                            variant="text"
                            v-bind="props"
                            @click="logout"
                        ></v-btn>
                    </template>
                </v-tooltip>
            </div>
        </div>

        <!-- Filter Form -->
        <v-card class="mb-6 pa-4">
            <v-card-title class="text-h6 mb-4">Filters</v-card-title>
            <v-row>
                <v-col cols="12" md="6" lg="3">
                    <MonthPicker v-model="selectedMonth" />
                </v-col>
                <v-col cols="12" md="6" lg="3">
                    <v-select
                        v-model="selectedSites"
                        :items="sites"
                        item-title="name"
                        item-value="id"
                        label="Sites"
                        multiple
                        clearable
                        chips
                        closable-chips
                    />
                </v-col>
                <v-col cols="12" md="6" lg="3">
                    <v-select
                        v-model="selectedAdvisors"
                        :items="advisors"
                        item-title="name"
                        item-value="id"
                        label="Advisors"
                        multiple
                        clearable
                        chips
                        closable-chips
                    />
                </v-col>
                <v-col cols="12" md="6" lg="3">
                    <v-select
                        v-model="selectedPlatforms"
                        :items="platforms"
                        item-title="name"
                        item-value="id"
                        label="Platforms"
                        multiple
                        clearable
                        chips
                        closable-chips
                    />
                </v-col>
            </v-row>
        </v-card>

        <!-- KPI Cards -->
        <v-row class="mb-6">
            <v-col cols="12" md="6">
                <KpiCard kpi-col-name="sales_volume" :filters="kpiFilters" />
            </v-col>
            <v-col cols="12" md="6">
                <KpiCard kpi-col-name="days_open" :filters="kpiFilters" />
            </v-col>
        </v-row>
    </v-container>
</template>

<script setup>
import { ref, watch, onMounted, computed } from "vue";
import { useRouter } from "vue-router";
import { useTheme } from "vuetify";
import { useAuthStore } from "../stores/auth";
import axios from "axios";
import KpiCard from "../components/KpiCard.vue";
import MonthPicker from "../components/MonthPicker.vue";

const router = useRouter();
const authStore = useAuthStore();
const theme = useTheme();

// Dark mode
const isDark = computed(() => theme.global.current.value.dark);

function toggleDarkMode() {
    theme.global.name.value = isDark.value ? 'light' : 'dark';
    localStorage.setItem('darkMode', isDark.value ? 'true' : 'false');
}

// Initialize dark mode from localStorage or system preference
if (localStorage.getItem('darkMode') === 'true' ||
    (!localStorage.getItem('darkMode') && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
    theme.global.name.value = 'dark';
}

// Get current month in YYYY-MM format
const now = new Date();
const currentMonth = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, "0")}`;

// Filter state
const sites = ref([]);
const advisors = ref([]);
const platforms = ref([]);
const selectedSites = ref([]);
const selectedAdvisors = ref([]);
const selectedPlatforms = ref([]);
const selectedMonth = ref(currentMonth);

// Computed filters object for KPI cards
const kpiFilters = computed(() => ({
    site_ids: selectedSites.value,
    advisor_ids: selectedAdvisors.value,
    platform_ids: selectedPlatforms.value,
    month: selectedMonth.value,
}));

// Load dimensions data on mount
onMounted(async () => {
    try {
        const [sitesRes, advisorsRes, platformsRes] = await Promise.all([
            axios.get("/api/sites"),
            axios.get("/api/advisors"),
            axios.get("/api/platforms"),
        ]);
        sites.value = sitesRes.data;
        advisors.value = advisorsRes.data;
        platforms.value = platformsRes.data;
    } catch (error) {
        console.error("Failed to load dimensions:", error);
    }
});

function logout() {
    axios.post("/api/logout").then(() => {
        authStore.logout();
        router.push("/login");
    });
}
</script>
