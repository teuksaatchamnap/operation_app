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
                            <v-text-field v-model="startdate" type="date" density="compact" label="Start Date"
                                hide-details="auto" />
                        </v-col>
                        <v-col cols="12" md="4">
                            <v-text-field v-model="enddate" type="date" density="compact" label="End Date"
                                hide-details="auto" />
                        </v-col>
                        <v-col cols="12" md="4">
                            <v-btn rounded="lg" prepend-icon="mdi-microsoft-excel" color="green" class="ma-4"
                                @click="downloadReport"> Download </v-btn>
                        </v-col>
                    </v-row>
                </v-toolbar-title>

                <!-- <v-btn icon="mdi-plus" color="red" size="x-large" @click="$router.push({ path: '/kol/form' })">
                </v-btn> -->
                <v-text-field v-model="searchValue" density="compact" label="Search site" hide-details clearable
                    class="shrink" prepend-inner-icon="mdi-clipboard-text-search" />
            </v-toolbar>
            <br>
            <v-window v-model="tab" class="left">
                <v-window-item >
                    <v-card flat>
                        <EasyDataTable :headers="headers" :items="saleData" :search-field="siteField"
                            :search-value="searchValue" border-cell buttons-pagination>
                            <template #item-Action="item">
                                <v-btn v-if="$store.state.user.permissions.includes('edit_kol')" icon="mdi-checkbox-marked-outline" density="compact" class="me-2" color="error" size="small"
                                    variant="tonal" @click="$router.push({ path: '/kol/' + item.id })" />

                                    <!-- <v-btn v-if="$store.state.user.permissions.includes('edit_kol')" icon="mdi-checkbox-marked-outline" density="compact" class="me-2" color="error" size="small"
                                    variant="tonal" @click="detailItem(item)" /> -->
                                </template>
                        </EasyDataTable>
                    </v-card>
                </v-window-item>
            </v-window>
        </v-card>
    </div>
    <div class="text-center">
        <v-dialog v-model="dialog" activator="parent" width="auto">
            <v-card>
                <v-card-text>
                    Report is in construction. Thank you for your patient !!!
                </v-card-text>
                <v-card-actions>
                    <v-btn color="primary" block @click=" dialog = false">Close</v-btn>
                </v-card-actions>
            </v-card>
        </v-dialog>
    </div>
</template>



<script lang="ts" setup>
import { Header, Item } from "vue3-easy-data-table";
import { computed, onMounted, ref, watch } from "vue";
import axios from "axios";

const tab = ref('');
const dialog = ref(false);
const saleData = ref([]);
const loading = ref(true);
import swal from "sweetalert2";
const platform = [
    'all_platform', 'PP', 'BTB', 'KSP', 'KC', 'SR'
];

const startdate = ref(new Date().toJSON().slice(0, 10));
const enddate = ref(new Date().toJSON().slice(0, 10));
const downloadReport = async () => {
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
            '/api/salSurveyDownloadReport?start_date=' + startdate.value +
            '&end_date=' + enddate.value,
            { responseType: 'blob' }
        );

        const url = URL.createObjectURL(new Blob([response.data], {
            type: 'application/vnd.ms-excel'
        }));
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', "sale_survey.xlsx");
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
}

const siteField = ref("site");
const searchField = ("site_platform");
const searchValue = ref('')
const headers: Header[] = [
    { text: "Site", value: "site", fixed: true, width: 30 },
    { text: "Date", value: "submitted_date", width: 70 },
    { text: "know_the_brand", value: "do_you_know_the_brand" },
    { text: "how_many_bottle_you_change", value: "how_many_bottle_you_change" },
    { text: "how_many_times_the_entrepreneur_came", value: "how_many_times_the_entrepreneur_came" },
    { text: "frequency_how_often_do_you_purchase_o_we", value: "frequency_how_often_do_you_purchase_o_we", width: 65 },
    { text: "how_satisfied_are_you_with_the_timeliness", value: "how_satisfied_are_you_with_the_timeliness", width: 70 },
    { text: "how_satisfied_are_you_with_the_regularity", value: "how_satisfied_are_you_with_the_regularity", width: 50 },
    { text: "how_satisfied_are_you_with_the_service", value: "how_satisfied_are_you_with_the_service", width: 90 },
    { text: "overall_how_satisfied_are_you_with_owe_on_a_scale", value: "overall_how_satisfied_are_you_with_owe_on_a_scale" },
    { text: "would_you_recommend_o_we", value: "would_you_recommend_o_we", width: 90 },
    { text: "if_yes_what_would_you_say", value: "if_yes_what_would_you_say", width: 90 },
    { text: "Action", value: "Action", width: 40 },
];

const items: Item[] = saleData.value;

const showItem = (i) => {
    console.log(i.value)
}

onMounted(async () => {
    const response = await axios.get('/api/saleSurvey');
    console.log(response.data)
    //saleData.value.push(...response.data);
    saleData.value = response.data;
    loading.value = false;
});

const filterData = computed(() => {
    if (searchValue.value == '') {
        return items;
    }
    else {
        return items.filter(item => (item).includes(searchValue.value))
    }
})
// const detailItem = (i: Item) => {
//          console.log(i)
// }

const alertId = (val) => {
    console.log(val);
}
</script>

<style>
/* wrap header text */
.easy-data-table__header th {
  white-space: normal !important;
  word-break: break-word;
}

/* wrap body cells */
.easy-data-table__body td {
  white-space: normal !important;
  word-break: break-word;
}
/* Target EasyDataTable cells */
.easy-data-table td,
.easy-data-table th {
    white-space: normal !important;
    word-wrap: break-word !important;
    word-break: break-word !important;
}

/* Or target specific class if EasyDataTable has one */
.v-data-table td,
.v-data-table th {
    white-space: normal !important;
    word-wrap: break-word !important;
    word-break: break-word !important;
}

/* For table cells in general */
table td,
table th {
    white-space: normal !important;
    word-wrap: break-word !important;
}
.operation_status {
    color: blue;
}

.non_operation_status {
    color: red;
}
.wrap-text {
    white-space: normal !important;
    word-wrap: break-word !important;
    word-break: break-word !important;
}
.left {
    padding-left: 10px;
    padding-right: 10px;
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
}</style>
