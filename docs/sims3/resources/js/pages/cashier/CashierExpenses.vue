<script setup>
import { useRoute, useRouter } from "vue-router";
import { ref, nextTick, computed } from "vue";
import EntrepreneurCard from "../../components/EntrepreneurCard.vue";
import FormattedNumberField from "../../components/FormattedNumberField.vue";
import TableExportPng from "../../components/TableExportPng.vue";
import { useStore } from "vuex";
import { useCashierNotifications } from "../../composables/useCashierNotifications";

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
const saving = ref(false);
const readOnly = ref(false);
const expenses = ref({});
const categories = ref({});
const tab = ref("production");
const errors = ref({});
const files = ref([]);
const existingFiles = ref([]);
const expensesNotificationMessage = ref({message:"សួរស្តីសហគ្រិន សូមអរគុណសម្រាប់ការផ្ញើទិន្នន័យ។ នេះគឺជារបាយការណ៍ចំណាយប្រចាំខែរបស់អ្នក។ \n អរគុណ!"});

const expensesToIgnore = ["entrepreneur_contribution", "WinS_invoice", "stock_ts", "debt"];

const store = useStore();
const { fetchNotificationMessage } = useCashierNotifications();

const createObjectURL = (file) => {
    return URL.createObjectURL(file);
};

const isCashierAdmin = computed(() => {
    const user = store.state.user;
    return !!(
        user &&
        user.permissions &&
        user.permissions.includes("cashier_admin")
    );
});

const total = computed(() => {
    let grandTotal = 0;
    Object.keys(categories.value).forEach((category) => {
        const expenseRefs = categories.value[category];
        expenseRefs.forEach((expenseRef) => {
            const expenseData = expenses.value[expenseRef];
            if (expenseData && expenseData.length > 0) {
                const amount = parseFloat(expenseData[0].Amount_expenses) || 0;
                grandTotal += amount;
            }
        });
    });
    return grandTotal;
});

fetchNotificationMessage('expenses').then(message => {
    if (message) {
        expensesNotificationMessage.value = message;
    }
});

window.axios
    .get("/api/cashier/expenses", {
        params: queryParams,
    })
    .then((response) => {
        const expenseNormalized = response.data.expenses;
        const expenseCleaned = Object.keys(expenseNormalized).filter(exp => !expensesToIgnore.includes(exp));
        if (expenseCleaned.length > 0 && isCashierAdmin.value == false) {
            readOnly.value = true;
        }
        categories.value = response.data.categories;
        Object.keys(categories.value).forEach((cat) => {
            categories.value[cat].forEach((exp) => {
                if (!expenseNormalized[exp]) {
                    expenseNormalized[exp] = [
                        {
                            Ref_expenses: exp,
                            Category_expenses: cat,
                            Month: startDate,
                            Id_Site: siteId,
                            Amount_expenses: null,
                        },
                    ];
                }
            });
        });

        // Auto fill Stock TS and Bottle invoice from imported invoices if not already saved
        const stockInvoice = response.data.invoices.filter(i => i.invoice_type == "Stock Invoice");
        if (stockInvoice.length > 0 && expenseNormalized.stock_ts[0].Amount_expenses === null) {
            expenseNormalized.stock_ts[0].Amount_expenses = stockInvoice[0].beginning_balance
        }
        const bottleInvoice = response.data.invoices.filter(i => i.invoice_type == "Consumable Bottle");
        if (bottleInvoice.length > 0 && expenseNormalized.bottle_invoice[0].Amount_expenses === null) {
            expenseNormalized.bottle_invoice[0].Amount_expenses = bottleInvoice[0].beginning_balance
        }
        const deliveryInvoice = response.data.invoices.filter(i => i.invoice_type == "Delivery Program Fee");
        if (deliveryInvoice.length > 0 && expenseNormalized.delivery_program_fee[0].Amount_expenses === null) {
            expenseNormalized.delivery_program_fee[0].Amount_expenses = deliveryInvoice[0].beginning_balance
        }

        expenses.value = expenseNormalized;
        existingFiles.value = response.data.images;
        loading.value = false;
    });

const formatNumber = (num) => {
    return new Intl.NumberFormat("en-US", {
        style: "currency",
        currency: "KHR",
        maximumFractionDigits: 0,
        currencyDisplay: "symbol",
    })
        .format(num)
        .replace("KHR", "៛")
        .trim();
};

const calculateCategoryTotal = (category) => {
    const expenseRefs = categories.value[category];
    if (!expenseRefs || !expenses.value) return "0.00";
    let total = 0;
    expenseRefs.forEach((expenseRef) => {
        const expenseData = expenses.value[expenseRef];
        if (expenseData && expenseData.length > 0) {
            const amount = parseFloat(expenseData[0].Amount_expenses) || 0;
            total += amount;
        }
    });
    return formatNumber(total);
};

const isValidAmount = (val) => {
    if (val === null || val === "" || val === undefined) return true;
    const num = Number(val);
    return !isNaN(num) && num >= 0;
};

const validateExpense = (expense, val) => {
    errors.value[expense] = !isValidAmount(val);
};

const validateCurrentTab = () => {
    if (tab.value === "review") return true;
    const currentExpenses = categories.value[tab.value];
    if (!currentExpenses) return true;

    let valid = true;
    currentExpenses.forEach((expense) => {
        const val = expenses.value[expense][0].Amount_expenses;
        if (!isValidAmount(val)) {
            errors.value[expense] = true;
            valid = false;
        } else {
            errors.value[expense] = false;
        }
    });
    return valid;
};

const onTabChange = (newTab) => {
    if (validateCurrentTab()) {
        tab.value = newTab;
    }
};

const goToNextTab = () => {
    if (!validateCurrentTab()) return;
    const values = Object.keys(categories.value);
    const currentIndex = values.indexOf(tab.value);
    if (currentIndex > -1 && currentIndex < values.length - 1) {
        tab.value = values[currentIndex + 1];
        nextTick(() => {
            const activeWindow = document.querySelector(
                ".v-window-item--active"
            );
            if (activeWindow) {
                const firstInput = activeWindow.querySelector("input");
                if (firstInput) {
                    firstInput.focus();
                }
            }
        });
    } else {
        tab.value = "review";
    }
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
    formData.append("type", "expenses");
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

const save = () => {
    saving.value = true;
    const expensesFormatted = Object.values(expenses.value).map((a) => a[0]);
    console.log(expensesFormatted);
    window.axios
        .post("/api/cashier/expenses", { expenses: expensesFormatted })
        .then(() => {
            uploadFiles();
            saving.value = false;
            router.push("/cashier?tab=expenses");
        })
        .catch(() => {
            saving.value = false;
            alert("An error occurred while saving expenses.");
        });
};

const focusNext = (e) => {
    const focusable = Array.from(
        document.querySelectorAll(
            'input:not([disabled]):not([readonly]), button:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])'
        )
    ).filter((el) => el.offsetParent !== null);
    const index = focusable.indexOf(e.target);
    if (index > -1 && index < focusable.length - 1) {
        focusable[index + 1].focus();
    }
};

const tableExportRef = ref({});
</script>

<template>
    <div>
        <div v-if="loading" class="d-flex justify-center mt-10 pt-10">
            <v-progress-circular indeterminate :size="60" color="primary" />
        </div>
        <div v-else>
            <div class="d-flex flex-row">
                <v-btn
                    class="ml-1 mr-5 mt-2"
                    prepend-icon="mdi-arrow-left"
                    append-icon="mdi-view-dashboard"
                    @click="$router.push('/cashier?tab=expenses')"
                >
                    {{ $t("cashier.back_to_dashboard") }}
                </v-btn>
                <h4 class="pa-4">
                    Expenses for site {{ siteId }}
                    <small> {{ startDate }} - {{ endDate }}</small>
                </h4>
            </div>
            <v-sheet elevation="4">
                <v-tabs
                    :model-value="tab"
                    color="primary"
                    align-tabs="center"
                    @update:model-value="onTabChange"
                >
                    <v-tab
                        v-if="readOnly == false"
                        v-for="(key, category) in categories"
                        :key="category"
                        :value="category"
                    >
                        {{ category }}
                    </v-tab>
                    <v-tab value="review"> Review </v-tab>
                </v-tabs>
                <v-divider />
                <v-tabs-window v-model="tab">
                    <v-tabs-window-item
                        v-for="(expensesValues, category) in categories"
                        :key="'win' + category"
                        :value="category"
                    >
                        <v-sheet>
                            <div class="expenses-container">
                                <FormattedNumberField
                                    v-for="expense in expensesValues"
                                    :key="expense"
                                    v-model="
                                        expenses[expense][0].Amount_expenses
                                    "
                                    :error="errors[expense]"
                                    class="expense-input"
                                    :label="$t('cashier.' + expense)"
                                    type="text"
                                    @update:model-value="
                                        validateExpense(expense, $event)
                                    "
                                    @keydown.enter.prevent="focusNext"
                                />
                            </div>
                            <div class="text-center">
                                <v-btn
                                    class="mx-5 my-5"
                                    :loading="saving"
                                    :disabled="saving"
                                    append-icon="mdi-arrow-right"
                                    prepend-icon="mdi-check"
                                    variant="flat"
                                    color="primary"
                                    @click="goToNextTab()"
                                >
                                    Next
                                </v-btn>
                            </div>
                        </v-sheet>
                    </v-tabs-window-item>
                    <v-tabs-window-item value="review">
                        <v-sheet>
                            <v-row align="center" justify="center" class="pt-5">
                                <div ref="tableExportRef">
                                    <v-table
                                        density="compact"
                                        striped="even"
                                    >
                                        <thead>
                                            <tr>
                                                <th>Category</th>
                                                <th>Expense</th>
                                                <th>Cost</th>
                                                <th>Total</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            <template
                                                v-for="(
                                                    expensesValues, category
                                                ) in categories"
                                                :key="'cat-group-' + category"
                                            >
                                                <tr>
                                                    <td
                                                        :rowspan="
                                                            expensesValues.length
                                                        "
                                                    >
                                                        {{ category }}
                                                    </td>
                                                    <td>
                                                        {{
                                                            $t(
                                                                "cashier." +
                                                                    expensesValues[0]
                                                            )
                                                        }}
                                                    </td>
                                                    <td>
                                                        {{
                                                            formatNumber(
                                                                expenses[
                                                                    expensesValues[0]
                                                                ][0].Amount_expenses
                                                            )
                                                        }}
                                                    </td>
                                                    <td
                                                        :rowspan="
                                                            expensesValues.length
                                                        "
                                                    >
                                                        {{
                                                            calculateCategoryTotal(
                                                                category
                                                            )
                                                        }}
                                                    </td>
                                                </tr>
                                                <tr
                                                    v-for="(
                                                        expense, index
                                                    ) in expensesValues.slice(1)"
                                                    :key="
                                                        'rev-' +
                                                        category +
                                                        '-' +
                                                        index
                                                    "
                                                >
                                                    <td>
                                                        {{
                                                            $t("cashier." + expense)
                                                        }}
                                                    </td>
                                                    <td>
                                                        {{
                                                            formatNumber(
                                                                expenses[expense][0]
                                                                    .Amount_expenses
                                                            )
                                                        }}
                                                    </td>
                                                </tr>
                                            </template>
                                            <tr>
                                                <td colspan="3" class="text-right" style="border-top: 1px solid black">Total</td>
                                                <td style="border-top: 1px solid black">{{ formatNumber(total) }}</td>
                                            </tr>
                                        </tbody>
                                    </v-table>
                                </div>
                            </v-row>

                            <v-row align="center" justify="center">
                                <v-col
                                    v-for="(file, index) in existingFiles"
                                    :key="'existingFiles' + index"
                                    class="pic-scroll"
                                >
                                    <v-img
                                        :src="
                                            file.path.replace(
                                                'public/',
                                                'storage/'
                                            )
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

                            <div class="text-center">
                                <TableExportPng
                                    :table-ref="tableExportRef"
                                    :site-id="siteId"
                                    filename-prefix="expenses"
                                    :message="expensesNotificationMessage"
                                />
                                <v-btn
                                    v-if="readOnly == false"
                                    class="mx-5 my-5"
                                    :loading="saving"
                                    :disabled="saving"
                                    prepend-icon="mdi-check"
                                    variant="flat"
                                    color="primary"
                                    @click="save()"
                                >
                                    Save
                                </v-btn>
                                <v-btn
                                    v-else
                                    class="mx-5 my-5"
                                    :loading="saving"
                                    :disabled="saving"
                                    prepend-icon="mdi-check"
                                    variant="flat"
                                    color="primary"
                                    @click="
                                        $router.push('/cashier?tab=expenses')
                                    "
                                >
                                    {{ $t("cashier.back_to_dashboard") }}
                                </v-btn>
                            </div>
                        </v-sheet>
                    </v-tabs-window-item>
                </v-tabs-window>
            </v-sheet>
            <div class="mt-5">
                <EntrepreneurCard :site="route.params.site" />
            </div>
        </div>
    </div>
</template>

<style scoped>
td[rowspan] {
    z-index: 50;
    background-color: white;
    position:relative;
}
.w-300 {
    width: 300px;
}
.pic-scroll {
    max-height: 200px;
    overflow-y: scroll;
    max-width: 95%;
}
.expense-input {
    max-width: 400px;
    min-width: 300px;
}

.expenses-container {
    display: flex;
    flex-direction: column;
    gap: 0.1rem;
    align-items: center;
    margin-top: 0.5rem;
    flex-wrap: wrap;
}

.buttons {
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
}
</style>
