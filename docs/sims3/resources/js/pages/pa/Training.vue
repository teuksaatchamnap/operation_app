<template>
    <v-card class="ma-4">
        <v-tabs v-model="tab" bg-color="yellow" :touch="false">
            <v-tab value="my-training"> My Traning </v-tab>
            <v-tab value="manager"> My Team Training </v-tab>
            <v-tab value="admin"> All Training </v-tab>
        </v-tabs>
        <v-card-text v-if="loading" class="d-flex justify-center mt-10">
            <v-progress-circular indeterminate :size="60" color="primary" />
        </v-card-text>
        <v-card-text v-else>
            <div class="d-flex flex-row align-center mb-3">
                <!-- <v-btn class="mr-5" color="blue" icon="mdi-hospital" @click="$router.push({ path: '/pa/form' })" /> -->
                <v-text-field
                    v-model="search"
                    density="compact"
                    label="Search"
                    hide-details
                    clearable
                    class="shrink"
                    prepend-inner-icon="mdi-clipboard-text-search"
                />
                <!-- <v-btn class="ml-5 mt-2 mr-5" color="secondary" icon="mdi-microsoft-excel" @click="exportExcel()" /> -->
            </div>
            <!-- show data -->
            <v-data-table
                v-model:items-per-page="itemsPerPage"
                :headers="headers"
                :items="filterTraining"
                density="compact"
                item-value="sample_date"
                class="pa-4"
            >
                <template #item.total="{ item }">
                    <!-- <span v-if="item.status != 'loading'"> -->
                    <!-- <v-chip v-if="item.cooperate_score + item.entrepreneur_score > 30 ">
               pass
            </v-chip> -->
                    <v-chip>
                        {{
                            item.cooperate_score +
                            item.entrepreneur_score +
                            item.sale_and_maketing_score +
                            item.water_quality_score
                        }}
                    </v-chip>

                    <!-- </span> -->
                    <!-- <v-progress-linear v-else indeterminate color="yellow-darken-2" /> -->
                </template>
            </v-data-table>
        </v-card-text>
    </v-card>
    <div class="text-center">
        <v-dialog v-model="dialog" activator="parent" width="auto">
            <v-card>
                <v-card-text>
                    Download excel is in construction !!! Thank you for your
                    patient
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
    name: "Training",
    components: {
        
    },
    data: function () {
        return {
            open: false,
            dialog: false,
            loading: true,
            training: [],
            itemsPerPage: 15,
            search: "",
            tab: "my-training",
            throttleTimer: -1,
            headers: [
                { title: "Name", align: "start", key: "staff_email" },
                {
                    title: "Cooperation",
                    align: "center",
                    key: "cooperate_score",
                },
                {
                    title: "Entrepreneur",
                    align: "center",
                    key: "entrepreneur_score",
                },
                {
                    title: "Sale & Marketing",
                    align: "center",
                    key: "sale_and_maketing_score",
                },
                {
                    title: "Water Quality",
                    align: "center",
                    key: "water_quality_score",
                },
                { title: "Total Score", align: "center", key: "total" },
                // { title: 'Result', align: 'center', key: 'final_result' },
            ],
        };
    },
    computed: {
        filterTraining() {
            if (this.search == "") {
                return this.training;
            } else {
                return this.training.filter((m) =>
                    m.staff_email.includes(this.search)
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
                this.GetTraining();
            });
        },
    },
    mounted() {
        this.GetTraining();
    },
    methods: {
        GetTraining() {
            if (this.$route.params.id) {
                window.axios
                    .get("/api/training/" + this.$route.params.id)
                    .then((response) => {
                        this.training = response.data;
                        this.loading = false;
                    });
            } else {
                this.loading = true;
                window.axios
                    .get("/api/training?" + this.tab + "=1")
                    .then((response) => {
                        this.training = response.data;
                        this.loading = false;
                    });
            }
        },
        printExcel() {
            // alert ("Download excel is in construction !!! Thank you for your patient")
            this.dialog = true;
        },
        open() {
            alert(
                "Download excel is in construction !!! Thank you for your patient"
            );
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
