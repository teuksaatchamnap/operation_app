<script setup>
import { ref, computed } from "vue";
import { useI18n } from "vue-i18n";
import { useCurrency } from "../composables/useCurrency";
import { usePermissions } from "../composables/usePermissions";
import { formatDateForDisplay } from "../utils/dateUtils";

const props = defineProps({
    sales: { type: Object, required: true },
    types: { type: Array, required: true },
    dates: { type: Array, required: true },
    site: { type: String, required: true },
    readonly: { type: Boolean, default: false },
    lockedDates: { type: Array, default: () => [] },
});

const emit = defineEmits(["edit-column", "add-column"]);

const { t } = useI18n();
const { formatKHR } = useCurrency();
const { isCashierAdmin } = usePermissions();
const tableRef = ref(null);

const calculateRowTotal = (date) => {
    let total = 0;
    props.types.forEach((type) => {
        const key = `${type.index}-${type.type}-${type.unit_price}`;
        const sale = props.sales[key]?.[date]?.[0];
        if (sale && sale.quantity) {
            total += sale.quantity * type.unit_price;
        }
    });
    return formatKHR(total);
};

const grandTotal = computed(() => {
    const total = props.dates.reduce((sum, date) => {
        const rowTotal = props.types.reduce((rowSum, type) => {
            const key = `${type.index}-${type.type}-${type.unit_price}`;
            const sale = props.sales[key]?.[date]?.[0];
            return (
                rowSum +
                (sale && sale.quantity ? sale.quantity * type.unit_price : 0)
            );
        }, 0);
        return sum + rowTotal;
    }, 0);
    return formatKHR(total);
});

const calculateColTotal = (type) => {
    let totalQuantity = 0;
    const key = `${type.index}-${type.type}-${type.unit_price}`;
    if (props.sales[key]) {
        props.dates.forEach((date) => {
            const sale = props.sales[key]?.[date]?.[0];
            if (sale && sale.quantity) {
                totalQuantity += Number(sale.quantity);
            }
        });
    }
    return totalQuantity;
};

const selectAllContent = (event) => {
    event.target.select();
};


const handleKeyNavigation = (rowIndex, colIndex, direction) => {
    if (props.readonly) return;

    let targetRowIndex = rowIndex;
    if (direction === "down") {
        targetRowIndex = rowIndex + 1;
    } else if (direction === "up") {
        targetRowIndex = rowIndex - 1;
    }

    if (targetRowIndex >= 0 && targetRowIndex < props.dates.length) {
        const tableElement = tableRef.value?.$el || tableRef.value;
        const tableBody = tableElement?.querySelector("tbody");
        if (!tableBody) return;
        const targetRow = tableBody.children[targetRowIndex];
        const targetCell = targetRow?.children[colIndex + 1];
        if (!targetCell) return;
        const focusTarget = targetCell.querySelector("input");
        if (focusTarget) {
            focusTarget.focus();
        }
    }
};


const isRowLocked = (date) => {
    if (isCashierAdmin.value) return false;
    return props.lockedDates.includes(date);
};
</script>

<template>
    <v-table
        ref="tableRef"
        density="compact"
        class="sales-table pt-2"
        fixed-header
    >
        <thead>
            <tr>
                <th class="text-center w-120 site-name">
                    {{ site }}
                </th>
                <th
                    v-for="type in types"
                    :key="'titre' + type.type"
                    class="text-center"
                    :class="{ 'editable-header': !readonly }"
                    @click="
                        !readonly &&
                            (lockedDates.length === 0 || isCashierAdmin) &&
                            emit('edit-column', type)
                    "
                >
                    {{ $t("cashier." + type.type) }}
                    <v-icon
                        v-if="
                            !readonly &&
                            (lockedDates.length === 0 || isCashierAdmin)
                        "
                        size="x-small"
                        >mdi-pencil</v-icon
                    >
                </th>
                <th class="text-center">
                    <v-btn
                        v-if="
                            !readonly &&
                            (lockedDates.length === 0 || isCashierAdmin)
                        "
                        color="primary"
                        variant="flat"
                        class="mx-0 my-0"
                        density="compact"
                        icon="mdi-plus"
                        @click="emit('add-column')"
                    />
                </th>
            </tr>
            <tr class="unit-prices">
                <th />
                <th
                    v-for="type in types"
                    :key="'unitprice' + type.type"
                    class="text-center"
                    @click="
                        !readonly &&
                            (lockedDates.length === 0 || isCashierAdmin) &&
                            emit('edit-column', type)
                    "
                >
                    {{ type.unit_price }}
                </th>
                <th>Total</th>
            </tr>
        </thead>
        <tbody>
            <tr v-for="(date, rowIndex) in dates" :key="date">
                <td class="text-right">
                    <v-chip>{{ formatDateForDisplay(date) }}</v-chip>
                </td>
                <td
                    v-for="(type, colIndex) in types"
                    :key="date + type.type"
                    class="py-0 px-0 mx-0 my-0"
                >
                    <div v-if="readonly" class="text-center">
                        {{
                            sales[
                                `${type.index}-${type.type}-${type.unit_price}`
                            ][date][0].quantity || "-"
                        }}
                    </div>
                    <v-number-input
                        v-else
                        v-model="
                            sales[
                                `${type.index}-${type.type}-${type.unit_price}`
                            ][date][0].quantity
                        "
                        :class="{
                            danger:
                                sales[
                                    `${type.index}-${type.type}-${type.unit_price}`
                                ][date][0].quantity > 9999,
                        }"
                        density="compact"
                        class="py-0 px-1 mx-0 my-0 text-center no-underline"
                        hide-details
                        :disabled="isRowLocked(date)"
                        control-variant="hidden"
                        :min="0"
                        autocomplete="off"
                        @focus="selectAllContent"
                        @keydown.enter.prevent="
                            handleKeyNavigation(rowIndex, colIndex, 'down')
                        "
                        @keydown.up.capture.prevent.stop="
                            handleKeyNavigation(rowIndex, colIndex, 'up')
                        "
                        @keydown.down.capture.prevent.stop="
                            handleKeyNavigation(rowIndex, colIndex, 'down')
                        "
                    />
                </td>
                <td class="total-row">
                    {{ calculateRowTotal(date) }}
                </td>
            </tr>
            <tr>
                <td class="text-right">Total</td>
                <td
                    v-for="type in types"
                    :key="type.type"
                    class="text-center total-row"
                >
                    {{ calculateColTotal(type) }}
                </td>
                <td class="total-row">
                    {{ grandTotal }}
                </td>
            </tr>
        </tbody>
    </v-table>
</template>

<style scoped>
.w-120 {
    width: 120px;
}
.text-center :deep(input) {
    text-align: center;
}
.text-right :deep(input) {
    text-align: right;
}
.unit-prices {
    font-size: smaller;
    height: 10px;
}
.unit-prices th {
    padding-top: 0 !important;
    padding-bottom: 0 !important;
    line-height: 16px;
    height: 16px !important;
}
.total-row {
    text-align: right;
    font-size: smaller;
    color: gray;
}
.editable-header {
    cursor: pointer;
    color: #1867c0;
}
.site-name {
    font-size: 2rem;
}
.sales-table table th:not(:first-child),
.sales-table table td:not(:first-child) {
    border-left: thin solid #e0e0e0;
}
.danger :deep(input) {
    box-shadow: inset 0 0 0 3px red;
    background-color: coral;
}
</style>
