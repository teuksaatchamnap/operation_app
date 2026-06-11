<template>
  <div
    v-if="loading"
    class="d-flex justify-center mt-10"
  >
    <v-progress-circular
      indeterminate
      :size="60"
      color="primary"
    />
  </div>
  <div v-else>
    <div class="d-flex flex-row align-center ma-3">
      <v-text-field
        v-model="selectedDate"
        density="compact"
        hide-details
        class="flex-grow-0 mr-5"
        label="Month"
        type="month"
      />
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
        class="ml-5 mt-2 mr-5"
        :class="{ 'rotate-button': loadingExcel }"
        color="secondary"
        :icon="loadingExcel ? 'mdi-loading' : 'mdi-microsoft-excel'"
        :disabled="loadingExcel"
        @click="exportExcel()"
      />
    </div>
    <v-data-table
      :items-per-page="25"
      :headers="headers"
      :items="filteredItems"
      density="compact"
      item-value="id"
      class="small-text"
    />
  </div>
</template>

<script>
// import { VDataTable } from 'vuetify/labs/VDataTable'
export default {
    name: "FinanceDashboard",
    components: {
        
    },
    data: function () {
        return {
            loading: true,
            loadingExcel: false,
            items: [],
            selectedDate: "",
            search: "",
            headers: [
                { title: "Site", align: "start", key: "site", width: "20px" },
                { title: "Platform", align: "center", key: "platform" },
                { title: "Status", align: "center", key: "status" },
                { title: "Open Date", align: "center", key: "open_date" },
                { title: "Closed Date", align: "center", key: "closed_date" },
                {
                    title: "Reason Closed",
                    align: "center",
                    key: "reason_closed",
                },
                { title: "Entre_Name", align: "center", key: "entre_name" },
                {
                    title: "Start Work Date",
                    align: "center",
                    key: "date_entre_work",
                },
                { title: "Date Resign", align: "center", key: "when_resign" },
                {
                    title: "Reason Resign",
                    align: "center",
                    key: "reason_resign",
                },
                {
                    title: "Detail Resign",
                    align: "center",
                    key: "detail_resign",
                },
            ],
        };
    },
    computed: {
        filteredItems() {
            if (!this.search || this.search == "") {
                return this.items;
            } else {
                //  return this.items.filter((i => i.site !== null && i.site.includes(this.search)) || (i => i.status !== null && i.status.includes(this.search)));

                return this.items.filter(
                    (i) =>
                        (i.site !== null &&
                            i.site
                                .toLowerCase()
                                .includes(this.search.toLowerCase())) ||
                        (i.status !== null &&
                            i.status
                                .toLowerCase()
                                .includes(this.search.toLowerCase()))
                );
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
        date.setMonth(date.getMonth(), 1);
        this.selectedDate = date.toISOString().slice(0, 7);
        console.log(this.selectedDate);
    },
    methods: {
        getItems() {
            this.loading = true;
            let getDate = new Date(this.selectedDate);
            getDate.setMonth(getDate.getMonth() - 1);
            let r = getDate.toISOString().slice(0, 7);
            let date = r.split("-");
            let year = parseInt(date[0]);
            let month = parseInt(date[1]);
            window.axios
                .get("/api/getSiteStatus?month=" + month + "-" + year)
                .then((response) => {
                    this.items = response.data;
                    console.log(response.data);
                    this.loading = false;
                });
        },
        exportExcel() {
            this.loadingExcel = true;
            let getDate = new Date(this.selectedDate);
            getDate.setMonth(getDate.getMonth() - 1);
            let r = getDate.toISOString().slice(0, 7);
            let date = r.split("-");
            let year = parseInt(date[0]);
            let month = parseInt(date[1]);
            window.axios
                .get(
                    "/api/getSiteStatus?month=" +
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
                        month + "-" + year + "siteStatus.xlsx"
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
.small-text {
    font-size: 15px;
}

.small-text thead {
    font-size: 15px;
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
