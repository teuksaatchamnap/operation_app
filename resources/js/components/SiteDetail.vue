<template>
    <v-dialog
        :model-value="modelValue"
        @update:model-value="$emit('update:modelValue', $event)"
        scrollable
        max-width="90vw"
        transition="dialog-bottom-transition"
    >
        <v-card>
            <div class="flex-shrink-0">
                <v-toolbar density="compact">
                    <v-toolbar-title class="text-h6">
                        {{ site?.name ?? "Site Detail" }}
                    </v-toolbar-title>
                    <v-spacer />
                    <v-btn
                        icon
                        variant="text"
                        @click="$emit('update:modelValue', false)"
                    >
                        <v-icon>mdi-close</v-icon>
                    </v-btn>
                </v-toolbar>

                <v-tabs v-model="tab" fixed-tabs density="compact" class="">
                    <v-tab value="site-analysis">Site analysis</v-tab>
                    <v-tab value="sales">Sales</v-tab>
                    <v-tab value="pnl">P&L</v-tab>
                    <v-tab value="technical">Technical</v-tab>
                    <v-tab value="site">Site</v-tab>
                </v-tabs>

                <v-divider />
            </div>

            <v-card-text class="pa-6">
                <v-tabs-window v-model="tab">
                    <v-tabs-window-item value="site-analysis">
                        <SiteAnalysisContent :site="site" />
                    </v-tabs-window-item>
                    <v-tabs-window-item value="sales">
                        <div class="text-medium-emphasis">Sales content</div>
                    </v-tabs-window-item>
                    <v-tabs-window-item value="pnl">
                        <div class="text-medium-emphasis">P&L content</div>
                    </v-tabs-window-item>
                    <v-tabs-window-item value="technical">
                        <div class="text-medium-emphasis">
                            Technical content
                        </div>
                    </v-tabs-window-item>
                    <v-tabs-window-item value="site">
                        <div class="text-medium-emphasis">Site content</div>
                    </v-tabs-window-item>
                </v-tabs-window>
            </v-card-text>
        </v-card>
    </v-dialog>
</template>

<script setup>
import { ref } from "vue";
import SiteAnalysisContent from "./SiteAnalysisContent.vue";

defineProps({
    modelValue: {
        type: Boolean,
        required: true,
    },
    site: {
        type: Object,
        default: null,
    },
});

defineEmits(["update:modelValue"]);

const tab = ref("site-analysis");
</script>
