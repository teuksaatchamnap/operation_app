<template>
    <v-menu v-model="menu" :close-on-content-click="false" location="bottom">
        <template v-slot:activator="{ props }">
            <v-text-field
                :model-value="modelValue"
                :label="label"
                placeholder="YYYY-MM"
                prepend-inner-icon="mdi-calendar"
                readonly
                clearable
                v-bind="props"
                @click:clear="$emit('update:modelValue', null)"
                hide-details
            />
        </template>
        <v-card min-width="280">
            <v-card-text>
                <v-text-field
                    v-model="pickerYear"
                    label="Year"
                    type="number"
                    class="mb-4"
                />
                <v-row density="comfortable">
                    <v-col
                        v-for="(month, index) in months"
                        :key="index"
                        cols="3"
                    >
                        <v-btn
                            :color="isSelectedMonth(index) ? 'primary' : ''"
                            variant="text"
                            size="small"
                            block
                            @click="selectMonth(index)"
                        >
                            {{ month }}
                        </v-btn>
                    </v-col>
                </v-row>
            </v-card-text>
        </v-card>
    </v-menu>
</template>

<script setup>
import { ref, computed } from "vue";

const props = defineProps({
    modelValue: {
        type: String,
        default: null,
    },
    label: {
        type: String,
        default: "Month",
    },
});

const emit = defineEmits(["update:modelValue"]);

const months = [
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec",
];

const now = new Date();
const menu = ref(false);
const pickerYear = ref(now.getFullYear());

// Initialize pickerYear from modelValue if provided
if (props.modelValue) {
    const [year] = props.modelValue.split("-");
    pickerYear.value = parseInt(year);
}

function isSelectedMonth(monthIndex) {
    if (!props.modelValue) return false;
    const [year, month] = props.modelValue.split("-");
    return (
        parseInt(year) === pickerYear.value &&
        parseInt(month) === monthIndex + 1
    );
}

function selectMonth(monthIndex) {
    const month = String(monthIndex + 1).padStart(2, "0");
    emit("update:modelValue", `${pickerYear.value}-${month}`);
    menu.value = false;
}
</script>
