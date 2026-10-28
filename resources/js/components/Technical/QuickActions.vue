<template>
    <div class="px-6 pb-6">
        <div class="d-flex align-center justify-space-between mb-3">
            <span class="text-subtitle-2 font-weight-bold text-medium-emphasis text-uppercase"
                style="letter-spacing:.08em">Quick Actions</span>
            <v-divider class="ml-3 flex-1" />
        </div>
        <v-card elevation="1" rounded="lg" class="pa-3">
            <div class="d-flex align-center flex-wrap ga-2">
                <template v-for="(action, i) in actions" :key="action.type">
                    <v-divider v-if="i > 0" vertical class="mx-1" style="height:24px" />
                    <v-btn variant="tonal" :color="action.color" size="small" class="erp-btn"
                        @click="openAction(action.type)">
                        <v-icon start size="15">{{ action.icon }}</v-icon>
                        {{ action.label }}
                    </v-btn>
                </template>
            </div>
        </v-card>

        <!-- Loaded only after the first button click -->
        <QuickActionDialog v-if="activeAction" v-model="dialogOpen" :type="activeAction" />
    </div>
</template>

<script setup>
import { ref, defineAsyncComponent } from 'vue'

const QuickActionDialog = defineAsyncComponent(() => import('./QuickActionDialog.vue'))

const actions = [
    { type: 'issue',      label: 'Create Issue',    icon: 'mdi-wrench',                color: 'blue-darken-2' },
    { type: 'routine',    label: 'Routine Check',   icon: 'mdi-clipboard-check',       color: 'green-darken-2' },
    { type: 'assessment', label: 'Site Assessment', icon: 'mdi-file-document-outline', color: 'orange-darken-2' },
    { type: 'water',      label: 'Water Sample',    icon: 'mdi-water',                 color: 'teal-darken-1' },
]

const activeAction = ref(null)
const dialogOpen = ref(false)

const openAction = (type) => { activeAction.value = type; dialogOpen.value = true }
</script>

<style scoped>
.erp-btn {
    font-size: 12px !important;
    font-weight: 600 !important;
    letter-spacing: 0.02em !important;
    text-transform: none !important;
    border-radius: 6px !important;
}
</style>
