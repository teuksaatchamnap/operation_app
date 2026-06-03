<template>
    <div class="d-flex align-center ga-1">
        <span class="currency-label">USD</span>
        <v-switch
            v-model="currency"
            true-value="riel"
            false-value="usd"
            color="primary"
            hide-details
            density="compact"
            class="currency-switch"
        />
        <span class="currency-label">KHR</span>
    </div>
</template>

<script setup>
import { useCurrency } from "../composables/useCurrency";

const { currency } = useCurrency();
</script>

<style scoped>
.currency-switch {
    --v-switch-thumb-width: 18px;
    --v-switch-track-width: 32px;
}

.currency-switch :deep(.v-selection-control--density-compact) {
    transform: scale(0.8);
}

.currency-label {
    font-size: 0.75rem;
    font-weight: 500;
}
</style>
