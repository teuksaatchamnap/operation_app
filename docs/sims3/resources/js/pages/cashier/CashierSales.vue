<script setup>
import { useRoute, useRouter } from "vue-router";
import { ref, computed } from "vue";
import { useI18n } from "vue-i18n";
import EntrepreneurCard from "../../components/EntrepreneurCard.vue";
import CashierWaterMeter from "./CashierWaterMeter.vue";
import CashierSalesTable from "../../components/CashierSalesTable.vue";
import TableExportPng from "../../components/TableExportPng.vue";
import { useCashierNotifications } from "../../composables/useCashierNotifications";
const files = ref([]);
const existingFiles = ref([]);
const route = useRoute();
const siteId = route.params.site;
const startDate = route.params.startDate;
const endDate = route.params.endDate;

const router = useRouter();
const queryParams = {
    start: startDate,
    end: endDate,
    site: siteId,
};
const loading = ref(true);
const sales = ref({});
const saving = ref(false);
const tab = ref("sales");
const salesNotificationMessage = ref("សួរស្តីសហគ្រិន សូមអរគុណសម្រាប់ការផ្ញើទិន្នន័យ។ នេះគឺជារបាយការណ៍ប្រចាំសប្តាហ៍របស់អ្នក។ \n អរគុណ!");
const waterMeter = ref(null);
const lastWaterMeter = ref(null);
const waterMeterRef = ref(null);
const lockedDates = ref([]);
const salesTableRef = ref({});

// Dialog related refs
const editingColumn = ref(null);
const showAddColumnDialog = ref(false);
const newColumnType = ref("");
const newColumnUnitPrice = ref(0);
const newColumnTypes = [
    "free",
    "hod",
    "wis",
    "onsite",
    "shop",
    "bottle",
    "other",
    "emergency",
];

const { t } = useI18n();
const { fetchNotificationMessage } = useCashierNotifications();
const typesList = computed(() => {
    return newColumnTypes.map((type) => ({
        title: t(`cashier.${type}`),
        value: type,
    }));
});

const dialogTitle = computed(() => {
    return editingColumn.value && editingColumn.value.type
        ? "Edit Sales Column"
        : "Add New Sales Column";
});

const types = ref([]);
const allDatesBetween = computed(() => {
    const dates = [];
    let currentDate = new Date(startDate);
    const stopDate = new Date(endDate);
    while (currentDate <= stopDate) {
        const dateString = currentDate.toISOString().slice(0, 10);
        dates.push(dateString);
        currentDate = new Date(currentDate);
        currentDate.setDate(currentDate.getDate() + 1);
    }
    return dates;
});

const openAddColumnDialog = (type = null) => {
    editingColumn.value = type;
    newColumnType.value = "";
    newColumnUnitPrice.value = 0;
    if (type) {
        newColumnType.value = type.type;
        newColumnUnitPrice.value = type.unit_price;
    }
    showAddColumnDialog.value = true;
};

const saveColumn = () => {
    if (editingColumn.value && editingColumn.value.type) {
        // Editing existing column
        const oldKey = `${editingColumn.value.index}-${editingColumn.value.type}-${editingColumn.value.unit_price}`;
        editingColumn.value.type = newColumnType.value;
        editingColumn.value.unit_price = newColumnUnitPrice.value;
        const newKey = `${editingColumn.value.index}-${editingColumn.value.type}-${editingColumn.value.unit_price}`;
        if (oldKey !== newKey) {
            sales.value[newKey] = sales.value[oldKey];
            delete sales.value[oldKey];
        }
    } else {
        // Adding new column
        const maxIndex = types.value.reduce(
            (max, type) => Math.max(max, type.index),
            0
        );
        const newType = {
            index: maxIndex + 1,
            type: newColumnType.value,
            unit_price: newColumnUnitPrice.value,
        };
        types.value.push(newType);
        const newColumnKey = `${newType.index}-${newType.type}-${newType.unit_price}`;
        sales.value[newColumnKey] = {};
        allDatesBetween.value.forEach((date) => {
            sales.value[newColumnKey][date] = [{ quantity: null }];
        });
    }
    types.value.sort((a, b) => a.index - b.index);
    showAddColumnDialog.value = false;
};

const deleteColumn = () => {
    if (!editingColumn.value) return;
    const keyToDelete = `${editingColumn.value.index}-${editingColumn.value.type}-${editingColumn.value.unit_price}`;
    const indexInTypes = types.value.findIndex(
        (t) =>
            t.index === editingColumn.value.index &&
            t.type === editingColumn.value.type &&
            t.unit_price === editingColumn.value.unit_price
    );
    if (indexInTypes > -1) {
        types.value.splice(indexInTypes, 1);
    }
    if (sales.value[keyToDelete]) {
        delete sales.value[keyToDelete];
    }
    editingColumn.value = null;
    showAddColumnDialog.value = false;
};

const uploadFiles = async () => {
    if (files.value.length === 0) {
        return;
    }
    const formData = new FormData();
    files.value.forEach((file) => {
        formData.append("files[]", file);
    });
    formData.append("site", siteId);
    formData.append("related_date", endDate);
    formData.append("type", "sales");
    try {
        await window.axios.post("/api/cashier/upload", formData, {
            headers: { "Content-Type": "multipart/form-data" },
        });
        console.log("Files uploaded successfully in the background.");
        files.value = [];
    } catch (error) {
        console.error("Error uploading files:", error);
    }
};

const saveAndClose = async () => {
    saving.value = true;
    try {
        await window.axios.post("/api/cashier/sales", {
            site: siteId,
            startDate: startDate,
            endDate: endDate,
            sales: sales.value,
            types: types.value,
        });
        uploadFiles();

        if (waterMeterRef.value && waterMeter.value > 0) {
            console.log("wm save");
            await waterMeterRef.value.save();
        }
        router.push("/cashier");
    } catch (error) {
        console.error("Error saving sales data:", error);
    } finally {
        saving.value = false;
    }
};
const createObjectURL = (file) => {
    return URL.createObjectURL(file);
};

const formatNumber = (num) => {
    return new Intl.NumberFormat("en-US", {
        maximumFractionDigits: 1,
    }).format(num);
};

const totalSales = computed(() => {
    let total = 0;
    if (sales.value) {
        Object.values(sales.value).forEach((typeSales) => {
            Object.values(typeSales).forEach((dateSales) => {
                if (dateSales && dateSales.length > 0) {
                    total += Number(dateSales[0].quantity) || 0;
                }
            });
        });
    }
    return total;
});

fetchNotificationMessage('sales').then(message => {
    if (message) {
        salesNotificationMessage.value = message;
    }
});

window.axios
    .get("/api/cashier/sales", {
        params: queryParams,
    })
    .then((response) => {
        sales.value =
            response.data.sales &&
            typeof response.data.sales === "object" &&
            !Array.isArray(response.data.sales)
                ? response.data.sales
                : {};

        const datesWithData = new Set();
        if (sales.value) {
            Object.values(sales.value).forEach((typeSales) => {
                if (typeSales) {
                    Object.entries(typeSales).forEach(([date, records]) => {
                        if (
                            records &&
                            records.length > 0 &&
                            records[0].quantity !== null &&
                            records[0].quantity !== ""
                        ) {
                            datesWithData.add(date);
                        }
                    });
                }
            });
        }
        lockedDates.value = Array.from(datesWithData);
        types.value = response.data.types;
        existingFiles.value = response.data.images;
        loading.value = false;
        types.value.forEach((type) => {
            const key = `${type.index}-${type.type}-${type.unit_price}`;
            if (!sales.value[key]) {
                sales.value[key] = {};
            }
            allDatesBetween.value.forEach((date) => {
                if (!sales.value[key][date]) {
                    sales.value[key][date] = [{ quantity: null }];
                }
            });
        });
    });
</script>

<template>
    <div>
        <div v-if="loading" class="d-flex justify-center mt-10 pt-10">
            <v-progress-circular indeterminate :size="60" color="primary" />
        </div>
        <div v-else>
            <v-sheet elevation="4" class="position-relative">
                <v-btn
                    class="position-absolute left-0 top-0 ml-5 mt-2"
                    style="z-index: 1"
                    prepend-icon="mdi-arrow-left"
                    append-icon="mdi-view-dashboard"
                    @click="$router.push('/cashier')"
                >
                    {{ $t("cashier.back_to_dashboard") }}
                </v-btn>
                <v-tabs v-model="tab" color="primary" align-tabs="center">
                    <v-tab value="sales"> Sales </v-tab>
                    <v-tab value="water"> Water meter </v-tab>
                    <v-tab value="review"> Review </v-tab>
                </v-tabs>
                <v-divider />
                <v-tabs-window v-model="tab">
                    <v-tabs-window-item value="sales">
                        <v-row align="center" justify="center">
                            <v-col class="px-5" cols="auto">
                                <CashierSalesTable
                                    :sales="sales"
                                    :types="types"
                                    :dates="allDatesBetween"
                                    :site="route.params.site"
                                    :locked-dates="lockedDates"
                                    @edit-column="openAddColumnDialog"
                                    @add-column="openAddColumnDialog({})"
                                />
                            </v-col>
                        </v-row>

                        <v-row align="center" justify="center">
                            <v-col
                                v-for="(file, index) in existingFiles"
                                :key="'existingFiles' + index"
                                class="pic-scroll"
                            >
                                <v-img
                                    :src="
                                        file.path.replace('public/', 'storage/')
                                    "
                                    style="min-height: 500px; width: 100%"
                                >
                                    <template #placeholder>
                                        <v-row
                                            class="fill-height ma-0"
                                            align="center"
                                            justify="center"
                                        >
                                            <v-progress-circular
                                                indeterminate
                                                color="grey-lighten-5"
                                            />
                                        </v-row>
                                    </template>
                                </v-img>
                            </v-col>
                        </v-row>

                        <v-row align="center" justify="center">
                            <v-col
                                v-if="!files.length"
                                class="px-5"
                                cols="auto"
                            >
                                <div class="text-center">
                                    <v-file-input
                                        v-model="files"
                                        label="Add picture from entrepreneur"
                                        multiple
                                        placeholder="Add picture from entrepreneur"
                                        prepend-icon="mdi-paperclip"
                                        variant="outlined"
                                        accept="image/*"
                                        class="w-300"
                                    />
                                </div>
                            </v-col>
                            <v-col
                                v-for="(file, index) in files"
                                v-else
                                :key="index"
                                class="pic-scroll"
                            >
                                <v-img
                                    :src="createObjectURL(file)"
                                    style="min-height: 500px; width: 100%"
                                >
                                    <template #placeholder>
                                        <v-row
                                            class="fill-height ma-0"
                                            align="center"
                                            justify="center"
                                        >
                                            <v-progress-circular
                                                indeterminate
                                                color="grey-lighten-5"
                                            />
                                        </v-row>
                                    </template>
                                </v-img>
                                <div class="text-center">
                                    <v-btn
                                        class="mt-2 text-center"
                                        @click="files = []"
                                    >
                                        delete picture
                                    </v-btn>
                                </div>
                            </v-col>
                        </v-row>

                        <div class="buttons">
                            <EntrepreneurCard :site="route.params.site" />
                            <div>
                                <v-btn
                                    class="mx-5 my-5"
                                    :loading="saving"
                                    :disabled="saving"
                                    append-icon="mdi-arrow-right"
                                    prepend-icon="mdi-check"
                                    variant="flat"
                                    color="primary"
                                    @click="tab = 'water'"
                                >
                                    Next
                                </v-btn>
                            </div>
                        </div>
                    </v-tabs-window-item>
                    <v-tabs-window-item value="water" eager>
                        <CashierWaterMeter
                            ref="waterMeterRef"
                            v-model:lastWaterMeter="lastWaterMeter"
                            v-model:currentWaterMeter="waterMeter"
                        />
                        <div class="buttons">
                            <EntrepreneurCard :site="route.params.site" />
                            <div>
                                <v-btn
                                    class="mx-5 my-5"
                                    :loading="saving"
                                    :disabled="saving"
                                    append-icon="mdi-arrow-left"
                                    variant="flat"
                                    color="secondary"
                                    @click="tab = 'sales'"
                                >
                                    Back
                                </v-btn>
                                <v-btn
                                    class="mx-5 my-5"
                                    :loading="saving"
                                    :disabled="saving"
                                    append-icon="mdi-arrow-right"
                                    prepend-icon="mdi-check"
                                    variant="flat"
                                    color="primary"
                                    @click="tab = 'review'"
                                >
                                    Next
                                </v-btn>
                            </div>
                        </div>
                    </v-tabs-window-item>
                    <v-tabs-window-item value="review">
                        <v-row align="center" justify="center">
                            <v-col class="px-5" cols="auto">
                                <div ref="salesTableRef">
                                    <CashierSalesTable
                                        :sales="sales"
                                        :types="types"
                                        :dates="allDatesBetween"
                                        :site="route.params.site"
                                        readonly
                                    />
                                </div>
                            </v-col>
                            <v-col class="px-5" cols="auto">
                                <v-sheet class="pa-2" border>
                                    <h3>Water meter</h3>
                                    <p>
                                        Previous Week Reading :
                                        {{ formatNumber(lastWaterMeter) }}
                                    </p>
                                    <p>
                                        Current Week Reading :
                                        <span v-if="waterMeter">{{
                                            formatNumber(waterMeter)
                                        }}</span>
                                        <span v-else>No data yet</span>
                                    </p>
                                    <p v-if="waterMeter">
                                        Consumption :
                                        {{
                                            formatNumber(
                                                (waterMeter - lastWaterMeter) *
                                                    1000
                                            )
                                        }}
                                        Liters
                                    </p>
                                    <p v-if="waterMeter">
                                        Water Loss :
                                        {{
                                            formatNumber(
                                                (waterMeter - lastWaterMeter) *
                                                    1000 -
                                                    totalSales * 20
                                            )
                                        }}
                                        Liters
                                        <span
                                            v-if="
                                                waterMeter - lastWaterMeter > 0
                                            "
                                        >
                                            ({{
                                                formatNumber(
                                                    (((waterMeter -
                                                        lastWaterMeter) *
                                                        1000 -
                                                        totalSales * 20) /
                                                        ((waterMeter -
                                                            lastWaterMeter) *
                                                            1000)) *
                                                        100
                                                )
                                            }}%)
                                        </span>
                                    </p>
                                </v-sheet>
                            </v-col>
                        </v-row>
                        <div class="buttons">
                            <EntrepreneurCard :site="route.params.site" />
                            <div>
                                <TableExportPng
                                    :table-ref="salesTableRef"
                                    :site-id="siteId"
                                    filename-prefix="sales"
                                    :message="salesNotificationMessage"
                                />
                                <v-btn
                                    class="mx-5 my-5"
                                    :loading="saving"
                                    :disabled="saving"
                                    append-icon="mdi-arrow-left"
                                    variant="flat"
                                    color="secondary"
                                    @click="tab = 'water'"
                                >
                                    Back
                                </v-btn>
                                <v-btn
                                    class="mx-5 my-5"
                                    :loading="saving"
                                    :disabled="saving"
                                    prepend-icon="mdi-check"
                                    variant="flat"
                                    color="primary"
                                    @click="saveAndClose"
                                >
                                    Save
                                </v-btn>
                            </div>
                        </div>
                    </v-tabs-window-item>
                </v-tabs-window>
            </v-sheet>
        </div>

        <!-- Add Column Dialog -->
        <v-dialog v-model="showAddColumnDialog" max-width="500px">
            <v-card>
                <v-card-title>{{ dialogTitle }}</v-card-title>
                <v-card-text>
                    <v-select
                        v-model="newColumnType"
                        label="Type Name"
                        :items="typesList"
                        required
                    />
                    <v-text-field
                        v-model.number="newColumnUnitPrice"
                        label="Unit Price"
                        type="number"
                        min="0"
                        required
                    />
                </v-card-text>
                <v-card-actions>
                    <v-btn
                        v-if="editingColumn"
                        color="red-darken-1"
                        variant="text"
                        @click="deleteColumn"
                    >
                        Delete
                    </v-btn>
                    <v-spacer />
                    <v-btn
                        color="blue-darken-1"
                        variant="text"
                        @click="showAddColumnDialog = false"
                    >
                        Cancel
                    </v-btn>
                    <v-btn
                        color="blue-darken-1"
                        variant="text"
                        @click="saveColumn"
                    >
                        {{ editingColumn ? "Save" : "Add Column" }}
                    </v-btn>
                </v-card-actions>
            </v-card>
        </v-dialog>
    </div>
</template>

<style scoped>
.w-300 {
    width: 300px;
}
.pic-scroll {
    max-height: 200px;
    overflow-y: scroll;
    max-width: 95%;
}
.buttons {
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
}
</style>
