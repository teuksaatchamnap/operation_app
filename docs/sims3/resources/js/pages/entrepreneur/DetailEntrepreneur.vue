<template>
    <div v-if="loading" class="d-flex justify-center mt-10 pt-10">
        <v-progress-circular :size="50" color="primary" indeterminate></v-progress-circular>
    </div>
    <div v-else>
        <v-card>
            <v-toolbar color="white" class="compresstile">
                <v-btn color="error" class="mx-5" icon @click="emit('cancel-modal')">
                    <v-icon size="36" style="border: 2px solid red; border-radius: 50%; padding: 2px;">mdi-close</v-icon>
                </v-btn>
                <v-toolbar-title class="text-center w-100 colorTitle" style="font-size: 2rem; font-weight: bold; letter-spacing: 2px; text-shadow: 1px 1px 4px #b3c6ff;">
                    Detail on site : <span style="color: #1976d2; text-decoration: underline dotted; font-weight: 900;">{{ siteDetail }}</span>
                </v-toolbar-title>

                <!-- <v-spacer></v-spacer> -->
                <!-- <v-btn rounded="lg" color="green" class="ma-4" @click="downloadReport(siteDetail)"> Download </v-btn> <br> -->
            </v-toolbar>
            <v-window v-model="tab" class="left" :touch="false">
                <v-window-item>
                    <v-card flat>
                        <EasyDataTable :headers="headers" :items="items" :search-field="siteField"
                            :search-value="searchValue" border-cell buttons-pagination>

                            <template #item-status="item">
                                <div v-if="item.Resignation == 0" class="good-icon">
                                    Active
                                </div>
                                <div v-else class="bad-icon">
                                    Stop work
                                </div>
                            </template>
                             <template #item-Contract="item">
                            <v-chip v-if="item.Contract && item.Contract !== ''"
                                @click="downloadFile(item.Contract)">
                                <v-icon size="small" icon="mdi-cloud-download" />
                            </v-chip>
                            <v-chip v-else>
                                No contract
                            </v-chip>
                            <!-- <v-chip v-else>
                                <v-icon size="small" icon="mdi-minus-circle" color="red" />
                            </v-chip> -->
                        </template>
                            <!-- <template #item-contract="item">
                                <v-chip @click="downloadImages(item)">
                        <v-icon size="large" icon="mdi-cloud-download"  />
                    </v-chip>
                            </template> -->
                            <template #item-Date_start_working="item">
                                <div v-if="item.Date_start_working !== null">
                                    {{ new Date(item.Date_start_working).toLocaleDateString('en-GB') }}
                                </div>
                            </template>
                            <template #item-Resignation_date="item">
                                <div v-if="item.Resignation_date !== null">
                                    {{ new Date(item.Resignation_date).toLocaleDateString('en-GB') }}
                                </div>
                            </template>
                            <template #item-delete="item">
                                <!-- <v-btn density="compact" class="me-2" color="blue" size="small"
                                    variant="tonal" @click="$router.push({ path: '/newEntrepreneur/form', query:{site:item.Id_Site} })">
                                    <v-icon left>mdi-pencil</v-icon> Modify -->
                                <v-icon v-if="$store.state.user.permissions.includes('upload_entre_contract')"
                                    color="red" class="me-2" style="cursor:pointer" @click="deleteRecord(item.id)">
                                    mdi-delete
                                </v-icon>

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
import { computed, onMounted, ref, watch } from "vue";
import axios from "axios";
import Swal from 'sweetalert2';
import { useRoute } from 'vue-router';

const props = defineProps({
    getDataToForm: {
        type: String,
        default: 0 // Or any default value you prefer
    }
});
const emit = defineEmits(['site-saved', 'cancel-modal']);
const siteDetail = computed(() => props.getDataToForm);

const route = useRoute();
const tab = ref('');
const dataTechnical = ref([]);
const loading = ref(true);

const siteField = ref("site");
const searchValue = ref('')
const headers: Header[] = [

    { text: "Site", value: "Id_Site", fixed: true, width: 15 },
    // { text: "Status", value: "Status", width: 25 },
    { text: "Kh_Name", value: "Entrepreneur_Khmer_name", width: 25 },
    { text: "En_Name", value: "Entrepreneur_English_name", width: 25 },
    { text: "Sex", value: "Sex", width: 20 },
    { text: "Working_Date", value: "Working_Date", width: 20 },
    { text: "Resign Date", value: "Resignation_Date", width: 20 },
    { text: "Reason Leave", value: "Reason_Resign", width: 40 },
    { text: "Detail", value: "Detail_Resign", width: 60 },
    //  { text: "Contract", value: "Contract", width: 25 },
    { text: "", value: "delete", width: 10 },
];

const items: Item[] = dataTechnical.value;

onMounted(async () => {
   // const response = await axios.get('/api/newEntrepreneurDetail/detail/' + route.params.id);
    const response = await axios.get('/api/newEntrepreneurDetail/detail/' + siteDetail.value);
    console.log(response.data)
    dataTechnical.value.push(...response.data);
    // dataTechnical.value.push(...response.data.getData);

    loading.value = false;
});

const downloadFile = async (fileName) => {
    try {
        // Show progress notification or spinner (optional)
        const toastLoading = Swal.fire({
            title: 'Downloading...',
            text: 'Please wait while the file is being downloaded.',
            allowOutsideClick: false,
            didOpen: () => {
                Swal.showLoading();
            }
        });

        const response = await axios.get(`/api/downloadEntrepreneurContract/${fileName}`, {
            responseType: 'blob',
            onDownloadProgress: (progressEvent) => {
                const percentCompleted = Math.round(
                    (progressEvent.loaded * 100) / (progressEvent.total || 1)
                );
                // Optionally update progress UI here
                console.log(`Download progress: ${percentCompleted}%`);
            }
        });

        // Finish the loading toast
        Swal.close();

        // Trigger download
        const blob = new Blob([response.data], { type: response.headers['content-type'] });
        const link = document.createElement('a');
        link.href = URL.createObjectURL(blob);
        link.download = fileName;
        link.click();

        // Show success message
        Swal.fire('Success', 'File downloaded successfully.', 'success');

    } catch (error) {
        console.error('Error downloading file:', error);

        Swal.fire('Error', "Couldn't download the file. Please try again.", 'error');
    }
};


const downloadImages = (id) => {
    console.log(id.Code_Entrepreneur);
    alert("Download contract is in construction " + id.Code_Entrepreneur)
}
const deleteRecord = async (id) => {
    // Import SweetAlert2 if not already imported
    // import Swal from 'sweetalert2';
    emit('cancel-modal');
    const result = await Swal.fire({
        title: 'Are you sure?',
        text: "Do you really want to delete this record?",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#d33',
        cancelButtonColor: '#3085d6',
        confirmButtonText: 'Yes, delete it!'
    });

    if (result.isConfirmed) {
        try {
            const response = await axios.delete(`/api/entrepreneur/delete/${id}`);
            if (response.data.status === 'success') {
                Swal.fire('Deleted!', 'Record has been deleted.', 'success');
                window.location.reload();
            } else {
                Swal.fire('Failed!', 'Failed to delete record.', 'error');
            }
        } catch (error) {
            console.error("Error deleting record:", error);
            Swal.fire('Error!', 'An error occurred while deleting the record.', 'error');
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