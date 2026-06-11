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
                            <v-btn rounded="lg" prepend-icon="mdi-microsoft-excel" color="green" class="ma-4"
                                @click="downloadReportExcel()"> Download </v-btn>
                        </v-col>
                        <v-col cols="12" md="4">
                            <v-select v-model="academy_year" label="Academy Year" density="compact" hide-details="auto" :items="academyYears" />
                        </v-col>
                        <v-col cols="12" md="3">
                            <v-select v-model="platformSelect" label="Platform" density="compact" hide-details="auto" :items="itemFilter" />
                        </v-col>
                    </v-row>
                </v-toolbar-title>
                            <!-- <v-btn  prepend-icon="mdi-check-circle" color="blue" class="ma-4" @click="synData()">
                                Syn Data
                            </v-btn> -->
                            <v-btn v-if="user.permissions.includes('md_validatd')" prepend-icon="mdi-check-circle" color="blue" class="ma-4" @click="validatedSchool()">
                                Validation
                            </v-btn>
                            <v-btn  prepend-icon="mdi-check-circle" color="blue" class="ma-4" @click="printByPlatform()">
                                Print
                            </v-btn>
                       
                <v-text-field v-model="searchValue" density="compact" label="Search site" hide-details clearable
                    class="shrink" prepend-inner-icon="mdi-clipboard-text-search" />
            </v-toolbar>
            <br>
            <v-window v-model="tab" class="left">
                    <v-card flat>
                        <EasyDataTable :headers="headers" :items="saleData" :search-field="searchField"
                            :search-value="searchValue" border-cell buttons-pagination>
                            <template #item-Action="item">
                                
                                <v-btn v-if="user.permissions.includes('edit_school_program')" density="compact" class="me-2" color="black" size="small" icon="mdi-tag-outline"
                                    variant="tonal" @click="$router.push({ path: '/schoolProgram/detail/'+ item.id })" > </v-btn>
                                    |
                                    <v-btn v-if="item.status=='validation'" density="compact" class="me-2" color="green" size="small" icon="mdi-briefcase-download"
                                    variant="tonal" @click="downloadReport(item.id)" > </v-btn>
                                    |
                                    <v-btn v-if="user.permissions.includes('md_validatd')" density="compact" class="me-2" color="red" size="small" icon="mdi-delete"
                                    variant="tonal" @click="deleteSchool(item.id)" > </v-btn>
                                    <!-- send data to form, put path in app.js. The Query will hold 2 parameters-->
                            </template>
                            <template #item-status="item">
                                    <div v-if="item.status=='waiting_validation'" class="bad-icon">
                                        {{ item.status }}
                                    </div>
                                    <div v-else class="good-icon">
                                        {{ item.status }}
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
                            
                            <template #item-province="item">
                                    {{ item.province.split("/")[0] }}
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
import { useRouter } from 'vue-router';
import Swal from "sweetalert2";
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
const platformSelect =ref('')
const academy_year = ref(null);       // selected year
const academyYears = ref([]);

watch(academy_year, async (newYear) => {
    //const response = await axios.get('/api/saleRecord');
   await fetchData();
});
const downloadReport = (id) => {
    //dialog.value = true
    axios.get('/api/schoolProgramDownload?id=' + id, { responseType: 'blob' }).then(response => {
        const url = URL.createObjectURL(new Blob([response.data], {
             type: 'application/msword'
        }))
        const link = document.createElement('a')
        link.href = url
        link.setAttribute('download', "School Contract.docx")
        document.body.appendChild(link)
        link.click()
        link.remove()
    });
}
const i =['','KC','KSP','PP','SR','BTB','All'];

const fetchYears = async () => {
  try {
    const response = await axios.get('/api/getAllYears');
    academyYears.value = response.data;

    // set default to latest year (first item, because sorted desc)
    if (academyYears.value.length > 0) {
      academy_year.value = academyYears.value[0]; // 👈 this updates v-model
    }
  } catch (error) {
    console.error("Error fetching years:", error);
  }
};

const deleteSchool = async (schoolId) => {
    const result = await Swal.fire({
        title: 'Are you sure?',
        text: 'Do you want to delete this school program?',
        icon: 'warning',
        showCancelButton: true,
        confirmButtonText: 'Yes, delete it!',
        cancelButtonText: 'Cancel',
        reverseButtons: true
    });

    if (result.isConfirmed) {
        try {
            await axios.delete(`/api/deleteSchoolProgram/${schoolId}`);
            // remove the deleted item from the local list so the UI updates immediately
            saleData.value = saleData.value.filter(item => item.id !== schoolId);
            await Swal.fire('Deleted!', 'School program deleted successfully.', 'success');
        } catch (error) {
            console.error('Error deleting school program:', error);
            Swal.fire('Error', 'Failed to delete school program.', 'error');
        }
    }
}

const validatedSchool =() =>{
    if (platformSelect.value == "")
        {
            alert ("Please select platform you want to validate")
        }
    else if (academy_year.value == "")
        {
            alert ("Please select academic year")
        }
    else{
        let result = confirm("Are you sure you want to validate "+ platformSelect.value+ " school program")
    if(result) 
       {
        axios.put(`/api/validateSchool?platform=` + platformSelect.value + `&year=` + academy_year.value)
        .then(response => {
          console.log(response.data)
          alert("Thank you for your validation")
          fetchData()
        })
        .catch(error => {
          console.error('Error fetching data:', error);
        });
       }   
    }
    
}
const printByPlatform =() =>{
    if(platformSelect.value == "")
    {
        alert("Please select platform")
    }
    else if (academy_year.value == "")
        {
            alert ("Please select academic year")
        }
    else{
        let data = platformSelect.value;
        let year = academy_year.value;
       // const url = `/schoolsContractPrint?parameter=${platformSelect.value}`;
        //window.open(url, '_blank');   
        // const url = $router.push(`/api/schoolsContractPrint/${platformSelect.value}`);
        // const url = `/api/schoolsContractPrint/${platformSelect.value}`;
        //  window.open(url, '_blank');
       // console.log (url)
       router.push({
        path: '/schoolsContractPrint',
        query:{
        platform:data,
        year:year
        }
      });
    }
}
const downloadReportExcel = () => {
    //dialog.value = true
    axios.get('/api/schoolProgramDownloadExcel?year=' + academy_year.value, { responseType: 'blob' }).then(response => {
        const url = URL.createObjectURL(new Blob([response.data], {
             type: 'application/vnd.ms-excel'
        }))
        const link = document.createElement('a')
        link.href = url
        link.setAttribute('download', "School_Validation.xlsx")
        document.body.appendChild(link)
        link.click()
        link.remove()
    });
}

const searchField = ["Id_Site","platform"];
const searchValue = ref('')
const headers: Header[] = [
    { text: "Site", value: "Id_Site", fixed: true, width: 20 },
    { text: "Platform", value: "platform", fixed: true, width: 30 },
    { text: "En_Name", value: "en_name_english", fixed: true, width: 40,sortable: true },
    { text: "En_Phone", value: "en_phone_number", width: 30 },
    { text: "School_code", value: "school_code", width: 30 },
    { text: "School_name", value: "school_name_english", width: 55 },
    { text: "Sc_director_name", value: "school_director_name_english", width: 45 },
    { text: "Nb_classes", value: "number_of_classes", width: 30 },
    { text: "School_Request", value: "bottle_requested_by_school", width: 40 },
    // { text: "number_of_boys", value: "number_of_boys", width: 40 },
    // { text: "number_of_boys", value: "number_of_girls", width: 40 }, 
    { text: "bottle_approved", value: "bottle_approved", width: 40 },
    // { text: "Bottle Status", value: "status_bottle", width: 30 },
    { text: "Status Approval", value: "status", width: 40 },
    { text: " ", value: "Action", width: 30 },
];

const items: Item[] = saleData.value;
onMounted(async () => {
    selectedDate.value = new Date().toISOString().slice(0, 7)
    start_date.value =new Date().toISOString().slice(0, 10)
    end_date.value =new Date().toISOString().slice(0, 10)
    //const response = await axios.get('/api/saleRecord');
    await fetchYears();
    await fetchData();

});
const download = (id)=>{
    alert("your id:" +id)
}
const showReport = ()=>{
    dialog.value=true
}

const validatedAllSchool = ()=> {
      
    
}
const user= computed(() =>{
    //console.log(store.state.user.permissions.includes("close_site"))
    return store.state.user
});
const itemFilter = computed(()=>{
    if(store.state.user.permissions.includes("finance_check"))
{
    return i
}
else
    return i.slice(0,-1);
})

const fetchData = async ()=> {
    loading.value = false;
    if(!selectedDate.value){
        return;
    }
    Swal.fire({
    title: "Loading data...",
    text: "Please wait while we fetch records.",
    allowOutsideClick: false,
    didOpen: () => {
      Swal.showLoading();
    }
  });
    try {
        // Send academy_year as a query parameter
        const response = await axios.get('/api/schoolProgram', {
            params: {
                academy_year: academy_year.value
            }
        });
        saleData.value = response.data;
        Swal.close();
        console.log(saleData.value)
    } catch (error) {
        console.error('Error fetching data:', error);
    } finally {
        // Optionally set loading to false here if needed
    }
};

const synData = async () => {
    try {
        const response = await axios.get('/api/insertRecordFromGoogle');
        console.log(response.data);
        alert("Data synchronized successfully");
        
    } catch (error) {
        console.error('Error synchronizing data:', error);
        alert("Failed to synchronize data");
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
