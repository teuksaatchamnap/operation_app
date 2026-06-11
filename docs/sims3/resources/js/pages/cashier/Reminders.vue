<template>
    <v-sheet class="pa-5">
        <v-data-table :headers="headers" :items="reminders" :loading="loading" class="elevation-1">
            <template v-slot:top>
                <v-toolbar flat>
                    <v-toolbar-title>Reminders</v-toolbar-title>
                    <v-spacer></v-spacer>
                        <v-dialog v-model="dialog" max-width="600px">
                        <template v-slot:activator="{ props }">
                            <v-btn color="primary" variant="outlined" dark class="mb-2" v-bind="props">
                                <v-icon start>mdi-plus</v-icon>
                                New Reminder
                            </v-btn>
                        </template>
                        <v-card>
                            <v-card-title>
                                <span class="text-h5">{{ formTitle }}</span>
                            </v-card-title>
                            <v-card-text>
                                <v-container class="pa-0">
                                    <v-row no-gutters>
                                        <v-col cols="12" class="pb-2">
                                            <v-text-field v-model="editedItem.name" label="Name" density="compact" required></v-text-field>
                                        </v-col>
                                        <v-col cols="12" class="pb-2">
                                            <v-textarea v-model="editedItem.message" label="Message" rows="8" density="compact" required></v-textarea>
                                        </v-col>
                                        <v-col cols="6" class="pb-2 pr-2">
                                            <v-select v-model="editedItem.day_of_month" :items="dayOptions" item-title="title" item-value="value" label="Day of Month" density="compact" required></v-select>
                                        </v-col>
                                        <v-col cols="6" class="pb-2 pl-2">
                                            <v-text-field v-model="editedItem.time" label="Time" type="time" density="compact" required></v-text-field>
                                        </v-col>
                                        <v-col cols="6" class="pb-2">
                                            <v-select v-model="editedItem.target" :items="targetOptions" label="Recipients" density="compact" required></v-select>
                                        </v-col>
                                        <v-col cols="6" class="pl-4">
                                            <v-switch v-model="editedItem.active" label="Active" color="green" density="compact" :false-value="0" :true-value="1"></v-switch>
                                        </v-col>
                                        <v-col cols="12" class="pb-2 pt-2">
                                            <v-file-input
                                                v-model="audioFile"
                                                label="Audio File (.ogg)"
                                                accept=".ogg,audio/ogg"
                                                prepend-icon="mdi-music"
                                                show-size
                                                density="compact"
                                                @change="handleAudioChange"
                                            ></v-file-input>
                                        </v-col>
                                        <v-col cols="12" v-if="audioPreviewUrl || editedItem.audio" class="pb-2">
                                            <v-card flat>
                                                <v-card-text class="pa-2">
                                                    <audio controls :src="audioPreviewUrl || `/storage/${editedItem.audio}`" style="width: 100%; height: 32px;"></audio>
                                                </v-card-text>
                                            </v-card>
                                        </v-col>
                                    </v-row>
                                </v-container>
                            </v-card-text>
                            <v-card-actions>
                                <v-spacer></v-spacer>
                                <v-btn color="blue-darken-1" variant="text" @click="close">Cancel</v-btn>
                                <v-btn color="blue-darken-1" variant="text" @click="save">Save</v-btn>
                            </v-card-actions>
                        </v-card>
                    </v-dialog>
                    <v-dialog v-model="dialogDelete" max-width="500px">
                        <v-card>
                            <v-card-title class="text-h5">Are you sure you want to delete this reminder?</v-card-title>
                            <v-card-actions>
                                <v-spacer></v-spacer>
                                <v-btn color="blue-darken-1" variant="text" @click="closeDelete">Cancel</v-btn>
                                <v-btn color="blue-darken-1" variant="text" @click="deleteItemConfirm">OK</v-btn>
                                <v-spacer></v-spacer>
                            </v-card-actions>
                        </v-card>
                    </v-dialog>
                </v-toolbar>
            </template>
            <template v-slot:item.message="{ item }">
                {{ item.message.substring(0, 150) }}{{ item.message.length > 150 ? '...' : '' }}
            </template>
            <template v-slot:item.active="{ item }">
                <v-icon v-if="item.active" color="green">mdi-check-circle</v-icon>
                <v-icon v-else color="red">mdi-cancel</v-icon>
            </template>
            <template v-slot:item.audio="{ item }">
                <v-btn
                    v-if="item.audio"
                    :icon="playingReminderId === item.id ? 'mdi-stop' : 'mdi-play'"
                    density="compact"
                    :color="playingReminderId === item.id ? 'red' : 'primary'"
                    @click="toggleAudio(item.audio, item.id)"
                ></v-btn>
                <span v-else>-</span>
            </template>
            <template v-slot:item.actions="{ item }">
                <v-icon size="small" class="me-2" @click="editItem(item)">
                    mdi-pencil
                </v-icon>
                <v-icon size="small" @click="deleteItem(item)">
                    mdi-delete
                </v-icon>
            </template>
        </v-data-table>
    </v-sheet>

    <v-divider class="my-4"></v-divider>

    <CashierNotification />
</template>

<script>
import CashierNotification from './CashierNotification.vue'

export default {
    name: "Reminders",
    components: {
        CashierNotification
    },
    data: () => ({
        dialog: false,
        dialogDelete: false,
        loading: false,
        headers: [
            { title: 'Name', key: 'name', align: 'start' },
            { title: 'Message', key: 'message', align: 'start' },
            { title: 'Schedule', key: 'schedule', align: 'start' },
            { title: 'Target', key: 'target', align: 'start' },
            { title: 'Audio', key: 'audio', align: 'start' },
            { title: 'Active', key: 'active', align: 'start' },
            { title: 'Actions', key: 'actions', sortable: false, align: 'end' }
        ],
        reminders: [],
        targetOptions: ['ALL SITES'],
        editedIndex: -1,
        editedItem: {
            id: 0,
            name: '',
            message: '',
            day_of_month: -2,
            time: '06:00',
            target: 'ALL SITES',
            active: 1,
            audio: null
        },
        defaultItem: {
            id: 0,
            name: '',
            message: '',
            day_of_month: -2,
            time: '06:00',
            target: 'ALL SITES',
            active: 1,
            audio: null
        },
        audioFile: null,
        audioPreviewUrl: null,
        playingReminderId: null,
        audioElement: null,
    }),
    computed: {
        formTitle() {
            return this.editedIndex === -1 ? 'New Reminder' : 'Edit Reminder'
        },
        dayOptions() {
            const options = [                
                { title: 'Before last day of month', value: -2 },
                { title: 'Last day of month', value: -1 }
            ]
            for (let i = 1; i <= 31; i++) {
                options.push({ title: i.toString(), value: i })
            }
            return options
        }
    },
    watch: {
        dialog(val) {
            val || this.close()
        },
        dialogDelete(val) {
            val || this.closeDelete()
        },
    },
    created() {
        this.initialize()
    },
    beforeUnmount() {
        if (this.audioElement) {
            this.audioElement.pause()
            this.audioElement = null
        }
    },
    methods: {
        initialize() {
            this.loading = true
            window.axios.get('/api/reminders')
                .then(response => {
                    this.reminders = response.data.map(reminder => ({
                        ...reminder,
                        schedule: this.formatSchedule(reminder.day_of_month, reminder.time)
                    }))
                    this.loading = false
                })
                .catch(error => {
                    console.error('Error fetching reminders:', error)
                    this.loading = false
                })
            window.axios.get('/api/telegram-groups')
                .then(response => {
                    this.targetOptions = ['ALL SITES', ...response.data.map(group => group.site).sort()]
                })
                .catch(error => {
                    console.error('Error fetching telegram groups:', error)
                })
        },

        formatSchedule(dayOfMonth, time) {
            let dayText
            const dayNum = parseInt(dayOfMonth)
            if (dayNum === -2) {
                dayText = 'Before last day of month'
            } else if (dayNum === -1) {
                dayText = 'Last day of month'
            } else {
                dayText = `${dayNum}${this.getDaySuffix(dayNum)} of the month`
            }
            return `${dayText} at ${time}`
        },

        getDaySuffix(day) {
            if (day >= 11 && day <= 13) return 'th'
            const lastDigit = day % 10
            if (lastDigit === 1) return 'st'
            if (lastDigit === 2) return 'nd'
            if (lastDigit === 3) return 'rd'
            return 'th'
        },

        editItem(item) {
            this.editedIndex = this.reminders.indexOf(item)
            this.editedItem = { ...item }
            this.dialog = true
        },

        deleteItem(item) {
            this.editedIndex = this.reminders.indexOf(item)
            this.editedItem = { ...item }
            this.dialogDelete = true
        },

        deleteItemConfirm() {
            this.loading = true
            window.axios.delete(`/api/reminders/${this.editedItem.id}`)
                .then(() => {
                    this.reminders.splice(this.editedIndex, 1)
                    this.closeDelete()
                    this.loading = false
                })
                .catch(error => {
                    console.error('Error deleting reminder:', error)
                    this.loading = false
                })
        },

        close() {
            this.dialog = false
            this.$nextTick(() => {
                this.editedItem = { ...this.defaultItem }
                this.editedIndex = -1
                this.audioFile = null
                this.audioPreviewUrl = null
            })
        },

        closeDelete() {
            this.dialogDelete = false
            this.$nextTick(() => {
                this.editedItem = { ...this.defaultItem }
                this.editedIndex = -1
            })
        },

        handleAudioChange(file) {
            if (file) {
                this.audioPreviewUrl = URL.createObjectURL(file)
            } else {
                this.audioPreviewUrl = null
            }
        },

        toggleAudio(audioPath, reminderId) {
            if (this.playingReminderId === reminderId && this.audioElement) {
                this.audioElement.pause()
                this.audioElement.currentTime = 0
                this.playingReminderId = null
                this.audioElement = null
            } else {
                if (this.audioElement) {
                    this.audioElement.pause()
                    this.audioElement.currentTime = 0
                }
                this.audioElement = new Audio(`/storage/${audioPath}`)
                this.playingReminderId = reminderId
                this.audioElement.play()
                this.audioElement.onended = () => {
                    this.playingReminderId = null
                    this.audioElement = null
                }
                this.audioElement.onerror = () => {
                    this.playingReminderId = null
                    this.audioElement = null
                }
            }
        },

        save() {
            const formData = new FormData()
            formData.append('name', this.editedItem.name)
            formData.append('message', this.editedItem.message)
            formData.append('day_of_month', this.editedItem.day_of_month)
            formData.append('time', this.editedItem.time)
            formData.append('target', this.editedItem.target)
            formData.append('active', this.editedItem.active ? 1 : 0)
            if (this.audioFile) {
                formData.append('audio', this.audioFile)
            }

            const config = {
                headers: {
                    'Content-Type': 'multipart/form-data'
                }
            }

            if (this.editedIndex > -1) {
                this.loading = true
                formData.append('_method', 'PUT')
                window.axios.post(`/api/reminders/${this.editedItem.id}`, formData, config)
                    .then(response => {
                        this.initialize();
                        this.close()
                        this.loading = false
                    })
                    .catch(error => {
                        console.error('Error updating reminder:', error)
                        this.loading = false
                    })
            } else {
                this.loading = true
                window.axios.post('/api/reminders', formData, config)
                    .then(response => {
                        this.initialize();
                        this.close()
                        this.loading = false
                    })
                    .catch(error => {
                        console.error('Error creating reminder:', error)
                        this.loading = false
                    })
            }
        },
    },
}
</script>
