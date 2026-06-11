<template>
    <v-text-field
        :model-value="formattedValue"
        :label="label"
        v-bind="$attrs"
        prefix="៛"
        @update:model-value="onInput"
    />
</template>

<script setup>
import { computed } from "vue";

const props = defineProps({
    modelValue: [String, Number, null],
    label: String,
});
const emit = defineEmits(["update:modelValue"]);

const format = (value) => {
    const num = parseFloat(value);
    if (isNaN(num)) return "";

    return new Intl.NumberFormat("en-US", {
        maximumFractionDigits: 0,
    }).format(num);
};

const parse = (text) => {
    const cleanedText = String(text).replace(/,/g, "");
    if (cleanedText === "") return null;
    return cleanedText;
};

const formattedValue = computed(() => {
    return format(props.modelValue);
});

const onInput = (newValue) => {
    const parsedValue = parse(newValue);
    emit("update:modelValue", parsedValue);
};
</script>
