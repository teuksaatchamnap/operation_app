<template>
    <v-container fluid class="pa-6 white-bg">
        <v-row class="mb-4">
            <v-col cols="12" md="3">
                <v-text-field v-model="selectedMonth" type="month" label="Select Month" variant="outlined"
                    density="comfortable" min="2025-11" @change="fetchInvoices" />
            </v-col>
            <v-col cols="12" md="4">
                <v-text-field v-model="searchValue" label="Search site / item" prepend-inner-icon="mdi-magnify"
                    clearable variant="outlined" density="comfortable" />
            </v-col>
            <v-col cols="12" md="2">
                <v-btn color="primary" class="mt-2" @click="exportExcel">
                    <v-icon left>mdi-file-export</v-icon> Export
                </v-btn>
            </v-col>
        </v-row>

        <!-- ===== ERP TABLE ===== -->
        <v-card class="pa-4 rounded-lg elevation-1 mb-6" style="position: relative;">

            <!-- Loading overlay -->
            <div v-if="loading" class="loading-overlay">
                <v-progress-circular indeterminate color="primary" size="64"></v-progress-circular>
            </div>

            <EasyDataTable :headers="headers" :items="filteredInvoices"  :search-field="searchFields"
                :search-value="searchValue" border-cell buttons-pagination table-class-name="erp-table">
                    <template #item.difference="{ item }">
    <div>
        TEST: {{ item.difference }}
    </div>
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

    </v-container>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'

const invoices = ref([])
const selectedMonth = ref(new Date().toISOString().slice(0, 7))
const searchValue = ref("")
const searchFields = ["site", "platform"]
const loading = ref(false)

const headers = [
    { text: "Site", value: "site" },
    { text: "Month", value: "month" },
    { text: "Platform", value: "platform" },
    { text: "School Budget By TS", value: "total_school_budget" },
    { text: "Total Advisor Put System", value: "total_advisor_put_system" },
    { text: "Difference", value: "difference" },
]

/* ===== MODAL ===== */
const showDialog = ref(false)
const currentPicture = ref(null)
const viewPicture = (path) => {
   currentPicture.value = path
   showDialog.value = true
 }
/* ===== FETCH DATA ===== */
const fetchInvoices = async () => {
    try {
        loading.value = true
        const res = await axios.get("/api/school", {
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

/* ===== EXPORT ===== */
const exportExcel = () => {
    window.open(`/api/school?month=${selectedMonth.value}&excel=1`, '_blank')
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
.redColor {
    color: #d32f2f;
    font-weight: bold;
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
