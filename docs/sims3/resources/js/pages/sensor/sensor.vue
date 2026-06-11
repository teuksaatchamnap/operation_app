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
                <v-text-field v-model="searchValue" density="compact" label="Search site" hide-details clearable
                    class="shrink" prepend-inner-icon="mdi-clipboard-text-search" />
            </v-toolbar>
            <br>
            <v-window v-model="tab" class="left">
                <v-card flat>
                    <EasyDataTable :headers="headers" :items="items" :search-field="siteField"
                        :search-value="searchValue" border-cell buttons-pagination>

                    </EasyDataTable>
                </v-card>
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

const saleData = ref([]);
const loading = ref(true);
const dialog = ref(false);


const startdate = ref(new Date().toJSON().slice(0, 10));
const enddate = ref(new Date().toJSON().slice(0, 10));
const downloadReport = () => {
    dialog.value = true
    // axios.get('/api/downloadReport?startdate=' + startdate.value + '&enddate=' + enddate.value, { responseType: 'blob' }).then(response => {
    //     const url = URL.createObjectURL(new Blob([response.data], {
    //         type: 'application/vnd.ms-excel'
    //     }))
    //     const link = document.createElement('a')
    //     link.href = url
    //     link.setAttribute('download', "Technical_Intervention.xlsx")
    //     document.body.appendChild(link)
    //     link.click()
    //     link.remove()
    // });
}

const siteField = ref(["site.Id_Site", "site.Platform"]);
const searchField = ("site_platform");
const searchValue = ref('');
const headers: Header[] = [
    { text: "Site", value: "site.Id_Site", fixed: true, width: 30 },
    { text: "Platform", value: "site.Platform", width: 50 },
    { text: "Sensor", value: "sensor_id", width: 50 },
    { text: "Date", value: "day", width: 60 },
    { text: "Water Start", value: "water_start_of_day", width: 60 },
    { text: "Water End", value: "water_end_of_day", width: 60 },
    { text: "Elec Start ", value: "electricity_start", width: 60 },
    { text: "Elec End", value: "electricity_end", width: 60 },
    { text: "Voltage Min", value: "voltage_start", width: 60 },
    { text: "Voltage Max", value: "voltage_start", width: 60 },
    { text: "Current Max", value: "current_start", width: 50 },
    // { text: "Current End", value: "current_end", width: 50 },
    // { text: "Flowrate Start", value: "flowrate_start", width: 40 },
    // { text: "Flowrate End", value: "flowrate_end", width: 40 },
    // { text: "D1", value: "d1", width: 40 },

];

const items: Item[] = saleData.value;



onMounted(async () => {
    const response = await axios.get('/api/sensor');
    saleData.value.push(...response.data);
    loading.value = false;
    // console.log(saleData[0]['site'].value)
});




</script>

<style>
.operation_status {
    color: blue;
}

.non_operation_status {
    color: red;
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
}
</style>
