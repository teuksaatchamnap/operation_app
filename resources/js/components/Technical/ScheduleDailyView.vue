<template>
    <div v-if="tasks.length === 0" class="text-center text-medium-emphasis py-10">
        <v-icon size="44" color="grey-lighten-1">mdi-calendar-blank-outline</v-icon>
        <div class="mt-2 text-body-2">No activities scheduled for this day</div>
    </div>

    <v-row dense>
        <v-col v-for="(task, i) in tasks" :key="i" cols="12" md="4">
            <div class="task-row pa-4 rounded-lg h-100 d-flex flex-column">
                <!-- Header: time + type chip -->
                <div class="d-flex align-center justify-space-between mb-3">
                    <div class="d-flex align-center ga-2">
                        <div class="time-dot" :style="{ background: task.typeColor }"></div>
                        <span class="text-caption font-weight-bold text-blue-darken-2">{{ task.time }}</span>
                    </div>
                    <v-chip size="x-small" :color="task.typeColor" variant="tonal">{{ task.type }}</v-chip>
                </div>

                <!-- Code + title -->
                <div class="mb-2">
                    <div class="text-body-2 font-weight-bold">{{ task.code }} – {{ task.title }}</div>
                </div>

                <!-- Site -->
                <div class="text-caption text-medium-emphasis mb-1">
                    <v-icon size="12" class="mr-1">mdi-map-marker-outline</v-icon>{{ task.site }}
                </div>

                <!-- Note -->
                <div v-if="task.note" class="text-caption text-medium-emphasis mb-3">
                    <v-icon size="12" class="mr-1">mdi-note-outline</v-icon>{{ task.note }}
                </div>

                <v-spacer />

                <!-- Open Details button -->
                <div class="mt-2 d-flex justify-center">
                    <v-btn variant="outlined" size="x-small" @click="emit('open', task)">
                        <v-icon start size="12">mdi-open-in-new</v-icon>
                        Open Details
                    </v-btn>
                </div>
            </div>
        </v-col>
    </v-row>
</template>

<script setup>
defineProps({
    tasks: { type: Array, required: true },
})

const emit = defineEmits(['open'])
</script>

<style scoped>
.task-row {
    background: #fafafa;
    border: 1px solid #f0f0f0;
    transition: background 0.15s, border-color 0.15s;
}

.task-row:hover {
    background: #f0f4ff;
    border-color: #bbdefb;
}

.time-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    margin: 0 auto;
}
</style>
