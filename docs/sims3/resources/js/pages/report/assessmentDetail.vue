<template>
    <div v-if="loading" class="d-flex justify-center mt-10 pt-10">
        <v-progress-circular :size="50" color="primary" indeterminate></v-progress-circular>
    </div>
    <div v-else-if="error" class="d-flex justify-center mt-10 pt-10">
        <v-alert type="error" class="ma-4">
            {{ error }}
            <v-btn color="error" @click="loadData" class="ml-4">Retry</v-btn>
        </v-alert>
    </div>
    <div v-else>
        <v-card>
            <v-toolbar color="white" class="compresstile">
                <v-btn color="error" class="mx-5" icon @click="closeModal">
                    <v-icon size="36" style="border: 2px solid red; border-radius: 50%; padding: 2px;">mdi-close</v-icon>
                </v-btn>
                <v-toolbar-title class="text-center w-100 colorTitle" style="font-size: 2rem; font-weight: bold; letter-spacing: 2px; text-shadow: 1px 1px 4px #b3c6ff;">
                    Detail on site : <span style="color: #1976d2; text-decoration: underline dotted; font-weight: 900;">{{ siteDetail }}</span>
                </v-toolbar-title>
            </v-toolbar>
            
            <v-window v-model="tab" class="left" :touch="false">
                <v-window-item>
                    <v-card flat>
                        <div v-if="type =='assessment'">
                        <EasyDataTable :headers="headers" :items="items" :search-field="siteField" :search-value="searchValue" border-cell buttons-pagination :loading="tableLoading">
                            <template #loading>
                                <div class="d-flex justify-center pa-4">
                                    <v-progress-circular indeterminate color="primary"></v-progress-circular>
                                </div>
                            </template>
                        </EasyDataTable>
                        </div>
                        <div v-else>
                        <EasyDataTable :headers="headers1" :items="items" :search-field="siteField" :search-value="searchValue" border-cell buttons-pagination :loading="tableLoading">
                            <template #loading>
                                <div class="d-flex justify-center pa-4">
                                    <v-progress-circular indeterminate color="primary"></v-progress-circular>
                                </div>
                            </template>
                        </EasyDataTable>
                        </div>
                    </v-card>
                </v-window-item>
            </v-window>
        </v-card>
    </div>
</template>

<script lang="ts" setup>
import { Header, Item } from "vue3-easy-data-table";
import { computed, onMounted, ref, watch } from "vue";
import axios from "axios";
import Swal from 'sweetalert2';
import { useRoute } from 'vue-router';

const props = defineProps({
    getDataToForm: {
        type: String,
        default: ""
    },
    type: {
        type: String,
        default: ""
    }
});

const emit = defineEmits(['site-saved', 'cancel-modal']);

// Reactive data
const siteDetail = computed(() => props.getDataToForm);
const type = computed(() => props.type);
const route = useRoute();
const tab = ref('');
const dataTechnical = ref<Item[]>([]);
const loading = ref(true);
const tableLoading = ref(false);
const error = ref<string | null>(null);

const siteField = ref("site");
const searchValue = ref('');

// Headers definition
const headers: Header[] = [
    { text: "Site", value: "site", fixed: true, width: 15 },
    { text: "Date", value: "date_form", width: 25 },
    { text: "Technician", value: "technician", width: 25 },
    { text: "First_Assessment", value: "first_site_assessment", width: 20 },
    { text: "Modify Part", value: "which_part_do_you_want_to_modify", width: 20 },
    { text: "Main Water Source", value: "main_source_of_water", width: 20 },
    { text: "Main Source Electricity", value: "main_source_of_electricity", width: 40 },
];
const headers1: Header[] = [
    { text: "Site", value: "site", fixed: true, width: 15 },
    { text: "Date", value: "date", width: 25 },
    { text: "Technician", value: "technician", width: 25 },
    { text: "Raw Water Tank", value: "condition_of_raw_water_tank", width: 20 },
    { text: "AC_Filter", value: "condition_of_ac_filter_tank", width: 20 },
    { text: "Sand Filter", value: "condition_of_sand_filter_tank", width: 20 },
    { text: "Resin Filter", value: "condition_of_resin_filter_tank", width: 40 },
    { text: "Clear Water Tank", value: "condition_of_clear_water_tank", width: 40 },
    { text: "CIP", value: "frequency_of_the_cip_on_pipes", width: 40 },
];

// Computed items that react to dataTechnical changes
const items = computed<Item[]>(() => dataTechnical.value);

// Define loadData FIRST before using it in watch
const loadData = async () => {
    if (!siteDetail.value) {
        error.value = 'No site ID provided';
        loading.value = false;
        return;
    }

    loading.value = true;
    tableLoading.value = true;
    error.value = null;

    try {
        const response = await axios.get(`/api/assessmentDetail/detail/${siteDetail.value}?type=${type.value}`);
        console.log('API Response:', response.data);
        
        dataTechnical.value = response.data; // Direct assignment, no push
    } catch (err: any) {
        console.error('Error loading assessment data:', err);
        error.value = err.response?.data?.message || 'Failed to load assessment data';
        
        Swal.fire({
            title: 'Error!',
            text: error.value,
            icon: 'error',
            confirmButtonText: 'OK'
        });
    } finally {
        loading.value = false;
        tableLoading.value = false;
    }
};

// NOW define the watch after loadData is defined
watch(siteDetail, (newSite) => {
    if (newSite) {
        console.log('Site changed, loading data for:', newSite);
        loadData();
    }
}, { immediate: true });

const closeModal = () => {
    console.log('Closing assessment modal');
    emit('cancel-modal');
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
.swal2-popup-high {
    z-index: 3000 !important; /* higher than Vuetify dialogs */
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