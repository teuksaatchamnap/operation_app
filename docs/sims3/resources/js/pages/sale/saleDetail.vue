<template>
    <v-btn
        icon="mdi-arrow-left-bold-circle"
        color="blue"
        size="small"
        @click="$router.push({ path: '/saleRecord' })"
    ></v-btn
    ><br />
    <v-card class="ma-4">
        <v-tabs v-model="tab" bg-color="green" :touch="false">
            <v-tab value="sale_by_day"> Total Sale By Day </v-tab>
            <v-tab value="detail_sale"> Detail Sale 1 Month </v-tab>
        </v-tabs>
        <v-card-text v-if="loading" class="d-flex justify-center mt-10">
            <v-progress-circular indeterminate :size="60" color="primary" />
        </v-card-text>
        <v-card-text v-else>
            <div v-if="tab == 'sale_by_day'">
                <!-- show data -->
                <v-data-table
                    v-model:items-per-page="itemsPerPage"
                    :headers="headerSaleByDay"
                    :items="filterPA"
                    density="compact"
                    item-value="sample_date"
                    class="pa-4"
                >
                </v-data-table>
            </div>
            <div v-if="tab == 'detail_sale'">
                <!-- show data -->
                <v-data-table
                    v-model:items-per-page="itemsPerPage"
                    :headers="headerDetailSaleByDay"
                    :items="filterPA"
                    density="compact"
                    item-value="sample_date"
                    class="pa-4"
                >
                    <template #item.total_bottle_sell="{ item }">
                        {{
                            item.free +
                            item.new_bottle +
                            item.lending_bottle +
                            item.refill
                        }}
                    </template>
                    <template #item.sale_officer="{ item }">
                        {{ item.sale_officer1 }},{{ item.sale_officer2 }},{{
                            item.sale_officer3
                        }},{{ item.sale_officer4 }}
                    </template>
                    <template #item.Action="{ item }">
                        <v-chip
                            size="small"
                            color="primary"
                            @click="
                                $router.push({
                                    path: '/saleRecord/' + item.id,
                                })
                            "
                        >
                            <v-icon
                                start
                                size="x-small"
                                icon="mdi-pencil"
                            />Modify
                        </v-chip>
                        |
                        <v-chip
                            size="small"
                            color="primary"
                            @click="deleteItembox(item.id)"
                        >
                            <v-icon
                                start
                                size="x-small"
                                icon="mdi-pencil"
                            />Delete
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
                    Are you sure you want to delete it ?
                </v-card-text>
                <v-card-actions>
                    <v-btn
                        prepend-icon="mdi-cancel"
                        rounded="lg"
                        color="error"
                        class="ma-4"
                        size="large"
                        @click="deleteItem()"
                    >
                        Delete
                    </v-btn>
                </v-card-actions>
            </v-card>
        </v-dialog>
    </div>
</template>

<script>
// import { VDataTable } from 'vuetify/labs/VDataTable'
export default {
    name: "saleDetail",
    components: {
        
    },
    data: function () {
        return {
            idDelete: "",
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
            headerSaleByDay: [
                {
                    title: "Site",
                    align: "start",
                    key: "site",
                    width: 40,
                    sortable: true,
                },
                {
                    title: "Date",
                    align: "center",
                    key: "sale_date",
                    width: 120,
                },
                {
                    title: "Customer",
                    align: "center",
                    key: "customer",
                    width: 100,
                },
                { title: "Free", align: "center", key: "free", width: 40 },
                {
                    title: "New Bottle",
                    align: "center",
                    key: "new_bottle",
                    width: 40,
                },
                { title: "Refill", align: "center", key: "refill", width: 40 },
                {
                    title: "Lending",
                    align: "center",
                    key: "lending_bottle",
                    width: 40,
                },
                {
                    title: "Total_Bottle",
                    align: "center",
                    key: "total_bottle",
                    width: 40,
                },
            ],
            headerDetailSaleByDay: [
                {
                    title: "Site",
                    align: "start",
                    key: "site",
                    width: 40,
                    sortable: true,
                },
                {
                    title: "Date",
                    align: "center",
                    key: "sale_date",
                    width: 120,
                },
                {
                    title: "Sale Type",
                    align: "center",
                    key: "sale_type",
                    width: 120,
                },
                {
                    title: "Customer",
                    align: "center",
                    key: "customer",
                    width: 100,
                },
                {
                    title: "Village",
                    align: "center",
                    key: "village",
                    width: 130,
                },
                { title: "Free", align: "center", key: "free", width: 40 },
                {
                    title: "New Bottle",
                    align: "center",
                    key: "new_bottle",
                    width: 40,
                },
                { title: "Refill", align: "center", key: "refill", width: 40 },
                {
                    title: "Lending",
                    align: "center",
                    key: "lending_bottle",
                    width: 40,
                },
                {
                    title: "Total_Bottle",
                    align: "center",
                    key: "total_bottle_sell",
                    width: 40,
                },
                { title: "Sale Team", align: "center", key: "sale_officer" },
                { title: "Action", align: "center", key: "Action" },
            ],
        };
    },
    computed: {
        filterPA() {
            if (this.search == "") {
                return this.PA;
            } else {
                return this.PA.filter((m) =>
                    (m.site + m.code).includes(this.search)
                );
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
            const receiveDate = this.$route.query.date;
            const site = this.$route.query.site;

            this.loading = true;
            window.axios
                .get(
                    "/api/saleRecord/detail?" +
                        this.tab +
                        "=1&site=" +
                        site +
                        "&selectDate=" +
                        receiveDate
                )
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
        deleteItembox(id) {
            this.dialog = true;
            this.idDelete = id;
        },
        deleteItem() {
            this.dialog = false;
            window.axios
                .delete("/api/saleRecord/delete/" + this.idDelete)
                .then(() => {
                    this.getData();
                })
                .catch(() => {
                    this.loading = false;
                    this.hasError = true;
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
