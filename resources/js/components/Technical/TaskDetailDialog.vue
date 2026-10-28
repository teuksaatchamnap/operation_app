<template>
    <v-dialog v-model="open" max-width="520">
        <v-card rounded="xl">
            <!-- Header -->
            <div class="detail-dialog-header px-6 py-5 d-flex align-start justify-space-between">
                <div>
                    <div class="d-flex align-center ga-2 mb-1">
                        <v-chip :color="task.typeColor" size="small" variant="flat"
                            class="text-white font-weight-bold">
                            {{ task.type }}
                        </v-chip>
                        <span class="text-h6 font-weight-bold text-white">{{ task.code }}</span>
                    </div>
                    <div class="text-body-2 text-white" style="opacity:.85">{{ task.title }}</div>
                </div>
                <v-btn icon size="small" variant="text" color="white" @click="open = false">
                    <v-icon>mdi-close</v-icon>
                </v-btn>
            </div>

            <v-card-text class="pa-6">
                <!-- Info rows -->
                <v-row dense>
                    <v-col cols="6">
                        <div class="detail-info-block pa-3 rounded-lg">
                            <div class="text-caption text-medium-emphasis mb-1">
                                <v-icon size="12" class="mr-1">mdi-clock-outline</v-icon>Scheduled Time
                            </div>
                            <div class="text-body-2 font-weight-bold">{{ task.time }}</div>
                        </div>
                    </v-col>
                    <v-col cols="6">
                        <div class="detail-info-block pa-3 rounded-lg">
                            <div class="text-caption text-medium-emphasis mb-1">
                                <v-icon size="12" class="mr-1">mdi-calendar-outline</v-icon>Date
                            </div>
                            <div class="text-body-2 font-weight-bold">{{ date }}</div>
                        </div>
                    </v-col>
                    <v-col cols="12">
                        <div class="detail-info-block pa-3 rounded-lg">
                            <div class="text-caption text-medium-emphasis mb-1">
                                <v-icon size="12" class="mr-1">mdi-map-marker-outline</v-icon>Site Location
                            </div>
                            <div class="text-body-2 font-weight-bold">{{ task.site }}</div>
                        </div>
                    </v-col>
                    <v-col cols="12" v-if="task.note">
                        <div class="detail-info-block pa-3 rounded-lg">
                            <div class="text-caption text-medium-emphasis mb-1">
                                <v-icon size="12" class="mr-1">mdi-note-text-outline</v-icon>Notes
                            </div>
                            <div class="text-body-2">{{ task.note }}</div>
                        </div>
                    </v-col>
                    <v-col cols="12">
                        <div class="detail-info-block pa-3 rounded-lg">
                            <div class="text-caption text-medium-emphasis mb-1">
                                <v-icon size="12" class="mr-1">mdi-account-outline</v-icon>Assigned Technician
                            </div>
                            <div class="text-body-2 font-weight-bold">{{ task.technician }}</div>
                        </div>
                    </v-col>
                    <v-col cols="6">
                        <div class="detail-info-block pa-3 rounded-lg">
                            <div class="text-caption text-medium-emphasis mb-1">
                                <v-icon size="12" class="mr-1">mdi-flag-outline</v-icon>Priority
                            </div>
                            <v-chip
                                :color="task.priority === 'High' ? 'error' : task.priority === 'Medium' ? 'warning' : 'success'"
                                size="x-small" variant="tonal">
                                {{ task.priority }}
                            </v-chip>
                        </div>
                    </v-col>
                    <v-col cols="6">
                        <div class="detail-info-block pa-3 rounded-lg">
                            <div class="text-caption text-medium-emphasis mb-1">
                                <v-icon size="12" class="mr-1">mdi-check-circle-outline</v-icon>Status
                            </div>
                            <v-chip :color="task.done ? 'success' : 'warning'" size="x-small" variant="tonal">
                                {{ task.done ? 'Completed' : 'Pending' }}
                            </v-chip>
                        </div>
                    </v-col>
                </v-row>
            </v-card-text>

            <v-divider />
            <v-card-actions class="pa-4 ga-2">
                <v-btn variant="outlined" rounded="lg" @click="open = false">Close</v-btn>
                <v-spacer />
                <v-btn :color="task.done ? 'grey' : 'success'" variant="flat" rounded="lg"
                    @click="emit('toggle-done')">
                    <v-icon start>{{ task.done ? 'mdi-refresh' : 'mdi-check' }}</v-icon>
                    {{ task.done ? 'Mark Pending' : 'Mark Complete' }}
                </v-btn>
            </v-card-actions>
        </v-card>
    </v-dialog>
</template>

<script setup>
const open = defineModel({ type: Boolean, default: false })

defineProps({
    task: { type: Object, required: true },
    date: { type: String, required: true },
})

const emit = defineEmits(['toggle-done'])
</script>

<style scoped>
.detail-dialog-header {
    background: linear-gradient(135deg, #1565C0 0%, #1976D2 100%);
    border-radius: 12px 12px 0 0;
}

.detail-info-block {
    background: #f8faff;
    border: 1px solid #e8eef8;
}
</style>
