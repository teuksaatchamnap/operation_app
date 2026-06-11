<template>
    <div v-if="loading" class="d-flex justify-center mt-10">
        <v-progress-circular indeterminate :size="60" color="primary" />
    </div>
    <div v-else>

        <div class="d-flex flex-row align-center ma-3">
            <v-text-field v-model="selectedDate" density="compact" hide-details class="flex-grow-0 mr-5" label="Month"
                type="month" />
            <v-text-field v-model="search" density="compact" label="Search" hide-details clearable class="shrink"
                prepend-inner-icon="mdi-clipboard-text-search" />
            <v-btn class="ml-5 mt-2 mr-5" :class="{ 'rotate-button': loadingExcel }" color="secondary"
                :icon="loadingExcel ? 'mdi-loading' : 'mdi-microsoft-excel'" :disabled="loadingExcel"
                @click="exportExcel()" />
        </div>

        <v-data-table :items-per-page="25" :headers="headers" :items="filteredItems" density="compact" item-value="id"
            class="small-text">
            <template #item.receipt="{ item }">
                <v-btn
                    v-if="item.receipt && item.receipt.length"
                    size="x-small"
                    color="blue"
                    variant="tonal"
                    prepend-icon="mdi-receipt"
                    @click="openPreview(item.receipt[0], 'Receipt')"
                >
                    View
                </v-btn>
            </template>
            <template #item.pictures="{ item }">
                <v-btn
                    v-if="item.pictures && item.pictures.length"
                    size="x-small"
                    color="purple"
                    variant="tonal"
                    prepend-icon="mdi-qrcode"
                    @click="openPreview(item.pictures[0], 'QR Picture')"
                >
                    View
                </v-btn>
            </template>
            <template #item.school_pictures="{ item }">
                <v-btn
                    size="x-small"
                    color="teal"
                    variant="tonal"
                    prepend-icon="mdi-image-multiple"
                    :loading="schoolPictureLoading && schoolPictureSite === item.site"
                    @click="openSchoolPictures(item)"
                >
                    Photos
                </v-btn>
            </template>
        </v-data-table>

        <!-- ── SCHOOL PICTURES DIALOG ─────────────────────────────── -->
        <v-dialog v-model="schoolPictureDialog" max-width="1200" scrollable>
            <v-card rounded="xl">
                <!-- // test -->
                <!-- Header -->
                <div class="d-flex align-center pa-4 bg-teal">
                    <v-icon color="white" class="mr-2">mdi-image-multiple</v-icon>
                    <span class="text-subtitle-1 font-weight-bold text-white">
                        School Pictures — {{ schoolPictureSite }}
                    </span>
                    <v-spacer />
                    <span class="text-caption text-white opacity-80 mr-3">{{ schoolPictures.length }} photo(s)</span>
                    <v-btn icon size="small" variant="text" color="white" @click="schoolPictureDialog = false">
                        <v-icon>mdi-close</v-icon>
                    </v-btn>
                </div>

                <v-card-text class="pa-4">
                    <!-- Loading -->
                    <div v-if="schoolPictureLoading" class="d-flex justify-center py-10">
                        <v-progress-circular indeterminate color="teal" size="52" />
                    </div>

                    <!-- No pictures -->
                    <div v-else-if="schoolPictures.length === 0"
                        class="d-flex flex-column align-center justify-center py-12 text-grey">
                        <v-icon size="56" color="grey-lighten-1">mdi-image-off</v-icon>
                        <div class="mt-2">No pictures found for this site.</div>
                    </div>

                    <!-- Grid -->
                    <v-row v-else dense>
                        <v-col v-for="(pic, i) in schoolPictures" :key="i" cols="6" sm="4" md="3" lg="2">
                            <v-card rounded="lg" elevation="1" class="overflow-hidden cursor-pointer"
                                @click="openPreview(pic.url, pic.filename)">
                                <v-img
                                    :src="'/api/showPicture?path=' + encodeURIComponent(pic.url)"
                                    aspect-ratio="1"
                                    cover
                                >
                                    <template #placeholder>
                                        <div class="d-flex justify-center align-center fill-height">
                                            <v-progress-circular indeterminate color="teal" size="24" />
                                        </div>
                                    </template>
                                    <template #error>
                                        <div class="d-flex justify-center align-center fill-height bg-grey-lighten-3">
                                            <v-icon color="grey">mdi-image-broken</v-icon>
                                        </div>
                                    </template>
                                </v-img>
                                <div class="px-2 py-1 text-caption text-truncate text-grey-darken-1">
                                    {{ pic.filename }}
                                </div>
                            </v-card>
                        </v-col>
                    </v-row>
                </v-card-text>

                <v-divider />
                <v-card-actions class="justify-end pa-3">
                    <v-btn variant="text" @click="schoolPictureDialog = false">Close</v-btn>
                </v-card-actions>
            </v-card>
        </v-dialog>

        <!-- ── FULL-SIZE PREVIEW ───────────────────────────────────── -->
        <v-dialog v-model="previewDialog" max-width="900" @after-leave="previewPic = null">
            <v-card v-if="previewPic" rounded="lg">

                <div style="position:relative; min-height:320px; background:#f5f5f5;">
                    <!-- Spinner overlay while loading -->
                    <div v-if="previewLoading"
                        style="position:absolute; inset:0; display:flex; align-items:center; justify-content:center; z-index:1;">
                        <v-progress-circular indeterminate color="primary" size="56" />
                    </div>
                    <!-- Native img — always fires load/error reliably -->
                    <img
                        :src="'/api/showPicture?path=' + encodeURIComponent(previewPic.url)"
                        :style="{ visibility: previewLoading ? 'hidden' : 'visible', display:'block', maxWidth:'100%', maxHeight:'80vh', margin:'auto' }"
                        @load="previewLoading = false"
                        @error="previewLoading = false"
                    />
                </div>

                <v-card-actions class="justify-space-between pa-3">
                    <span class="text-caption text-grey">{{ previewPic.filename }}</span>
                    <div class="d-flex ga-2">
                        <v-btn size="small" color="teal" variant="tonal" prepend-icon="mdi-open-in-new"
                            :href="'/api/showPicture?path=' + encodeURIComponent(previewPic.url)" target="_blank">
                            Open full size
                        </v-btn>
                        <v-btn size="small" variant="text" @click="previewDialog = false">Close</v-btn>
                    </div>
                </v-card-actions>
            </v-card>
        </v-dialog>

    </div>
</template>

<script>
// import { VDataTable } from 'vuetify/labs/VDataTable'
export default {
    name: "FinanceDashboard",
    data: function () {
        return {
            loading: true,
            loadingExcel: false,
            items: [],
            selectedDate: "",
            search: "",
            schoolPictureDialog: false,
            schoolPictureLoading: false,
            schoolPictureSite: '',
            schoolPictures: [],
            previewDialog: false,
            previewLoading: false,
            previewPic: null,
            headers: [
                { title: "Advisor", align: "start", key: "advisor" },
                { title: "Date", align: "center", key: "date" },
                { title: "Site", align: "center", key: "site", width: "40px" },
                {
                    title: "Platform",
                    align: "center",
                    key: "pf",
                    width: "40px",
                },
                { title: "Save/Debt", align: "center", key: "save_debt" },
                {
                    title: "Balance beginning of month",
                    align: "center",
                    key: "amount_begin",
                },
                {
                    title: "Transaction amount",
                    align: "center",
                    key: "received",
                },
                { title: "Cash receipt", align: "center", key: "cash_receipt" },
                { title: "Invoice ref", align: "center", key: "invoice_ref" },
                { title: "Invoice type", align: "center", key: "invoice_type" },
                { title: "Remaining", align: "center", key: "remaining" },
                { title: "Cash Receipt", align: "center", key: "receipt" },
                { title: "QR", align: "center", key: "pictures" },
                { title: "School Pic", align: "center", key: "school_pictures" },
                { title: "Payment", align: "center", key: "payment_method" },
            ],
        };
    },
    computed: {
        filteredItems() {
            if (!this.search || this.search == "") {
                return this.items;
            } else {
                //  return this.items.filter((i =>i.site !==null && i.site.includes(this.search)) || (i =>i.advisor !==null && i.advisor.includes(this.search)) || (i =>i.site !==null && i.pf.includes(this.search)) || (i =>i.site !==null &&i.invoice_ref.includes(this.search)));
                return this.items.filter((item) => {
                    const searchTerm = this.search.toLowerCase(); // Ensure case-insensitive search
                    return (
                        (item.site !== null &&
                            item.site.toLowerCase().includes(searchTerm)) ||
                        (item.advisor !== null &&
                            item.advisor.toLowerCase().includes(searchTerm)) ||
                        (item.pf !== null &&
                            item.pf.toLowerCase().includes(searchTerm)) ||
                        (item.invoice_ref !== null &&
                            item.invoice_ref.toLowerCase().includes(searchTerm))
                    );
                });
            }
        },
    },
    watch: {
        selectedDate() {
            this.getItems();
        },
    },
    mounted() {
        let date = new Date();
        date.setMonth(date.getMonth() - 1);
        this.selectedDate = date.toISOString().slice(0, 7);
    },
    methods: {
        openPreview(url, filename) {
            this.previewPic = { url, filename };
            this.previewLoading = true;
            this.previewDialog = true;
        },
        openSchoolPictures(item) {
            this.schoolPictureSite = item.site;
            this.schoolPictures = [];
            this.schoolPictureLoading = true;
            this.schoolPictureDialog = true;
            const [year, month] = this.selectedDate.split('-');
            const monthParam = parseInt(month) + '-' + year;   // "5-2026"
            window.axios
                .get('/api/datastore/schoolPictures', {
                    params: { site: item.site, month: monthParam }
                })
                .then(response => {
                    this.schoolPictures = response.data;
                })
                .catch(() => {
                    this.schoolPictures = [];
                })
                .finally(() => {
                    this.schoolPictureLoading = false;
                });
        },
        getItems() {
            this.loading = true;
            let date = this.selectedDate.split("-");
            let year = parseInt(date[0]);
            let month = parseInt(date[1]);
            window.axios
                .get("/api/datastore/settleForms?month=" + month + "-" + year)
                .then((response) => {
                    this.items = response.data;
                    console.log(response.data);
                    this.loading = false;
                });
        },
        exportExcel() {
            this.loadingExcel = true;
            let date = this.selectedDate.split("-");
            let year = parseInt(date[0]);
            let month = parseInt(date[1]);
            window.axios
                .get(
                    "/api/datastore/settleForms?month=" +
                    month +
                    "-" +
                    year +
                    "&excel=1",
                    { responseType: "blob" }
                )
                .then((response) => {
                    this.loadingExcel = false;
                    const url = URL.createObjectURL(
                        new Blob([response.data], {
                            type: "application/vnd.ms-excel",
                        })
                    );
                    const link = document.createElement("a");
                    link.href = url;
                    link.setAttribute(
                        "download",
                        month + "-" + year + "_payment_received.xlsx"
                    );
                    document.body.appendChild(link);
                    link.click();
                    link.remove();
                });
        },
        async downloadPictures() {
            let d = this.selectedDate.split("-");
            let y = parseInt(d[0]);
            let m = parseInt(d[1]);
            let fullMonth = m + "-" + y;
            try {
                // const response = await axios.get("/api/downloadPictures", {
                //   params: { month: this.month },
                //   responseType: "blob"
                // });
                const response = await axios.get("/api/downloadPictures", {
                    params: { month: fullMonth },
                    responseType: "blob",
                });

                const blob = new Blob([response.data], {
                    type: "application/zip",
                });
                const link = document.createElement("a");
                link.href = URL.createObjectURL(blob);
                link.download = `pictures_${this.month}.zip`;
                link.click();
                URL.revokeObjectURL(link.href);
            } catch (error) {
                console.error("Download failed", error);
            }
        },
    },
};
</script>

<style>
.small-text {
    font-size: 0.8rem;
}

.small-text thead {
    font-size: 0.6rem;
}

.small-text table {
    table-layout: fixed;
}

@keyframes rotate {
    from {
        transform: rotate(0deg);
    }

    to {
        transform: rotate(360deg);
    }
}

.rotate-button {
    animation: rotate 1s linear infinite;
}
</style>
