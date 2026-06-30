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
                    <v-toolbar-title>
                        <div class="d-flex align-center ga-3">
                            <v-icon color="primary" size="28"
                                >mdi-store-outline</v-icon
                            >
                            <div>
                                <div class="text-h6">
                                    {{ site?.name ?? "Site Detail" }}
                                </div>
                                <div class="text-caption text-medium-emphasis">
                                    {{ site?.platform ?? "" }}
                                </div>
                            </div>
                        </div>
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

                <v-tabs
                    v-model="tab"
                    show-arrows
                    density="compact"
                    slider-color="primary"
                >
                    <v-tab
                        value="site-analysis"
                        prepend-icon="mdi-chart-box-outline"
                    >
                        Analysis
                    </v-tab>
                    <v-tab value="sales" prepend-icon="mdi-chart-line">
                        Sales
                    </v-tab>
                    <v-tab value="pnl" prepend-icon="mdi-cash-multiple">
                        P&amp;L
                    </v-tab>
                    <v-tab value="technical" prepend-icon="mdi-tune-variant">
                        Technical
                    </v-tab>
                    <v-tab value="site" prepend-icon="mdi-information-outline">
                        Site
                    </v-tab>
                </v-tabs>

                <v-divider />
            </div>

            <v-card-text class="pa-6" style="min-height: 85vh">
                <v-tabs-window v-model="tab">
                    <v-tabs-window-item value="site-analysis">
                        <SiteAnalysisContent
                            :site="site"
                            :initial-month="initialMonth"
                        />
                    </v-tabs-window-item>
                    <v-tabs-window-item value="sales">
                        <SiteSalesContent
                            :site="site"
                            :initial-month="initialMonth"
                        />
                    </v-tabs-window-item>
                    <v-tabs-window-item value="pnl">
                        <SitePnlContent
                            :site="site"
                            :initial-month="initialMonth"
                        />
                    </v-tabs-window-item>
                    <v-tabs-window-item value="technical">
                        <div class="text-medium-emphasis">
                            Technical content
                        </div>
                    </v-tabs-window-item>
                    <v-tabs-window-item value="site">
                        <SiteSiteContent :site="site" />
                    </v-tabs-window-item>
                </v-tabs-window>
            </v-card-text>
        </v-card>
    </v-dialog>
</template>

<script setup>
import { ref } from "vue";
import SiteAnalysisContent from "./SiteAnalysisContent.vue";
import SiteSalesContent from "./SiteSalesContent.vue";
import SitePnlContent from "./SitePnlContent.vue";
import SiteSiteContent from "./SiteSiteContent.vue";

defineProps({
    modelValue: {
        type: Boolean,
        required: true,
    },
    site: {
        type: Object,
        default: null,
    },
    initialMonth: {
        type: String,
        default: "",
    },
});

defineEmits(["update:modelValue"]);

const tab = ref("site-analysis");
</script>
