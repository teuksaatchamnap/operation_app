<template>
    <v-container>
        <div class="flex justify-between items-center mb-6">
            <h1 class="text-2xl font-bold">📡 Command Center</h1>
            <v-btn
                color="error"
                variant="outlined"
                prepend-icon="mdi-logout"
                @click="logout"
            >
                Logout
            </v-btn>
        </div>

        <v-alert type="success" variant="tonal" class="mb-6">
            Welcome, {{ authStore.user?.name }}!
        </v-alert>

        <!-- Filter Form -->
        <v-card class="mb-6 pa-4">
            <v-card-title class="text-h6 mb-4">Filters</v-card-title>
            <v-row>
                <v-col cols="12" md="6" lg="3">
                    <v-menu
                        v-model="monthMenu"
                        :close-on-content-click="false"
                        location="bottom"
                    >
                        <template v-slot:activator="{ props }">
                            <v-text-field
                                v-model="selectedMonth"
                                label="Month"
                                placeholder="YYYY-MM"
                                prepend-inner-icon="mdi-calendar"
                                readonly
                                clearable
                                v-bind="props"
                            />
                        </template>
                        <v-card min-width="280">
                            <v-card-text>
                                <v-text-field
                                    v-model="pickerYear"
                                    label="Year"
                                    type="number"
                                    class="mb-4"
                                />
                                <v-row density="comfortable">
                                    <v-col
                                        v-for="(month, index) in months"
                                        :key="index"
                                        cols="3"
                                    >
                                        <v-btn
                                            :color="
                                                isSelectedMonth(index)
                                                    ? 'primary'
                                                    : ''
                                            "
                                            variant="text"
                                            size="small"
                                            block
                                            @click="selectMonth(index)"
                                        >
                                            {{ month }}
                                        </v-btn>
                                    </v-col>
                                </v-row>
                            </v-card-text>
                        </v-card>
                    </v-menu>
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
                <KpiCard
                    kpi-col-name="sales_volume"
                    :filters="kpiFilters"
                />
            </v-col>
            <v-col cols="12" md="6">
                <KpiCard
                    kpi-col-name="days_open"
                    :filters="kpiFilters"
                />
            </v-col>
        </v-row>
    </v-container>
</template>

<script setup>
import { ref, watch, onMounted, computed } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "../stores/auth";
import axios from "axios";
import KpiCard from "../components/KpiCard.vue";

const router = useRouter();
const authStore = useAuthStore();

// Get current month in YYYY-MM format
const now = new Date();
const currentMonth = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, "0")}`;

// Month picker data
const months = [
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
const pickerYear = ref(now.getFullYear());

// Filter state
const sites = ref([]);
const advisors = ref([]);
const platforms = ref([]);
const selectedSites = ref([]);
const selectedAdvisors = ref([]);
const selectedPlatforms = ref([]);
const selectedMonth = ref(currentMonth);
const monthMenu = ref(false);

// Computed filters object for KPI cards
const kpiFilters = computed(() => ({
    site_ids: selectedSites.value,
    advisor_ids: selectedAdvisors.value,
    platform_ids: selectedPlatforms.value,
    month: selectedMonth.value,
}));

function isSelectedMonth(monthIndex) {
    if (!selectedMonth.value) return false;
    const [year, month] = selectedMonth.value.split("-");
    return (
        parseInt(year) === pickerYear.value &&
        parseInt(month) === monthIndex + 1
    );
}

function selectMonth(monthIndex) {
    const month = String(monthIndex + 1).padStart(2, "0");
    selectedMonth.value = `${pickerYear.value}-${month}`;
    monthMenu.value = false;
}

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
