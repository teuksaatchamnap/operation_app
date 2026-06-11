<template>
    <div v-if="loading" class="d-flex justify-center mt-10 pt-10">
        <v-progress-circular :size="50" color="primary" indeterminate></v-progress-circular>
    </div>
    <div v-else>
        <v-card>
            <v-toolbar color="white" class="compresstile">
                <v-toolbar-title>
                    <v-row>
                        <!-- <v-col cols="12" md="4">
                            <v-text-field v-model="selectedDate" class="flex-grow-0 mr-5" label="Month" type="month" />
                        </v-col> -->
                        <v-col cols="12" md="4">
                            <v-btn rounded="lg" prepend-icon="mdi-microsoft-excel" color="green" class="ma-4"
                                @click="showReport()"> Download </v-btn>
                        </v-col>
                        <!-- <v-col cols="12" md="4">
                            <v-btn rounded="lg" prepend-icon="mdi-cloud-upload" color="blue" class="ma-4"
                                @click="uploadDialog = true">
                                Upload Contract
                            </v-btn>
                        </v-col> -->
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
                        :search-value="searchValue" border-cell buttons-pagination style="--easy-table-header-background-color: yellow;
                             --easy-table-header-text-color: green;">
                        <template #item-Action="item">
                            <!-- <v-btn density="compact" class="me-2" color="green" size="small"
                                    variant="tonal" @click="$router.push({ path: '/saleRecord/detail', query:{site:item.site, date:selectedDate } })" > Detail </v-btn>  -->
                            <!-- <v-btn density="compact" class="me-2" color="green"
                                @click="$router.push({ path: '/newEntrepreneur/detail/' + item.Id_Site })">
                                <v-icon left>mdi-pencil</v-icon>
                                Click
                            </v-btn> -->
                            <v-btn density="compact" class="me-2" color="green"
                                @click="popupDetailEntre(item)">
                                <v-icon left>mdi-pencil</v-icon>
                                Click
                            </v-btn>
                            <!-- send data to form, put path in app.js. The Query will hold 2 parameters-->
                        </template>

                        <template #item-En_Data.Contract="item">
                            <v-chip v-if="item.En_Data && item.En_Data.Contract && item.En_Data.Contract !== ''"
                                @click="downloadFile(item.En_Data.Contract)">
                                <v-icon size="small" icon="mdi-cloud-download" />
                            </v-chip>
                            <!-- <v-chip v-else>
                                <v-icon size="small" icon="mdi-minus-circle" color="red" />
                            </v-chip> -->
                        </template>

                        <template #item-modify="item">
                            <!-- <v-btn density="compact" class="me-2" color="blue" size="small"
                                    variant="tonal" @click="$router.push({ path: '/newEntrepreneur/form', query:{site:item.Id_Site} })">
                                    <v-icon left>mdi-pencil</v-icon> Modify -->
                            <!-- <v-chip size="small" color="primary" v-if="$store.state.user.permissions.includes('upload_entre_contract')" -->
                            <v-chip size="small" color="primary" 
                                @click="$router.push({ path: '/enForm/' + item.En_Data.id })">
                                <v-icon start size="x-small" icon="mdi-pencil" />
                            </v-chip> ||
                            <v-chip v-if="$store.state.user.permissions.includes('upload_entre_contract')" density="compact" class="me-2" color="blue" @click="formModify(item.En_Data?.id, item.Id_Site)">
                                <v-icon left>mdi-cloud-upload</v-icon>
                            </v-chip>
                        </template>
                        <template #item-En_Data.Entrepreneur_Phone="item">
                            {{ item.En_Data?.Entrepreneur_Phone ? '0' + item.En_Data.Entrepreneur_Phone : '' }}
                        </template>
                        <template #item-Entrepreneur_English_Name="item">
                            <div class="tooltip-container">
                                {{ item.Entrepreneur_English_Name }}
                                <span class="tooltip-text">
                                    <table border="1" bordercolor="green">
                                        <tr>
                                            <th>English Name</th>
                                            <th>Khmer Name</th>
                                            <th>Site</th>
                                        </tr>
                                        <tr>
                                            <td>{{ item.Entrepreneur_English_Name }}</td>
                                            <td>{{ item.Entrepreneur_Khmer_Name }}</td>
                                            <td>{{ item.Id_Site }}</td>
                                        </tr>
                                    </table>
                                </span>
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
                <v-card-text>
                    Report is in construction !!! Thank for your patient
                </v-card-text>
                <v-spacer></v-spacer>
                <v-card-actions>
                    <v-row>
                        <v-col cols="12" md="12" align="center">
                            <v-btn color="error" block @click="dialog = false">OK</v-btn>
                        </v-col>
                    </v-row>
                </v-card-actions>
            </v-card>
        </v-dialog>
    </div>

    <v-dialog v-model="uploadDialog" max-width="500px">
        <v-card>
            <v-card-title class="text-h6">
                Upload Contract File Site :  <span style="font-weight:bold; color:blue">{{ selectedSiteName }}</span>
            </v-card-title>
            <v-card-text>
                <v-file-input v-model="uploadFile" label="Choose PDF or ZIP" accept=".pdf,.zip" :multiple="false"
                    show-size outlined :error="fileError"
                    :error-messages="fileError ? 'Please select a file before uploading.' : ''" />

            </v-card-text>
            <v-card-actions>
                <v-spacer></v-spacer>
                <v-btn color="blue" @click="submitUpload">Upload</v-btn>
                <v-btn color="grey" @click="uploadDialog = false">Cancel</v-btn>
            </v-card-actions>
        </v-card>
    </v-dialog>
    <!-- Dialog to show popup detail -->
    <div class="text-center">
        <v-dialog v-model="popupDetailEntrepreneur" persistent max-width="1400px" content-class="custom-dialog">
            <v-card>
                <DetailEntrepreneur :getDataToForm="selectedItem.Id_Site" @cancel-modal="popupDetailEntrepreneur = false" @site-saved="popupDetailEntrepreneur = false">
                </DetailEntrepreneur>
            </v-card>
        </v-dialog>
    </div>

</template>

<script lang="ts" setup>
import { Header, Item } from "vue3-easy-data-table";
import { computed, onMounted, ref, watch } from "vue";
import axios from "axios";
import Swal from 'sweetalert2';
import DetailEntrepreneur from "./DetailEntrepreneur.vue";

const dialog = ref(false);
const tab = ref('');
const popupDetailEntrepreneur = ref(false);
const selectedItem = ref(null);
const saleData = ref([]);
const loading = ref(true);
const selectedDate = ref('');
const start_date = ref('')
const end_date = ref('')
const fileError = ref(false)
const uploadDialog = ref(false);
const uploadFile = ref<File | null>(null);
const selectedSiteId = ref(null);
const selectedSiteName = ref(null);
// Triggered from Modify button
const formModify = (siteId, siteName) => {
    if (!siteId || siteId === '' || typeof siteId === 'undefined') {
        Swal.fire('Error', "Sorry, this site might be dead or inactive site, can't upload contract.", 'error');
        return;
    }
    selectedSiteId.value = siteId;
    selectedSiteName.value = siteName;
    uploadFile.value = null;
    uploadDialog.value = true;
};

const popupDetailEntre = (item) => {
    if (!item || !item.Id_Site) {
        Swal.fire('Error', 'Invalid site data.', 'error');
        return;
    }
    setTimeout(() => {
        // loading.value = false;
        selectedItem.value = item;
        popupDetailEntrepreneur.value = true;
        console.log(selectedItem.value)
    }, 10);
};


const submitUpload = async () => {
    fileError.value = !uploadFile.value;

    if (fileError.value || !selectedSiteId.value) {
        return; // stop if file or site ID is missing
    }

    
    let formData = new FormData();
    
    // Handle both single file and file array
    let fileToUpload = Array.isArray(uploadFile.value) ? uploadFile.value[0] : uploadFile.value;
    
    formData.append("file", fileToUpload);
    formData.append("site_id", selectedSiteId.value);

    try {
        // Show SweetAlert upload progress
        Swal.fire({
            title: 'Uploading...',
            text: 'Please wait while the file is being uploaded.',
            allowOutsideClick: false,
            didOpen: () => {
                Swal.showLoading();

                // Bring SweetAlert to front of Vuetify dialog
                const swalContainer = document.querySelector('.swal2-container');
                if (swalContainer) {
                    swalContainer.style.zIndex = '3000'; // Higher than Vuetify dialog
                }
            }
        });

        const response = await axios.post('/api/uploadEntrepreneurContract', formData, {
            headers: {
                'Content-Type': 'multipart/form-data'
            },
            onUploadProgress: (progressEvent) => {
                const percentCompleted = Math.round(
                    (progressEvent.loaded * 100) / (progressEvent.total || 1)
                );
                console.log(`Upload progress: ${percentCompleted}%`);
                // You can update the Swal text dynamically if desired
            }
        });

        Swal.close(); // Close the upload modal

        // Show success
        Swal.fire('Success', 'File uploaded successfully.', 'success');

        // Reset UI state
        uploadDialog.value = false;
        uploadFile.value = null;

        fetchData(); // Refresh table or data

    } catch (error) {
        console.error(error);

        Swal.close();
        Swal.fire('Error', 'Failed to upload file. Please contact IT.', 'error');
    }
};

const popupDetail = (item) => {
    if (!item || !item.Id_Site) {
        Swal.fire('Error', 'Invalid site data.', 'error');
        return;
    }
    // Navigate to detail page with query parameters
    window.location.href = `/newEntrepreneur/detail/${item.Id_Site}`;
};

watch(uploadFile, (newVal) => {
    if (newVal) fileError.value = false;
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


const searchField = ["Id_Site", "Platform","Advisor"];
const searchValue = ref('')

const headers: Header[] = [
    { text: "Site", value: "Id_Site", fixed: true, width: 15, sortable: true },
    { text: "Platform", value: "Platform", fixed: true, width: 20, sortable: true },
    { text: "Advisor", value: "Advisor", width: 55 },
    { text: "En_Name", value: "En_Data.Entrepreneur_English_name", width: 55 },
    { text: "Kh_Name", value: "En_Data.Entrepreneur_Khmer_name", width: 55 },
    { text: "Sex", value: "En_Data.Sex", width: 20 },
    { text: "Phone", value: "En_Data.Entrepreneur_Phone", width: 35 },
    { text: "Education", value: "En_Data.Education", width: 55 },
    { text: "Previous_Job", value: "En_Data.Previous_Job", width: 40 },
    { text: "Working Date", value: "En_Data.Working_Date", width: 30 },
    { text: "Contract", value: "En_Data.Contract", width: 20 },
    { text: "History", value: "Action", width: 25 },
    { text: "Upload Contract", value: "modify", width: 35 },
];

// const headers: Header[] = [
//     { text: "Site", value: "Id_Site", fixed: true, width: 15, sortable: true },
//     { text: "Platform", value: "Platform", fixed: true, width: 20, sortable: true },
//     { text: "En_Name", value: "Entrepreneur_English_Name", width: 55 },
//     { text: "Kh_Name", value: "Entrepreneur_Khmer_Name", width: 55 },
//     { text: "Sex", value: "Sex", width: 20 },
//     { text: "Phone", value: "Phone_Number", width: 35 },
//     { text: "Education", value: "Education_Background", width: 55 },
//     { text: "Previous_Job", value: "Previous_Job", width: 40 },
//     { text: "Working Date", value: "Date_start_working", width: 30 },
//     // { text: "Contract", value: "path", width: 20 },
//     { text: "History", value: "Action", width: 25 },
//     // { text: "Upload Contract", value: "modify", width: 25 },
// ];

const items: Item[] = saleData.value;
onMounted(async () => {
    selectedDate.value = new Date().toISOString().slice(0, 7)
    start_date.value = new Date().toISOString().slice(0, 10)
    end_date.value = new Date().toISOString().slice(0, 10)
    //const response = await axios.get('/api/saleRecord');
    fetchData()

});
const showReport = () => {
    Swal.fire({
        icon: 'info',
        title: 'Report Status',
        text: 'Report is under construction. Thank you for your patience!',
    });
    // dialog.value=true
}

const fetchData = async () => {
    loading.value = true;
    if (!selectedDate.value) {
        return;
    }
    try {
        const response = await axios.get('/api/getAllEntrepreneur');
        saleData.value = [];
        //saleData.value.push(...response.data); // if put copy this result, easy data table must follow item with const items
        saleData.value = response.data; // change items in easytable to variable that retrieve array data
        console.log(saleData.value)
        loading.value = false;
    } catch (error) {
        console.error('Error fetching data:', error);

    } finally {

    }
};

</script>

<style scoped>
.hover-container {
    position: relative;
    display: inline-block;
}

.hover-info {
    position: absolute;
    background: rgba(0, 0, 0, 0.8);
    color: white;
    padding: 5px 10px;
    border-radius: 4px;
    white-space: nowrap;
    left: 100%;
    /* Move it to the right of the text */
    top: 50%;
    transform: translateY(-50%);
    z-index: 10;
}

.swal-zindex-fix {
    z-index: 3000 !important;
}

.tooltip-text th {
    background-color: #444;
    text-align: left;
    padding-right: 20px;
    /* Add padding to the right */
}

.tooltip-container {
    position: relative;
    display: inline-block;
}

.tooltip-text {
    visibility: hidden;
    width: 200px;
    background-color: #333;
    color: #fff;
    text-align: center;
    border-radius: 6px;
    padding: 5px;
    position: absolute;
    z-index: 1;
    bottom: 125%;
    /* Position above the element */
    left: 50%;
    margin-left: -100px;
    /* Center the tooltip */
    opacity: 0;
    transition: opacity 0.3s;
}

.tooltip-container:hover .tooltip-text {
    visibility: visible;
    opacity: 1;
}

/* Optional: Add an arrow to the tooltip */
.tooltip-text::after {
    content: "";
    position: absolute;
    top: 100%;
    left: 50%;
    margin-left: -5px;
    border-width: 5px;
    border-style: solid;
    border-color: #333 transparent transparent transparent;
}

.operation_status {
    color: blue;
}

.intervention {
    color: chocolate;
}

.myColor {
    color: blue !important;

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
