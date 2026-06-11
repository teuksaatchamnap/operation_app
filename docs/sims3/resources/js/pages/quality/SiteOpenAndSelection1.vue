<template>
    <v-btn
        icon="mdi-arrow-left-bold-circle"
        color="blue"
        size="small"
        @click="$router.push({ path: '/quality' })"
    ></v-btn>
    <v-card class="ma-3">
        <v-tabs v-model="tab" bg-color="green">
            <v-tab value="site_intervention"> Site Intervention </v-tab>
            <v-tab value="site_selection"> Site Selection </v-tab>
            <v-tab value="site_opening"> Site Opening </v-tab>
        </v-tabs>
        <v-card-text v-if="loading" class="d-flex justify-center mt-10">
            <v-progress-circular indeterminate :size="60" color="primary" />
        </v-card-text>
        <v-card-text v-else>
            <div v-if="tab == 'site_opening'">
                <div class="d-flex flex-row align-center mb-3">
                    <v-row>
                        <v-col cols="12" md="3">
                            <v-text-field
                                v-model="startdate"
                                type="date"
                                density="compact"
                                label="Start Date"
                                hide-details="auto"
                            />
                        </v-col>
                        <v-col cols="12" md="3">
                            <v-text-field
                                v-model="enddate"
                                type="date"
                                density="compact"
                                label="End Date"
                                hide-details="auto"
                            />
                        </v-col>
                        <v-col cols="12" md="2">
                            <v-btn
                                class="ml-5 mt-2 mr-5"
                                color="secondary"
                                icon="mdi-microsoft-excel"
                                @click="printExcel('site_opening')"
                            />
                        </v-col>
                    </v-row>
                    <v-text-field
                        v-model="search"
                        density="compact"
                        label="Search"
                        hide-details
                        clearable
                        class="shrink"
                        prepend-inner-icon="mdi-clipboard-text-search"
                    />
                </div>
                <!-- show data -->
                <v-data-table
                    v-model:items-per-page="itemsPerPage"
                    :headers="headersSiteOpening"
                    :items="filterPA"
                    density="compact"
                    item-value="sample_date"
                    class="pa-4"
                >
                    <template #item.actions="{ item }">
                        <v-chip
                            size="small"
                            color="Blue"
                            v-if="
                                item.site_open_final_judgement == '' ||
                                item.site_open_final_judgement == null
                            "
                            @click="
                                $router.push({
                                    path: '/quality/sample/' + item.id,
                                })
                            "
                        >
                            <v-icon
                                start
                                size="x-small"
                                icon="mdi-apple-keyboard-shift"
                            />Modify
                        </v-chip>
                    </template>
                </v-data-table>
            </div>
            <div v-if="tab == 'site_selection'">
                <div class="d-flex flex-row align-center mb-3">
                    <v-row>
                        <v-col cols="12" md="3">
                            <v-text-field
                                v-model="startdate"
                                type="date"
                                density="compact"
                                label="Start Date"
                                hide-details="auto"
                            />
                        </v-col>
                        <v-col cols="12" md="3">
                            <v-text-field
                                v-model="enddate"
                                type="date"
                                density="compact"
                                label="End Date"
                                hide-details="auto"
                            />
                        </v-col>
                        <v-col cols="12" md="2">
                            <v-btn
                                class="ml-5 mt-2 mr-5"
                                color="secondary"
                                icon="mdi-microsoft-excel"
                                @click="printExcel('Site_Selection')"
                            />
                        </v-col>
                    </v-row>
                    <v-text-field
                        v-model="search"
                        density="compact"
                        label="Search"
                        hide-details
                        clearable
                        class="shrink"
                        prepend-inner-icon="mdi-clipboard-text-search"
                    />
                </div>
                <!-- show data -->
                <v-data-table
                    v-model:items-per-page="itemsPerPage"
                    :headers="headersSiteSelection"
                    :items="filterPA"
                    density="compact"
                    item-value="sample_date"
                    class="pa-4"
                >
                    <template #item.actions="{ item }">
                        <v-chip
                            v-if="
                                item.site_open_final_judgement == '' ||
                                item.site_open_final_judgement == null
                            "
                            size="small"
                            color="green"
                            @click="
                                $router.push({
                                    path: '/quality/sample/' + item.id,
                                })
                            "
                        >
                            <v-icon
                                start
                                size="x-small"
                                icon="mdi-apple-keyboard-shift"
                            />Detail
                        </v-chip>
                    </template>
                    <template #item.document="{ item }">
                        <v-chip @click="downloadImages(item.id)">
                            <v-icon size="large" icon="mdi-cloud-download" />
                        </v-chip>
                    </template>
                </v-data-table>
            </div>
            <div v-if="tab == 'site_intervention'">
                <div class="d-flex flex-row align-center mb-3">
                    <v-row>
                        <v-col cols="12" md="3">
                            <v-text-field
                                v-model="startdate"
                                type="date"
                                density="compact"
                                label="Start Date"
                                hide-details="auto"
                            />
                        </v-col>
                        <v-col cols="12" md="3">
                            <v-text-field
                                v-model="enddate"
                                type="date"
                                density="compact"
                                label="End Date"
                                hide-details="auto"
                            />
                        </v-col>
                        <v-col cols="12" md="2">
                            <v-btn
                                class="ml-5 mt-2 mr-5"
                                color="secondary"
                                icon="mdi-microsoft-excel"
                                @click="printExcel('site_intervention')"
                            />
                        </v-col>
                    </v-row>
                    <v-text-field
                        v-model="search"
                        density="compact"
                        label="Search"
                        hide-details
                        clearable
                        class="shrink"
                        prepend-inner-icon="mdi-clipboard-text-search"
                    />
                </div>
                <!-- show data -->
                <v-data-table
                    v-model:items-per-page="itemsPerPage"
                    :headers="headersSiteOpening"
                    :items="filterPA"
                    density="compact"
                    item-value="sample_date"
                    class="pa-4"
                >
                    <template #item.actions="{ item }">
                        <v-chip
                            v-if="
                                item.site_open_final_judgement == '' ||
                                item.site_open_final_judgement == null
                            "
                            size="small"
                            color="green"
                            @click="
                                $router.push({
                                    path: '/quality/sample/' + item.id,
                                })
                            "
                        >
                            <v-icon
                                start
                                size="x-small"
                                icon="mdi-apple-keyboard-shift"
                            />Detail
                        </v-chip>
                    </template>
                </v-data-table>
            </div>
        </v-card-text>
    </v-card>
    <div class="text-center">
        <v-dialog v-model="dialog" activator="parent" width="auto">
            <v-card>
                <v-card-text>
                    Excel download is in construction. Please be patient !!!
                </v-card-text>
                <v-card-actions>
                    <v-btn color="primary" block @click="dialog = false"
                        >Close</v-btn
                    >
                </v-card-actions>
            </v-card>
        </v-dialog>
    </div>
</template>

<script>
// import { VDataTable } from 'vuetify/labs/VDataTable'
export default {
    name: "HomeSite",
    components: {
        
    },
    data: function () {
        return {
            open: false,
            startdate: new Date().toJSON().slice(0, 10),
            enddate: new Date().toJSON().slice(0, 10),
            position: "",
            positionData: [],
            dialog: false,
            loading: true,
            PA: [],
            itemsPerPage: 15,
            search: "",
            tab: "Site_Opening",
            throttleTimer: -1,
            headersSiteOpening: [
                { title: "", align: "center", key: "actions" },
                {
                    title: "Site",
                    align: "start",
                    key: "site",
                    width: 40,
                    sortable: true,
                },
                {
                    title: "Sample Date",
                    align: "center",
                    key: "site_open_sample_date",
                    width: 80,
                },
                {
                    title: "Sample Type",
                    align: "center",
                    key: "site_open_sample_type",
                    width: 80,
                },
                {
                    title: "Description",
                    align: "center",
                    key: "site_open_project_type",
                    width: 80,
                },
                {
                    title: "Sample By",
                    align: "center",
                    key: "site_open_sample_by",
                    width: 60,
                },
                { title: "Lab", align: "center", key: "laboratory", width: 40 },
                {
                    title: "Coliform (machine)",
                    align: "center",
                    key: "total_coliform",
                },
                {
                    title: "Ecoli (machine)",
                    align: "center",
                    key: "escherichia",
                },
                { title: "pH", align: "center", key: "ph" },
                { title: "Turbidity", align: "center", key: "turbidity" },
                { title: "Cond", align: "center", key: "conductivity" },
                { title: "TDS", align: "center", key: "tds" },
                { title: "Hardness", align: "center", key: "hardness" },
                { title: "Comment", align: "center", key: "site_open_comment" },
                {
                    title: "Judgement",
                    align: "center",
                    key: "site_open_judgement",
                },
                {
                    title: "Solution",
                    align: "center",
                    key: "site_open_solution",
                },
                {
                    title: "Final Decision",
                    align: "center",
                    key: "site_open_final_judgement",
                },
            ],
            headersSiteSelection: [
                { title: "", align: "center", key: "actions" },
                {
                    title: "Code",
                    align: "start",
                    key: "sample_code",
                    width: 30,
                    sortable: true,
                },
                {
                    title: "Date",
                    align: "center",
                    key: "site_open_sample_date",
                    width: 110,
                },
                {
                    title: "en_location",
                    align: "center",
                    key: "sample_en_location",
                    width: 50,
                },
                {
                    title: "Project Name",
                    align: "center",
                    key: "site_open_project_type",
                    width: 50,
                },
                {
                    title: "Sample By",
                    align: "center",
                    key: "site_open_sample_by",
                    width: 50,
                },
                { title: "pH", align: "center", key: "ph" },
                { title: "Turbidity", align: "center", key: "turbidity" },
                { title: "Cond", align: "center", key: "conductivity" },
                { title: "TDS", align: "center", key: "tds" },
                { title: "Comment", align: "center", key: "site_open_comment" },
                {
                    title: "Judgement",
                    align: "center",
                    key: "site_open_judgement",
                },
                {
                    title: "Solution",
                    align: "center",
                    key: "site_open_solution",
                },
                {
                    title: "Final Decision",
                    align: "center",
                    key: "site_open_final_judgement",
                },
                { title: "Picture", align: "center", key: "document" },
            ],
        };
    },
    computed: {
        filterPA() {
            if (this.tab == "site_intervention") {
                if (this.search == "") {
                    return this.PA;
                } else {
                    // return this.PA.filter(m => (m.site).includes(this.search))

                    return this.PA.filter((item) => {
                        return item.site.includes(
                            this.search.toLocaleUpperCase()
                        );
                    });
                }
            } else if (this.tab == "site_selection") {
                console.log("you are here for site_selection");
                if (this.search == "") {
                    return this.PA;
                } else {
                    return this.PA.filter((item) => {
                        return item.sample_code
                            .toString()
                            .includes(this.search);
                    });
                }
            } else {
                if (this.search == "") {
                    return this.PA;
                } else {
                    return this.PA.filter((item) => {
                        return item.site.includes(
                            this.search.toLocaleUpperCase()
                        );
                    });
                }
            }
        },
    },
    watch: {
        tab() {
            // we throttle the call in case people click too much
            if (this.throttleTimer) {
                clearTimeout(this.throttleTimer);
            }
            this.throttleTimer = setTimeout(() => {
                this.getData();
            });
        },
    },
    mounted() {
        this.getData();
    },
    methods: {
        getData() {
            this.loading = true;
            window.axios
                .get("/api/siteOpening/?" + this.tab + "=1")
                .then((response) => {
                    console.log(response.data);
                    this.PA = response.data;
                    this.loading = false;
                });
        },
        showExcelDownloadMessage() {
            // alert ("Download excel is in construction !!! Thank you for your patient")
            setTimeout(() => {
                this.dialog = true;
            }, 50);
        },
        downloadImages(id) {
            axios
                .get("/api/siteSelection/donwloadPicture?sample_id=" + id, {
                    responseType: "blob",
                })
                .then((response) => {
                    console.log("success");
                    const url = URL.createObjectURL(
                        new Blob([response.data], {
                            type: "application/zip",
                        })
                    );
                    // console.log(response.data)
                    const link = document.createElement("a");
                    link.href = url;
                    link.setAttribute("download", ".zip");
                    document.body.appendChild(link);
                    link.click();
                    link.remove();
                });
        },
        printExcel(type) {
            window.axios
                .get("/api/sampleExcelSiteOpenOrSiteSelection?type=" + type, {
                    responseType: "blob",
                })
                .then((response) => {
                    const url = URL.createObjectURL(
                        new Blob([response.data], {
                            type: "application/vnd.ms-excel",
                        })
                    );
                    console.log(response.data);
                    const link = document.createElement("a");
                    link.href = url;
                    link.setAttribute("download", type + ".xlsx");
                    document.body.appendChild(link);
                    link.click();
                    link.remove();
                });
        },
    },
};
</script>

<style>
.waiting {
    color: red;
    font-weight: bold;
}

.validated {
    color: orange;
    font-weight: bold;
}

.advanced {
    color: green;
    font-weight: bold;
}

.expense_validated {
    color: #666666;
    font-weight: bold;
}
</style>
