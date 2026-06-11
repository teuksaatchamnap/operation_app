<template>
    <div v-if="loading" class="d-flex justify-center mt-10 pt-10">
        <v-progress-circular :size="50" color="primary" indeterminate></v-progress-circular>
    </div>
    <div v-else>
        <v-card>
            <v-toolbar color="white" class="compresstile">
                <v-toolbar-title>

                    <v-row>
                        <v-col cols="12" md="4">
                            <v-text-field v-model="selectedDate" class="flex-grow-0 mr-5" label="Month" type="month" />
                        </v-col>
                        <v-col cols="12" md="4">
                            <v-btn rounded="lg" prepend-icon="mdi-microsoft-excel" color="green" class="ma-4"
                                @click="showReport"> Download </v-btn>
                        </v-col>
                    </v-row>
                </v-toolbar-title>

                <!-- <v-btn icon="mdi-plus" color="red" size="x-large" @click="$router.push({ path: '/saleRecord/form' })">
                </v-btn> -->
                <v-text-field v-model="searchValue" density="compact" label="Search site" hide-details clearable
                    class="shrink" prepend-inner-icon="mdi-clipboard-text-search" />
            </v-toolbar>
            <br>
            <v-window v-model="tab" class="left">
                <v-card flat>
                    <EasyDataTable :headers="headers" :items="saleData" :search-field="searchField"
                        :search-value="searchValue" border-cell buttons-pagination>
                        <template #item-Action="item">
                            <v-btn density="compact" class="me-2" color="green" size="small" variant="tonal"
                                @click="$router.push({ path: '/saleRecord/detail', query: { site: item.site, date: selectedDate } })">
                                Detail </v-btn>
                            <!-- send data to form, put path in app.js -->
                        </template>

                        <template #item-sale_type="item">
                            <div v-if="item.sale_type == 'opening_site'" class="good-icon">
                                {{ item.sale_type }}
                            </div>
                            <div v-else class="bad-icon">
                                {{ item.sale_type }}
                            </div>
                        </template>
                        <template #item-target="item">
                            <div v-if="item.sale_type == 'opening_site'">
                                500
                            </div>
                            <div v-else>
                                150
                            </div>
                        </template>
                        <template #item-rate="item">
                            <div v-if="item.sale_type == 'opening_site'">
                                <div v-if="(item.total_bottle / 500) * 100 > 100" class="operation_status">
                                    <v-icon large color="blue">mdi-arrow-up-bold-circle</v-icon>
                                    {{ ((item.customer / 500) * 100).toFixed(2) }} %
                                </div>
                                <div v-else class="intervention">
                                    <v-icon large color="red">mdi-arrow-down-bold-circle</v-icon>
                                    {{ ((item.customer / 500) * 100).toFixed(2) }} %
                                </div>
                            </div>
                            <div v-else>
                                <div v-if="(item.total_bottle / 150) * 100 > 100" class="operation_status">
                                    <v-icon large color="blue">mdi-arrow-up-bold-circle</v-icon>
                                    {{ ((item.customer / 150) * 100).toFixed(2) }} %
                                </div>
                                <div v-else class="intervention">
                                    <v-icon large color="red">mdi-arrow-down-bold-circle</v-icon>
                                    {{ ((item.customer / 150) * 100).toFixed(2) }} %
                                </div>

                            </div>
                        </template>

                    </EasyDataTable>
                </v-card>

            </v-window>
        </v-card>
    </div>
    <div class="text-center">
        <v-dialog v-model="dialog" activator="parent" width="500px">
            <v-card>
                <v-card-text align="center">
                    Report Type
                </v-card-text>
                <v-card>
                    <v-select v-model="select_report" label="Which report do you want ?" density="compact"
                        hide-details="auto" :items="['Monthly Report', 'Specific Range Date Report']" />
                </v-card>
                <v-card v-if="select_report == 'Specific Range Date Report'">
                    <v-row>
                        <v-col cols="12" md="6">
                            <v-text-field v-model="start_date" type="date" density="compact" label="Start Date"
                                hide-details="auto" />
                        </v-col>
                        <v-col cols="12" md="6">
                            <v-text-field v-model="end_date" type="date" density="compact" label="End Date"
                                hide-details="auto" />
                        </v-col>
                    </v-row>

                </v-card>
                <v-spacer></v-spacer>
                <v-card-actions>
                    <v-row>
                        <v-col cols="12" md="6">
                            <v-btn color="primary" block @click="downloadReport()">Download</v-btn>
                        </v-col>
                        <v-col cols="12" md="6">
                            <v-btn color="error" block @click="dialog = false">Cancel</v-btn>
                        </v-col>
                    </v-row>
                </v-card-actions>
            </v-card>
        </v-dialog>
    </div>
</template>

<script lang="ts" setup>
import { Header, Item } from "vue3-easy-data-table";
import { computed, onMounted, ref, watch } from "vue";
import axios from "axios";
import swal from "sweetalert2";

const dialog = ref(false);
const tab = ref('');
const saleData = ref([]);
const loading = ref(true);
const selectedDate = ref('');
const select_report = ref('')
const start_date = ref('')
const end_date = ref('')

const showReport = () => {
    dialog.value = true

}

const downloadReport = async () => {
    if (!select_report.value) {
        alert('Please select a report type before downloading.');
        return;
    }
    // Close the first dialog before showing SweetAlert
     dialog.value = false;

    // Show loading SweetAlert
    swal.fire({
        title: 'Downloading...',
        text: 'Please wait while the report is being generated.',
        allowOutsideClick: false,
        didOpen: () => {
            swal.showLoading();
        }
    });

    try {
        const response = await axios.get(
            '/api/saleDownloadReport?selectDate=' + selectedDate.value +
            '&select_report=' + select_report.value +
            '&start_date=' + start_date.value +
            '&end_date=' + end_date.value,
            { responseType: 'blob' }
        );

        const url = URL.createObjectURL(new Blob([response.data], {
            type: 'application/vnd.ms-excel'
        }));
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', "SaleConsolidate.xlsx");
        document.body.appendChild(link);
        link.click();
        link.remove();

        // Replace loader with auto-closing success message
        swal.fire({
            icon: 'success',
            title: 'Downloaded!',
            text: 'Report downloaded successfully.',
            showConfirmButton: false,
            timer: 2000   // auto close after 2s
        });
    } catch (error) {
        // Replace loader with error message
        swal.fire({
            icon: 'error',
            title: 'Error',
            text: 'Failed to download report.'
        });
    }
};
const searchField = ["site", "sex", "sale_date"];
const searchValue = ref('')
const headers: Header[] = [
    { text: "Site", value: "site", fixed: true, width: 30 },
    { text: "Platform", value: "Platform", fixed: true, width: 30 },
    { text: "Sale Type", value: "sale_type", width: 55 },
    { text: "Customer", value: "customer", width: 55 },
    { text: "Free", value: "free", width: 55 },
    { text: "Refill", value: "refill", width: 55 },
    { text: "New Bottle", value: "new_bottle", width: 55 },
    { text: "Lending Bottle", value: "lending_bottle", width: 55 },
    { text: "Total Bottle", value: "total_bottle", width: 40 },
    { text: "Target", value: "target", width: 40 },
    { text: "Rate (%)", value: "rate", width: 40 },
    { text: "Action", value: "Action", width: 25 },
];

const items: Item[] = saleData.value;

const showItem = (i) => {
    console.log(i.value)
}

onMounted(async () => {
    selectedDate.value = new Date().toISOString().slice(0, 7)
    start_date.value = new Date().toISOString().slice(0, 10)
    end_date.value = new Date().toISOString().slice(0, 10)
    //const response = await axios.get('/api/saleRecord');
    //fetchData()

});

const fetchData = async () => {
    loading.value = true; // show spinner while fetching
    if (!selectedDate.value) {
        loading.value = false;
        return;
    }

    try {
        const response = await axios.get('/api/saleRecord?selectDate=' + selectedDate.value);
        saleData.value = response.data;
        console.log(saleData.value);
    } catch (error) {
        console.error('Error fetching data:', error);
        // you can also show swal error if needed
        // swal.fire('Error', 'Failed to load data', 'error');
    } finally {
        loading.value = false; // hide spinner after fetching
    }
};

watch(selectedDate, (newValue) => {
    if (newValue) {
        fetchData(); // Trigger data fetch on change
    }
});

const filterData = computed(() => {
    if (searchValue.value == '') {
        return items;
    }
    else {
        return items.filter(item => (item).includes(searchValue.value))
    }
})

</script>

<style>
.operation_status {
    color: blue;
}

.intervention {
    color: chocolate;
}

.left {
    padding-left: 10px;
    padding-right: 10px;
}

.good-icon {
    color: green;
}

.bad-icon {
    color: red;
}

.add {
    margin-right: 40px;
    width: 40px;
    height: 40px;
    color: blueviolet;
}

.buttonshow {
    background-color: darkblue;
}

.alertProblemSolution {
    width: 10px;
    height: 10px;
}

.colorTitle {
    color: blue;
}

.swal2-popup {
    font-size: 15px !important;
    font-family: Georgia, serif;
}

.swal2-styled {
    padding: 10px 32px 10px 32px !important;
    margin: 20px 10px 0px 10px !important;
    width: 170px;
    height: 45px;
}

.Validate_Ongoing {
    color: peru;
}

.Fixed {
    color: green;
}
</style>
