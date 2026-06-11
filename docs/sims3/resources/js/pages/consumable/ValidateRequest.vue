<template>
    <div v-if="loading" class="d-flex justify-center mt-10 pt-10">
        <v-progress-circular :size="50" color="primary" indeterminate></v-progress-circular>
    </div>
    <div v-else>
        <v-card>
            <v-toolbar color="white" class="compresstile">
                <v-spacer></v-spacer>
                <v-btn rounded="lg" color="blue" class="ma-4" elevation="2" outlined
                    @click="validateItem(email, dateapproval)">
                    <v-icon left>mdi-check</v-icon>
                    Validate
                </v-btn>
                <v-spacer></v-spacer>
                <v-btn rounded="lg" color="red" class="ma-4" elevation="2" outlined
                    @click="rejectValidate(email, dateapproval)">
                    <v-icon left>mdi-check</v-icon>
                    Rejected
                </v-btn>
                <v-spacer></v-spacer>

            </v-toolbar>
            <v-window v-model="tab" class="left" :touch="false">
                <v-window-item>
                    <v-card flat>
                        <EasyDataTable :headers="headers" :items="items" :search-field="siteField"
                            :search-value="searchValue" border-cell buttons-pagination>
                            <template #item-Validate="item">
                                <div v-if="item.Validate == 0">
                                    <span class="non_operation_status">
                                        Wait Approval
                                    </span>
                                </div>
                                <div v-else>
                                    <span class="Fixed">
                                        Approved
                                    </span>
                                </div>
                            </template>
                            <template #item-Price_Item="item">
                                <span>{{ (parseFloat(item.Price_Item) / 4070).toFixed(2) }}</span>
                            </template>
                        </EasyDataTable>
                        <div class="text-center font-bold mt-2">
                            <strong>Total Amount : </strong>
                            <span style="color: red; font-weight: bold;">
                                 <strong>{{ (totalPrice / 4070).toFixed(2) }} $</strong>
                            </span>
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
import Swal from "sweetalert2";
import { useRoute } from 'vue-router';

const route = useRoute();
const tab = ref('');
const dataTechnical = ref([]);
const loading = ref(true);

const siteField = ref("site");
const searchValue = ref('')
const headers: Header[] = [
    { text: "Site", value: "Id_Site", fixed: true, width: 30 },
    { text: "Month", value: "Month", width: 45 },
    { text: "Item Code", value: "Item", width: 40 },
    { text: "Kh Name", value: "Khmer_name", width: 100 },
    { text: "Eng Name", value: "English_name", width: 100 },
    { text: "QTY", value: "Number_Item", width: 30 },
    { text: "Price $", value: "Price_Item", width: 45 },
    { text: "Payment", value: "Payment_method", width: 70 },
    { text: "PO", value: "PO", width: 50 },
    { text: "Supplier", value: "Supplier", width: 50 },
    { text: "Requestor", value: "EmailRequestor", width: 110 },
    { text: "Status", value: "Validate", width: 60 },
];

const items: Item[] = dataTechnical.value;
const showItem = (i) => {
    console.log(i.value)
}
const email = route.params.email;
const dateapproval = route.params.dateapproval;
onMounted(async () => {
    // alert("email: " + email + " dateapproval: " + dateapproval);
    const response = await axios.get('/api/getRequestConsumable?email=' + email + "&dateapproval=" + dateapproval);
    console.log(response.data)
    dataTechnical.value.push(...response.data);
    loading.value = false;
});

const showitem = (val: Item) => {
    console.log(val);

};
const totalPrice = computed(() => {
    return items.reduce((sum, item) => {
        return sum + parseFloat(item.Price_Item || 0);
    }, 0).toFixed(2);
});
const rejectValidate = async (email, dateapproval) => {
    const { value: reason } = await Swal.fire({
        title: 'Reject Validation.',
        input: 'textarea',
        inputLabel: 'Remember if you reject, it will delete all items in table',
        inputPlaceholder: 'Type your reason here...',
        inputAttributes: {
            'aria-label': 'Type your reason here'
        },
        showCancelButton: true,
        confirmButtonText: 'Submit',
        cancelButtonText: 'Cancel',
    });

    if (!reason || reason.trim() === '') {
        Swal.fire('Error', 'Reason for rejection cannot be blank.', 'error');
        return;
    }
    
    Swal.fire({
        title: 'Submitting...',
        text: 'Please wait while the rejection is being processed.',
        allowOutsideClick: false,
        didOpen: () => {
            Swal.showLoading();
        },
    });
    try {
        const response = await axios.delete('/api/rejectValidation', {
            params: {
                email: email,
                dateapproval: dateapproval,
                reason: reason
            }
        });
        console.log(response.data);
        Swal.close();
        Swal.fire('Success', 'Rejection submitted successfully.', 'success');
        window.location.reload();
    } catch (error) {
        console.error(error);
        Swal.close();
        Swal.fire('Error', 'An error occurred while submitting the rejection.', 'error');
    }
};




const validateItem = async (email, dateapproval) => {
    const result = await Swal.fire({
        title: 'Are you sure?',
        text: 'You are about to validate the items.',
        icon: 'warning',
        showCancelButton: true,
        confirmButtonText: 'Yes, validate it!',
        cancelButtonText: 'Cancel',
    });

    if (result.isConfirmed) {
        Swal.fire({
            title: 'Validating...',
            text: 'Please wait while the items are being validated.',
            allowOutsideClick: false,
            didOpen: () => {
                Swal.showLoading();
            },
        });
        try {
            const response = await axios.put('/api/validateRequestConsumable?email=' + email + "&dateapproval=" + dateapproval);
            console.log(response.data)
            Swal.close();
            Swal.fire('Success', 'Item validated successfully.', 'success');
            window.location.reload();
        } catch (error) {
            console.error(error);
            Swal.close();
            Swal.fire('Error', 'An error occurred while validating the item.', 'error');
        }
    }
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