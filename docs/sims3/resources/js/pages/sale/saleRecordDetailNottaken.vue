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
                            <!-- <v-text-field v-model="selectedDate" class="flex-grow-0 mr-5" label="Month" type="month" /> -->
                            <v-btn icon="mdi-arrow-left-bold-circle" color="blue" size="x-large" @click="$router.push({ path: '/saleRecord' })"></v-btn>
                        </v-col>
                     
                        <!-- <v-col cols="12" md="4">
                            <v-btn rounded="lg" prepend-icon="mdi-microsoft-excel" color="green" class="ma-4"
                                @click="downloadReport"> Download </v-btn>
                        </v-col> -->
                    </v-row>
                </v-toolbar-title>

                <!-- <v-text-field v-model="searchValue" density="compact" label="Search site" hide-details clearable
                    class="shrink" prepend-inner-icon="mdi-clipboard-text-search" /> -->
            </v-toolbar>
            <br>
            <v-window v-model="tab" class="left">

                <v-card flat>
                    <EasyDataTable :headers="headers" :items="saleData" :search-field="searchField"
                        :search-value="searchValue" border-cell buttons-pagination>
                        <!-- <template #item-Action="item">
                            <v-btn icon="mdi-checkbox-marked-outline" density="compact" class="me-2" color="error"
                                size="small" variant="tonal"
                                @click="$router.push({ path: '/SaleRecord/' + item.id })" />

                        </template> -->

                        <template #item-sale_type="item">
                            <div v-if="item.sale_type == 'opening_site'" class="operation_status">
                                {{ item.sale_type }}
                            </div>
                            <div v-else class="intervention">
                                {{ item.sale_type }}
                            </div>
                        </template>

                        <template #item-sale_officer="item">
                            {{ item.sale_officer1 }}, {{ item.sale_officer2 }}, {{ item.sale_officer3 }}, {{
        item.sale_officer4 }}
                        </template>
                        <template #item-total_bottle_sell="item">
                            {{ item.new_bottle + item.refill + item.lending_bottle + item.free }}
                        </template>
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
import { computed, onMounted, ref, watch,onBeforeMount } from "vue";
import axios from "axios";
import { useRouter, useRoute } from 'vue-router'; // use to get another page.  

//const router = useRouter() ; // rounter.push("path")
const route = useRoute();
const dialog = ref(false);
const tab = ref('');
const saleData = ref([]);
const loading = ref(true);
const selectedDate = ref('');

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

const searchField = ["site", "sex", "sale_date"];
const searchValue = ref('')
const headers: Header[] = [
    { text: "Site", value: "site", fixed: true, width: 30 },
    { text: "Date", value: "sale_date", width: 50 },
    { text: "Sale Type", value: "sale_type", width: 55 },
    { text: "Customer", value: "customer", width: 55 },
    { text: "Village", value: "village", width: 55 },
    { text: "Free", value: "free", width: 40 },
    { text: "New Bottle", value: "new_bottle", width: 40 },
    { text: "Refill", value: "refill", width: 40 },
    { text: "Lending", value: "lending_bottle", width: 40 },
    { text: "Total Bottle", value: "total_bottle_sell", width: 40 },
    { text: "Sale Team", value: "sale_officer", width: 145 },
    
];

const items: Item[] = saleData.value;

const receiveDate = route.query.date
const site = route.query.site
    
onBeforeMount(async () => {
    fetchData()
    loading.value = false;
});

const fetchData = async () => {
    if (receiveDate) 
    {
        try 
        {
            const response = await axios.get('/api/saleRecord/datail?site=' + site+'&selectDate='+ receiveDate);
            saleData.value=[];
            
            saleData.value= response.data;
        } catch (error) {
            console.error('Error fetching data:', error);
          
        } finally {

        }
    }
};

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
