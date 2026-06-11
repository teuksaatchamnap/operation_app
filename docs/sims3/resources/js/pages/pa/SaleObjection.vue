<template>
    <v-card class="ma-4">
        <v-card-text v-if="loading" class="d-flex justify-center mt-10">
            <v-progress-circular indeterminate :size="60" color="primary" />
        </v-card-text>
        <v-card-text v-else>
            <div class="d-flex flex-row align-center mb-3">
                <v-text-field
                    v-model="search"
                    density="compact"
                    label="Search"
                    hide-details
                    clearable
                    class="shrink"
                    prepend-inner-icon="mdi-clipboard-text-search"
                />

                <v-btn
                    v-if="user.permissions.includes('site_edit')"
                    class="mx-1"
                    color="red"
                    icon
                    @click="openModalImport()"
                >
                    <v-icon icon="mdi-arrow-up-bold-box-outline" />
                    <v-tooltip activator="parent" location="top">
                        Import Objection
                    </v-tooltip>
                </v-btn>
                <v-btn
                    v-if="user.permissions.includes('site_edit')"
                    class="mx-1"
                    color="blue"
                    icon
                    @click="openModalImportTraining()"
                >
                    <v-icon icon="mdi-cloud-upload" />
                    <v-tooltip activator="parent" location="top">
                        Import site selection
                    </v-tooltip>
                </v-btn>
                <v-btn
                    v-if="user.permissions.includes('site_edit')"
                    class="mx-1"
                    color="blue"
                    icon
                    @click="openTechnician()"
                >
                    <v-icon icon="mdi-cloud-upload" />
                    <v-tooltip activator="parent" location="top">
                        Edit Technician Site
                    </v-tooltip>
                </v-btn>
                <!-- <v-btn class="mx-1" color="secondary" icon @click="exportExcel()">
            <v-icon icon="mdi-table-arrow-down" />
            <v-tooltip activator="parent" location="top">
              Export all sites as Excel
            </v-tooltip>
          </v-btn> -->
            </div>
            <v-data-table
                v-model:items-per-page="itemsPerPage"
                :headers="headers"
                :items="filteredSites"
                density="compact"
            >
                <template #item.answer="{ item }">
                    <span v-if="item.answer && item.answer.length < 40">{{
                        item.answer
                    }}</span>
                    <span v-else="item.answer">
                        {{ item.answer.substring(0, 80) }}
                        <v-tooltip :text="item.answer" location="top">
                            <template #activator="{ props }">
                                <v-btn
                                    v-bind="props"
                                    density="compact"
                                    icon="mdi-dots-horizontal"
                                />
                            </template>
                        </v-tooltip>
                    </span>
                </template>
                <template #item.detail="{ item }">
                    <v-chip
                        size="small"
                        color="primary"
                        @click.prevent="detailInfo(item)"
                    >
                        <v-icon start size="x-small" />ចំលើយលំអិត
                    </v-chip>
                </template>
            </v-data-table>
        </v-card-text>
    </v-card>
    <!-- SHOW detail answer-->

    <div class="text-xs-center">
        <v-dialog v-model="dialog" width="500">
            <v-card>
                <v-card-title class="headline grey lighten-2" primary-title>
                    ចំលើយ :
                </v-card-title>

                <v-card-text>
                    {{ detail.raw.answer }}
                </v-card-text>

                <v-divider></v-divider>

                <v-card-actions>
                    <v-spacer></v-spacer>
                    <v-btn color="primary" flat @click="dialog = false">
                        OK
                    </v-btn>
                </v-card-actions>
            </v-card>
        </v-dialog>
    </div>

    <v-dialog
        v-model="showForm"
        transition="dialog-bottom-transition"
        width="80vw"
    >
        <SiteForm :site="selectedSite" @site-saved="getSites()" />
    </v-dialog>
    <v-dialog
        v-model="showModalImport"
        transition="dialog-bottom-transition"
        width="600px"
    >
        <v-card :loading="importing" class="mx-auto pa-12 w-100">
            <v-file-input
                v-model="file"
                accept="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet, application/vnd.ms-excel"
                label="Select an excel file to import"
                hide-details
            />
            <a
                href="/api/sites/template"
                class="text-button py-3 text-right"
                download
                >Download template</a
            >
            <v-btn
                class="mx-1"
                color="secondary"
                @click="importExcel('analyse')"
            >
                Analyse file
            </v-btn>
            <div v-if="analyseResult != null" class="pa-2">
                <p class="py-2">
                    This file will create
                    {{ analyseResult.created.length }} site(s).
                    <v-chip prepend-icon="mdi-playlist-plus">
                        List of created sites
                        <v-tooltip activator="parent" location="start">
                            {{
                                analyseResult.created
                                    .map((s) => s.Id_Site)
                                    .join(", ")
                            }}
                        </v-tooltip>
                    </v-chip>
                </p>
                <p class="py-2">
                    This file will update
                    {{ analyseResult.updated.length }} site(s).
                    <v-chip prepend-icon="mdi-playlist-edit">
                        List of updated sites
                        <v-tooltip activator="parent" location="start">
                            {{
                                analyseResult.updated
                                    .map((s) => s.Id_Site)
                                    .join(", ")
                            }}
                        </v-tooltip>
                    </v-chip>
                </p>
            </div>
            <v-btn
                v-if="analyseResult != null"
                class="mx-1"
                color="red"
                @click="importExcel('import')"
            >
                Import file
            </v-btn>
        </v-card>
    </v-dialog>
    <v-dialog
        v-model="showModalImportTraning"
        transition="dialog-bottom-transition"
        width="600px"
    >
        <v-card :loading="importing" class="mx-auto pa-12 w-100">
            <v-file-input
                v-model="file"
                accept="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet, application/vnd.ms-excel"
                label="Select an excel file to import"
                hide-details
            />
            <br />
            <v-btn
                class="ma-2"
                color="primary"
                @click="importExcelTraining('analyse')"
            >
                Import site selection
                <v-icon dark right> mdi-checkbox-marked-circle </v-icon>
            </v-btn>
        </v-card>
    </v-dialog>

    <v-dialog
        v-model="showModalTechnician"
        transition="dialog-bottom-transition"
        width="600px"
    >
        <v-card :loading="importing" class="mx-auto pa-12 w-100">
            <v-file-input
                v-model="file"
                accept="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet, application/vnd.ms-excel"
                label="Select an excel file to import"
                hide-details
            />
            <br />
            <v-btn
                class="ma-2"
                color="primary"
                @click="editTechnicianSite('analyse')"
            >
                Edit Technician Site
                <v-icon dark right> mdi-checkbox-marked-circle </v-icon>
            </v-btn>
        </v-card>
    </v-dialog>
</template>

<script>
// import { VDataTable } from 'vuetify/labs/VDataTable'
import SiteForm from "../sites/SiteForm.vue";
export default {
    name: "SiteHome",
    components: {
        
        SiteForm,
    },
    data: function () {
        return {
            loading: true,
            detail: {},
            dialog: false,
            importing: false,
            sites: [],
            selectedSite: {},
            itemsPerPage: 15,
            analyseResult: null,
            showForm: false,
            showModalImport: false,
            showModalImportTraning: false,
            showModalTechnician: false,
            file: null,
            search: "",
            headers: [
                { title: "សំណួរ", align: "start", key: "question", width: 500 },
                { title: "ចំលើយ", align: "start", key: "answer" },
                { title: "លំអិត", align: "start", key: "detail" },
            ],
        };
    },
    computed: {
        filteredSites() {
            if (this.search == "") {
                return this.sites;
            } else {
                return this.sites.filter((m) =>
                    (m.question + m.answer).includes(this.search)
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
            window.axios.get("/api/saleobjection").then((response) => {
                this.sites = response.data;
                console.log(this.sites);
                this.loading = false;
            });
        },
        openSiteForm(evt, data) {
            this.showForm = true;
            this.selectedSite = data.item;
        },
        detailInfo(i) {
            this.dialog = true;
            this.detail = i;
            console.log(this.detail);
        },
        openModalImport() {
            this.showModalImport = true;
        },
        openModalImportTraining() {
            this.showModalImportTraning = true;
        },
        openTechnician() {
            this.showModalTechnician = true;
        },
        importExcel(mode) {
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
        editTechnicianSite(mode) {
            this.importing = true;
            let formData = new FormData();
            formData.append("file", this.file[0]);
            window.axios
                .post("/api/editTechnicianSite", formData, {
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
