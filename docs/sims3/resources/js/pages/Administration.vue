<template>
    <div v-if="loading" class="d-flex justify-center pt-10">
        <v-progress-circular indeterminate :size="60" color="primary" />
    </div>
    <div v-if="!loading" class="pa-4">
        <v-toolbar density="compact">
            <v-tabs v-model="tab">
                <v-tab
                    v-for="item in ['Users management', 'Configuration']"
                    :key="item"
                    :value="item"
                >
                    {{ item }}
                </v-tab>
            </v-tabs>
        </v-toolbar>
        <v-window v-model="tab" :touch="false">
            <v-window-item value="Users management">
                <v-card flat>
                    <h3 class="mb-4 mt-4 d-flex align-center">
                        <v-text-field
                            v-model="search"
                            density="compact"
                            label="Search"
                            hide-details="auto"
                            clearable
                            class="ml-10"
                            prepend-inner-icon="mdi-account-search"
                        />
                        <v-btn
                            color="primary"
                            icon="mdi-account-plus"
                            class="ml-10 mr-5"
                            @click="
                                selectedUser = { email: '', permissions: [] };
                                newUser = true;
                                showEditForm = true;
                            "
                        />
                    </h3>
                    <v-data-table
                        v-model:items-per-page="itemsPerPage"
                        :headers="headers"
                        :items="
                            users.filter(
                                (u) =>
                                    !search ||
                                    u.email
                                        .toLowerCase()
                                        .includes(search.toLowerCase()) ||
                                    u.manager
                                        .toLowerCase()
                                        .includes(search.toLowerCase())
                            )
                        "
                        density="compact"
                        item-value="email"
                        class="elevation-1"
                    >
                        <template #item.permissions="{ item }">
                            <v-chip-group>
                                <v-chip
                                    v-for="p in item.permissions.slice(0, 3)"
                                    :key="p"
                                    rounded="xl"
                                    color="primary"
                                    size="x-small"
                                >
                                    {{ p }}
                                </v-chip>
                                <v-chip
                                    v-if="item.permissions.length > 3"
                                    rounded="xl"
                                    color="secondary"
                                    variant="flat"
                                    size="x-small"
                                >
                                    ... and
                                    {{ item.permissions.length - 3 }} more
                                </v-chip>
                            </v-chip-group>
                        </template>
                        <template #item.actions="{ item }">
                            <v-btn
                                icon="mdi-pencil"
                                density="compact"
                                color="primary"
                                variant="tonal"
                                size="small"
                                class="me-2"
                                @click="editUser(item)"
                            />
                            <v-btn
                                icon="mdi-account-remove"
                                density="compact"
                                color="red"
                                size="small"
                                class="me-2"
                                @click="
                                    selectedUser = { ...item };
                                    showConfirmDelete = true;
                                "
                            />
                        </template>
                    </v-data-table>
                </v-card>
            </v-window-item>
            <v-window-item value="Configuration">
                <v-card flat>
                    <v-select
                        v-model="selectedConfiguration"
                        label="App configurations"
                        class="mt-4"
                        item-value="id"
                        :items="configurations"
                    >
                        <template #item="{ props, item }">
                            <v-list-item
                                v-bind="props"
                                :title="item.app + ' | ' + item.name"
                            />
                        </template>
                        <template #selection="{ item }">
                            {{ item.app }} | {{ item.name }}
                        </template>
                    </v-select>
                    <div class="json-editor mt-2">
                        <VueJSONEditor
                            :content="jsonEditor"
                            :on-change="onJSONChange"
                        />
                    </div>
                    <div class="d-flex flex-row ma-2">
                        <v-btn
                            prepend-icon="mdi-content-save"
                            class="mr-4"
                            color="primary"
                            @click="saveConfiguration()"
                        >
                            Save
                        </v-btn>
                        <v-btn
                            prepend-icon="mdi-cancel"
                            @click="cancelConfiguration()"
                        >
                            Cancel
                        </v-btn>
                    </div>
                </v-card>
            </v-window-item>
        </v-window>
    </div>
    <v-dialog v-model="showConfirmDelete" width="500">
        <v-card>
            <v-card-text>
                <h3>Do you really want to delete {{ selectedUser.email }} ?</h3>
                <v-row class="ma-2" justify="center">
                    <v-btn
                        prepend-icon="mdi-cancel"
                        rounded="lg"
                        color="green"
                        class="ma-4"
                        size="large"
                        @click="showConfirmDelete = false"
                    >
                        Cancel
                    </v-btn>
                    <v-btn
                        prepend-icon="mdi-account-remove"
                        rounded="lg"
                        color="error"
                        class="ma-4"
                        size="large"
                        @click="deleteUser()"
                    >
                        Yes, delete
                    </v-btn>
                </v-row>
            </v-card-text>
        </v-card>
    </v-dialog>
    <v-dialog
        v-model="showEditForm"
        fullscreen
        :scrim="false"
        transition="dialog-bottom-transition"
    >
        <v-card>
            <v-card-title>
                {{ newUser ? "Add New User" : "Edit User" }}
            </v-card-title>
            <v-card-text>
                <v-form ref="userForm" @submit.prevent="saveUser">
                    <v-row>
                        <v-col cols="12" md="4">
                            <v-text-field
                                v-model="selectedUser.email"
                                density="compact"
                                label="Email"
                                :disabled="!newUser"
                                :rules="[emailValidation]"
                            />
                        </v-col>
                        <v-col cols="12" md="4">
                            <v-select
                                v-model="selectedUser.manager"
                                density="compact"
                                label="Manager"
                                item-title="email"
                                item-value="email"
                                :items="filteredList"
                                :rules="required"
                            />
                        </v-col>
                        <v-col cols="12" md="4">
                            <v-select
                                v-model="selectedUser.position"
                                density="compact"
                                label="Position"
                                :items="['staff', 'manager', 'excom', 'ed']"
                                :rules="required"
                            />
                        </v-col>
                    </v-row>
                    <v-row>
                        <v-col cols="12" md="1">
                            <v-text-field
                                v-model="selectedUser.staff_id"
                                density="compact"
                                label="Staff ID"
                            />
                        </v-col>
                        <v-col cols="12" md="2">
                            <v-text-field
                                v-model="selectedUser.staff_name"
                                density="compact"
                                label="Staff Name"
                            />
                        </v-col>
                        <v-col cols="12" md="1">
                            <v-select
                                v-model="selectedUser.staff_sex"
                                density="compact"
                                label="Sex"
                                :items="['Male', 'Female']"
                                :rules="required"
                            />
                        </v-col>
                        <v-col cols="12" md="2">
                            <v-select
                                v-model="selectedUser.staff_dept"
                                density="compact"
                                label="Department"
                                :items="department"
                                item-title="department"
                                :rules="required"
                            />
                        </v-col>
                        <v-col cols="12" md="2">
                            <v-select
                                v-model="selectedUser.staff_position"
                                density="compact"
                                label="Position"
                                :items="refill"
                                item-title="name"
                                :rules="required"
                            />
                        </v-col>
                        <v-col cols="12" md="2">
                            <v-text-field
                                v-model="selectedUser.staff_join_date"
                                type="date"
                                density="compact"
                                label="Staff Join Date"
                            />
                        </v-col>
                        <v-col cols="12" md="2">
                            <v-text-field
                                v-model="selectedUser.staff_supervisor_by"
                                density="compact"
                                label="Supervisor"
                            />
                        </v-col>
                    </v-row>
                    <v-row> </v-row>
                    <v-row> </v-row>
                    <div class="text-subtitle-1 mt-4 text-medium-emphasis">
                        Permissions
                    </div>
                    <v-list class="permission-list" density="compact">
                        <v-list-group
                            v-for="app in allPermissions"
                            :key="app.id"
                            :value="app.id"
                        >
                            <template #activator="{ props }">
                                <v-list-item
                                    v-bind="props"
                                    prepend-icon="mdi-plus"
                                    :title="app.name"
                                />
                            </template>
                            <v-row dense>
                                <v-col
                                    v-for="perm in app.permissions"
                                    :key="perm.id"
                                    cols="12"
                                    sm="6"
                                    md="3"
                                >
                                    <v-checkbox
                                        v-model="selectedUser.permissions"
                                        :value="perm.id"
                                        :label="perm.name"
                                        hide-details
                                        density="compact"
                                        class="permission-checkbox"
                                    />
                                </v-col>
                            </v-row>
                        </v-list-group>
                    </v-list>
                    <v-row class="ma-2" justify="center">
                        <v-btn
                            prepend-icon="mdi-cancel"
                            rounded="lg"
                            color="error"
                            class="ma-4"
                            size="large"
                            @click="showEditForm = false"
                        >
                            Cancel
                        </v-btn>
                        <v-btn
                            prepend-icon="mdi-content-save"
                            rounded="lg"
                            color="primary"
                            class="ma-4"
                            size="large"
                            type="submit"
                        >
                            Save
                        </v-btn>
                    </v-row>
                </v-form>
            </v-card-text>
        </v-card>
    </v-dialog>
</template>

<script>
import VueJSONEditor from "../components/VueJSONEditor.vue";
import Swal from "sweetalert2";

export default {
    name: "AdministrationPage",
    components: {
        VueJSONEditor,
    },
    data: function () {
        return {
            tab: "Users management",
            loading: true,
            showEditForm: false,
            showConfirmDelete: false,
            users: [],
            refill: [],
            itemsPerPage: 15,
            selectedUser: {},
            allPermissions: [],
            newUser: false,
            filteredList: [],
            configurations: [],
            jsonEditor: { json: {} },
            selectedConfiguration: null,
            editedJson: null,
            search: "",
            department: [
                {
                    department: "Executive Committee",
                    position: [
                        { name: "Managing Director" },
                        { name: "Partnership & Development Director" },
                        { name: "Finance & Admin Director" },
                    ],
                },
                {
                    department: "Admin Department",
                    position: [
                        { name: "Admin Manager" },
                        { name: "Cashier & Admin" },
                        { name: "PNP Cleaner" },
                        { name: "PNP Security Guard" },
                        { name: "Driver" },
                        { name: "BTB Cleaner" },
                        { name: "BTB Security Guard" },
                        { name: "KPC Cleaner" },
                        { name: "KPC Security Guard" },
                        { name: "SR Cleaner" },
                        { name: "SR Security Guard" },
                    ],
                },
                {
                    department: "Finance department",
                    position: [
                        { name: "Finance Manager" },
                        { name: "Chief Accountant" },
                        { name: "Accountant" },
                        { name: "Stock Controller" },
                    ],
                },
                {
                    department: "Procurement department",
                    position: [
                        { name: "Procurement Coordinator" },
                        { name: "Procurement Officer" },
                    ],
                },
                {
                    department: "IT department",
                    position: [{ name: "IT Manager" }, { name: "IT Officer" }],
                },
                {
                    department: "HR Department",
                    position: [
                        { name: "HR Manager" },
                        { name: "Black Belt Manager" },
                        { name: "HR Officer" },
                    ],
                },
                {
                    department: "Partnership and Development Department",
                    position: [
                        { name: "WQ and Tecnical Engineer" },
                        { name: "M&E Coordinator" },
                        { name: "Project Manager" },
                        { name: "Construction and technical supervisor" },
                        { name: "Project Technician" },
                        { name: "Site Selection Officer" },
                    ],
                },
                {
                    department: "Kiosk 2.0",
                    position: [{ name: "Project Manager - Kiosk 2.0" }],
                },
                {
                    department: "Operations Department",
                    position: [
                        { name: "Quality Control Coordinator" },
                        { name: "Communcation Officer" },
                        { name: "Operations Support Officer" },
                        { name: "Sales Manager" },
                        { name: "Sales Officer" },
                        { name: "Tech. & WQ Manager" },
                        { name: "National Technician Supervisor" },
                        { name: "Tech. & WQ Technician" },
                        { name: "Water Quality Lab officer" },
                        { name: "KPC Regional Operation Manager" },
                        { name: "Senior Advisor" },
                        { name: "Advisor" },
                        { name: "Driver" },
                        { name: "Trainer of Entrepreneur" },
                        { name: "SR Regional Operation Manager" },
                        { name: "Senior Advisor" },
                        { name: "Trainer of Entrepreneur" },
                        { name: "BTB Regional Operation Manager" },
                        { name: "KSP Regional Operation Manager" },
                        { name: "Advisor Mobile" },
                        { name: "PP Regional Operation Manager" },
                        { name: "Operations Volunteer" },
                        { name: "KSP Regional Operation Manager" },
                    ],
                },
                {
                    department: "1001fontaines - Experts",
                    position: [
                        { name: "Senior Admin & Finance Advisor" },
                        { name: "Coordination Volunteer" },
                    ],
                },
            ],
            headers: [
                { title: "email", align: "start", key: "email" },
                { title: "permissions", align: "center", key: "permissions" },
                { title: "position", align: "center", key: "position" },
                { title: "manager", align: "center", key: "manager" },
                { title: "", align: "center", key: "actions" },
            ],
            requiredEmail: [
                (value) => {
                    if (
                        value &&
                        value.match(
                            /^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$/
                        )
                    )
                        return true;
                    return "This field is required and must be a valid email.";
                },
            ],
            required: [
                (value) => {
                    if (value) return true;
                    return "This field is required.";
                },
            ],
        };
    },
    watch: {
        selectedConfiguration(newVal) {
            const selectedConf = this.configurations.find(
                (c) => c.id == newVal
            );
            if (selectedConf) {
                this.jsonEditor = { json: JSON.parse(selectedConf.value) };
                this.editedJson = this.jsonEditor.json;
            }
        },
        "selectedUser.staff_dept": function () {
            const a = this.department.find(
                (depart) => depart.department == this.selectedUser.staff_dept
            );
            if (a) {
                this.refill = a.position;
            }
        },
        "selectedUser.staff_join_date": function (newVal) {
            if (newVal) {
                // Ensure date is in YYYY-MM-DD format without timezone conversion
                const date = new Date(newVal);
                this.selectedUser.staff_join_date = date
                    .toISOString()
                    .split("T")[0];
            }
        },
    },
    computed: {
        emailValidation() {
            return (value) => {
                if (!value) return "Email is required!";
                if (this.newUser === true) {
                    if (
                        this.users.some((user) => user.email === value.trim())
                    ) {
                        return "User with this email already exists!";
                    }
                }
                return true;
            };
        },
    },
    mounted() {
        this.loadUsers();
        this.loadPermissions();
        this.loadConfigurations();
    },
    methods: {
        onJSONChange(content) {
            this.editedJson = content.json;
        },
        loadUsers() {
            window.axios
                .get("/api/users")
                .then((response) => {
                    this.users = response.data;
                    this.filteredList = this.users.filter((item) => {
                        return item.position !== "staff";
                    });
                    console.log("Users response:", response.data);
                    this.loading = this.allPermissions.length === 0;
                    this.selectedUser = {};
                })
                .catch((error) => {
                    console.error("Error loading users:", error);
                    this.loading = false;
                });
        },
        loadConfigurations() {
            this.selectedConfiguration = null;
            window.axios
                .get("/api/configurations")
                .then((response) => {
                    this.configurations = response.data;
                    this.selectedConfiguration = response.data[0]?.id || null;
                    this.loading =
                        this.users.length === 0 ||
                        this.allPermissions.length === 0;
                })
                .catch((error) => {
                    console.error("Error loading configurations:", error);
                    this.loading = false;
                });
        },
        loadPermissions() {
            window.axios
                .get("/api/allPermissions")
                .then((response) => {
                    const permissions = response.data;
                    console.log("Permissions response:", permissions);
                    const appMap = new Map();
                    permissions.forEach((perm, index) => {
                        const permissionId = perm.name
                            ? perm.name
                            : perm.app_name || "unknown";
                        const appName = perm.app_name || "General";
                        if (!appMap.has(appName)) {
                            appMap.set(appName, {
                                id: `app-${appName}-${index}`,
                                name: appName,
                                permissions: [],
                            });
                        }
                        appMap.get(appName).permissions.push({
                            id: permissionId,
                            name:
                                perm.name ||
                                perm.app_name ||
                                "Unknown Permission",
                        });
                    });
                    this.allPermissions = Array.from(appMap.values());
                    console.log(
                        "Permissions for v-list-group:",
                        this.allPermissions
                    );
                    this.loading =
                        this.users.length === 0 ||
                        this.allPermissions.length === 0;
                })
                .catch((error) => {
                    console.error("Error loading permissions:", error);
                    this.loading = false;
                });
        },
        editUser(user) {
            this.selectedUser = {
                ...user,
                permissions: Array.isArray(user.permissions)
                    ? user.permissions
                    : [],
                staff_join_date: user.staff_join_date
                    ? user.staff_join_date.split(" ")[0]
                    : null, // Extract YYYY-MM-DD
            };
            console.log("Editing user:", this.selectedUser);
            this.newUser = false;
            this.showEditForm = true;
        },
        deleteUser() {
            this.loading = true;
            this.showConfirmDelete = false;
            window.axios
                .delete("/api/users/" + this.selectedUser.email)
                .then(() => {
                    this.loadUsers();
                })
                .catch((error) => {
                    console.error("Error deleting user:", error);
                    this.loading = false;
                });
        },
        async saveUser() {
            console.log("saveUser triggered with:", this.selectedUser);
            const valid = await this.$refs.userForm.validate();
            if (valid.valid) {
                this.loading = true;
                this.showEditForm = false;
                try {
                    const payload = {
                        ...this.selectedUser,
                        permissions: this.selectedUser.permissions,
                    };
                    console.log("Sending payload:", payload);
                    if (this.newUser) {
                        await window.axios.post("/api/users", payload);
                        console.log("User created successfully");
                    } else {
                        await window.axios.put(
                            "/api/users/" + this.selectedUser.email,
                            payload
                        );
                        console.log("User updated successfully");
                    }
                    this.loadUsers();
                } catch (error) {
                    console.error("Error saving user:", error);
                    Swal.fire({
                        icon: "error",
                        title: "Error",
                        text: "Failed to save user: " + error.message,
                    });
                    this.loading = false;
                }
            } else {
                console.log("Form validation failed:", valid.errors);
                Swal.fire({
                    icon: "error",
                    title: "Validation Error",
                    text: "Please fill all required fields correctly.",
                });
            }
        },
        saveConfiguration() {
            this.loading = true;
            let editedConf = {
                ...this.configurations.find(
                    (c) => c.id == this.selectedConfiguration
                ),
            };
            editedConf.value = JSON.stringify(this.editedJson);
            window.axios
                .put(
                    "/api/configurations/" + this.selectedConfiguration,
                    editedConf
                )
                .then(() => {
                    this.loadConfigurations();
                })
                .catch((error) => {
                    console.error("Error saving configuration:", error);
                    this.loading = false;
                });
        },
        cancelConfiguration() {
            this.loading = true;
            this.loadConfigurations();
        },
    },
};
</script>

<style scoped>
.v-dialog .v-overlay__content {
    width: 100vw;
    height: 100vh;
    margin: 0;
    max-height: 100vh;
}
.permission-list {
    max-height: 300px;
    overflow-y: auto;
    border: 1px solid #e0e0e0;
    border-radius: 4px;
    padding: 8px;
    background-color: #fafafa;
}
.permission-checkbox {
    margin: 4px 0;
}
</style>
