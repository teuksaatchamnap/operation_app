<template>
    <div v-if="loading" class="d-flex justify-center mt-10 pt-10">
        <v-progress-circular :size="50" color="primary" indeterminate></v-progress-circular>
    </div>
    <div v-else>
        <v-card>
            <v-toolbar color="white" class="compresstile">
                <v-toolbar-title>
                    <!-- 'vuthy.n@teuksaat1001.com', 'pisak.m@teuksaat1001.com', 'phanith.m@teuksaat1001.com', 'phalla.p@teuksaat1001.com'
                                , 'darith.s@teuksaat1001.com', 'dara.s@teuksaat1001.com', 'theary.m@teuksaat1001.com', 'sak.s@teuksaat1001.com', 'odom.p@teuksaat1001.com'
                                , 'veasna.r@teuksaat1001.com' -->
                    <v-row>
                        <v-col cols="12" md="4">
                            <v-text-field v-model="selectedDate" class="flex-grow-0 mr-5" label="Month" type="month" />
                        </v-col>
                        <v-col cols="12" md="4">
                            <v-select v-model="technician" label="Select Technician"  class="flex-grow-0 mr-5"
                            :items="[' ','Ros Veasna', 'Pin Phalla', 'Morn Phanith', 'Pech Odom', 'Touch Bros', 'Neang Vuthy',
                             'Men Pisak', 'Sok Dara', 'Sok Darith','Khy Sopheap','Houl Vicheat','Leak Leab'
                            ]" />
                        </v-col>
                        <v-col cols="12" md="4">
                            <v-btn rounded="lg" :disabled="isExportingDashboard" :class="{ 'rotate-icon': isExportingDashboard }" class="ml-5 mt-2 mr-5 text-white" :icon="isExportingDashboard ? 'mdi-loading' : 'mdi-file-chart-outline'"
                            prepend-icon="mdi-microsoft-excel" color="blue"
                                @click="downloadDN(technician)"> Print </v-btn>
                        </v-col>
                    </v-row>
                </v-toolbar-title>

                <v-text-field v-model="searchValue" density="compact" label="Search site" hide-details clearable
                    class="shrink" prepend-inner-icon="mdi-clipboard-text-search" />
            </v-toolbar>
            <br>
            <v-window v-model="tab" class="left">
                    <v-card flat>
                        <EasyDataTable :headers="headers" :items="saleData" :search-field="searchField"
                            :search-value="searchValue" border-cell buttons-pagination>

                            <template #item-stock_limit="item">
                                <div v-if="item.item_code== 113002" >
                                    1
                                </div>
                                <div v-else-if="item.item_code== 112002" >
                                    1
                                </div>
                                <div v-else-if="item.item_code== 212010" >
                                    1
                                </div>
                                <div v-else-if="item.item_code== 208009" >
                                    5
                                </div>
                                <div v-else-if="item.item_code== 208011" >
                                    1
                                </div>
                                <div v-else-if="item.item_code== 208004" >
                                    1
                                </div>
                                <div v-else-if="item.item_code== 208005" >
                                    1
                                </div>
                                <div v-else-if="item.item_code== 208010" >
                                    4
                                </div>
                                <div v-else-if="item.item_code== 208012" >
                                    1
                                </div>
                                <div v-else-if="item.item_code== 209009" >
                                    4
                                </div>
                                <div v-else >
                                    0
                                </div>
                                </template>
                            <template #item-status="item">
                                <div v-if="item.total_qty && item.item_code== 113002" class="bad-icon">
                                               {{ 1 - item.total_qty }}
                                </div>
                                <div v-if="item.total_qty && item.item_code== 112002" class="bad-icon">
                                    {{ 1 - item.total_qty }}
                                </div>
                                <div v-if="item.total_qty && item.item_code== 212010" class="bad-icon">
                                    {{ 1 - item.total_qty }}
                                </div>
                                <div v-if="item.total_qty && item.item_code== 208009" class="bad-icon">
                                               {{ 5 - item.total_qty }}
                                </div>
                                <div v-if="item.total_qty && item.item_code== 208011" class="bad-icon">
                                    {{ 1 - item.total_qty }}
                                </div>
                                <div v-if="item.total_qty && item.item_code== 208004" class="bad-icon">
                                    {{ 1 - item.total_qty }}
                                </div>
                                <div v-if="item.total_qty && item.item_code== 208005" class="bad-icon">
                                    {{ 1 - item.total_qty }}
                                </div>
                                <div v-if="item.total_qty && item.item_code== 208010" class="bad-icon">
                                     {{ 4 - item.total_qty }}
                                </div>
                                <div v-if="item.total_qty && item.item_code== 208012" class="bad-icon">
                                    {{ 1 - item.total_qty }}
                                </div>
                                <div v-if="item.total_qty && item.item_code== 209009" class="bad-icon">
                                     {{ 4 - item.total_qty }}
                                </div>
                                <div v-else class="bad-icon">

                                </div>
                                </template>
                            <!-- <template #item-download="item">
                                <v-btn icon="mdi-microsoft-excel"
                                    density="compact" class="me-2" color="green" size="medium" variant="tonal"
                                    @click="downloadDN(item.email)" />
                            </template> -->
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
                    hide-details="auto" :items="['Monthly Report','Specific Range Date Report']"  />
                </v-card>
                <v-card v-if="select_report=='Specific Range Date Report'">
                    <v-row>
                        <v-col cols="12" md="6">
                            <v-text-field v-model="start_date" type="date" density="compact"
                            label="Start Date" hide-details="auto" />
                        </v-col>
                        <v-col cols="12" md="6">
                            <v-text-field v-model="end_date" type="date" density="compact"
                            label="End Date" hide-details="auto" />
                        </v-col>
                    </v-row>

                </v-card>
                <v-spacer>``</v-spacer>
                <v-card-actions>
                    <v-row>
                        <v-col cols="12" md="6">
                            <v-btn color="primary" block @click="downloadReport()">Download</v-btn>
                        </v-col>
                        <v-col cols="12" md="6">
                            <v-btn color="error" block @click="dialog=false">Cancel</v-btn>
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
import Swal from "sweetalert2";

const dialog = ref(false);
const tab = ref('');
const saleData = ref([]);
const loading = ref(true);
const selectedDate = ref('');
const select_report= ref('')
const start_date= ref('')
const end_date= ref('')
const technician = ref('')
const isExportingDashboard = ref(false);
const showReport = () => {
    dialog.value = true

}
const downloadDN =(technician) =>{
    if (!technician) {
        Swal.fire({
            icon: 'error',
            text: 'Please select technician ',
        })
    }
    else
    {
        Swal.fire({
            icon: 'success',
            text: 'Please wait a moment, we are preparing the file for you',
        })
        isExportingDashboard.value = true;
        axios.get('/api/downloadMinimumStock?selectDate=' + selectedDate.value+'&email='+technician, { responseType: 'blob' }).then(response => {
            const url = URL.createObjectURL(new Blob([response.data], {
                type: 'application/vnd.ms-excel'
            }))
            const link = document.createElement('a')
            link.href = url
            link.setAttribute('download', "MinimumStock.xlsx")
            document.body.appendChild(link)
            link.click()
            link.remove()
            isExportingDashboard.value = false;
            Swal.close();
        });
    }
}
const DownloadExcelMinimumStock = () => {
    if (technician.value == ' ') {
        alert('Please select technician email')
        return;
    }
    axios.get('/api/DownloadExcelMinimumStock?email='+technician.value, { responseType: 'blob' }).then(response => {
        const url = URL.createObjectURL(new Blob([response.data], {
            type: 'application/vnd.ms-excel'
        }))
        const link = document.createElement('a')
        link.href = url
        link.setAttribute('download', "PrintMinimumStock.xlsx")
        document.body.appendChild(link)
        link.click()
        link.remove()
    });
}
const downloadReport = () => {
    //dialog.value = true
    axios.get('/api/saleDownloadReport?selectDate=' + selectedDate.value+'&select_report='+select_report.value+'&start_date='+start_date.value+'&end_date='+end_date.value, { responseType: 'blob' }).then(response => {
        const url = URL.createObjectURL(new Blob([response.data], {
            type: 'application/vnd.ms-excel'
        }))
        const link = document.createElement('a')
        link.href = url
        link.setAttribute('download', "SaleConsolidate.xlsx")
        document.body.appendChild(link)
        link.click()
        link.remove()
    });
}

const searchField = ["email","item_code","item_name"];
const searchValue = ref('')
const headers: Header[] = [
    { text: "Technician", value: "email", width: 20, sortable: true },
    { text: "Item Code", value: "item_code", width: 25 },
    { text: "Item Name", value: "item_name", width: 150 },
    { text: "Unit", value: "item_unit", width: 25 },
    { text: "Stock Provided", value: "stock_limit", width: 25 },
    { text: "QTY used", value: "total_qty", width: 25 },
    // { text: "Paid By", value: "pay_by", width: 20 },
    { text: "QTY Remain", value: "status", width: 20 },
    // { text: "Download", value: "download", width: 20 },

];

const items: Item[] = saleData.value;

const showItem = (i) => {
    console.log(i.value)
}

onMounted(async () => {
    selectedDate.value = new Date().toISOString().slice(0, 7)
    start_date.value =new Date().toISOString().slice(0, 10)
    end_date.value =new Date().toISOString().slice(0, 10)
    //const response = await axios.get('/api/saleRecord');
    //fetchData()

});

const fetchData = async ()=>{
    loading.value = false;
    if(!selectedDate.value){
        return;
    }
    try {
    const response = await axios.get('/api/minimumStock?selectDate='+ selectedDate.value);
    //const response = await axios.get('/api/getDataMinimumStock?selectDate='+ selectedDate.value);
    saleData.value=[];
    //saleData.value.push(...response.data); // if put copy this result, easy data table must follow item with const items
    saleData.value= response.data; // change items in easytable to variable that retrieve array data
    console.log(saleData.value)
  } catch (error) {
    console.error('Error fetching data:', error);
    // Handle errors (e.g., display an error message to the user)
  } finally {

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
    color:chocolate;
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
.rotate-icon {
  animation: rotate 1s infinite linear;
}

@keyframes rotate {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style>
