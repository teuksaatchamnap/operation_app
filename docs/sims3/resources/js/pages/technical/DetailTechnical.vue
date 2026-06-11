<template>
    <div v-if="loading" class="d-flex justify-center mt-10 pt-10">
        <v-progress-circular :size="50" color="primary" indeterminate></v-progress-circular>
    </div>
    <div v-else>
        <v-card>
            <v-toolbar color="white" class="compresstile">
                <v-btn color="primary" class="mx-5" icon="mdi-arrow-left" @click="$router.go(-1)" /> 
                <v-spacer></v-spacer>     
                <!-- <v-btn rounded="lg" color="green" class="ma-4" @click="downloadReport(siteDetail)"> Download </v-btn> <br> -->
            </v-toolbar>
            <v-window v-model="tab" class="left" :touch="false">
                <v-window-item >
                    <v-card flat>
                        <EasyDataTable  :headers="headers" :items="items" :search-field="siteField" :search-value="searchValue" border-cell buttons-pagination>
                            <template #item-Action="item">
                                <!-- <v-btn v-if="$store.state.user.permissions.includes('edit_technical')"
                                    icon="mdi-checkbox-marked-outline" density="compact" class="me-2" color="error"
                                    size="small" variant="tonal"
                                    @click="$router.push({ path: '/technical/form/' + item.id })" /> -->
                            </template>
                            
                        </EasyDataTable>
                    </v-card>
                </v-window-item>
            </v-window>
        </v-card>
    </div>
</template>



<script lang="ts" setup>
import { Header, Item } from "vue3-easy-data-table";
import { computed, onMounted, ref, watch} from "vue";
import axios from "axios";
import Swal from "sweetalert2";
import { useRoute } from 'vue-router';
import technicalForm from './TechnicalForm.vue'
const route = useRoute();
const tab = ref('');
const dataTechnical = ref([]);
const loading = ref(true);


const startdate = ref(new Date().toJSON().slice(0, 10));
const enddate = ref(new Date().toJSON().slice(0, 10));


const downloadReport = (site) => {
    axios.get('/api/technical/downloadSite?site=' + site, { responseType: 'blob' }).then(response => {
        const url = URL.createObjectURL(new Blob([response.data], {
            type: 'application/vnd.ms-excel'
        }))
        const link = document.createElement('a')
        link.href = url
        link.setAttribute('download', "Request&DN.xlsx")
        document.body.appendChild(link)
        link.click()
        link.remove()
    });
}

const siteField = ref("site");
const searchValue = ref('')
const headers: Header[] = [
    { text: "Site", value: "site", fixed: true, width: 30 },
    { text: "Platform", value: "site_platform", width: 40 },
    { text: "Problem Date", value: "problem_date", width: 50 },
    { text: "Intervention Date", value: "end_intervention", width: 50 },
    { text: "Site status", value: "problem_status", width: 70 },
    { text: "Problem", value: "problem_categories", width: 90 },
    { text: "Solution", value: "solutoin", width: 105 },
    { text: "Comment", value: "detailSolution", width: 90 },
    { text: "Technician", value: "technician", width:50 }, 
];

const items: Item[] = dataTechnical.value;
const showItem = (i) => {
    console.log(i.value)
}
const siteDetail = route.params.id;
onMounted(async () => {
    console.log("Your Data :" +route.params.id)
    const response = await axios.get('/api/technical/detail/'+route.params.id );
    console.log(response.data)
    dataTechnical.value.push(...response.data);
    loading.value = false;
});

const showitem = (val: Item) => {
    console.log(val);

};
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