<template>
    <v-container fluid class="pa-6 white-bg">
        <v-row align="center" class="mb-4">
            <v-col cols="auto">
                <v-btn
                    prepend-icon="mdi-arrow-left"
                    variant="tonal"
                    color="primary"
                    @click="$router.push('/cashier')"
                >
                    Back
                </v-btn>
            </v-col>

            <v-spacer />

            <v-col cols="auto" class="d-flex align-center ga-1">
                <v-btn icon size="small" variant="tonal" @click="changeMonth(-1)">
                    <v-icon>mdi-chevron-left</v-icon>
                </v-btn>
                <v-text-field v-model="selectedMonth" type="month" label="Select Month" variant="outlined"
                    density="compact" hide-details style="min-width: 160px;" @change="fetchInvoices" />
                <v-btn icon size="small" variant="tonal" @click="changeMonth(1)">
                    <v-icon>mdi-chevron-right</v-icon>
                </v-btn>
            </v-col>
            <v-col cols="12" sm="auto" style="min-width: 220px;">
                <v-text-field v-model="searchValue" label="Search site / item" prepend-inner-icon="mdi-magnify"
                    clearable variant="outlined" density="compact" hide-details />
            </v-col>
            <v-col cols="auto">
                <v-btn color="success" variant="flat" prepend-icon="mdi-file-excel" @click="exportExcel">
                    Export
                </v-btn>
            </v-col>
        </v-row>

        <!-- ===== ERP TABLE ===== -->
        <v-card class="pa-4 rounded-lg elevation-1 mb-6" style="position: relative;">

            <!-- Loading overlay -->
            <div v-if="loading" class="loading-overlay">
                <v-progress-circular indeterminate color="primary" size="64"></v-progress-circular>
            </div>

            <EasyDataTable :headers="headers" :items="filteredInvoices" :search-field="searchFields"
                :search-value="searchValue" border-cell buttons-pagination table-class-name="erp-table">
                <!-- Format balances -->
                <template #item-beginning_balance="{ beginning_balance }">
                    {{ format(beginning_balance) }}
                </template>

                <template #item-transaction_amount="{ transaction_amount }">
                    {{ format(transaction_amount) }}
                </template>

                <!-- Format Month as YYYY-MM -->
                <template #item-month="{ month }">
                    {{ formatMonth(month) }}
                </template>
                <template #item-aba_date="{ aba_date }">
                    {{ aba_date }}
                </template>

                <!-- Picture QR -->
                <template #item-pictureQR="{ pictureQR }">
                    <div v-if="pictureQR" class="d-flex align-center ga-1">
                        <v-btn size="x-small" color="primary" icon @click="viewPicture(pictureQR)">
                            <v-icon size="14">mdi-eye</v-icon>
                        </v-btn>
                    ||
                        <v-btn size="x-small" color="secondary" icon :href="pictureQR" target="_blank" download>
                            <v-icon size="14">mdi-download</v-icon>
                        </v-btn>
                    </div>
                    <span v-else></span>
                </template>
                <template #item-button="item">
                    <v-btn size="x-small" color="primary" @click="invoicesRecord(item.site, item.month)">
                        <v-icon size="14">mdi-exit-to-app</v-icon>
                    </v-btn>
                </template>
            </EasyDataTable>

        </v-card>

        <!-- VIEW MODAL -->
        <v-dialog v-model="showDialog" max-width="400">
            <v-card>
                <v-img :src="currentPicture" aspect-ratio="1"></v-img>
                <v-card-actions>
                    <v-spacer></v-spacer>
                    <v-btn text color="red" @click="showDialog = false">Close</v-btn>
                </v-card-actions>
            </v-card>
        </v-dialog>

        <v-dialog v-model="showInvoiceRecord" max-width="1000">
            <v-card class="rounded-xl">
                <v-card-title class="d-flex justify-center align-center py-4 bg-grey-darken-4">
                    <span class="text-h5 font-weight-bold text-white">Invoice Records</span>
                </v-card-title>

                <v-card-text class="pa-0">
                    <v-progress-linear v-if="loadingRecords" indeterminate color="primary" height="4" />

                    <v-table v-else density="comfortable" class="custom-table">
                        <thead>
                            <tr class="bg-blue-darken-4">
                                <th class="text-center text-white">Tran ID</th>
                                <th class="text-center text-white">Month</th>
                                <th class="text-center text-white">Amount</th>
                                <th class="text-center text-white">Issue Date</th>
                                <th class="text-center text-white">Status</th>
                                <th class="text-center text-white">Sync</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="item in invoiceRecords" :key="item.id">
                                <td class="text-center font-weight-medium">{{ item.transaction_id }}</td>
                                <td class="text-center">{{ formatMonth(item.month) }}</td>
                                <td class="text-center text-green-darken-2 font-weight-bold">
                                    ៛ {{ parseFloat(item.amount).toLocaleString() }}
                                </td>
                                <td class="text-center">{{ formatMonth(item.issue_date) }}</td>
                                <td class="text-center">
                                    <v-chip :color="getStatusColor(item.payment_status)" size="small" variant="flat"
                                        class="font-weight-bold">
                                        {{ item.payment_status }}
                                    </v-chip>
                                </td>
                                <td class="text-center pa-1">
                                    <v-btn variant="text" density="compact" size="x-small"
                                        :color="item.payment_status === 'APPROVED' ? 'success' : 'primary'"
                                        :disabled="item.payment_status === 'APPROVED'" :loading="isSyncing[item.id]"
                                        @click="syncData(item)" class="sync-button">
                                        <v-icon size="16">mdi-sync</v-icon>
                                    </v-btn>
                                </td>
                            </tr>

                            <tr v-if="invoiceRecords.length === 0">
                                <td colspan="6" class="text-center py-8">
                                    <v-icon icon="mdi-file-document-outline" size="48" color="grey"></v-icon>
                                    <p class="text-grey mt-2">No invoice records found</p>
                                </td>
                            </tr>
                        </tbody>
                    </v-table>
                </v-card-text>

                <v-divider></v-divider>

                <v-card-actions class="pa-4 bg-grey-lighten-4">
                    <v-spacer></v-spacer>
                    <v-btn color="error" variant="elevated" @click="showInvoiceRecord = false" prepend-icon="mdi-close">
                        Close
                    </v-btn>
                </v-card-actions>
            </v-card>
        </v-dialog>

    </v-container>
</template>

<script lang="ts" setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { Header, Item } from "vue3-easy-data-table";
import axios from 'axios'
import Swal from 'sweetalert2'
const route = useRoute()
const invoices = ref([])
const selectedMonth = ref((route.query.month as string) || new Date().toISOString().slice(0, 7))
const searchValue = ref("")
const searchFields = ["site", "platform"]
const loading = ref(false)
const showInvoiceRecord = ref(false)
const receivedSite = ref(null)
const receivedMonth = ref(null)
const invoiceRecords = ref([])
const loadingRecords = ref(false)
const isSyncing = ref({})
const headers: Header[] = [
    { text: "Advisor", value: "advisor" },
    // { text: "Month", value: "month" },
    { text: "Site", value: "site" },
    { text: "Platform", value: "platform" },
    { text: "Beginning Balance", value: "beginning_balance" },
    { text: "Transaction Amount", value: "transaction_amount" },
    { text: "Invoice Ref", value: "invoice_ref" },
    { text: "Invoice Type", value: "invoice_type" },
    { text: "Remaining Amount", value: "remain_amount" },
    { text: "Invoice Status", value: "status" },
    { text: "Picture QR", value: "pictureQR" },
    { text: "ABA Status", value: "aba_status_code" },
    { text: "ABA Amount", value: "aba_amount" },
    { text: "Transaction ID", value: "aba_transaction_id" },
    { text: "ABA Date", value: "aba_date" },
    { text: "Button", value: "button" }

]
const items: Item[] = invoices.value;
/* ===== MODAL ===== */
const showDialog = ref(false)
const currentPicture = ref(null)
// const baseUrl = "https://sims3.teuksaat1001.com/storage/"
// const localUrl = "http://localhost:8000/storage/"
// const viewPicture = (path) => {
//   currentPicture.value = localUrl + path
//   showDialog.value = true
// }

const syncData = async (item) => {
    // Set loading to true when clicked
    isSyncing.value[item.id] = true

    try {
        const res = await axios.get('/api/getTransactionDetail', {
            params: {
                transaction_id: item.transaction_id
            }
        })

        console.log("FULL RESPONSE:", res)
        console.log("DATA:", res.data)
        console.log("data.data:", res.data?.data)

        if (res.data?.data) {
            item.payment_status = res.data.data.payment_status
        }

    } catch (error) {
        console.error("Error syncing data for transaction_id:", item.transaction_id, error)

        Swal.fire({
            icon: 'error',
            title: 'Sync Failed',
            text: `Failed to sync data for transaction ID: ${item.transaction_id}`
        })
    } finally {
        // Set loading to false when done (success or error)
        isSyncing.value[item.id] = false
    }
}
// In your component script (Composition API with Vue 3)
const getStatusColor = (status) => {
    switch (status?.toUpperCase()) {
        case 'APPROVED':
            return 'success'
        case 'PENDING':
            return 'warning'
        case 'REJECTED':
            return 'error'
        case 'PAID':
            return 'info'
        default:
            return 'grey'
    }
}

// Make sure to return it if using setup() or it's automatically available in <script setup>
const viewPicture = (path) => {
    currentPicture.value = path
    showDialog.value = true
}
/* ===== FETCH DATA ===== */
const fetchInvoices = async () => {
    console.log("Fetching invoices for month:", selectedMonth.value)
    try {
        loading.value = true
        const res = await axios.get("/api/newCashier", {
            params: { month: selectedMonth.value }
        })
        invoices.value = res.data
    } catch (err) {
        console.error(err)
    } finally {
        loading.value = false
    }
}

onMounted(() => {
    fetchInvoices()
})


const invoicesRecord = async (site, month) => {
    showInvoiceRecord.value = true
    try {
        // ✅ Show loading
        Swal.fire({
            title: 'Loading...',
            text: 'Fetching invoice records',
            allowOutsideClick: false,
            didOpen: () => {
                Swal.showLoading()
            }
        })
        const res = await axios.get('/api/invoicesRecordHistory', {
            params: {
                site: site,
                month: month
            }
        })
        invoiceRecords.value = res.data.data
        // ✅ Close loading
        Swal.close()
    } catch (error) {
        Swal.close()

        console.error(error)

        Swal.fire({
            icon: 'error',
            title: 'Error',
            text: 'Failed to fetch invoice records'
        })
    }
}
/* ===== CLIENT SIDE FILTER ===== */
const filteredInvoices = computed(() => invoices.value)

/* ===== GRAND TOTAL ===== */
const netTotal = computed(() =>
    filteredInvoices.value.reduce((sum, item) => sum + item.transaction_amount, 0)
)

/* ===== FORMAT FUNCTIONS ===== */
const format = v => `៛ ${Number(v).toLocaleString()}`

const formatMonth = (month) => {
    if (!month) return ''
    const d = new Date(month)
    return d.toISOString().slice(0, 7) // YYYY-MM
}

const formatDateABA = (date) => {
    if (!date) return '';

    // handle string case
    if (typeof date === 'string') {
        if (date.startsWith('0000-00-00')) return '';
        return date.slice(0, 10);
    }

    // handle Date object (invalid date case)
    const d = new Date(date);
    if (isNaN(d.getTime())) return '';

    return d.toISOString().slice(0, 10);
};
/* ===== MONTH NAVIGATION ===== */
const changeMonth = (delta: number) => {
    const [year, month] = selectedMonth.value.split('-').map(Number)
    const d = new Date(year, month - 1 + delta, 1)
    selectedMonth.value = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`
    fetchInvoices()
}

/* ===== EXPORT ===== */
const exportExcel = () => {
    window.open(`/api/invoices/export?month=${selectedMonth.value}`, '_blank')
}
</script>

<style scoped>
.white-bg {
    background: #fff;
}

/* ERP Table styling */
.erp-table {
    --easy-table-border-color: #ddd;
}

/* Header styling */
.erp-table th {
    background: linear-gradient(90deg, #1976d2, #42a5f5);
    color: white;
    font-weight: 600;
    font-size: 14px;
}

/* Profit/Loss colors */
.text-success {
    color: #2e7d32;
    font-weight: bold;
}
.sync-button {
    min-width: 28px !important;
    width: 28px !important;
    height: 28px !important;
    padding: 0 !important;
}
.rotate {
    animation: spin 1s linear infinite;
}

@keyframes spin {
    0% {
        transform: rotate(0deg);
    }

    100% {
        transform: rotate(360deg);
    }
}

.text-error {
    color: #d32f2f;
    font-weight: bold;
}

/* Loading overlay */
.loading-overlay {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(255, 255, 255, 0.7);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 10;
}
</style>
