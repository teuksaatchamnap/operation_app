<template>
    <div v-if="loading" class="d-flex justify-center mt-10 pt-10">
        <v-progress-circular :size="50" color="primary" indeterminate></v-progress-circular>
    </div>
    <div v-else>
        <v-card>
            <v-toolbar color="white" class="compresstile">
                <v-toolbar-title>
                    <v-row>
                        <v-col cols="12" md="3">
                            <v-btn rounded="lg" prepend-icon="mdi-arrow-left-bold-circle" color="green" class="ma-4" size="big"
                            @click="$router.push({ path: '/flashReport'})" />
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
                            <template #item-Action="item">
                                <v-btn v-if="user.permissions.includes('pa-view')" density="compact" class="me-2" color="black" size="small" icon="mdi-tag-outline"
                                    variant="tonal" @click="$router.push({ path: '/flashReport/'+ item.Code_Flash_report})" > </v-btn>
                            </template>
                            <template #item-Period="item">
                                    <div v-if="item.Period== 'EndMonth'" class="bad-icon">
                                        Monthly Flash Report
                                    </div>
                                    <div v-else-if="item.Period== 'MidMonth'" class="good-icon">
                                        Mid Flash Report
                                    </div> 
                                    <div v-else>
                                        Weelkly Flash Report
                                    </div>
                            </template>
                            <template #item-status_bottle="item">
                                    <div v-if="item.status_bottle=='Over'" class="bad-icon">
                                        {{ item.status_bottle }}
                                    </div>
                                    <div v-else class="good-icon">
                                        {{ item.status_bottle }}
                                    </div> 
                            </template>
                            <template #item-Month="item">
                                    {{ item.Month.slice(0,7) }}
                            </template>
                        </EasyDataTable>
                    </v-card>
            </v-window>
        </v-card>
    </div>
    <div class="text-center">
        <v-dialog v-model="dialog" activator="parent" width="500px">
            <v-card>
                <v-card-text >
                    Report is in construction !!! Thank for your patient
                </v-card-text>
                <v-spacer></v-spacer>
                <v-card-actions>
                    <v-row>
                        <v-col cols="12" md="12" align="center">
                            <v-btn color="error" block @click="dialog=false">OK</v-btn>
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
import { useStore } from 'vuex';
import axios from "axios";
import { useRouter,useRoute } from 'vue-router';
const route = useRoute();
const router = useRouter();
const store = useStore();
const dialog = ref(false);
const tab = ref('');
const saleData = ref([]);
const loading = ref(true);
const selectedDate = ref('');
const select_report= ref('')
const start_date= ref('')
const end_date= ref('')


const searchField = ["Id_Site","site.Platform","site.Advisor"];
const searchValue = ref('')
const headers: Header[] = [
    { text: "Site", value: "Id_Site", fixed: true, width: 20 },
    { text: "Platform", value: "site.Platform", fixed: true, width: 30},
    { text: "Advisor", value: "site.Advisor", fixed: true, width: 30},
    { text: "Report Type", value: "Period", fixed: true, width: 30 },
    { text: "Month", value: "Month", fixed: true, width: 30 },
    { text: "Village", value: "Number_jugs_village", fixed: true, width: 40,sortable: true },
    { text: "School", value: "Number_jugs_school", width: 30 },
    { text: "Comment", value: "Comment", width: 30 },
    { text: " ", value: "Action", width: 10 },
];

const items: Item[] = saleData.value;
onMounted(async () => {
    selectedDate.value = new Date().toISOString().slice(0, 7)
    start_date.value =new Date().toISOString().slice(0, 10)
    end_date.value =new Date().toISOString().slice(0, 10)
    //const response = await axios.get('/api/saleRecord');
    fetchData()
    
});
const user= computed(() =>{
    //console.log(store.state.user.permissions.includes("close_site"))
    return store.state.user
});

const fetchData = async ()=>{
   
     const receiveDate = route.query.date
     console.log(receiveDate)
     const report_type = route.query.report_type
    loading.value = false;
    if(!selectedDate.value){
        return;
    }
    try {
    const response = await axios.get('/api/flashReportDashboard?receiveDate='+ receiveDate+"&report_type="+report_type);
    saleData.value=[];
    //saleData.value.push(...response.data); // if put copy this result, easy data table must follow item with const items
    saleData.value= response.data; // change items in easytable to variable that retrieve array data
    console.log(saleData.value)
  } catch (error) {
    console.error('Error fetching data:', error);
    
  } finally {
   
  }
};

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
.validate-icon {
  color:blue;
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
