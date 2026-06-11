<template>
    <v-btn icon="mdi-arrow-left-bold-circle" color="blue" size="small"
        @click="$router.push({ path: '/quality' })"></v-btn>
    <v-card class="ma-3">
        <v-tabs v-model="tab" bg-color="green">
            <v-tab value="site_intervention"> Site Intervention </v-tab>
            <v-tab value="site_selection"> Site Selection </v-tab>
            <v-tab value="site_opening"> Site Re-Opening </v-tab>
            <v-tab value="external_test"> External Sampling </v-tab>
            <v-tab value="raw_water"> Raw Water </v-tab>
        </v-tabs>
        <v-card-text v-if="loading" class="d-flex justify-center mt-10">
            <v-progress-circular indeterminate :size="60" color="primary" />
        </v-card-text>
        <v-card-text v-else>
            <div v-if="tab == 'site_opening'">
                <div class="d-flex flex-row align-center mb-3">
                    <v-row>
                        <v-col cols="12" md="3">
                            <v-text-field v-model="startdate" type="date" density="compact" label="Start Date"
                                hide-details="auto" />
                        </v-col>
                        <v-col cols="12" md="3">
                            <v-text-field v-model="enddate" type="date" density="compact" label="End Date"
                                hide-details="auto" />
                        </v-col>
                        <v-col cols="12" md="2">
                            <v-btn class="ml-5 mt-2 mr-5" color="secondary" icon="mdi-microsoft-excel"
                                @click="printExcel('site_opening')" />
                        </v-col>
                    </v-row>
                    <v-text-field v-model="search" density="compact" label="Search" hide-details clearable
                        class="shrink" prepend-inner-icon="mdi-clipboard-text-search" />
                </div>
                <!-- show data -->
                <v-data-table v-model:items-per-page="itemsPerPage" :headers="headersSiteOpening" :items="filterPA"
                    density="compact" item-value="sample_date" class="pa-4">
                    <template #item.actions="{ item }">
                        <v-chip color="blue" @click="showExcelDownloadMessage(item)">Detail</v-chip>
                    </template>
                    <template #item.print="{ item }">
                        <v-chip @click="printCertificate(item.id)">
                            <v-icon size="large" color="blue" icon="mdi-cloud-print" />
                        </v-chip>
                    </template>
                </v-data-table>
            </div>
            <div v-if="tab == 'site_selection'">
                <div class="d-flex flex-row align-center mb-3">
                    <v-row>
                        <v-col cols="12" md="3">
                            <v-text-field v-model="startdate" type="date" density="compact" label="Start Date"
                                hide-details="auto" />
                        </v-col>
                        <v-col cols="12" md="3">
                            <v-text-field v-model="enddate" type="date" density="compact" label="End Date"
                                hide-details="auto" />
                        </v-col>
                        <v-col cols="12" md="2">
                            <v-btn class="ml-5 mt-2 mr-5" color="secondary" icon="mdi-microsoft-excel"
                                @click="printExcel('Site_Selection')" />
                        </v-col>
                    </v-row>
                    <v-text-field v-model="search" density="compact" label="Search" hide-details clearable
                        class="shrink" prepend-inner-icon="mdi-clipboard-text-search" />
                </div>
                <!-- show data -->
                <v-data-table v-model:items-per-page="itemsPerPage" :headers="headersSiteSelection" :items="filterPA"
                    density="compact" item-value="sample_date" class="pa-4">
                    <template #item.actions="{ item }">
                        <!-- <v-chip v-if="item.site_open_final_judgement == '' || item.site_open_final_judgement == null"  color="blue"
                     @click="showExcelDownloadMessage(item)">Detail</v-chip> -->
                        <v-chip color="blue" @click="showExcelDownloadMessage(item)">Detail</v-chip>
                    </template>
                    <template #item.document="{ item }">
                        <v-chip @click="downloadImages(item.id)">
                            <v-icon size="large" icon="mdi-cloud-download" />
                        </v-chip>
                    </template>
                    <!-- <template #item.print="{ item }">
                    <v-chip @click="printCertificate(item.id)">
                        <v-icon size="large" color="blue" icon="mdi-cloud-print"  />
                    </v-chip>
                </template> -->
                </v-data-table>
            </div>
            <div v-if="tab == 'site_intervention'">
                <div class="d-flex flex-row align-center mb-3">
                    <v-row>
                        <v-col cols="12" md="3">
                            <v-text-field v-model="startdate" type="date" density="compact" label="Start Date"
                                hide-details="auto" />
                        </v-col>
                        <v-col cols="12" md="3">
                            <v-text-field v-model="enddate" type="date" density="compact" label="End Date"
                                hide-details="auto" />
                        </v-col>
                        <v-col cols="12" md="2">
                            <v-btn class="ml-5 mt-2 mr-5" color="secondary" icon="mdi-microsoft-excel"
                                @click="printExcel('site_intervention')" />
                        </v-col>
                    </v-row>
                    <v-text-field v-model="search" density="compact" label="Search" hide-details clearable
                        class="shrink" prepend-inner-icon="mdi-clipboard-text-search" />
                </div>
                <!-- show data -->
                <v-data-table v-model:items-per-page="itemsPerPage" :headers="headersSiteOpening" :items="filterPA"
                    density="compact" item-value="sample_date" class="pa-4">
                    <template #item.actions="{ item }">
                        <!-- <v-chip v-if="item.site_open_final_judgement == '' || item.site_open_final_judgement == null " size="small" color="green"  @click="$router.push({ path: '/quality/sample/' + item.id })">
                        <v-icon start size="x-small" icon="mdi-apple-keyboard-shift" />Detail
                    </v-chip> -->
                        <v-chip color="blue" @click="showExcelDownloadMessage(item)">Detail</v-chip>
                    </template>
                </v-data-table>
            </div>
            <div v-if="tab == 'external_test'">
                <div class="d-flex flex-row align-center mb-3">
                    <v-row>
                        <v-col cols="12" md="2">
                            <v-btn class="mx-2" fab dark small color="blue" @click="
                                $router.push({
                                    path: '/quality/ExternalSample',
                                })
                                ">
                                <v-icon dark>mdi-pencil</v-icon> ADD
                            </v-btn>
                        </v-col>
                        <v-text-field v-model="search" density="compact" label="Search" hide-details clearable
                        class="shrink" prepend-inner-icon="mdi-clipboard-text-search" />
                    </v-row>
                </div>
                <!-- show data -->
                <v-data-table v-model:items-per-page="itemsPerPage" :headers="headersExternal" :items="filterPA"
                    density="compact" item-value="site" class="pa-4">
                    <template #item.download="{ item }">
                        <v-chip @click="downloadFileExternal(item.upload_path)">
                            <v-icon size="large" icon="mdi-cloud-download" />
                        </v-chip>
                    </template>
                    <template #item.modify="{ item }">
                        <v-chip @click="deleteExternalSample(item.id)" color="green">
                            Delete
                        </v-chip>
                    </template>
                </v-data-table>
            </div>
            <div v-if="tab == 'raw_water'">
                <div class="d-flex flex-row align-center mb-3">
                    <v-row>
                        <v-col cols="12" md="3">
                            <v-text-field v-model="startdate" type="date" density="compact" label="Start Date"
                                hide-details="auto" />
                        </v-col>
                        <v-col cols="12" md="3">
                            <v-text-field v-model="enddate" type="date" density="compact" label="End Date"
                                hide-details="auto" />
                        </v-col>
                        <v-col cols="12" md="2">
                            <v-btn class="ml-5 mt-2 mr-5" color="secondary" icon="mdi-microsoft-excel"
                                @click="printExcel('Raw_Water')" />
                        </v-col>
                    </v-row>
                    <v-text-field v-model="search" density="compact" label="Search" hide-details clearable
                        class="shrink" prepend-inner-icon="mdi-clipboard-text-search" />
                </div>
                <!-- show data -->
                <v-data-table v-model:items-per-page="itemsPerPage" :headers="headersRawWater" :items="filterPA"
                    density="compact" item-value="site" class="pa-4">
                    <template #item.actions="{ item }">
                        <!-- <v-chip v-if="item.site_open_final_judgement == '' || item.site_open_final_judgement == null " size="small" color="green"  @click="$router.push({ path: '/quality/sample/' + item.id })">
                        <v-icon start size="x-small" icon="mdi-apple-keyboard-shift" />Detail
                    </v-chip> -->
                        <v-chip color="blue" @click="showExcelDownloadMessage(item)">Detail</v-chip>
                    </template>
                    <template #item.created_at="{ item }">
                        {{ formatDateRawWater(item.created_at) }}
                    </template>
                </v-data-table>
            </div>
        </v-card-text>
    </v-card>
    <div class="text-center">
        <v-dialog v-model="dialog" activator="parent" width="auto">
            <v-card>
                <!-- <v-card-text>
                    Excel is {{ selectedItem.id }}
                </v-card-text>
                <v-card-actions>
                    <v-btn color="primary" block @click=" dialog = false">Close</v-btn>
                </v-card-actions> -->
                <DialogForm :getData="selectedItem.id" @cancel-modal="dialog = false"></DialogForm>
            </v-card>
        </v-dialog>
    </div>
</template>

<script>
// import { VDataTable } from 'vuetify/labs/VDataTable'
import { formToJSON } from "axios";
import DialogForm from "./DialogForm.vue";
export default {
    name: "HomeSite",
    components: {

        DialogForm,
    },
    data: function () {
        return {
            open: false,
            startdate: "",
            enddate: "",
            position: "",
            positionData: [],
            dialog: false,
            loading: true,
            PA: [],
            selectedItem: null,
            itemsPerPage: 15,
            search: "",
            tab: "Site_Opening",
            throttleTimer: -1,
            headersSiteOpening: [
                { title: "Action", align: "center", key: "actions" },
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
                { title: "Print", align: "center", key: "print" },
            ],
            headersSiteSelection: [
                { title: "Action", align: "center", key: "actions" },
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
                { title: "Print", align: "center", key: "print" },
            ],
            headersRawWater: [
                { title: "Action", align: "center", key: "actions" },
                {
                    title: "Site",
                    align: "start",
                    key: "site.Id_Site",
                    width: 30,
                    sortable: true,
                },
                {
                    title: "Platform",
                    align: "start",
                    key: "site.Platform",
                    width: 30,
                    sortable: true,
                },
                {
                    title: "Date",
                    align: "center",
                    key: "created_at",
                    width: 110,
                },
                {
                    title: "Sample Type",
                    align: "center",
                    key: "site_open_sample_type",
                    width: 50,
                },
                { title: "pH", align: "center", key: "ph" },
                { title: "Turbidity", align: "center", key: "turbidity" },
                { title: "Cond", align: "center", key: "conductivity" },
                { title: "TDS", align: "center", key: "tds" },
                { title: "Print", align: "center", key: "print" },
            ],
            headersExternal: [
                {
                    title: "Site",
                    align: "start",
                    key: "site",
                    width: 30,
                    sortable: true,
                },
                {
                    title: "Test Date",
                    align: "start",
                    key: "test_date",
                    width: 30,
                    sortable: true,
                },
                {
                    title: "Result",
                    align: "center",
                    key: "download",
                    width: 310,
                },
                { title: "Modify", align: "center", key: "modify", width: 310 },
            ],
        };
    },
    computed: {
        filterPA() {
            if (this.tab == "site_intervention") {
                return this.PA.filter((item) => {
                    // Filter by date range
                    const sampleDate = new Date(item.site_open_sample_date);
                    const isAfterStartDate = this.startdate
                        ? sampleDate >= new Date(this.startdate)
                        : true;
                    const isBeforeEndDate = this.enddate
                        ? sampleDate <= new Date(this.enddate)
                        : true;

                    // Filter by site name (case-insensitive)
                    const matchesSite = this.search
                        ? item.site
                            .toLowerCase()
                            .includes(this.search.toLowerCase())
                        : true;

                    return isAfterStartDate && isBeforeEndDate && matchesSite;
                });
            } else if (this.tab == "site_selection" || this.tab == "site_opening") {
                // if (this.search == "") {
                //     return this.PA
                // } else {
                //     return this.PA.filter(item => {
                //       return item.sample_code.toString().includes(this.search);
                //                 });
                // }

                return this.PA.filter((item) => {
                    // Filter by date range
                    const sampleDate = new Date(item.site_open_sample_date);
                    const isAfterStartDate = this.startdate
                        ? sampleDate >= new Date(this.startdate)
                        : true;
                    const isBeforeEndDate = this.enddate
                        ? sampleDate <= new Date(this.enddate)
                        : true;

                    // Filter by site name (case-insensitive)
                    const sample_code = this.search
                        ? item.sample_code
                            .toString()
                            .includes(this.search.toLowerCase())
                        : true;
                    const sample_by = this.search
                        ? item.site_open_sample_by &&
                        item.site_open_sample_by &&
                        item.sample_en_location
                            .toLowerCase()
                            .includes(this.search.toLowerCase())
                        : true;
                    return (
                        isAfterStartDate &&
                        isBeforeEndDate &&
                        (sample_code || sample_by)
                    );

                    //  return isAfterStartDate && isBeforeEndDate && sample_code;
                });
            } else if (this.tab == "raw_water") {
                return this.PA.filter((item) => {
                    const sampleDate = new Date(item.created_at);
                    const isAfterStartDate = this.startdate ? sampleDate >= new Date(this.startdate) : true;
                    const isBeforeEndDate  = this.enddate   ? sampleDate <= new Date(this.enddate)   : true;

                    const matchesSite = this.search
                        ? (item.site?.Id_Site ?? '').toLowerCase().includes(this.search.toLowerCase())
                          || (item.site?.Platform ?? '').toLowerCase().includes(this.search.toLowerCase())
                        : true;

                    return isAfterStartDate && isBeforeEndDate && matchesSite;
                });
            }
            else if (this.tab == "external_test") {
                if (this.search == "") {
                    return this.PA
                } else {
                    return this.PA.filter(item => {
                      return item.site.includes(this.search.toLocaleUpperCase());
                                });
                }

                // return this.PA.filter((item) => {
                //     // Filter by date range
                //     const sampleDate = new Date(item.site_open_sample_date);
                //     const isAfterStartDate = this.startdate
                //         ? sampleDate >= new Date(this.startdate)
                //         : true;
                //     const isBeforeEndDate = this.enddate
                //         ? sampleDate <= new Date(this.enddate)
                //         : true;

                //     // Filter by site name (case-insensitive)
                //     const matchesSite = this.search
                //         ? item.site
                //             .toLowerCase()
                //             .includes(this.search.toLowerCase())
                //         : true;

                //     return isAfterStartDate && isBeforeEndDate && matchesSite;
                // });
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
            this.startdate = "";
            this.enddate = "";
            this.search = "";
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
        formatDateRawWater (dateString) {
    return dateString.slice(0, 10)
},
        printCertificate(id) {
            const i = id;
            this.$router.push({
                path: "/labCertificate",
                query: {
                    id: i,
                },
            });
        },
        deleteExternalSample(id) {
            const con = confirm("Are you sure you want to delete");
            if (con) {
                window.axios
                    .delete("/api/deleteExternalSample/" + id)
                    .then((response) => {
                        console.log(response.data.message);
                        this.getData();
                        this.loading = false;
                    });
            }
        },
        showExcelDownloadMessage(item) {
            //alert ("Your Item :" + item.id)
            setTimeout(() => {
                this.selectedItem = item;
                this.dialog = true;
            }, 50);
        },
        downloadImages(id) {
            axios.get("/api/siteSelection/donwloadPicture?sample_id=" + id, {
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
        downloadFileExternal(filePath) {
            const filename = filePath.split("/").pop();
            axios.get("/api/downloadFile/" + filename, { responseType: "blob" })
                .then((response) => {
                    console.log("success");
                    const url = URL.createObjectURL(new Blob([response.data]));
                    // console.log(response.data)
                    const link = document.createElement("a");
                    link.href = url;
                    link.setAttribute("download", filePath.split("/").pop());
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
        // downloadFile(filePath) {
        //     // Create a temporary link to trigger the download
        //     const link = document.createElement('a');
        //     link.href = `storage/${filePath}`; // Replace with your actual file path or URL
        //     link.download = 'document'; // Replace with the desired filename
        //     document.body.appendChild(link);
        //     link.click();
        //     document.body.removeChild(link);
        // }
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
