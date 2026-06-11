<template>
    <v-card class="ma-4">
        <v-card-text v-if="loading" class="d-flex justify-center mt-10">
            <v-progress-circular indeterminate :size="60" color="primary" />
        </v-card-text>
        <v-card-text v-else>
            <div class="d-flex flex-row align-center mb-3">
                <v-select v-model="selectedHeader" :items="possibleHeaders" label="Columns to display" density="compact"
                    class="mr-3" multiple hide-details />
                <v-text-field v-model="search" density="compact" label="Search" hide-details clearable class="shrink"
                    prepend-inner-icon="mdi-clipboard-text-search" />
                <!-- <v-btn v-if="user.permissions.includes('site_edit')" class="mx-1" color="primary" icon
            @click="openSiteForm({}, {})">
            <v-icon icon="mdi-water-well" />
            <v-tooltip activator="parent" location="start">
              Create a new site
            </v-tooltip>
          </v-btn> -->
                <v-btn v-if="user.permissions.includes('site_edit')" class="mx-1" color="red" icon
                    @click="openModalImport()">
                    <v-icon icon="mdi-arrow-up-bold-box-outline" />
                    <v-tooltip activator="parent" location="top">
                        Import KPI
                    </v-tooltip>
                </v-btn>
                <v-btn v-if="user.permissions.includes('site_edit')" class="mx-1" color="blue" icon
                    @click="openModalImportTraining()">
                    <v-icon icon="mdi-cloud-upload" />
                    <v-tooltip activator="parent" location="top">
                        Import Training
                    </v-tooltip>
                </v-btn>
                <v-btn v-if="user.permissions.includes('site_edit')" class="mx-1" color="blue" icon
                    @click="openModalImportPA()">
                    <v-icon icon="mdi-cloud-upload" />
                    <v-tooltip activator="parent" location="top">
                        Import PA
                    </v-tooltip>
                </v-btn>
                <v-btn v-if="user.permissions.includes('site_edit')" class="mx-1" color="yellow" icon
                    @click="openModalSiteAssessment()">
                    <v-icon icon="mdi-alert" />
                    <v-tooltip activator="parent" location="top">
                        Site Assessment
                    </v-tooltip>
                </v-btn>
                <v-btn v-if="user.permissions.includes('site_edit')" class="mx-1" color="green" icon
                    @click="openModalSiteRountine()">
                    <v-icon icon="mdi-ambulance" />
                    <v-tooltip activator="parent" location="top">
                        Invoice
                    </v-tooltip>
                </v-btn>
                <v-btn v-if="user.permissions.includes('site_edit')" class="mx-1" color="green" icon
                    @click="openModalTechnicianSite()">
                    <v-icon icon="mdi-ambulance" />
                    <v-tooltip activator="parent" location="top">
                        Technician Site
                    </v-tooltip>
                </v-btn>
            </div>
            <v-data-table v-model:items-per-page="itemsPerPage" :headers="headers" :items="filteredSites"
                density="compact" @click:row="openSiteForm" />
        </v-card-text>
    </v-card>
    <v-dialog v-model="showForm" transition="dialog-bottom-transition" width="80vw">
        <SiteForm :site="selectedSite" @site-saved="getSites()" />
    </v-dialog>
    <v-dialog v-model="showModalImport" transition="dialog-bottom-transition" width="600px">
        <v-card :loading="importing" class="mx-auto pa-12 w-100">
            <v-file-input v-model="file"
                accept="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet, application/vnd.ms-excel"
                label="Select an excel file to import" hide-details />
            <a href="/api/sites/template" class="text-button py-3 text-right" download></a>
            <v-btn class="mx-1" color="secondary" @click="importExcel('analyse')">
                KPI Import
            </v-btn>
            
        </v-card>
    </v-dialog>
    <v-dialog v-model="showModalImportTraning" transition="dialog-bottom-transition" width="600px">
        <v-card :loading="importing" class="mx-auto pa-12 w-100">
            <v-file-input v-model="file"
                accept="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet, application/vnd.ms-excel"
                label="Select an excel file to import" hide-details />
            <br />
            <v-btn class="ma-2" color="primary" @click="importExcelTraining('analyse')">
                Import
                <v-icon dark right> mdi-checkbox-marked-circle </v-icon>
            </v-btn>
        </v-card>
    </v-dialog>
    <v-dialog v-model="showModalImportPA" transition="dialog-bottom-transition" width="600px">
        <v-card :loading="importing" class="mx-auto pa-12 w-100">
            <v-file-input v-model="file"
                accept="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet, application/vnd.ms-excel"
                label="Select an excel file to import" hide-details />
            <br />
            <v-btn class="ma-2" color="primary" @click="importExcelPA('analyse')">
                Import PA
                <v-icon dark right> mdi-checkbox-marked-circle </v-icon>
            </v-btn>
        </v-card>
    </v-dialog>
    <!-- Import Technician Site -->
     <v-dialog v-model="showModalTechnicianSite" transition="dialog-bottom-transition" width="600px">
        <v-card :loading="importing" class="mx-auto pa-12 w-100">
            <v-file-input v-model="file"
                accept="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet, application/vnd.ms-excel"
                label="Select an excel file to import" hide-details />
            <br />
            <v-btn class="ma-2" color="primary" @click="importTechnicianSite('analyse')">
                Import Technician Site
                <v-icon dark right> mdi-checkbox-marked-circle </v-icon>
            </v-btn>
        </v-card>
    </v-dialog>
    <!-- Import Site Assessment  -->
    <v-dialog v-model="showModalSiteAssessment" transition="dialog-bottom-transition" width="600px">
        <v-card :loading="importing" class="mx-auto pa-12 w-100">
            <v-file-input v-model="file"
                accept="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet, application/vnd.ms-excel"
                label="Select an excel file to import" hide-details />
            <br />
            <v-btn class="ma-2" color="primary" @click="importSiteAssessment('analyse')">
                Site Assessment
                <v-icon dark right> mdi-checkbox-marked-circle </v-icon>
            </v-btn>
        </v-card>
    </v-dialog>
    <v-dialog v-model="showModalSiteRountine" transition="dialog-bottom-transition" width="600px">
        <v-card :loading="importing" class="mx-auto pa-12 w-100">
            <v-file-input v-model="file"
                accept="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet, application/vnd.ms-excel"
                label="Select an excel file to import" hide-details />
            <br />
            <v-btn class="ma-2" color="primary" @click="importSiteRountine('analyse')">
                Import Invoices
                <v-icon dark right> mdi-checkbox-marked-circle </v-icon>
            </v-btn>
        </v-card>
    </v-dialog>
</template>

<script>
import SiteForm from "../sites/SiteForm.vue";
import Swal from "sweetalert2";
export default {
    name: "SiteHome",
    components: {
        SiteForm,
    },
    data: function () {
        return {
            loading: true,
            importing: false,
            sites: [],
            selectedSite: {},
            itemsPerPage: 15,
            analyseResult: null,
            showForm: false,
            showModalImport: false,
            showModalImportTraning: false,
            showModalImportPA: false,
            showModalSiteAssessment: false,
            showModalSiteRountine: false,
            showModalTechnicianSite: false,
            file: null,
            search: "",
            headers: [
                { title: "Site", align: "start", key: "Id_Site" },
                { title: "Platform", align: "start", key: "Platform" },
                { title: "Advisor", align: "start", key: "Advisor" },
            ],
            possibleHeaders: [],
            selectedHeader: ["Id_Site", "Platform", "Advisor"],
        };
    },
    computed: {
        filteredSites() {
            if (this.search == "") {
                return this.sites;
            } else {
                return this.sites.filter((m) =>
                    (m.Id_Site + m.Platform + m.Province + m.Advisor).includes(
                        this.search
                    )
                );
            }
        },
        user() {
            return this.$store.state.user;
        },
    },
    watch: {
        selectedHeader() {
            this.headers.splice(0, this.headers.length);
            this.selectedHeader.forEach((col) =>
                this.headers.push({ title: col, align: "start", key: col })
            );
        },
    },
    mounted() {
        this.getSites();
    },
    methods: {
        getSites() {
            this.loading = true;
            this.showForm = false;
            window.axios.get("/api/sites?siteAdmin=1").then((response) => {
                this.sites = response.data;
                const cols = Object.keys(this.sites[0]);
                cols.forEach((column) => {
                    this.possibleHeaders.push({
                        title: column,
                        align: "start",
                        key: column,
                    });
                });
                this.loading = false;
            });
        },
        openSiteForm(evt, data) {
            this.showForm = true;
            this.selectedSite = data.item.raw;
        },
        openModalImport() {
            this.showModalImport = true;
        },
        openModalImportTraining() {
            this.showModalImportTraning = true;
        },
        openModalImportPA() {
            this.showModalImportPA = true;
        },
        openModalSiteAssessment() {
            this.showModalSiteAssessment = true;
        },
        openModalSiteRountine() {
            this.showModalSiteRountine = true;
        },
        openModalTechnicianSite() {
            this.showModalTechnicianSite = true;
        },
        importExcel(mode) {
            this.showModalImport = true;
            let formData = new FormData();
            let fileToUpload = Array.isArray(this.file) ? this.file[0] : this.file;
    
    formData.append("file", fileToUpload);
   
            window.axios
                .post("/api/kpi", formData, {
                    headers: {
                        "Content-Type": "multipart/form-data",
                    },
                })
                .then((response) => {
                    this.showModalImport = false;
                    Swal.fire({
                        icon: "success",
                        title: "Import KPI Successfully",
                        text:
                            "created " +
                            response.data.created +
                            " users and updated " +
                            response.data.updated +
                            " users",
                    });
                })
                .catch((error) => {
                    console.error(error);
                    this.importing = false;
                });
        },
        importExcelTraining(mode) {
            this.importing = true;
            let formData = new FormData();
            formData.append("file", this.file[0]);
            window.axios
                .post("/api/trainingImport", formData, {
                    headers: {
                        "Content-Type": "multipart/form-data",
                    },
                })
                .then((response) => {
                    console.log(response);
                    this.importing = false;
                })
                .catch((error) => {
                    console.error(error);
                    this.importing = false;
                });
        },
        importExcelPA(mode) {
            this.importing = true;
            let formData = new FormData();
            formData.append("file", this.file[0]);
            window.axios
                .post("/api/saleobjection", formData, {
                    headers: {
                        "Content-Type": "multipart/form-data",
                    },
                })
                .then((response) => {
                    console.log(response);
                    this.importing = false;
                })
                .catch((error) => {
                    console.error(error);
                    this.importing = false;
                });
        },
        importTechnicianSite(mode) {
    this.importing = true;
    let formData = new FormData();
    
    // Handle both single file and file array
    let fileToUpload = Array.isArray(this.file) ? this.file[0] : this.file;
    
    if (!fileToUpload) {
        console.error("No file selected");
        this.importing = false;
        return;
    }
    
    formData.append("file", fileToUpload);
    
    window.axios
        .post("/api/uploadSiteTechnician", formData, {
            headers: {
                "Content-Type": "multipart/form-data",
            },
        })
        .then((response) => {
            console.log(response);
            this.importing = false;
            this.showModalTechnicianSite = false; // Close modal on success
            this.file = null; // Clear file input
        })
        .catch((error) => {
            console.error(error);
            this.importing = false;
        });
},
        importSiteRountine(mode) {
            this.importing = true;
            let formData = new FormData();
            let fileToUpload = Array.isArray(this.file) ? this.file[0] : this.file;
    
            if (!fileToUpload) {
                console.error("No file selected");
                this.importing = false;
                return;
            }
    
            formData.append("file", fileToUpload);
            //window.axios.post('/api/importSiteRountine', formData, {
            window.axios
                .post("/api/importInvoice", formData, {
                    headers: {
                        "Content-Type": "multipart/form-data",
                    },
                })
                .then((response) => {
                    console.log(response);
                    this.importing = false;
                })
                .catch((error) => {
                    console.error(error);
                    this.importing = false;
                });
        },
        importSiteAssessment(mode) {
            this.importing = true;
            let formData = new FormData();
            formData.append("file", this.file[0]);
            window.axios
                .post("/api/importSiteAssessment", formData, {
                    headers: {
                        "Content-Type": "multipart/form-data",
                    },
                })
                .then((response) => {
                    console.log(response);
                    this.importing = false;
                })
                .catch((error) => {
                    console.error(error);
                    this.importing = false;
                });
        },
        exportExcel() {
            window.axios
                .get("/api/sites/export", { responseType: "blob" })
                .then((response) => {
                    const url = URL.createObjectURL(
                        new Blob([response.data], {
                            type: "application/vnd.ms-excel",
                        })
                    );
                    const link = document.createElement("a");
                    link.href = url;
                    link.setAttribute(
                        "download",
                        "sites_" +
                        new Date().toISOString().substring(0, 10) +
                        ".xlsx"
                    );
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
