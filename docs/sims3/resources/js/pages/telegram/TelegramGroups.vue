<template>
    <div v-if="loading" class="d-flex justify-center mt-10 pt-10">
        <v-progress-circular :size="50" color="primary" indeterminate />
    </div>
    <div v-else>
        <v-card class="ma-4">
            <v-toolbar density="compact">
                <v-text-field
                    v-model="search"
                    density="compact"
                    label="Search"
                    hide-details
                    clearable
                    class="shrink"
                    prepend-inner-icon="mdi-clipboard-text-search"
                />
                <v-btn
                    color="primary"
                    class="ml-2"
                    @click="openCreateDialog"
                >
                    ADD <v-icon>mdi-plus</v-icon>
                    <v-tooltip activator="parent" location="top">
                        Add Telegram Group
                    </v-tooltip>
                </v-btn>
            </v-toolbar>
            <v-data-table
                v-model:items-per-page="itemsPerPage"
                :headers="headers"
                :items="telegramGroups"
                :search="search"
                density="compact"
                class="elevation-1"
            >
                <template #item.site="{ item }">
                    <router-link
                        v-if="item.siteDetails"
                        :to="'/site/' + item.site"
                        class="text-decoration-none text-primary"
                    >
                        {{ item.site }}
                    </router-link>
                    <span v-else>{{ item.site }}</span>
                </template>
                <template #item.invite_url="{ item }">
                    <a
                        v-if="item.invite_url"
                        :href="item.invite_url"
                        target="_blank"
                        rel="noopener noreferrer"
                        class="text-decoration-none"
                    >
                        {{  item.invite_url }}<v-icon size="small" color="primary">mdi-open-in-new</v-icon>
                    </a>
                    <span v-else class="text-grey">-</span>
                </template>
                <template #item.actions="{ item }">
                    <v-btn
                        icon="mdi-email"
                        density="compact"
                        color="success"
                        variant="tonal"
                        size="small"
                        class="mr-4"
                        v-tooltip="'Send test message'"
                        @click="sendTestMessage(item)"
                    />
                    <v-btn
                        icon="mdi-pencil"
                        density="compact"
                        color="primary"
                        variant="tonal"
                        size="small"
                        class="me-2"
                        v-tooltip="'Edit group'"
                        @click="openEditDialog(item)"
                    />
                    <v-btn
                        icon="mdi-delete"
                        density="compact"
                        color="red"
                        size="small"
                        class="me-2"
                        v-tooltip="'Delete group'"
                        @click="confirmDelete(item)"
                    />
                </template>
            </v-data-table>
        </v-card>
    </div>

    <v-dialog v-model="showDialog" max-width="600px">
        <v-card>
            <v-card-title>
                {{ dialogMode === 'create' ? 'Add Telegram Group' : 'Edit Telegram Group' }}
            </v-card-title>
            <v-card-text>
                <v-form ref="telegramForm" @submit.prevent="saveTelegramGroup">
                    <v-row>
                        <v-col cols="12">
                            <v-select
                                v-model="selectedGroup.site"
                                :items="sites"
                                item-title="Id_Site"
                                item-value="Id_Site"
                                density="compact"
                                label="Site"
                                :rules="validationRules.site"
                                :disabled="dialogMode === 'edit'"
                                hide-details="auto"
                            />
                        </v-col>
                        <v-col cols="12">
                            <v-text-field
                                v-model="selectedGroup.chat_id"
                                density="compact"
                                label="Chat ID"
                                :rules="validationRules.chat_id"
                                hide-details="auto"
                            />
                        </v-col>
                        <v-col cols="12">
                            <v-text-field
                                v-model="selectedGroup.invite_url"
                                density="compact"
                                label="Invite URL"
                                :rules="validationRules.invite_url"
                                hide-details="auto"
                                placeholder="https://t.me/..."
                            />
                        </v-col>
                    </v-row>
                </v-form>
            </v-card-text>
            <v-card-actions>
                <v-spacer />
                <v-btn color="error" @click="showDialog = false">
                    Cancel
                </v-btn>
                <v-btn color="primary" @click="saveTelegramGroup">
                    Save
                </v-btn>
            </v-card-actions>
        </v-card>
    </v-dialog>

    <v-dialog v-model="showDeleteDialog" max-width="400px">
        <v-card>
            <v-card-title>Confirm Delete</v-card-title>
            <v-card-text>
                Do you really want to delete the telegram group for site {{ selectedGroup.site }}?
            </v-card-text>
            <v-card-actions>
                <v-spacer />
                <v-btn color="primary" @click="showDeleteDialog = false">
                    Cancel
                </v-btn>
                <v-btn color="error" @click="deleteTelegramGroup">
                    Delete
                </v-btn>
            </v-card-actions>
        </v-card>
    </v-dialog>
</template>

<script>
import Swal from "sweetalert2";

export default {
    name: "TelegramGroups",
    data() {
        return {
            loading: true,
            telegramGroups: [],
            sites: [],
            showDialog: false,
            showDeleteDialog: false,
            selectedGroup: {
                site: '',
                chat_id: '',
                invite_url: ''
            },
            search: '',
            dialogMode: 'create',
            itemsPerPage: 15,
            headers: [
                { title: 'Site', key: 'site' },
                { title: 'Chat ID', key: 'chat_id' },
                { title: 'Invite URL', key: 'invite_url' },
                { title: 'Actions', key: 'actions', sortable: false }
            ],
            validationRules: {
                site: [
                    v => !!v || 'Site is required'
                ],
                chat_id: [
                    v => !!v || 'Chat ID is required',
                    v => /^-?[0-9]+$/.test(v) || 'Chat ID must be numeric'
                ],
                invite_url: [
                    v => {
                        if (!v) return true;
                        return /^https?:\/\/.+/.test(v) || 'Invalid URL format';
                    }
                ]
            }
        };
    },
    mounted() {
        this.loadTelegramGroups();
        this.loadSites();
    },
    methods: {
        loadTelegramGroups() {
            window.axios
                .get('/api/telegram-groups')
                .then(response => {
                    this.telegramGroups = response.data;
                    this.loading = false;
                })
                .catch(error => {
                    console.error('Error loading telegram groups:', error);
                    Swal.fire({
                        icon: 'error',
                        title: 'Error',
                        text: 'Failed to load telegram groups'
                    });
                    this.loading = false;
                });
        },
        loadSites() {
            window.axios
                .get('/api/sites')
                .then(response => {
                    this.sites = response.data;
                })
                .catch(error => {
                    console.error('Error loading sites:', error);
                });
        },
        openCreateDialog() {
            this.dialogMode = 'create';
            this.selectedGroup = {
                site: '',
                chat_id: '',
                invite_url: ''
            };
            this.showDialog = true;
        },
        openEditDialog(group) {
            this.dialogMode = 'edit';
            this.selectedGroup = {
                id: group.id,
                site: group.site,
                chat_id: group.chat_id,
                invite_url: group.invite_url || ''
            };
            this.showDialog = true;
        },
        async saveTelegramGroup() {
            const valid = await this.$refs.telegramForm.validate();
            if (valid.valid) {
                this.loading = true;
                const payload = {
                    site: this.selectedGroup.site,
                    chat_id: this.selectedGroup.chat_id,
                    invite_url: this.selectedGroup.invite_url || null
                };

                const request = this.dialogMode === 'create'
                    ? window.axios.post('/api/telegram-groups', payload)
                    : window.axios.put(`/api/telegram-groups/${this.selectedGroup.id}`, payload);

                request
                    .then(() => {
                        this.showDialog = false;
                        this.loadTelegramGroups();
                        Swal.fire({
                            icon: 'success',
                            title: 'Success',
                            text: this.dialogMode === 'create' ? 'Telegram group created successfully' : 'Telegram group updated successfully',
                            timer: 2000,
                            showConfirmButton: false
                        });
                    })
                    .catch(error => {
                        console.error('Error saving telegram group:', error);
                        let errorMessage = 'Failed to save telegram group';
                        if (error.response && error.response.data && error.response.data.message) {
                            errorMessage = error.response.data.message;
                        } else if (error.response && error.response.data && error.response.data.errors) {
                            const errors = error.response.data.errors;
                            errorMessage = Object.values(errors).flat().join('\n');
                        }
                        Swal.fire({
                            icon: 'error',
                            title: 'Error',
                            text: errorMessage
                        });
                        this.loading = false;
                    });
            } else {
                Swal.fire({
                    icon: 'error',
                    title: 'Validation Error',
                    text: 'Please fill all required fields correctly'
                });
            }
        },
        confirmDelete(group) {
            this.selectedGroup = group;
            this.showDeleteDialog = true;
        },
        deleteTelegramGroup() {
            this.loading = true;
            this.showDeleteDialog = false;
            window.axios
                .delete(`/api/telegram-groups/${this.selectedGroup.id}`)
                .then(() => {
                    this.loadTelegramGroups();
                    Swal.fire({
                        icon: 'success',
                        title: 'Success',
                        text: 'Telegram group deleted successfully',
                        timer: 2000,
                        showConfirmButton: false
                    });
                })
                .catch(error => {
                    console.error('Error deleting telegram group:', error);
                    Swal.fire({
                        icon: 'error',
                        title: 'Error',
                        text: 'Failed to delete telegram group'
                    });
                    this.loading = false;
                });
        },
        async sendTestMessage(group) {
            const { value: text } = await Swal.fire({
                title: 'Send Test Message',
                input: 'textarea',
                inputLabel: 'Message',
                inputPlaceholder: 'Enter your test message (optional)',
                inputValue: '',
                showCancelButton: true,
                confirmButtonText: 'Send',
                cancelButtonText: 'Cancel',
                inputValidator: (value) => {
                    if (value && value.length > 1000) {
                        return 'Message must be less than 1000 characters';
                    }
                }
            });

            if (text !== undefined) {
                this.loading = true;
                window.axios
                    .post('/api/telegram/send-test-message', {
                        site: group.site,
                        message: text || null
                    })
                    .then((response) => {
                        Swal.fire({
                            icon: 'success',
                            title: 'Success',
                            text: JSON.stringify(response.data),
                            timer: 10000,
                            showConfirmButton: true
                        });
                        this.loading = false;
                    })
                    .catch(error => {
                        console.error('Error sending test message:', error);
                        Swal.fire({
                            icon: 'error',
                            title: 'Error',
                            text: JSON.stringify(error.data),
                        });
                        this.loading = false;
                    });
            }
        }
    }
};
</script>

<style scoped>
.v-data-table {
    cursor: pointer;
}
</style>
