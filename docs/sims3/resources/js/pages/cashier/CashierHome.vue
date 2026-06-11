<template>
    <v-sheet v-if="!loading" elevation="4">
        <v-tabs v-model="tab" align-tabs="center" color="deep-purple-accent-4">
            <v-tab value="sales">
                {{ $t("cashier.sales") }}
            </v-tab>
            <v-tab value="expenses">
                {{ $t("cashier.expenses") }}
            </v-tab>
            <v-tab value="invoices">
                {{ $t("cashier.invoices") }}
            </v-tab>
            <v-tab value="wis">
                {{ $t("cashier.wis") }}
            </v-tab>
            <v-tab v-if="user.permissions.includes('cashier_admin')" value="reminders">
                Reminders
            </v-tab>
        </v-tabs>
        <v-divider />
        <v-tabs-window v-model="tab">
            <v-tabs-window-item value="sales">
                <v-sheet class="pa-5">
                    <div v-if="!loading" class="d-flex flex-row">
                        <v-select v-model="selectedPlatform" class="flex-grow-0 mr-5 platform-select" label="Platform"
                            :items="platformFilterItems" />
                        <div class="flex-grow-1 mr-5 week-select">
                            <TeuksaatPeriodPicker :start-date="selectedWeek.start" :end-date="selectedWeek.end"
                                @select-week="handleWeekSelection" />
                        </div>
                        <v-text-field v-model="search" class="flex-grow-0 mr-5 search" label="Search site"
                            type="text" />
                    </div>

                    <v-table v-if="!loading" density="compact">
                        <thead>
                            <tr>
                                <th />
                                <th v-for="(
platformSites, platform
                                    ) in platformsToDisplay" :key="platform" class="text-center"
                                    :class="platform + '-header'">
                                    {{ platform }}
                                </th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr class="ma-0 pa-0">
                                <th class="text-subtitle-2 text-center">
                                    Submitted
                                </th>
                                <td v-for="(
platformSites, platform
                                    ) in platformsToDisplay" :key="platform">
                                    <div class="d-flex justify-center flex-wrap my-4">
                                        <v-tooltip v-for="site in platformSites.filter(
                                            (s) => s.distinct_sale_days >= daysBetween
                                        )" :key="site.Id_Site" text="Water meter data is missing"
                                            :disabled="!!site.waterMeter" location="top">
                                            <template v-slot:activator="{ props }">
                                                <v-chip v-bind="props" size="small" color="green-lighten-2"
                                                    variant="elevated" :class="{
                                                        site: 1,
                                                        highlighted:
                                                            search != '' &&
                                                            site.Id_Site.includes(
                                                                search.toUpperCase()
                                                            ),
                                                    }" @click="
                                                        openSiteSales(
                                                            site.Id_Site
                                                        )
                                                        ">
                                                    {{ site.Id_Site }}
                                                    <span v-if="
                                                        site.distinct_sale_days >
                                                        0
                                                    " class="badge">{{
                                                        site.distinct_sale_days
                                                    }}</span>
                                                    <span v-if="!site.waterMeter" class="badge-warning"><v-icon
                                                            icon="mdi-alert" size="10" /></span>
                                                </v-chip>
                                            </template>
                                        </v-tooltip>
                                    </div>
                                </td>
                            </tr>
                            <tr class="ma-0 pa-0">
                                <th class="text-subtitle-2 text-center">
                                    Partial
                                </th>
                                <td v-for="(
platformSites, platform
                                    ) in platformsToDisplay" :key="platform">
                                    <div class="d-flex justify-center flex-wrap my-4">
                                        <v-chip v-for="site in platformSites.filter(
                                            (s) =>
                                                s.distinct_sale_days > 0 &&
                                                s.distinct_sale_days < daysBetween
                                        )" :key="site.Id_Site" size="small" color="yellow-lighten-2" variant="elevated"
                                            :class="{
                                                site: 1,
                                                highlighted:
                                                    search != '' &&
                                                    site.Id_Site.includes(
                                                        search.toUpperCase()
                                                    ),
                                            }" @click="openSiteSales(site.Id_Site)">
                                            {{ site.Id_Site }}
                                            <span v-if="
                                                site.distinct_sale_days > 0
                                            " class="badge">{{
                                                site.distinct_sale_days
                                            }}</span>
                                        </v-chip>
                                    </div>
                                </td>
                            </tr>
                            <tr>
                                <td class="text-subtitle-2 text-center">
                                    Pending
                                </td>
                                <td v-for="(
platformSites, platform
                                    ) in platformsToDisplay" :key="platform">
                                    <div class="d-flex justify-center flex-wrap my-4">
                                        <v-chip v-for="site in platformSites.filter(
                                            (s) =>
                                                !sales[s.Id_Site] ||
                                                sales[s.Id_Site].length == 0
                                        )" :key="site.Id_Site" size="small" color="orange-lighten-2" variant="elevated"
                                            :class="{
                                                site: 1,
                                                highlighted:
                                                    search != '' &&
                                                    site.Id_Site.includes(
                                                        search.toUpperCase()
                                                    ),
                                            }" @click="openSiteSales(site.Id_Site)">
                                            {{ site.Id_Site }}
                                        </v-chip>
                                    </div>
                                </td>
                            </tr>
                        </tbody>
                    </v-table>
                </v-sheet>
            </v-tabs-window-item>
            <v-tabs-window-item value="expenses">
                <v-sheet class="pa-5">
                    <div v-if="!loading" class="d-flex flex-row">
                        <v-select v-model="selectedPlatform" class="flex-grow-0 mr-5 platform-select" label="Platform"
                            :items="platformFilterItems" />
                        <v-text-field v-model="selectedMonth" class="flex-grow-0 mr-5" label="Month" type="month">
                                <template v-slot:prepend-inner>
                                    <v-btn icon size="small" variant="text" @click="changeMonth(-1)">
                                        <v-icon>mdi-chevron-left</v-icon>
                                    </v-btn>
                                </template>
                                <template v-slot:append-inner>
                                    <v-btn icon size="small" variant="text" @click="changeMonth(1)">
                                        <v-icon>mdi-chevron-right</v-icon>
                                    </v-btn>
                                </template>
                            </v-text-field>
                        <v-text-field v-model="search" class="flex-grow-0 mr-5 search" label="Search site"
                            type="text" />
                    </div>

                    <v-table v-if="!loading" density="compact">
                        <thead>
                            <tr>
                                <th />
                                <th v-for="(
platformSites, platform
                                    ) in platformsToDisplay" :key="platform" class="text-center"
                                    :class="platform + '-header'">
                                    {{ platform }}
                                </th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr class="ma-0 pa-0">
                                <th class="text-subtitle-2 text-center">
                                    Submitted
                                </th>
                                <td v-for="(
platformSites, platform
                                    ) in platformsToDisplay" :key="platform">
                                    <div class="d-flex justify-center flex-wrap my-4">
                                        <v-chip v-for="site in platformSites.filter(
                                            (s) =>
                                                expenses[s.Id_Site] &&
                                                expenses[s.Id_Site].length >
                                                0
                                        )" :key="site.Id_Site" size="small" color="green-lighten-2" variant="elevated"
                                            :class="{
                                                site: 1,
                                                highlighted:
                                                    search != '' &&
                                                    site.Id_Site.includes(
                                                        search.toUpperCase()
                                                    ),
                                            }" @click="
                                                openSiteExpenses(site.Id_Site)
                                                ">
                                            {{ site.Id_Site }}
                                        </v-chip>
                                    </div>
                                </td>
                            </tr>
                            <tr>
                                <td class="text-subtitle-2 text-center">
                                    Pending
                                </td>
                                <td v-for="(
platformSites, platform
                                    ) in platformsToDisplay" :key="platform">
                                    <div class="d-flex justify-center flex-wrap my-4">
                                        <v-chip v-for="site in platformSites.filter(
                                            (s) =>
                                                !expenses[s.Id_Site] ||
                                                expenses[s.Id_Site]
                                                    .length == 0
                                        )" :key="site.Id_Site" size="small" color="orange-lighten-2" variant="elevated"
                                            :class="{
                                                site: 1,
                                                highlighted:
                                                    search != '' &&
                                                    site.Id_Site.includes(
                                                        search.toUpperCase()
                                                    ),
                                            }" @click="
                                                openSiteExpenses(site.Id_Site)
                                                ">
                                            {{ site.Id_Site }}
                                        </v-chip>
                                    </div>
                                </td>
                            </tr>
                        </tbody>
                    </v-table>
                </v-sheet>
            </v-tabs-window-item>
            <v-tabs-window-item value="invoices">
                <v-sheet class="pa-5">
                    <div v-if="!loading" class="d-flex flex-row">
                        <v-select v-model="selectedPlatform" class="flex-grow-0 mr-5 platform-select" label="Platform"
                            :items="platformFilterItems" />
                        <v-text-field v-model="selectedMonth" class="flex-grow-0 mr-5" label="Month" type="month">
                                <template v-slot:prepend-inner>
                                    <v-btn icon size="small" variant="text" @click="changeMonth(-1)">
                                        <v-icon>mdi-chevron-left</v-icon>
                                    </v-btn>
                                </template>
                                <template v-slot:append-inner>
                                    <v-btn icon size="small" variant="text" @click="changeMonth(1)">
                                        <v-icon>mdi-chevron-right</v-icon>
                                    </v-btn>
                                </template>
                            </v-text-field>
                        <v-text-field v-model="search" class="flex-grow-0 mr-5 search" label="Search site"
                            type="text" />

                            <v-btn color="primary" class="ml-auto align-self-center"
                                @click="$refs.invoicesDialog.cashierGenerateQR()">
                                <v-icon start>mdi-currency-usd</v-icon>
                                QR
                            </v-btn>
                            <v-btn color="primary" class="ml-auto align-self-center"
                                @click="$refs.invoicesDialog.depositAndwithdraw()">
                                <v-icon start>mdi-currency-usd</v-icon>
                                Balance
                            </v-btn>
                            <v-btn color="green" class="ml-2 align-self-center"
                                @click="$router.push({ path: '/dashboardCashier', query: { month: selectedMonth } })">
                                <v-icon start>mdi-file-excel</v-icon>
                                Excel
                            </v-btn>
                            <v-btn v-if="user.permissions.includes('import_invoices')" prepend-icon="mdi-finance"
                                color="orange-darken-1" class="ml-2 align-self-center"
                                @click="$router.push({ path: '/importInvoice' })">
                                Import Invoice
                            </v-btn>
                        </div>

                        <Invoices v-if="!loading" ref="invoicesDialog" :month="selectedMonth" :platform="selectedPlatform"
                            :search-query="search" />
                </v-sheet>
            </v-tabs-window-item>
            <v-tabs-window-item value="wis">
                <v-sheet class="pa-5">
                    <div v-if="!loading" class="d-flex flex-row">
                        <v-select v-model="selectedPlatform" class="flex-grow-0 mr-5 platform-select" label="Platform"
                            :items="platformFilterItems" />
                        <v-text-field v-model="selectedMonth" class="flex-grow-0 mr-5 month-picker" label="Month" type="month">
                                <template v-slot:prepend-inner>
                                    <v-btn icon size="small" variant="text" @click="changeMonth(-1)">
                                        <v-icon>mdi-chevron-left</v-icon>
                                    </v-btn>
                                </template>
                                <template v-slot:append-inner>
                                    <v-btn icon size="small" variant="text" @click="changeMonth(1)">
                                        <v-icon>mdi-chevron-right</v-icon>
                                    </v-btn>
                                </template>
                            </v-text-field>
                        <v-text-field v-model="search" class="flex-grow-0 mr-5 search" label="Search site"
                            type="text" />
                    </div>

                    <v-table v-if="!loading" density="compact">
                        <thead>
                            <tr>
                                <th />
                                <th v-for="(platformSites, platform) in platformsToDisplay" :key="platform"
                                    class="text-center" :class="platform + '-header'">
                                    {{ platform }}
                                </th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr class="ma-0 pa-0">
                                <th class="text-subtitle-2 text-center">
                                    Submitted
                                </th>
                                <td v-for="(platformSites, platform) in platformsToDisplay" :key="platform">
                                    <div class="d-flex justify-center flex-wrap my-4">
                                        <v-chip v-for="site in platformSites.filter(
                                            (s) => validated.includes(s.Id_Site)
                                        )" :key="site.Id_Site" size="small" color="green-lighten-2" variant="elevated"
                                            :class="{
                                                site: 1,
                                                highlighted:
                                                    search != '' &&
                                                    site.Id_Site.includes(
                                                        search.toUpperCase()
                                                    ),
                                            }" @click="
                                                openSiteWiS(site.Id_Site)
                                                ">
                                            {{ site.Id_Site }}
                                        </v-chip>
                                    </div>
                                </td>
                            </tr>
                            <tr>
                                <td class="text-subtitle-2 text-center">
                                    Pending
                                </td>
                                <td v-for="(platformSites, platform) in platformsToDisplay" :key="platform">
                                    <div class="d-flex justify-center flex-wrap my-4">
                                        <v-chip v-for="site in platformSites.filter(
                                            (s) => !validated.includes(s.Id_Site)
                                        )" :key="site.Id_Site" size="small" color="orange-lighten-2" variant="elevated"
                                            :class="{
                                                site: 1,
                                                highlighted:
                                                    search != '' &&
                                                    site.Id_Site.includes(
                                                        search.toUpperCase()
                                                    ),
                                            }" @click="
                                                openSiteWiS(site.Id_Site)
                                                ">
                                            {{ site.Id_Site }}
                                        </v-chip>
                                    </div>
                                </td>
                            </tr>
                        </tbody>
                    </v-table>
                </v-sheet>
            </v-tabs-window-item>
            <v-tabs-window-item v-if="user.permissions.includes('cashier_admin')" value="reminders">
                <Reminders />
            </v-tabs-window-item>
        </v-tabs-window>
    </v-sheet>

    <div v-if="loading" class="d-flex justify-center mt-10 pt-10">
        <v-progress-circular indeterminate :size="60" color="primary" />
    </div>
</template>

<script>
import TeuksaatPeriodPicker from "../../components/TeuksaatPeriodPicker.vue";
import { calculateDaysBetween } from "../../utils/dateUtils";
import Invoices from "../finance/Invoices.vue";
import Reminders from "./Reminders.vue";
export default {
    name: "CashierHome",
    components: {
        TeuksaatPeriodPicker,
        Invoices,
        Reminders,
    },
    data: function () {
        let selectedWeek = {
            start: null,
            end: null,
        };
        const storedWeek = localStorage.getItem("cashier_selected_week");
        if (storedWeek) {
            try {
                selectedWeek = JSON.parse(storedWeek);
            } catch (e) {
                console.error("Error parsing stored week", e);
            }
        }

        let selectedPlatform = "All";
        const storedPlatform = localStorage.getItem(
            "cashier_selected_platform"
        );
        if (storedPlatform) {
            selectedPlatform = storedPlatform;
        }

        let selectedMonth = "";
        const storedMonth = localStorage.getItem(
            "cashier_selected_month"
        );
        if (storedMonth) {
            selectedMonth = storedMonth;
        }

        return {
            loading: true,
            tab: "sales",
            search: "",
            selectedPlatform: "All",
            sales: [],
            sites: [],
            selectedWeek,
            selectedMonth,
            expenses: [],
            wis: {},
            validated: [],
        };
    },
    computed: {
        platformsToDisplay() {
            if (this.selectedPlatform === "All") {
                return this.sites;
            } else {
                return {
                    [this.selectedPlatform]: this.sites[this.selectedPlatform],
                };
            }
        },
        user() {
            return this.$store.state.user;
        },
        platformFilterItems() {
            let p = Object.keys(this.sites);
            p.unshift("All");
            return p;
        },
        daysBetween() {
            return calculateDaysBetween(this.selectedWeek.start, this.selectedWeek.end);
        },
    },
    watch: {
        selectedPlatform(newVal) {
            localStorage.setItem("cashier_selected_platform", newVal);
        },
        selectedMonth(newVal, oldVal) {
            console.log(oldVal, newVal);
            localStorage.setItem("cashier_selected_month", newVal);
            if (oldVal != "") {
                this.getExpenses();
                this.getWis();
            }
        },
        tab(newTab) {
            if (this.$route.query.tab !== newTab) {
                this.$router.replace({
                    query: { ...this.$route.query, tab: newTab },
                });
            }
        },
    },
    mounted() {
        this.getSales();
        this.getExpenses();
        this.getWis();
        if (this.$route.query.tab) {
            this.tab = this.$route.query.tab;
        }
    },
    methods: {
        getWis() {
            this.loading = true;
            const queryParams = {};
            if (this.selectedMonth) {
                queryParams.month = this.selectedMonth + "-01";
            }
            window.axios
                .get("/api/cashier/wis", {
                    params: queryParams,
                })
                .then((response) => {
                    this.wis = response.data.wis;
                    this.validated = response.data.validated;
                    if (!this.selectedMonth || this.selectedMonth == "") {
                        console.log("setting month", response.data.month);
                        this.selectedMonth = response.data.month.slice(0, 7);
                    }
                    this.loading = false;
                });
        },
        handleWeekSelection(week) {
            console.log("Week selected:", week.start, "to", week.end);
            if (
                week.start != this.selectedWeek.start ||
                week.end != this.selectedWeek.end
            ) {
                this.selectedWeek = { start: week.start, end: week.end };
                localStorage.setItem(
                    "cashier_selected_week",
                    JSON.stringify(this.selectedWeek)
                );
                this.getSales();
            }
        },
        getSales() {
            this.loading = true;
            const queryParams = {};
            if (this.selectedWeek.start && this.selectedWeek.end) {
                queryParams.start = this.selectedWeek.start;
                queryParams.end = this.selectedWeek.end;
            }
            window.axios
                .get("/api/cashier/sales", {
                    params: queryParams,
                })
                .then((response) => {
                    this.sales = response.data.sales;
                    this.sites = response.data.sites;
                    if (
                        this.selectedWeek.start == null ||
                        this.selectedWeek.end == null
                    ) {
                        console.log("setting week", response.data.start_date);
                        this.selectedWeek.start = response.data.start_date;
                        this.selectedWeek.end = response.data.end_date;
                    }
                    this.loading = false;
                });
        },
        getExpenses() {
            this.loading = true;
            const queryParams = {};
            if (this.selectedMonth) {
                queryParams.month = this.selectedMonth + "-01";
            }
            window.axios
                .get("/api/cashier/expenses", {
                    params: queryParams,
                })
                .then((response) => {
                    this.expenses = response.data.expenses;
                    if (!this.selectedMonth || this.selectedMonth == "") {
                        console.log("setting month", response.data.month);
                        this.selectedMonth = response.data.month.slice(0, 7);
                    }
                    this.loading = false;
                });
        },
        changeMonth(delta) {
            const [year, month] = this.selectedMonth.split('-').map(Number);
            const d = new Date(year, month - 1 + delta, 1);
            this.selectedMonth = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`;
        },
        openSiteExpenses(Id_Site) {
            console.log("Opening site expenses:", Id_Site);
            const [year, month] = this.selectedMonth.split("-").map(Number);
            const lastDay = new Date(Date.UTC(year, month, 0));
            this.$router.push({
                name: "CashierExpenses",
                params: {
                    site: Id_Site,
                    startDate: this.selectedMonth + "-01",
                    endDate: lastDay.toISOString().slice(0, 10),
                },
            });
        },
        openSiteWiS(Id_Site) {
            console.log("Opening site WiS:", Id_Site);
            const [year, month] = this.selectedMonth.split("-").map(Number);
            const lastDay = new Date(Date.UTC(year, month, 0));
            this.$router.push({
                name: "CashierWaterInSchool",
                params: {
                    site: Id_Site,
                    startDate: this.selectedMonth + "-01",
                    endDate: lastDay.toISOString().slice(0, 10),
                },
            });
        },
        openSiteSales(Id_Site) {
            console.log("Opening site sales:", Id_Site);
            this.$router.push({
                name: "CashierSales",
                params: {
                    site: Id_Site,
                    startDate: this.selectedWeek.start,
                    endDate: this.selectedWeek.end,
                },
            });
        },
    },
};
</script>

<style scoped>
.site {
    margin: 1px;
    overflow: visible;
}

.platform-select {
    min-width: 150px;
}

.week-select {
    max-width: 400px;
}

.badge {
    z-index: 100;
    box-sizing: border-box;
    font-size: 0.7em;
    color: white;
    background: #0094c7;
    width: 15px;
    height: 15px;
    margin: 0;
    border-radius: 50%;
    position: absolute;
    top: -3px;
    right: -6px;
    text-align: center;
    padding-top: 2px;
}

.badge-warning {
    z-index: 100;
    box-sizing: border-box;
    font-size: 0.7em;
    color: white;
    background: red;
    width: 15px;
    height: 15px;
    margin: 0;
    border-radius: 50%;
    position: absolute;
    top: 12px;
    right: -6px;
    text-align: center;
    padding-top: 0px;
}

.search {
    min-width: 200px;
}

.highlighted {
    animation: blinking ease 0.5s infinite alternate;
}

@keyframes blinking {
    0% {
        box-shadow: 0px 0px 1px 1px #2196f3;
    }

    100% {
        box-shadow: 0px 0px 8px 8px #03a9f4;
    }
}

.rotate-icon {
    animation: rotate 1s infinite linear;
}

@keyframes rotate {
    from {
        transform: rotate(0deg);
    }

    to {
        transform: rotate(360deg);
    }
}
</style>
