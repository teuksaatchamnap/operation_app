import "./bootstrap";
import "../css/app.css";

//import { createApp } from "vue";
import { createApp } from "vue/dist/vue.esm-bundler";
import App from "./App.vue";
import { createRouter, createWebHashHistory } from "vue-router";
import { createStore } from "vuex";
import vue3GoogleLogin from "vue3-google-login";

// Vuetify
import "vuetify/styles";
import "@mdi/font/css/materialdesignicons.css";
import { createVuetify } from "vuetify";
import * as components from "vuetify/components";
import * as directives from "vuetify/directives";
import { aliases, mdi } from "vuetify/lib/iconsets/mdi";
import "@mdi/font/css/materialdesignicons.css";
// Vue3-easy-data-table
import Vue3EasyDataTable from "vue3-easy-data-table";
import "vue3-easy-data-table/dist/style.css";
// use sweetalert2
// import VueSweetalert2 from 'vue-sweetalert2';

import { createI18n } from "vue-i18n";
import enMessages from "./locales/en.json";
import khMessages from "./locales/kh.json";
const i18n = createI18n({
    locale: "en",
    fallbackLocale: "en",
    messages: {
        en: enMessages,
        kh: khMessages,
    },
});

const vuetify = createVuetify({
    components,
    directives,
    icons: {
        defaultSet: "mdi",
        aliases,
        sets: {
            mdi,
        },
    },
});

const routes = [
    { path: "/", component: () => import("./pages/Login.vue"), name: "Login" },
    {
        path: "/welcome",
        component: () => import("./pages/Welcome.vue"),
        name: "Welcome",
    },
    {
        path: "/quality",
        component: () => import("./pages/quality/QualityHome.vue"),
    },
    {
        path: "/quality/sample",
        component: () => import("./pages/quality/SampleForm.vue"),
    },
    {
        path: "/quality/sample/:id",
        component: () => import("./pages/quality/SampleForm.vue"),
    },
    {
        path: "/quality/:site",
        component: () => import("./pages/quality/SiteDetails.vue"),
    },
    {
        path: "/quality/siteOpening",
        component: () => import("./pages/quality/SiteOpenAndSelection.vue"),
    },
    {
        path: "/mission",
        component: () => import("./pages/mission/MissionHome.vue"),
    },
    {
        path: "/mission/form",
        component: () => import("./pages/mission/MissionForm.vue"),
    },
    {
        path: "/mission/:id",
        component: () => import("./pages/mission/MissionForm.vue"),
    },
    { path: "/Admin", component: () => import("./pages/Administration.vue") },
    { path: "/Telegram", component: () => import("./pages/telegram/TelegramGroups.vue") },
    { path: "/technical", component: () => import("./pages/technical/TechnicalHomePage.vue") },
    { path: "/technical/emailForm", component: () => import("./pages/technical/EmailForm.vue") },
    { path: "/techStock", component: () => import("./pages/technical/minimumStock.vue") },
    { path: '/technical/form/:id', component: () => import("./pages/technical/TechnicalForm.vue")},
    { path: "/technical/emailForm/:id", component: () => import("./pages/technical/EmailForm.vue") },
    { path: '/technical/detail/:id', component: () => import("./pages/technical/DetailTechnical.vue")},
    { path: '/technical/form', component: () => import("./pages/technical/TechnicalForm.vue")},
    { path: '/consumable/excelUpload', component: () => import("./pages/consumable/ExcelUpload.vue")},
    { path: "/finance", component: () => import("./pages/finance/FinanceDashboard.vue") },
    { path: "/provinceReport", component: () => import("./pages/finance/ProvinceReport.vue") },
    { path: "/site", component: () => import("./pages/sites/SiteHome.vue")},
    { path: "/contractSite", component: () => import("./pages/sites/ContractSite.vue")},
    { path: "/site/form", component: () => import("./pages/sites/SiteForm.vue")},
    { path: "/site/:id", component: () => import("./pages/sites/SiteForm.vue")},
    { path: "/pa", component: () => import("./pages/pa/PaHome.vue")},
    { path: "/saleobjection", component: () => import("./pages/pa/SaleObjection.vue")},
    { path: "/pa/form", component: () => import("./pages/pa/FormPa.vue")},
    { path: "/pa/:id", component: () => import("./pages/pa/FormPa.vue")},
    { path: "/objective", component: () => import("./pages/pa/Objective.vue")},
    { path: "/training/:id", component: () => import("./pages/pa/TrainingDetail.vue")},
    { path: "/training", component: () => import("./pages/pa/Training.vue")},
    { path: "/kol", component: () => import("./pages/sale/Kol.vue")},
    { path: "/kol/form", component: () => import("./pages/sale/KolForm.vue")},
    { path: "/kol/:id", component: () => import("./pages/sale/KolForm.vue")},
    { path: "/saleRecord", component: () => import("./pages/sale/SaleRecord.vue")},
    { path: "/saleRecord/form", component: () => import("./pages/sale/SaleForm.vue")},
    { path: "/saleRecord/detail/", component: () => import("./pages/sale/saleDetail.vue")},
    { path: "/saleRecord/:id", component: () => import("./pages/sale/SaleForm.vue")},
    { path: "/sensor", component: () => import("./pages/sensor/sensor.vue")},
    { path: "/flashReport", component: () => import("./pages/flashReport/flashReport.vue")},
    { path: "/flashReport/:id", component: () => import("./pages/flashReport/flashReportForm.vue")},
    { path: "/flashReportDashboard", component: () => import("./pages/flashReport/dashboard.vue")},
    { path: "/analysis", component: () => import("./pages/siteAnalysis/siteAnalysis.vue")},
    { path: "/saleChart", component: () => import("./pages/testPage/saleChart.vue")},
    { path: "/assessment", component: () => import("./pages/assessment/index.vue")},
    { path: "/FormAssessment/:id", component: () => import("./pages/assessment/FormAssessment.vue")},
    { path: "/FormRoutine/:id", component: () => import("./pages/assessment/FormRoutine.vue")},
    { path: "/entrepreneur", component: () => import("./pages/entrepreneur/Home.vue")},
    { path: "/newEntrepreneur/detail/:id", component: () => import("./pages/entrepreneur/DetailEntrepreneur.vue")},
    { path: "/schoolProgram", component: () => import("./pages/schoolProgram/SchoolProgramHomePage.vue")},
    { path: "/schoolProgram/detail/:id", component: () => import("./pages/schoolProgram/SchoolForm.vue")},
    { path: "/schoolsContractPrint", component: () => import("./pages/schoolProgram/Print.vue")},
    { path: '/quality/Opening', component: () => import("./pages/quality/SiteOpenAndSelection1.vue")},
    { path: '/quality/ExternalSample', component: () => import("./pages/quality/ExternalSample.vue")},
    { path: '/labCertificate', component: () => import("./pages/quality/PrintCertificate.vue")},
    { path: '/siteActive', component: () => import("./pages/sites/SiteActive.vue")},
    { path: "/validateRequest/:email/:dateapproval", component: () => import("./pages/consumable/ValidateRequest.vue")},
    { path: "/treeview", component: () => import("./pages/testPage/translate.vue")},
    { path: "/enForm/:id", component: () => import("./pages/entrepreneur/EnForm.vue")},
    { path: "/siteAnalysis", component: () => import("./pages/report/siteAnalysis.vue")},
    { path: "/techAnalysis", component: () => import("./pages/report/technicalReport.vue")},
    { path: "/WQ-Report", component: () => import("./pages/report/wqReport.vue")},
    { path: "/re", component: () => import("./pages/report/reserveWQReport.vue")},
    { path: "/registerSale", component: () => import("./pages/finance/RegisterSale.vue")},
    { path: "/sale", component: () => import("./pages/finance/sale.vue")},
    { path: "/settleInvoice", component: () => import("./pages/finance/Invoices.vue")},
    { path: "/qr", component: () => import("./pages/finance/qr.vue")},
    { path: "/dashboardCashier", component: () => import("./pages/finance/dashboardCashier.vue")},
    { path: "/school", component: () => import("./pages/finance/schoolProgram.vue")},
    { path: "/SaleSurvey", component: () => import("./pages/sale/saleSurvey.vue")},
    { path: "/inlineEdit", component: () => import("./pages/testPage/inlineEdit.vue")},
    {
  path: "/cashReceipt",
  name: "cashReceipt",
  component: () => import("./pages/finance/CashReceipt.vue")
},
    { path: "/invoiceSend", component: () => import("./pages/finance/InvoiceSend.vue")},
    { path: "/importInvoice", component: () => import("./pages/finance/ImportInvoice.vue")},
    { path: "/inlineEdit", component: () => import("./pages/testPage/inlineEdit.vue")},

    {
        path: "/cashier",
        component: () => import("./pages/cashier/CashierHome.vue"),
    },
    {
        path: "/cashier/:site/sales/:startDate/:endDate",
        component: () => import("./pages/cashier/CashierSales.vue"),
        name: "CashierSales",
    },
    {
        path: "/cashier/:site/expenses/:startDate/:endDate",
        component: () => import("./pages/cashier/CashierExpenses.vue"),
        name: "CashierExpenses",
    },
    {
        path: "/cashier/:site/wis/:startDate/:endDate",
        component: () => import("./pages/cashier/CashierWaterInSchool.vue"),
        name: "CashierWaterInSchool",
    },
    {
        path: "/cashier/:site/water/:startDate/:endDate",
        component: () => import("./pages/cashier/CashierWaterMeter.vue"),
        name: "CashierWaterMeter",
    },

];

const router = createRouter({
    history: createWebHashHistory(),
    routes,
});

const store = createStore({
    state() {
        return {
            isAuthenticated: false,
            user: {},
            initialRoute: null,
        };
    },
    mutations: {
        login(state, user) {
            state.isAuthenticated = true;
            state.user = user;
        },
    },
});

router.beforeEach(async (to, from) => {
    if (!store.state.isAuthenticated && to.name !== "Login") {
        store.state.initialRoute = to.path;
        return { name: "Login" };
    }
});

const app = createApp(App);
app.use(router);
app.use(store);
app.use(vuetify);
app.use(i18n);
//app.use(VueSweetalert2);
app.component("EasyDataTable", Vue3EasyDataTable);
window.googleClientId =
    "736073153554-ka51oha7hvt3n5q4b1vqfhcsckpc3s96.apps.googleusercontent.com";
app.use(vue3GoogleLogin, {
    clientId: window.googleClientId,
});
app.mount("#app");
