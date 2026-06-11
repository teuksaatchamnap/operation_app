<template>
    <div v-if="loading" class="d-flex justify-center mt-10 pt-10">
        <v-progress-circular :size="50" color="primary" indeterminate></v-progress-circular>
    </div>
    <div v-else>
        <v-card>
            <v-toolbar color="white" class="compresstile">
                <v-toolbar-title>
                    <!-- <v-btn class="ml-5 mt-2 mr-5" color="secondary" icon="mdi-microsoft-excel" /> -->
                    <v-row>
                        <v-col cols="12" md="6">
                            <v-text-field v-model="displayStartDate" type="date" density="compact" label="Start Date"
                                hide-details="auto" />
                        </v-col>
                        <v-col cols="12" md="6">
                            <v-text-field v-model="displayEndDate" type="date" density="compact" label="End Date"
                                hide-details="auto" />
                        </v-col>
                    </v-row>
                </v-toolbar-title>
                <v-btn rounded="lg" color="blue" class="ma-4" prepend-icon="mdi-cloud-download" @click="downloadReport">
                    Report </v-btn>
                <v-btn rounded="lg" prepend-icon="mdi-microsoft-excel" color="green" class="ma-4 "
                    @click="downloadDashboard"> Dashboard </v-btn>
                <v-btn rounded="lg" prepend-icon="mdi-stocking" color="cyan" class="ma-4 "
                    @click="$router.push({ path: '/techStock' })"> Mini Stock </v-btn>
                <v-btn v-if="$store.state.user.permissions.includes('technician_advisor_site')" rounded="lg"
                    color="blue" class="ma-1" prepend-icon="mdi-cloud-download" @click="dialog1 = true">
                    Upload</v-btn>
                <v-btn prepend-icon="mdi-plus" color="red" rounded="lg"
                    @click="$router.push({ path: '/technical/emailForm' })">Add
                </v-btn>

                <v-text-field v-model="searchValue" density="compact" label="Search site only in all platform tab"
                    hide-details clearable class="shrink" prepend-inner-icon="mdi-clipboard-text-search" />

                <!--Dialog box-->
                <template v-slot:extension>
                    <v-tabs v-model="tab" align-tabs="title">
                        <v-tab v-for="titlePlatform in platform" :key="titlePlatform" :value="titlePlatform"
                            class="colorTitle">
                            <v-btn depressed color="primary">
                                {{ titlePlatform }}
                            </v-btn>
                        </v-tab>
                    </v-tabs>
                </template>
            </v-toolbar>

            <v-window v-model="tab" class="left" :touch="false">
                <v-window-item v-for="sitePlatform in platform" :key="sitePlatform" :value="sitePlatform">
                    <v-card flat>
                        <EasyDataTable v-if="sitePlatform == 'all_platform'" :headers="headers" :items="filterData"
                            :search-field="siteField" :search-value="searchValue" border-cell buttons-pagination>
                            <template #item-site.Id_Site="item">
                                <div v-if="item.status == 'Waiting Validation'">
                                    <span class="text-pink-500">
                                        <v-badge content="new" color="error" inline>
                                            {{ item.site.Id_Site }}
                                        </v-badge>
                                    </span>
                                </div>
                                <div v-else>
                                    <span class="text-pink-500">
                                        {{ item.site.Id_Site }}
                                    </span>
                                </div>
                            </template>

                            <template #item-problem_status="item">
                                <span class="non_operation_status">
                                    <div v-if="item.problem_status == 'Can Not Produce'">
                                        Non_Operation
                                    </div>
                                    <div v-else class="operation_status">
                                        Site_Operation
                                    </div>
                                </span>
                            </template>
                            <template #item-status="item">
                                <span class="non_operation_status">
                                    <div v-if="item.status == 'Waiting Validation'">
                                        {{ item.status }}
                                    </div>
                                    <div v-else-if="item.status == 'Validate_Ongoing'" class="Validate_Ongoing">
                                        {{ item.status }}
                                    </div>
                                    <div v-else class="Fixed">
                                        {{ item.status }}
                                    </div>
                                </span>
                            </template>
                            <template #item-solution="item">
                                <v-btn class="alertProblemSolution" color="success" size="small"
                                    @click="alertDisplay(item)">
                                    Detail
                                </v-btn>
                            </template>
                            <template #item-history="item">
                                <v-btn class="alertProblemSolution" color="blue" size="small"
                                    @click="$router.push({ path: '/technical/detail/' + item.site.Id_Site })">
                                    click
                                </v-btn>
                            </template>
                            <template #item-rt_request_stock="item">
                                <div v-if="item.managerValidateItem == 'validated_item'" class="Fixed">
                                    Validated Item
                                </div>
                                <div v-else>
                                    {{ item.rt_request_stock }}
                                </div>
                            </template>
                            <template #item-Action="item">
                                <v-btn
                                    v-if="item.site.technician_site == current_email || $store.state.user.permissions.includes('edit_technical')"
                                    icon="mdi-checkbox-marked-outline" density="compact" class="me-2" color="error"
                                    size="small" variant="tonal" @click="getData(item)" />
                            </template>
                            <template #item-Request="item">
                                <v-btn v-if="item.managerValidateItem == 'validated_item'" icon="mdi-microsoft-excel"
                                    density="compact" class="me-2" color="green" size="medium" variant="tonal"
                                    @click="downloadDN(item.id)" />
                            </template>
                        </EasyDataTable>

                        <!--Show else data-->
                        <EasyDataTable v-else :headers="headers" :items="filterData" :search-field="searchField"
                            :search-value="sitePlatform" border-cell buttons-pagination>
                            <template #item-solution="item">
                                <v-btn class="alertProblemSolution" color="success" size="small"
                                    @click="alertDisplay(item)">
                                    Detail
                                </v-btn>
                            </template>
                            <template #item-problem_status="item">
                                <span class="non_operation_status">
                                    <div v-if="item.problem_status == 'Can Not Produce'">
                                        Non_Operation
                                    </div>
                                    <div v-else class="operation_status">
                                        Site_Operation
                                    </div>
                                </span>
                            </template>
                            <template #item-history="item">
                                <v-btn class="alertProblemSolution" color="blue" size="small"
                                    @click="$router.push({ path: '/technical/detail/' + item.site.Id_Site })">
                                    click
                                </v-btn>
                            </template>
                            <template #item-status="item">
                                <span class="non_operation_status">
                                    <div v-if="item.status == 'Waiting Validation'">
                                        {{ item.status }}
                                    </div>
                                    <div v-else-if="item.status == 'Validate_Ongoing'" class="Validate_Ongoing">
                                        {{ item.status }}
                                    </div>
                                    <div v-else class="Fixed">
                                        {{ item.status }}
                                    </div>
                                </span>
                            </template>
                            <template #item-site.Id_Site="item">
                                <div v-if="item.status == 'Waiting Validation'">
                                    <span class="text-pink-500">
                                        <v-badge content="new" color="error" inline>
                                            {{ item.site.Id_Site }}
                                        </v-badge>
                                    </span>
                                </div>
                                <div v-else>
                                    <span class="text-pink-500">
                                        {{ item.site.Id_Site }}
                                    </span>
                                </div>
                            </template>
                            <template #item-rt_request_stock="item">
                                <div v-if="item.managerValidateItem == 'validated_item' || item.rt_request_stock == 'validated_item'"
                                    class="Fixed">
                                    Validated Item
                                </div>
                                <div v-else>
                                    {{ item.rt_request_stock }}
                                </div>

                            </template>
                            <template #item-Action="item">
                                <div v-if="item.status != 'Fixed'">
                                    <v-btn v-if="item.site.technician_site == current_email"
                                        icon="mdi-checkbox-marked-outline" density="compact" class="me-2" color="error"
                                        size="medium" variant="tonal" @click="getData(item)" />
                                </div>
                                <div v-else>
                                    <v-btn v-if="$store.state.user.permissions.includes('edit_technical')"
                                        icon="mdi-checkbox-marked-outline" density="compact" class="me-2" color="error"
                                        size="medium" variant="tonal" @click="getData(item)" />
                                </div>
                                <!-- @click="$router.push({ path: '/technical/form/' + item.id })" -->
                            </template>
                            <template #item-Request="item">
                                <v-btn v-if="item.managerValidateItem == 'validated_item'" icon="mdi-microsoft-excel"
                                    density="compact" class="me-2" color="green" size="medium" variant="tonal"
                                    @click="downloadDN(item.id)" />
                            </template>
                        </EasyDataTable>
                    </v-card>
                </v-window-item>
            </v-window>
        </v-card>
    </div>
    <div class="text-center">
        <v-dialog v-model="dialog" persistent max-width="1400px" content-class="custom-dialog">
            <v-card>
                <DialogForm :getDataToForm="selectedItem.id" @cancel-modal="dialog = false" @site-saved="getSites()">
                </DialogForm>
            </v-card>
        </v-dialog>
    </div>
    <div class="text-center">
        <v-dialog v-model="dialog1" max-width="500">
            <v-card>
                <v-row>
                    <v-col cols="6">
                        <v-card-title class="text-h6">
                            Upload Excel File
                        </v-card-title>
                    </v-col>
                    <v-col cols="6" class="d-flex align-center justify-end pr-8">
                        <a href="/api/templateSiteTechnician" class="text-h5">
                            <v-btn color="primary">Template</v-btn>
                        </a>
                    </v-col>
                    
                </v-row>
                <v-card-text>
                    <v-file-input ref="fileInput" accept=".xlsx,.xls,.csv" label="Select Excel file"
                        prepend-icon="mdi-file-excel" outlined :error="fileError"
                        :error-messages="fileError ? ['Please select an Excel file'] : []" />
                </v-card-text>

                <v-card-actions>
                    <v-spacer />
                    <v-btn text color="grey" @click="dialog1 = false">Cancel</v-btn>
                    <v-btn color="blue" :loading="loading" @click="submitUpload">
                        Upload
                    </v-btn>
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
import DialogForm from './TechnicalForm.vue';

const dialog1 = ref(false);
const file = ref(null);
const dialog = ref(false);
const selectedItem = ref(null);
const tab = ref('');
const dataTechnical = ref([]);
const loading = ref(true);
const platform = [
    'all_platform', 'PP', 'BTB', 'KSP', 'KC', 'SR'
];
const fileError = ref(false);
const fileInput = ref(null);
const submitUpload = async () => {
    const selectedFile = fileInput.value?.files?.[0]; // get actual File object

    if (!selectedFile) {
        fileError.value = true;
        return;
    }

    fileError.value = false;
    loading.value = true;

    const formData = new FormData();
    formData.append("file", selectedFile);

    try {
        await axios.post("/api/uploadSiteTechnician", formData, {
            headers: { "Content-Type": "multipart/form-data" },
        });

        dialog1.value = false;
        // reset input
        if (fileInput.value) fileInput.value.reset();
        fileError.value = false;

        Swal.fire({
            icon: 'success',
            title: 'Upload successful!',
            showConfirmButton: false,
            timer: 1500
        });
    } catch (error) {
        console.error(error);
        Swal.fire({
            icon: 'error',
            title: 'Upload failed!',
            showConfirmButton: false,
            timer: 1500
        });
    } finally {
        loading.value = false;
    }
};

const startdate = ref(null); // Used for filtering (null by default)
const displayStartDate = ref(new Date().toJSON().slice(0, 10)); // Used for display (current date)

const enddate = ref(null); // Used for filtering (null by default)
const displayEndDate = ref(new Date().toJSON().slice(0, 10)); // Used for display (current date)
watch(displayStartDate, (newValue) => {
    startdate.value = newValue || null; // Set startdate to null if newValue is empty
});

// Watch for changes in displayEndDate and update enddate
watch(displayEndDate, (newValue) => {
    enddate.value = newValue || null; // Set enddate to null if newValue is empty
});
const downloadReport = () => {
    if (startdate.value == "" || enddate.value == "") {
        Swal.fire({
            icon: 'error',
            text: 'Please select start date and end date!',
        })
        return
    }
    else {
        Swal.fire({
            title: 'Loading...',
            text: 'Please wait while the file is being prepared.',
            allowOutsideClick: false,
            didOpen: () => {
                Swal.showLoading();
            }
        });
        axios.get('/api/downloadReport?startdate=' + displayStartDate.value + '&enddate=' + displayEndDate.value, { responseType: 'blob' }).then(response => {
            const url = URL.createObjectURL(new Blob([response.data], {
                type: 'application/vnd.ms-excel'
            }))
            const link = document.createElement('a')
            link.href = url
            link.setAttribute('download', "Technical_Intervention.xlsx")
            document.body.appendChild(link)
            link.click()
            link.remove()
            Swal.close(); // Close the Swal loading dialog
        });
    }
}

const downloadDashboard = () => {
    const month = displayStartDate.value.slice(0, 7)
    // const month = new Date().toISOString().slice(0, 7);
    if (month == "") {
        Swal.fire({
            icon: 'error',
            text: 'Please select start date ',
        })
        return
    }
    else {
        Swal.fire({
            title: 'Loading...',
            text: 'Please wait while the file is being prepared.',
            allowOutsideClick: false,
            didOpen: () => {
                Swal.showLoading();
            }
        });
        axios.defaults.headers.get['Access-Control-Allow-Origin'] = '*';
        axios.get("https://dashboard.teuksaat1001.com/TechnicalDashboard?month=" + month + "&ts=" + (new Date()).toISOString(), {
            withCredentials: false,
            responseType: 'blob'
        }).then(response => {
            const url = URL.createObjectURL(new Blob([response.data], {
                type: 'application/vnd.ms-excel'
            }))
            const link = document.createElement('a')
            link.href = url
            link.setAttribute('download', "Technical_dashboard_" + month + ".xlsx")
            document.body.appendChild(link)
            link.click()
            link.remove()
            Swal.close(); // Close the Swal loading dialog
        }).catch(error => {
            Swal.fire({
                icon: 'error',
                title: 'Oops...',
                text: 'Something went wrong!',
            });
        });
    }
}
const downloadDN = (id) => {
    axios.get('/api/downloadDN?dnid=' + id, { responseType: 'blob' }).then(response => {
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
const sitePlatform = ref('');
const disabled = ref();
const siteField = ref("site.Id_Site");
const searchField = ("site_platform");
const searchValue = ref('')
const current_email = ref('')
const headers: Header[] = [
    { text: "Site", value: "site.Id_Site", fixed: true, width: 60 },
    { text: "Platform", value: "site_platform", width: 50 },
    { text: "Problem Date", value: "problem_date", width: 70 },
    { text: "Problem & solution", value: "solution", width: 70 },
    { text: "History", value: "history", width: 40 },
    { text: "Site status", value: "problem_status", width: 70 },
    { text: "Plan_Date", value: "start_intervention", width: 70 },
    { text: "Intervention Date", value: "end_intervention", width: 90 },
    { text: "Technician", value: "technician" },
    { text: "Intervention Type", value: "reporting", width: 105 },
    { text: "Status", value: "status" },
    { text: "Stock", value: "rt_request_stock", width: 75 },
    { text: "Action", value: "Action", width: 40 },
    { text: "Request", value: "Request", width: 40 },
];

const items: Item[] = dataTechnical.value;

onMounted(async () => {
    getSites();

});

const getSites = async () => {
    loading.value = true;
    const response = await axios.get('/api/technical');
    dataTechnical.value = [];
    dataTechnical.value = response.data.result;
    //dataTechnical.value.push(...response.data.result);
    current_email.value = response.data.email
    loading.value = false;
}

const getData = (item) => {
    // loading.value = true;
    setTimeout(() => {
        // loading.value = false;
        selectedItem.value = item;
        dialog.value = true;
    }, 10);
}

const alertDisplay = (val: Item) => {
    Swal.fire({
        title: 'Site Information',
        html: `
            <table border="1" style="width:100%;font-family: 'Arial'; font-size: 16px;" class="table table-bordered" >
                <tr>
                    <th>Site</th>
                    <td>${val.site.Id_Site}</td>
                </tr>
                <tr>
                    <th>Problem</th>
                    <td>${val.site_problem_description}</td>
                </tr>
                <tr>
                    <th>Detail Problem</th>
                    <td>${val.comment_problem}</td>
                </tr>
                <tr>
                    <th>Contact</th>
                    <td>${val.phone_number}</td>
                </tr>
                <tr>
                    <th>RT Solution</th>
                    <td>${val.rt_solution}</td>
                </tr>
                <tr>
                    <th>Report By</th>
                    <td>${val.report_by}</td>
                </tr>
            </table>
        `,
        customClass: {
            popup: 'swal2-popup',
            title: 'swal2-title',
            htmlContainer: 'swal2-html-container',
        }

    });
};
const showitem = (val: Item) => {
    console.log(val);

};

const filterData = computed(() => {
    // Parse startdate and enddate in UTC (if provided)
    const st = startdate.value ? new Date(startdate.value + 'T00:00:00Z') : null;
    const en = enddate.value ? new Date(enddate.value + 'T23:59:59.999Z') : null;
    const sea = searchValue.value ? searchValue.value.trim() : "";

    return dataTechnical.value.filter((row) => {
        // Parse problem_date in UTC
        const sampleDate = new Date(row.problem_date + 'T00:00:00Z');

        // Log problem_date and parsed UTC date for debugging
        // console.log("problem_date:", row.problem_date, "Parsed UTC Date:", sampleDate.toISOString());

        // Check if the parsed date is valid
        if (isNaN(sampleDate.getTime())) {
            console.error("Invalid problem_date:", row.problem_date);
            return false; // Exclude rows with invalid dates
        }

        // Date range logic:
        // If startdate is not provided, treat it as "no lower limit".
        // If enddate is not provided, treat it as "no upper limit".
        const isWithinDateRange = (!st || sampleDate >= st) && (!en || sampleDate <= en);

        // Text search logic:
        // If searchValue is not provided, treat it as "match all".
        const matchesText = sea
            ? row.site.Id_Site && row.site.Id_Site.toLowerCase().includes(sea.toLowerCase())
            : true;

        // Return true only if both conditions are met
        return isWithinDateRange && matchesText;
    });
});
// const filterData2 = computed(() => {
//     const st = startdate.value ? new Date(startdate.value).setHours(0, 0, 0, 0) : null;
//     const en = enddate.value ? new Date(enddate.value).setHours(23, 59, 59, 999) : null;
//     const sea = searchValue.value ? searchValue.value.trim() : "";

//     return dataTechnical.value.filter((row) => {
//         const sampleDate = new Date(row.problem_date).setHours(0, 0, 0, 0);
//         const isWithinDateRange =
//             (!st || sampleDate >= st) && (!en || sampleDate <= en);
//         // Match site field input (case-insensitive)
//         const matchesText = sea
//             ? row.site.Id_Site &&
//             row.site.Id_Site.toLowerCase().includes(sea.toLowerCase())
//             : true;
//         // Return true only if both conditions are met
//         return isWithinDateRange && matchesText;
//     });
// });

const alertId = (val) => {
    console.log(val);
}
</script>

<style>
.operation_status {
    color: blue;
}

.custom-dialog {
    z-index: 1050 !important;
    /* Higher than default */
}

.non_operation_status {
    color: red;
}

.left {
    padding-left: 10px;
    padding-right: 10px;
}

.swal-zindex {
    z-index: 10000 !important;
    /* Ensure this is higher than the z-index of v-dialog */
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