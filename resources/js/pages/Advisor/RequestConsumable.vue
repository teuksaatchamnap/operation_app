<template>
    <v-card rounded="xl" elevation="3" class="overflow-hidden">
                    <!-- Header -->
                    <div class="header-gradient pa-4 pa-md-5">
                        <div class="d-flex align-center justify-space-between">
                            <div>
                                <div class="text-h6 font-weight-bold text-white">Material Order Form</div>
                                <div class="text-caption text-white opacity-80 mt-1">Create and manage item orders</div>
                            </div>
                            <v-chip color="white" variant="flat" size="small" class="font-weight-bold">
                                {{ orderItems.length }} Item(s)
                            </v-chip>
                        </div>
                    </div>

                    <v-card-text class="pa-3 pa-md-4">
                        <!-- Site & Month -->
                        <v-row density="comfortable">
                            <v-col cols="12" md="6">
                                <v-autocomplete v-model="form.site" :items="sites" label="Site"
                                    prepend-inner-icon="mdi-map-marker" variant="outlined" density="compact"
                                    hide-details clearable autocomplete="off" />
                            </v-col>
                            <v-col cols="12" md="6">
                                <v-text-field v-model="form.month" label="Month" type="month"
                                    prepend-inner-icon="mdi-calendar" variant="outlined" density="compact"
                                    hide-details />
                            </v-col>
                        </v-row>

                        <!-- Add Item Panel -->
                        <v-card rounded="xl" class="pa-3 mt-3">
                            <v-autocomplete v-model="selectedItem" :items="items"
                                :item-title="(i) => `${i.code} || ${i.name}`" item-value="code" label="Search Item"
                                placeholder="Type item code or name" prepend-inner-icon="mdi-magnify"
                                variant="outlined" density="compact" return-object clearable class="mb-3"
                                autocomplete="off" @update:modelValue="selectItem">
                                <template #item="{ props, item }">
                                    <v-list-item v-if="item" v-bind="props" rounded="lg">
                                        <template #title>
                                            <span class="font-weight-bold">{{ item.code }}</span>
                                        </template>
                                        <template #subtitle>
                                            <div>{{ item.name }}</div>
                                            <div class="text-primary">{{ formatCurrency(item.price) }} / {{
                                                item.unit }}</div>
                                        </template>
                                    </v-list-item>
                                </template>
                            </v-autocomplete>

                            <v-row density="comfortable">
                                <v-col cols="12" sm="4">
                                    <v-text-field :model-value="formatCurrency(form.price)" label="Price"
                                        prepend-inner-icon="mdi-currency-riel" variant="outlined" density="compact"
                                        readonly hide-details />
                                </v-col>
                                <v-col cols="12" sm="4">
                                    <v-text-field v-model.number="form.qty" label="Quantity" type="number"
                                        prepend-inner-icon="mdi-counter" variant="outlined" density="compact" min="1"
                                        hide-details />
                                </v-col>
                                <v-col cols="12" sm="4">
                                    <v-text-field v-model="form.unit" label="Unit" prepend-inner-icon="mdi-ruler"
                                        variant="outlined" density="compact" readonly hide-details />
                                </v-col>
                            </v-row>

                            <div class="d-flex align-center justify-space-between mt-3">
                                <div>
                                    <div class="text-caption text-grey">Item Total</div>
                                    <div class="text-subtitle-1 font-weight-bold text-primary">{{
                                        formatCurrency(itemTotal) }}</div>
                                </div>
                                <v-btn color="primary" size="small" rounded="xl" prepend-icon="mdi-plus"
                                    class="text-none font-weight-bold" @click="addItem">
                                    Add Item
                                </v-btn>
                            </div>
                        </v-card>

                        <v-divider class="my-3" />

                        <!-- Empty State -->
                        <div v-if="!orderItems.length" class="text-center py-8">
                            <v-icon size="50" color="grey-lighten-1">mdi-cart-outline</v-icon>
                            <div class="text-body-1 mt-3 text-grey-darken-1">No Items Added Yet</div>
                            <div class="text-body-2 text-grey mt-1">Search and add items to create your order</div>
                        </div>

                        <!-- Mobile Cards -->
                        <div v-if="orderItems.length" class="d-flex d-md-none flex-column ga-3">
                            <v-card v-for="(item, index) in orderItems" :key="index" rounded="xl" variant="outlined"
                                class="pa-3">
                                <div class="d-flex justify-space-between align-start">
                                    <div>
                                        <div class="font-weight-bold">{{ item.code }}</div>
                                        <div class="text-body-2 mt-1 text-grey">{{ item.item_name }}</div>
                                    </div>
                                    <v-btn icon="mdi-delete" color="red" size="small" variant="text"
                                        @click="removeItem(index)" />
                                </div>
                                <div class="d-flex flex-wrap ga-3 mt-2 text-body-2">
                                    <span><span class="text-grey">Price:</span> {{ formatCurrency(item.price) }}</span>
                                    <span><span class="text-grey">Qty:</span> {{ item.qty }} {{ item.unit }}</span>
                                    <span class="ml-auto font-weight-bold text-primary">{{ formatCurrency(item.total)
                                        }}</span>
                                </div>
                            </v-card>
                        </div>

                        <!-- Desktop Table -->
                        <v-table v-if="orderItems.length" class="d-none d-md-block rounded-xl border">
                            <thead>
                                <tr>
                                    <th v-for="h in tableHeaders" :key="h">{{ h }}</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr v-for="(item, index) in orderItems" :key="index">
                                    <td>{{ item.site }}</td>
                                    <td class="font-weight-bold">{{ item.code }}</td>
                                    <td>{{ item.item_name }}</td>
                                    <td>{{ formatCurrency(item.price) }}</td>
                                    <td>{{ item.qty }}</td>
                                    <td>{{ item.unit }}</td>
                                    <td class="font-weight-bold text-primary">{{ formatCurrency(item.total) }}</td>
                                    <td width="80">
                                        <v-btn icon="mdi-delete" color="red" size="small" variant="text"
                                            @click="removeItem(index)" />
                                    </td>
                                </tr>
                            </tbody>
                        </v-table>
                    </v-card-text>

                    <!-- Footer -->
                    <v-divider />
                    <v-card-actions class="pa-3 pa-md-4">
                        <div class="w-100">
                            <div class="d-flex justify-space-between align-center mb-3">
                                <div>
                                    <div class="text-caption text-grey">Grand Total</div>
                                    <div class="text-h6 font-weight-bold text-primary">{{ formatCurrency(grandTotal) }}
                                    </div>
                                </div>
                                <v-chip color="primary" variant="tonal" size="small">{{ orderItems.length }}
                                    Item(s)</v-chip>
                            </div>
                            <v-btn color="success" size="large" rounded="xl" block class="text-none font-weight-bold"
                                prepend-icon="mdi-content-save" :disabled="!orderItems.length" @click="confirmDialog = true">
                                Submit Order
                            </v-btn>
                        </div>
                    </v-card-actions>
    </v-card>

    <!-- Confirm Submit Dialog -->
    <v-dialog v-model="confirmDialog" max-width="420">
        <v-card rounded="xl">
            <v-card-text class="pa-5 text-center">
                <v-icon size="48" color="success" class="mb-3">mdi-help-circle-outline</v-icon>
                <div class="text-h6 font-weight-bold">Submit this order?</div>
                <div class="text-body-2 text-grey mt-1">
                    {{ orderItems.length }} item(s) — Total {{ formatCurrency(grandTotal) }}
                </div>
            </v-card-text>
            <v-card-actions class="pa-4 pt-0">
                <v-btn variant="text" @click="confirmDialog = false">Cancel</v-btn>
                <v-spacer />
                <v-btn color="success" variant="flat" rounded="lg" @click="confirmSubmit">OK</v-btn>
            </v-card-actions>
        </v-card>
    </v-dialog>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import axios from 'axios'

const emit = defineEmits(['close'])

const selectedItem = ref(null)
const confirmDialog = ref(false)

const sites = ref([])
const fetchSites = async () => {
    try {
        const res = await axios.get('/api/sites')
        sites.value = (res.data ?? []).map(s => s.name ?? s)
    } catch (e) {
        console.error('Failed to load sites', e)
    }
}
onMounted(() => fetchSites())

const tableHeaders = ['Site','Code', 'Item Name', 'Price', 'Qty', 'Unit', 'Total', 'Action']

const items = ref([
    { code: '101001', name: 'Wall switch box single 86mm x 86mm x 30 mm', price: 2010, unit: 'Pc(s)' },
    { code: '101002', name: 'Wall switch double', price: 3500, unit: 'Pc(s)' },
    { code: '101003', name: 'LED Light 12W', price: 4500, unit: 'Pc(s)' },
    { code: '101004', name: 'Electric Wire', price: 8000, unit: 'Roll' },
    { code: '101005', name: 'PVC Pipe', price: 6500, unit: 'Pc(s)' },
    { code: '101006', name: 'Socket', price: 2200, unit: 'Pc(s)' },
])

const currentMonth = new Date().toISOString().slice(0, 7)
const form = reactive({ site: '', month: currentMonth, code: '', item_name: '', qty: 1, price: 0, unit: '' })
const orderItems = ref([])

const selectItem = (item) => {
    if (!item) return
    form.code = item.code
    form.item_name = item.name
    form.price = item.price
    form.unit = item.unit
}

const itemTotal = computed(() => Number(form.qty || 0) * Number(form.price || 0))
const grandTotal = computed(() => orderItems.value.reduce((sum, i) => sum + i.total, 0))

const addItem = () => {
    if (!form.code || !form.qty) return
    orderItems.value.push({
        site: form.site,
        code: form.code,
        item_name: form.item_name,
        price: form.price,
        qty: form.qty,
        unit: form.unit,
        total: itemTotal.value,
    })
    selectedItem.value = null
    Object.assign(form, { code: '', item_name: '', qty: 1, price: 0, unit: '' })
}

const removeItem = (index) => orderItems.value.splice(index, 1)

const confirmSubmit = () => {
    console.log({ site: form.site, month: form.month, items: orderItems.value, grand_total: grandTotal.value })
    confirmDialog.value = false
    emit('close')
}

const formatCurrency = (value) => Number(value || 0).toLocaleString()
</script>

<style scoped>
.header-gradient {
    background: linear-gradient(135deg, #1976d2, #42a5f5);
}

.border {
    border: 1px solid #e0e0e0;
}

:deep(.v-list-item:hover) {
    background-color: rgba(25, 118, 210, 0.08) !important;
}

:deep(.v-list-item--active) {
    background-color: rgba(25, 118, 210, 0.12) !important;
    color: #1976d2 !important;
}
</style>
