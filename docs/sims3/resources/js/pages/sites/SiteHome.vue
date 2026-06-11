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
                <v-btn v-if="user.permissions.includes('site_edit')" class="mx-1" color="primary" icon
                    @click="openSiteForm(false, false)">
                    <v-icon icon="mdi-water-well" />
                    <v-tooltip activator="parent" location="start">
                        Create a new site
                    </v-tooltip>
                </v-btn>
                <v-btn v-if="user.permissions.includes('site_edit')" class="mx-1" color="red" icon
                    @click="openModalImport()">
                    <v-icon icon="mdi-application-import" />
                    <v-tooltip activator="parent" location="top">
                        Import sites from Excel file
                    </v-tooltip>
                </v-btn>
                <v-btn class="mx-1" color="secondary" icon @click="exportExcel()">
                    <v-icon icon="mdi-table-arrow-down" />
                    <v-tooltip activator="parent" location="top">
                        Export all sites as Excel
                    </v-tooltip>
                </v-btn>
                <v-btn v-if="user.permissions.includes('edit_permissions')" class="mx-1" color="green" icon
                    @click="$router.push({ path: '/contractSite' })">
                    <v-icon icon="mdi-cloud-upload" />
                    <v-tooltip activator="parent" location="top">
                        Upload Commune & training contracts
                    </v-tooltip>
                </v-btn>
            </div>
            <v-data-table v-model:items-per-page="itemsPerPage" :headers="headers" :items="filteredSites"
                density="compact" @click:row="openSiteForm">
                <!-- <template #item.Contract="{ item }">
          <template v-if="item.site_contract">
            <v-chip @click="downloadFile(item.site_contract.path)">
              <v-icon size="large" icon="mdi-cloud-download" />
            </v-chip>
          </template>
</template> -->
                <template #item.Entrepreneur_English_Name="{ item }">
                    <v-menu>
                        <template #activator="{ props }">
                            <v-btn v-bind="props" variant="text" color="primary" size="small" icon>
                                {{ item.Entrepreneur_English_Name }}
                            </v-btn>
                        </template>
                        <v-list>
                            <v-list-item title="Show All Entrepreneur" prepend-icon="mdi-file-document-outline"
                                @click="$router.push({ path: '/entrepreneur' })" />
                            <v-list-item title="Show Entrepreneur only this site " prepend-icon="mdi-account" @click="
                                $router.push({
                                    path:
                                        '/newEntrepreneur/detail/' +
                                        item.Id_Site,
                                })
                                " />
                        </v-list>
                    </v-menu>
                </template>

                <template #item.Contract="{ item }">
                    <v-menu>
                        <template #activator="{ props }">
                            <v-btn v-if="
                                item.site_contract &&
                                (item.site_contract.commune_contract ||
                                    item.site_contract.training_contract)
                            " v-bind="props" variant="text" color="primary" size="small" icon>
                                <v-icon size="large" icon="mdi-cloud-download" color="green" />
                            </v-btn>
                        </template>
                        <v-list>
                            <!-- <v-list-item v-if="item.site_contract.commune_picture" @click="downloadFileCommuneContract(item.site_contract.commune_picture)" title="Commune Contract"
                prepend-icon="mdi-file-document-outline" :loading="loading"/> -->
                            <v-list-item title="Commune Contract" prepend-icon="mdi-file-document-outline"
                                :loading="loading" @click="
                                    downloadFileCommuneContract(
                                        item.site_contract.commune_contract
                                    )
                                    " />
                            <v-list-item title="Training Contract" prepend-icon="mdi-account" @click="
                                downloadTrainingContract(
                                    item.site_contract.training_contract
                                )
                                " />
                        </v-list>
                    </v-menu>
                </template>
            </v-data-table>
        </v-card-text>
    </v-card>
    <v-dialog v-model="showForm" transition="dialog-bottom-transition" width="80vw">
        <SiteForm :site="selectedSite" @site-saved="getSites()" @cancel-modal="showForm = false" />
    </v-dialog>
    <v-dialog v-model="showModalImport" transition="dialog-bottom-transition" width="600px">
        <v-card :loading="importing" class="mx-auto pa-12 w-100">
            <v-file-input v-model="file"
                accept="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet, application/vnd.ms-excel"
                label="Select an excel file to import" hide-details />
            <a href="/api/sites/template" class="text-button py-3 text-right" download>Download template</a>
            <v-btn class="mx-1" color="secondary" @click="importExcel('analyse')">
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
            <v-btn v-if="analyseResult != null" class="mx-1" color="red" @click="importExcel('import')">
                Import file
            </v-btn>
        </v-card>
    </v-dialog>
    <v-snackbar v-model="snackbar" color="red">
        There was an error importing your excel file. Please contact Chamnap,
        Jonathan or Axel.
        <template #actions>
            <v-btn color="white" variant="text" @click="snackbar = false">
                Close
            </v-btn>
        </template>
    </v-snackbar>
</template>

<script>
// import { VDataTable } from 'vuetify/labs/VDataTable'
import SiteForm from "./SiteForm.vue";
import Swal from "sweetalert2";
export default {
    name: "SiteHome",
    components: {
        SiteForm,
    },
    data: function () {
        return {
            loading1: false,
            downloadProgress: 0,
            loading: true,
            importing: false,
            sites: [],
            selectedSite: {},
            itemsPerPage: 15,
            analyseResult: null,
            showForm: false,
            showModalImport: false,
            snackbar: false,
            file: null,
            loading: false,
            email: "",
            search: "",
            headers: [
                { title: "Site", align: "start", key: "Id_Site" },
                { title: "Platform", align: "start", key: "Platform" },
                // { title: 'Advisor', align: 'start', key: 'Advisor' },
                {
                    title: "Entrepreneur",
                    align: "start",
                    key: "Entrepreneur_English_Name",
                },
                { title: "Contract", align: "start", key: "Contract" },
            ],
            possibleHeaders: [],
            selectedHeader: [
                "Id_Site",
                "Platform",
                "Entrepreneur_English_Name",
                "Contract",
            ],
        };
    },
    computed: {
        filteredSites() {
            if (this.search == "") {
                return this.sites;
            } else {
                return this.sites.filter((m) =>
                    (
                        m.Id_Site +
                        m.Platform +
                        m.Province +
                        m.Advisor +
                        m.Khmer_advisor
                    )
                        .toLowerCase()
                        .includes(this.search.toLowerCase())
                );
            }
        },
        user() {
            if (this.$store.state.user.permissions[0] == "edit_permissions") {
                console.log("User has edit permissions");
            } else {
                console.log("User does not have edit permissions");
            }
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
                console.log(this.sites);
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
        async downloadFileCommuneContract(filePath) {
            this.loading1 = true;

            try {
                const fileName = filePath.split("/").pop();
                const response = await axios.get(
                    `/api/downloadCommuneContract/${fileName}`,
                    {
                        responseType: "blob",
                        onDownloadProgress: (progressEvent) => {
                            const percentCompleted = Math.round(
                                (progressEvent.loaded * 100) /
                                (progressEvent.total || 1)
                            );
                            console.log(
                                `Download progress: ${percentCompleted}%`
                            );
                            this.downloadProgress = percentCompleted;
                        },
                    }
                );

                const blob = new Blob([response.data], {
                    type: response.headers["content-type"],
                });
                const link = document.createElement("a");
                link.href = URL.createObjectURL(blob);
                link.download = fileName;
                link.click();

                Swal.fire(
                    "Success",
                    "File downloaded successfully!",
                    "success"
                );
            } catch (error) {
                console.error("Error downloading file:", error);
                Swal.fire("Error", "No file found", "error");
            } finally {
                this.loading1 = false;
                this.downloadProgress = 0;
            }
        },
        async downloadTrainingContract(filePath) {
            this.loading = true; // show loading spinner (you need data() { return { loading: false } })

            try {
                const fileName = filePath.split("/").pop();
                const response = await axios.get(
                    `/api/downloadCommuneContract/${fileName}`,
                    {
                        responseType: "blob",
                    }
                );

                const blob = new Blob([response.data], {
                    type: response.headers["content-type"],
                });
                const link = document.createElement("a");
                link.href = URL.createObjectURL(blob);
                link.download = fileName;
                link.click();

                // success message
                Swal.fire("File downloaded successfully!");
            } catch (error) {
                console.error("Error downloading file:", error);
                // error message
                Swal.fire("Sorry, There is no file found");
            } finally {
                this.loading = false; // hide loading spinner
            }
        },

        openSiteForm(evt, data) {
            this.showForm = true;
            if (data) {
                this.selectedSite = data.item;
            } else {
                this.selectedSite = {};
            }
        },
        openModalImport() {
            this.showModalImport = true;
        },
        importExcel(mode) {
            this.importing = true;
            let formData = new FormData();
            formData.append("file", this.file[0]);
            window.axios
                .post("/api/sites/importExcel?" + mode + "=1", formData, {
                    headers: {
                        "Content-Type": "multipart/form-data",
                    },
                })
                .then((response) => {
                    if (mode == "analyse") {
                        this.analyseResult = {
                            created: response.data.filter(
                                (s) => s._new == true
                            ),
                            updated: response.data.filter(
                                (s) => s._new == false
                            ),
                        };
                    } else {
                        this.showModalImport = false;
                        this.getSites();
                    }
                    this.importing = false;
                })
                .catch((error) => {
                    console.error(error);
                    this.importing = false;
                    this.snackbar = true;
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
