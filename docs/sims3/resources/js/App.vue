<template>
    <v-layout class="rounded rounded-md">
        <v-navigation-drawer v-model="isCollapsed" permanent elevation="4">
            <v-list v-if="isAuthenticated">
                <v-list-item
                    class="d-flex justify-center mx-10 my-5"
                    @click="$router.push({ path: '/welcome' })"
                >
                    <img style="max-width: 50px" src="/img/logo.png" />
                </v-list-item>

                <v-list-group>
                    <template #activator="{ props }">
                        <v-list-item
                            v-bind="props"
                            title="Commcare"
                            prepend-icon="mdi-cup-water"
                        />
                    </template>

                    <!-- SiteAnalysis item -->
                    <v-list-item
                        title="SiteAnalysis"
                        prepend-icon="mdi-chart-line"
                        :active="mainRoute == '/analysis'"
                        @click="$router.push({ path: '/analysis' })"
                    />

                    <!-- Commcare item -->
                    <v-list-item
                        prepend-icon="mdi-monitor"
                        title="Commcare"
                        @click="openCommcare()"
                    />

                    <v-list-item
                        title="Flash Report"
                        prepend-icon="mdi-chart-pie"
                        :active="mainRoute == '/flashReport'"
                        @click="$router.push({ path: '/flashReport' })"
                    >
                        <template #title>
                            <span
                                style="
                                    color: #1976d2;
                                    font-family: 'Roboto', sans-serif;
                                "
                                >Flash Report</span
                            >
                        </template>
                    </v-list-item>
                </v-list-group>

                <v-list-item
                    v-if="user.permissions.includes('quality_view')"
                    prepend-icon="mdi-test-tube"
                    title="Quality"
                    :active="mainRoute == '/quality'"
                    @click="$router.push({ path: '/quality' })"
                />

                <v-list-group v-if="user.permissions.includes('finance_check')">
                    <template #activator="{ props }">
                        <v-list-item
                            v-bind="props"
                            title="Finance"
                            prepend-icon="mdi-chart-line"
                        />
                    </template>
            <v-list-item title="Clearance" prepend-icon="mdi-finance"
                      :active="mainRoute == '/finance'"
                      @click="$router.push({ path: '/finance' })" />
          <v-list-item title="Site Status" prepend-icon="mdi-finance"
                      :active="mainRoute == '/siteActive'"
                      @click="$router.push({ path: '/siteActive' })" />
                      <v-list-item title="School" prepend-icon="mdi-finance"
                      :active="mainRoute == '/school'"
                      @click="$router.push({ path: '/school' })" />
          <v-list-item title="Province Report" prepend-icon="mdi-file-document-outline"
                      :active="$route.path == '/provinceReport'"
                      @click="$router.push({ path: '/provinceReport' })" />
        </v-list-group>
                <v-list-group v-if="user.permissions.includes('finance_check')">
                    <v-list-item
                        title="Site Status"
                        prepend-icon="mdi-finance"
                        :active="mainRoute == '/siteActive'"
                        @click="$router.push({ path: '/siteActive' })"
                    />

                    <v-list-item
                        title="Settle Invoice"
                        prepend-icon="mdi-finance"
                        :active="mainRoute == '/settleInvoice'"
                        @click="$router.push({ path: '/settleInvoice' })"
                    />
                </v-list-group>

                <v-list-group>
                    <template #activator="{ props }">
                        <v-list-item
                            v-bind="props"
                            title="Technical"
                            prepend-icon="mdi-wrench-cog"
                        />
                    </template>

                    <!-- SiteAnalysis item -->
                    <v-list-item
                        title="Technical"
                        prepend-icon="mdi-wrench-cog"
                        :active="mainRoute == '/technical'"
                        @click="$router.push({ path: '/technical' })"
                    />

                    <v-list-item
                        title="Assessment"
                        prepend-icon="mdi-battery"
                        :active="mainRoute == '/assessment'"
                        @click="$router.push({ path: '/assessment' })"
                    />

                    <v-list-item
                        title="Sensor"
                        prepend-icon="mdi-script"
                        :active="mainRoute == '/sensor'"
                        @click="$router.push({ path: '/sensor' })"
                    />
                </v-list-group>

                <v-list-group>
                    <template #activator="{ props }">
                        <v-list-item
                            v-bind="props"
                            title="Site"
                            prepend-icon="mdi-water-well"
                        />
                    </template>

                    <!-- SiteAnalysis item -->
                    <v-list-item
                        title="Site"
                        prepend-icon="mdi-water-well"
                        :active="mainRoute == '/site'"
                        @click="$router.push({ path: '/site' })"
                    />

                    <v-list-item
                        title="Site Contract"
                        prepend-icon="mdi-battery"
                        :active="mainRoute == '/contractSite'"
                        @click="$router.push({ path: '/contractSite' })"
                    />
                </v-list-group>

                <v-list-group>
                    <template #activator="{ props }">
                        <v-list-item
                            v-bind="props"
                            title="Entrepreneur"
                            prepend-icon="mdi-motorbike"
                        />
                    </template>

                    <!-- SiteAnalysis item -->
                    <v-list-item
                        title="Entre Info"
                        prepend-icon="mdi-motorbike"
                        :active="mainRoute == '/entrepreneur'"
                        @click="$router.push({ path: '/entrepreneur' })"
                    />

                    <v-list-item
                        title="School Program"
                        prepend-icon="mdi-school"
                        :active="mainRoute == '/schoolProgram'"
                        @click="$router.push({ path: '/schoolProgram' })"
                    />
                </v-list-group>

                <v-list-group>
                    <template #activator="{ props }">
                        <v-list-item
                            v-bind="props"
                            title="PA"
                            prepend-icon="mdi-motorbike"
                        />
                    </template>

                    <!-- SiteAnalysis item -->
                    <v-list-item
                        v-if="user.permissions.includes('pa_view')"
                        title="PA"
                        prepend-icon="mdi-gavel"
                        :active="mainRoute == '/pa'"
                        @click="$router.push({ path: '/pa' })"
                    />

                    <v-list-item
                        v-if="user.permissions.includes('view_kpi_report')"
                        title="Objective"
                        prepend-icon="mdi-tag-text-outline"
                        :active="mainRoute == '/objective'"
                        @click="$router.push({ path: '/objective' })"
                    />
                    <v-list-item
                        title="Training"
                        prepend-icon="mdi-nature-people"
                        :active="mainRoute == '/training'"
                        @click="$router.push({ path: '/training' })"
                    />
                </v-list-group>
                <v-list-item
                    v-if="user.permissions.includes('consumable_request')"
                    title="Consumable"
                    prepend-icon="mdi-motorbike"
                    :active="mainRoute == '/consumable/excelUpload'"
                    @click="$router.push({ path: '/consumable/excelUpload' })"
                />
                <v-list-item
                    v-if="user.permissions.includes('cashier') || user.permissions.includes('cashier_admin')"
                    title="Cashier"
                    prepend-icon="mdi-cash-check"
                    :active="mainRoute.includes('cashier')"
                    @click="$router.push({ path: 'cashier' })"
                />
                <!-- <v-list-item title="Mission" prepend-icon="mdi-motorbike" :active="mainRoute == '/mission'"
          @click="$router.push({ path: '/mission' })" /> -->
                <!-- <v-list-item title="Site Status" prepend-icon="mdi-ambulance" :active="mainRoute == '/siteActive'"
          @click="$router.push({ path: '/siteActive' })" /> -->
                <!-- <v-list-item title="Assessment" prepend-icon="mdi-battery" :active="mainRoute == '/assessment'"
          @click="$router.push({ path: '/assessment' })" /> -->
                <!-- <v-list-item title="Entrepreneur Info" prepend-icon="mdi-motorbike" :active="mainRoute == '/entrepreneur'"
          @click="$router.push({ path: '/entrepreneur' })" />
        <v-list-item title="School Program" prepend-icon="mdi-school" :active="mainRoute == '/schoolProgram'"
          @click="$router.push({ path: '/schoolProgram' })" /> -->
                <!-- <v-list-item v-if="user.permissions.includes('finance_check')" title="Finance" prepend-icon="mdi-finance"
          :active="mainRoute == '/finance'" @click="$router.push({ path: '/finance' })" /> -->
                <!-- <v-list-item title="Technical" prepend-icon="mdi-wrench-cog" :active="mainRoute == '/technical'"
          @click="$router.push({ path: '/technical' })" /> -->
                <!-- <v-list-item title="Sites" prepend-icon="mdi-water-well" :active="mainRoute == '/site'"
          @click="$router.push({ path: '/site' })" /> -->
                <!-- <div v-if="user.permissions.includes('pa_view')">
          <v-list-item title="PA" prepend-icon="mdi-gavel" :active="mainRoute == '/pa'"
            @click="$router.push({ path: '/pa' })" />
          <v-list-item v-if="user.permissions.includes('view_kpi_report')" title="Objective"
            prepend-icon="mdi-tag-text-outline" :active="mainRoute == '/objective'"
            @click="$router.push({ path: '/objective' })" />
          <v-list-item title="Training" prepend-icon="mdi-nature-people" :active="mainRoute == '/training'"
            @click="$router.push({ path: '/training' })" />
          
           <v-list-item title="SiteAnalysis" prepend-icon="mdi-chart-line" :active="mainRoute == '/analysis'"
            @click="$router.push({ path: '/analysis' })" /> 
        </div> -->
                <!-- <v-list-item title="Flash Report" prepend-icon="mdi-chart-pie" :active="mainRoute == '/flashReport'"
          @click="$router.push({ path: '/flashReport' })">
          <template #title>
            <span
              style="
                                color: #1976d2;
                                font-family: 'Roboto', sans-serif;
                            "
            >Flash Report</span>
          </template>
        </v-list-item>
      -->

                <!--
                <v-list-item
                    title="Sensor"
                    prepend-icon="mdi-script"
                    :active="mainRoute == '/sensor'"
                    @click="$router.push({ path: '/sensor' })"
                />
                <v-list-item
                    title="SiteContract"
                    prepend-icon="mdi-script"
                    :active="mainRoute == '/contractSite'"
                    @click="$router.push({ path: '/contractSite' })"
                /> -->

                <v-list-group
                    v-if="user.permissions.includes('sale_view')"
                    value="salesMenu"
                >
                    <template #activator="{ props }">
                        <v-list-item
                            v-bind="props"
                            title="Sale"
                            prepend-icon="mdi-cup-water"
                        />
                    </template>

                    <v-list-item
                        v-for="([title, icon], i) in salesMenu"
                        :key="i"
                        :value="title"
                        :title="title"
                        :prepend-icon="icon"
                        @click="$router.push({ path: '/' + title })"
                    />
                </v-list-group>

                <v-list-group
                    v-if="user.permissions.includes('edit_permissions')"
                    value="report"
                >
                    <template #activator="{ props }">
                        <v-list-item
                            v-bind="props"
                            title="Report"
                            prepend-icon="mdi-cup-water"
                        />
                    </template>

                    <v-list-item
                        v-for="([title, icon], i) in Report"
                        :key="i"
                        :value="title"
                        :title="title"
                        :prepend-icon="icon"
                        @click="$router.push({ path: '/' + title })"
                    />
                </v-list-group>

                <v-list-group
                    v-if="user.permissions.includes('edit_permissions')"
                    value="permissionMenu"
                >
                    <template #activator="{ props }">
                        <v-list-item
                            v-bind="props"
                            title="Admin"
                            prepend-icon="mdi-cup-water"
                        />
                    </template>

                    <v-list-item
                        v-for="([title, icon], i) in Admin"
                        :key="i"
                        :value="title"
                        :title="title"
                        :prepend-icon="icon"
                        @click="$router.push({ path: '/' + title })"
                    />
                </v-list-group>
            </v-list>
            <template #append>
                <div class="pa-4">
                    <v-btn block @click="logout()">
                        logout
                        <v-icon>mdi-logout</v-icon>
                    </v-btn>
                </div>
            </template>
        </v-navigation-drawer>

        <v-app-bar color="primary" density="compact">
            <template #title>
                <router-link
                    :to="'/welcome'"
                    class="text-white text-decoration-none"
                >
                    &#128640; Sims 3
                </router-link>
            </template>
            <template #prepend>
                <v-app-bar-nav-icon @click="isCollapsed = !isCollapsed" />
            </template>
            <template #append>
                <div class="d-flex align-center mr-5">
                    <span
                        :class="{
                            'font-weight-bold text-white': !isKhLocale,
                            'text-medium-emphasis': isKhLocale,
                        }"
                        class="text-body-2"
                    >
                        EN
                    </span>
                    <v-switch
                        v-model="isKhLocale"
                        false-icon="mdi-translate"
                        true-icon="mdi-translate"
                        hide-details
                    />
                    <span
                        :class="{
                            'font-weight-bold text-white': isKhLocale,
                            'text-medium-emphasis': !isKhLocale,
                        }"
                        class="text-body-2"
                    >
                        KH
                    </span>
                </div>
                <v-switch
                    v-model="darkMode"
                    false-icon="mdi-lightbulb-on-10"
                    true-icon="mdi-weather-night"
                    hide-details
                />
            </template>
        </v-app-bar>

        <v-main class="d-flex" style="min-height: 300px">
            <v-container fluid class="pa-0">
                <router-view />
            </v-container>
        </v-main>
    </v-layout>
</template>

<script>
import { useTheme } from "vuetify";
import { watch, ref } from "vue";
import { useI18n } from "vue-i18n";
export default {
    setup() {
        const theme = useTheme();
        const { locale } = useI18n();
        const darkMode = ref(localStorage.getItem("darkMode") === "true");
        theme.change(darkMode.value ? "dark" : "light");
        watch(darkMode, (newVal) => {
            theme.change(newVal ? "dark" : "light");
            localStorage.setItem("darkMode", newVal);
        });
        const enIcon = "mdi-translate";
        const khIcon = "mdi-translate";

        const storedLocale = localStorage.getItem("locale");
        const defaultLocale = "en";
        const khLocaleCode = "kh";

        if (storedLocale && storedLocale !== locale.value) {
            locale.value = storedLocale;
        } else if (!storedLocale) {
            locale.value = defaultLocale;
            localStorage.setItem("locale", defaultLocale);
        }
        const isKhLocale = ref(locale.value === khLocaleCode);
        watch(isKhLocale, (newVal) => {
            const newLocale = newVal ? khLocaleCode : defaultLocale;
            locale.value = newLocale;
            localStorage.setItem("locale", newLocale);
        });

        return {
            darkMode,
            isKhLocale,
            enIcon,
            khIcon,
        };
    },
    data() {
        return {
            isCollapsed: false,
            salesMenu: [
                ["KOL", "mdi-plus-outline"],
                ["SaleRecord", "mdi-file-outline"],
                ["SaleSurvey", "mdi-file-search-outline"],
                // ['Update', 'mdi-update'],
                // ['Delete', 'mdi-delete'],
            ],
            Admin: [
                ["Admin", "mdi-update"],
                ["Telegram", "mdi-message"]],
            Report: [
                ["SiteAnalysis", "mdi-chart-line"],
                ["WQ-Report", "mdi-chart-line"],
                ["techAnalysis", "mdi-chart-line"],
            ],
        };
    },
    computed: {
        isAuthenticated() {
            return this.$store.state.isAuthenticated;
        },
        user() {
            return this.$store.state.user;
        },
        mainRoute() {
            if (this.$route.path.includes("quality")) {
                return "/quality";
            } else if (this.$route.path.includes("mission")) {
                return "/mission";
            } else if (this.$route.path.includes("technical")) {
                return "/technical";
            } else if (this.$route.path.includes("finance")) {
                return "/finance";
            } else if (this.$route.path.includes("admin")) {
                return "/Admin";
            } else if (this.$route.path.includes("site")) {
                return "/site";
            } else if (this.$route.path.includes("cashier")) {
                return "/cashier";
            } else {
                return "/unknown";
            }
        },
    },
    methods: {
        logout() {
            window.axios.post("/api/logout", {}).then(() => {
                window.location.href = "/";
            });
        },
        openCommcare() {
            window.open("https://dashboard.teuksaat1001.com/", "_blank");
        },
    },
};
</script>
<style scoped>
.container {
    display: flex;
    flex-direction: column;
    height: 100%;
}

.sidebar {
    width: 250px;
    background-color: #444654;
    color: white;
    padding: 20px;
    transition: 0.3s;
}

.content {
    display: flex;
    flex-direction: row;
    flex-grow: 1;
}

.header {
    background-color: #444654;
    color: white;
    display: flex;
    overflow-y: auto;
}

.main {
    flex-grow: 1;
    padding: 5px;
}

h3 {
    margin: 5px;
}

.collapse-btn {
    padding-left: 10px;
    padding-right: 20px;
    cursor: pointer;
}

.collapsed {
    width: 0;
}

@media print {
    /* Hide the toolbar */
    .app-toolbar {
        display: none;
    }

    .v-app-bar {
        display: none;
    }

    /* You can also hide other unnecessary elements like footers or sidebars */
    .footer,
    .sidebar {
        display: none;
    }

    /* Optional: Make sure the printable content takes full width */
    #printable {
        width: 100%;
    }
}
</style>
