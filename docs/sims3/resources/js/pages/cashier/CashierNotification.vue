<template>
    <v-sheet class="pa-5">
        <v-data-table :headers="headers" :items="notifications" :loading="loading" class="elevation-1">
            <template v-slot:top>
                <v-toolbar flat>
                    <v-toolbar-title>Cashier Notifications</v-toolbar-title>
                    <v-spacer></v-spacer>
                        <v-dialog v-model="dialog" max-width="600px">
                        <template v-slot:activator="{ props }">
                            <v-btn color="primary" variant="outlined" dark class="mb-2" v-bind="props">
                                <v-icon start>mdi-plus</v-icon>
                                New Notification
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
                                            <v-text-field v-model="editedItem.key" label="Key" density="compact" required></v-text-field>
                                        </v-col>
                                        <v-col cols="12" class="pb-2">
                                            <v-textarea v-model="editedItem.message" label="Message" rows="8" density="compact" required></v-textarea>
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
                            <v-card-title class="text-h5">Are you sure you want to delete this notification?</v-card-title>
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
            <template v-slot:item.audio="{ item }">
                <v-btn
                    v-if="item.audio"
                    :icon="playingNotificationId === item.id ? 'mdi-stop' : 'mdi-play'"
                    density="compact"
                    :color="playingNotificationId === item.id ? 'red' : 'primary'"
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
</template>

<script>
export default {
    name: "CashierNotification",
    data: () => ({
        dialog: false,
        dialogDelete: false,
        loading: false,
        headers: [
            { title: 'Key', key: 'key', align: 'start' },
            { title: 'Message', key: 'message', align: 'start' },
            { title: 'Audio', key: 'audio', align: 'start' },
            { title: 'Actions', key: 'actions', sortable: false, align: 'end' }
        ],
        notifications: [],
        editedIndex: -1,
        editedItem: {
            id: 0,
            key: '',
            message: '',
            audio: null
        },
        defaultItem: {
            id: 0,
            key: '',
            message: '',
            audio: null
        },
        audioFile: null,
        audioPreviewUrl: null,
        playingNotificationId: null,
        audioElement: null,
    }),
    computed: {
        formTitle() {
            return this.editedIndex === -1 ? 'New Notification' : 'Edit Notification'
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
            window.axios.get('/api/cashier-notifications')
                .then(response => {
                    this.notifications = response.data
                    this.loading = false
                })
                .catch(error => {
                    console.error('Error fetching notifications:', error)
                    this.loading = false
                })
        },

        editItem(item) {
            this.editedIndex = this.notifications.indexOf(item)
            this.editedItem = { ...item }
            this.dialog = true
        },

        deleteItem(item) {
            this.editedIndex = this.notifications.indexOf(item)
            this.editedItem = { ...item }
            this.dialogDelete = true
        },

        deleteItemConfirm() {
            this.loading = true
            window.axios.delete(`/api/cashier-notifications/${this.editedItem.id}`)
                .then(() => {
                    this.notifications.splice(this.editedIndex, 1)
                    this.closeDelete()
                    this.loading = false
                })
                .catch(error => {
                    console.error('Error deleting notification:', error)
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

        toggleAudio(audioPath, notificationId) {
            if (this.playingNotificationId === notificationId && this.audioElement) {
                this.audioElement.pause()
                this.audioElement.currentTime = 0
                this.playingNotificationId = null
                this.audioElement = null
            } else {
                if (this.audioElement) {
                    this.audioElement.pause()
                    this.audioElement.currentTime = 0
                }
                this.audioElement = new Audio(`/storage/${audioPath}`)
                this.playingNotificationId = notificationId
                this.audioElement.play()
                this.audioElement.onended = () => {
                    this.playingNotificationId = null
                    this.audioElement = null
                }
                this.audioElement.onerror = () => {
                    this.playingNotificationId = null
                    this.audioElement = null
                }
            }
        },

        save() {
            const formData = new FormData()
            formData.append('key', this.editedItem.key)
            formData.append('message', this.editedItem.message)
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
                window.axios.post(`/api/cashier-notifications/${this.editedItem.id}`, formData, config)
                    .then(response => {
                        this.initialize();
                        this.close()
                        this.loading = false
                    })
                    .catch(error => {
                        console.error('Error updating notification:', error)
                        this.loading = false
                    })
            } else {
                this.loading = true
                window.axios.post('/api/cashier-notifications', formData, config)
                    .then(response => {
                        this.initialize();
                        this.close()
                        this.loading = false
                    })
                    .catch(error => {
                        console.error('Error creating notification:', error)
                        this.loading = false
                    })
            }
        },
    },
}
</script>
