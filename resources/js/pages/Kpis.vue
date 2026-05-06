<template>
    <v-container>
        <div class="d-flex align-center mb-4">
            <h1 class="text-h5">KPIs</h1>
            <v-spacer></v-spacer>
            <!--v-btn color="primary" prepend-icon="mdi-plus" @click="openKpiDialog()">
                New KPI
            </v-btn-->
        </div>

        <v-alert
            v-if="alert"
            :type="alert.type"
            variant="tonal"
            closable
            class="mb-4"
            @click:close="alert = null"
        >
            {{ alert.message }}
        </v-alert>

        <v-data-table
            :headers="kpiHeaders"
            :items="kpis"
            :loading="loading"
            show-expand
            hover
            class="rounded-lg"
        >
            <template v-slot:item.actions="{ item }">
                <v-icon size="small" class="mr-2" @click="openKpiDialog(item)">
                    mdi-pencil
                </v-icon>
                <!--v-icon
                    size="small"
                    color="error"
                    @click="confirmDeleteKpi(item)"
                >
                    mdi-delete
                </v-icon-->
            </template>
            <template v-slot:expanded-row="{ item }">
                <td :colspan="kpiHeaders.length">
                    <div class="pa-4">
                        <div class="d-flex align-center mb-2">
                            <span class="text-subtitle-2">Objectives</span>
                            <v-spacer></v-spacer>
                            <v-btn
                                size="small"
                                prepend-icon="mdi-plus"
                                @click="openObjectiveDialog(item.id)"
                            >
                                Add Objective
                            </v-btn>
                        </div>

                        <v-data-table
                            :headers="objectiveHeaders"
                            :items="getObjectives(item.id)"
                            density="compact"
                            class="rounded-lg"
                        >
                            <template v-slot:item.start_date="{ value }">
                                {{ formatDate(value) }}
                            </template>
                            <template v-slot:item.end_date="{ value }">
                                {{ formatDate(value) }}
                            </template>
                            <template v-slot:item.actions="{ item: obj }">
                                <v-icon
                                    size="small"
                                    class="mr-2"
                                    @click="
                                        openObjectiveDialog(obj.kpi_id, obj)
                                    "
                                >
                                    mdi-pencil
                                </v-icon>
                                <v-icon
                                    size="small"
                                    color="error"
                                    @click="confirmDeleteObjective(obj)"
                                >
                                    mdi-delete
                                </v-icon>
                            </template>
                            <template v-slot:no-data>
                                No objectives defined.
                            </template>
                        </v-data-table>
                    </div>
                </td>
            </template>
        </v-data-table>

        <v-dialog v-model="kpiDialog" max-width="500">
            <v-card :title="editingKpi ? 'Edit KPI' : 'New KPI'">
                <v-card-text>
                    <v-text-field
                        v-model="kpiForm.name"
                        label="Name"
                        variant="outlined"
                        density="compact"
                    ></v-text-field>
                    <v-textarea
                        v-model="kpiForm.description"
                        label="Description"
                        variant="outlined"
                        density="compact"
                        rows="3"
                    ></v-textarea>
                    <v-text-field
                        v-model="kpiForm.col_name"
                        label="Column Name"
                        variant="outlined"
                        density="compact"
                    ></v-text-field>
                    <v-text-field
                        v-model="kpiForm.unit"
                        label="Unit"
                        variant="outlined"
                        density="compact"
                    ></v-text-field>
                    <v-select
                        v-model="kpiForm.periodicity"
                        :items="['monthly', 'year to date', 'year']"
                        label="Periodicity"
                        variant="outlined"
                        density="compact"
                    ></v-select>
                    <v-select
                        v-model="kpiForm.type"
                        :items="['quantitative', 'qualitative', 'calculated']"
                        label="Type"
                        variant="outlined"
                        density="compact"
                    ></v-select>
                </v-card-text>
                <v-card-actions>
                    <v-spacer></v-spacer>
                    <v-btn variant="text" @click="kpiDialog = false"
                        >Cancel</v-btn
                    >
                    <v-btn
                        color="primary"
                        variant="elevated"
                        :loading="saving"
                        @click="saveKpi"
                    >
                        Save
                    </v-btn>
                </v-card-actions>
            </v-card>
        </v-dialog>

        <v-dialog v-model="objectiveDialog" max-width="500">
            <v-card
                :title="editingObjective ? 'Edit Objective' : 'New Objective'"
            >
                <v-card-text>
                    <v-text-field
                        v-model="objectiveForm.start_date"
                        label="Start Date"
                        type="date"
                        variant="outlined"
                        density="compact"
                    ></v-text-field>
                    <v-text-field
                        v-model="objectiveForm.end_date"
                        label="End Date"
                        type="date"
                        variant="outlined"
                        density="compact"
                    ></v-text-field>
                    <v-text-field
                        v-model="objectiveForm.value"
                        label="Value"
                        type="number"
                        variant="outlined"
                        density="compact"
                    ></v-text-field>
                </v-card-text>
                <v-card-actions>
                    <v-spacer></v-spacer>
                    <v-btn variant="text" @click="objectiveDialog = false"
                        >Cancel</v-btn
                    >
                    <v-btn
                        color="primary"
                        variant="elevated"
                        :loading="saving"
                        @click="saveObjective"
                    >
                        Save
                    </v-btn>
                </v-card-actions>
            </v-card>
        </v-dialog>

        <v-dialog v-model="confirmDialog" max-width="400">
            <v-card title="Confirm Delete">
                <v-card-text>{{ confirmMessage }}</v-card-text>
                <v-card-actions>
                    <v-spacer></v-spacer>
                    <v-btn variant="text" @click="confirmDialog = false"
                        >Cancel</v-btn
                    >
                    <v-btn
                        color="error"
                        variant="elevated"
                        :loading="saving"
                        @click="executeDelete"
                    >
                        Delete
                    </v-btn>
                </v-card-actions>
            </v-card>
        </v-dialog>
    </v-container>
</template>

<script setup>
import { ref, onMounted } from "vue";
import axios from "axios";

const kpiHeaders = [
    { title: "Name", key: "name" },
    { title: "Column", key: "col_name" },
    { title: "Unit", key: "unit" },
    { title: "Periodicity", key: "periodicity" },
    { title: "Type", key: "type" },
    { title: "", key: "actions", sortable: false, align: "end" },
];

const objectiveHeaders = [
    { title: "Start Date", key: "start_date" },
    { title: "End Date", key: "end_date" },
    { title: "Value", key: "value" },
    { title: "", key: "actions", sortable: false, align: "end" },
];

const kpis = ref([]);
const objectives = ref([]);
const loading = ref(true);
const saving = ref(false);
const alert = ref(null);

const kpiDialog = ref(false);
const editingKpi = ref(null);
const kpiForm = ref({
    name: "",
    description: "",
    col_name: "",
    unit: "",
    periodicity: "monthly",
    type: "quantitative",
});

const objectiveDialog = ref(false);
const editingObjective = ref(null);
const objectiveKpiId = ref(null);
const objectiveForm = ref({
    start_date: "",
    end_date: "",
    value: "",
});

const confirmDialog = ref(false);
const confirmMessage = ref("");
const deleteAction = ref(null);

function showAlert(type, message) {
    alert.value = { type, message };
}

function formatDate(dateStr) {
    if (!dateStr) return "";
    return new Date(dateStr).toISOString().split("T")[0];
}

function getObjectives(kpiId) {
    return objectives.value.filter((o) => o.kpi_id === kpiId);
}

function openKpiDialog(item = null) {
    if (item) {
        editingKpi.value = item;
        kpiForm.value = {
            name: item.name,
            description: item.description || "",
            col_name: item.col_name,
            unit: item.unit,
            periodicity: item.periodicity,
            type: item.type,
        };
    } else {
        editingKpi.value = null;
        kpiForm.value = {
            name: "",
            description: "",
            col_name: "",
            unit: "",
            periodicity: "monthly",
            type: "quantitative",
        };
    }
    kpiDialog.value = true;
}

function openObjectiveDialog(kpiId, item = null) {
    objectiveKpiId.value = kpiId;
    if (item) {
        editingObjective.value = item;
        objectiveForm.value = {
            start_date: formatDate(item.start_date),
            end_date: formatDate(item.end_date),
            value: item.value,
        };
    } else {
        editingObjective.value = null;
        objectiveForm.value = {
            start_date: "",
            end_date: "",
            value: "",
        };
    }
    objectiveDialog.value = true;
}

function confirmDeleteKpi(item) {
    confirmMessage.value = `Delete KPI "${item.name}" and all its objectives?`;
    deleteAction.value = async () => {
        await axios.delete(`/api/kpis/${item.id}`);
        kpis.value = kpis.value.filter((k) => k.id !== item.id);
        objectives.value = objectives.value.filter((o) => o.kpi_id !== item.id);
        showAlert("success", `KPI "${item.name}" deleted.`);
    };
    confirmDialog.value = true;
}

function confirmDeleteObjective(item) {
    confirmMessage.value = "Delete this objective?";
    deleteAction.value = async () => {
        await axios.delete(`/api/kpis/${item.kpi_id}/objectives/${item.id}`);
        objectives.value = objectives.value.filter((o) => o.id !== item.id);
        showAlert("success", "Objective deleted.");
    };
    confirmDialog.value = true;
}

async function executeDelete() {
    saving.value = true;
    try {
        await deleteAction.value();
        confirmDialog.value = false;
    } catch (err) {
        showAlert("error", err.response?.data?.message || "Failed to delete.");
    } finally {
        saving.value = false;
    }
}

async function saveKpi() {
    saving.value = true;
    try {
        if (editingKpi.value) {
            const { data } = await axios.put(
                `/api/kpis/${editingKpi.value.id}`,
                kpiForm.value,
            );
            const index = kpis.value.findIndex((k) => k.id === data.id);
            kpis.value.splice(index, 1, data);
            showAlert("success", "KPI updated.");
        } else {
            const { data } = await axios.post("/api/kpis", kpiForm.value);
            kpis.value.push(data);
            showAlert("success", "KPI created.");
        }
        kpiDialog.value = false;
    } catch (err) {
        showAlert(
            "error",
            err.response?.data?.message || "Failed to save KPI.",
        );
    } finally {
        saving.value = false;
    }
}

async function saveObjective() {
    saving.value = true;
    try {
        const url = editingObjective.value
            ? `/api/kpis/${objectiveKpiId.value}/objectives/${editingObjective.value.id}`
            : `/api/kpis/${objectiveKpiId.value}/objectives`;
        const method = editingObjective.value ? "put" : "post";

        const { data } = await axios[method](url, {
            start_date: objectiveForm.value.start_date,
            end_date: objectiveForm.value.end_date,
            value: Number(objectiveForm.value.value),
        });

        if (editingObjective.value) {
            const index = objectives.value.findIndex((o) => o.id === data.id);
            objectives.value.splice(index, 1, data);
            showAlert("success", "Objective updated.");
        } else {
            objectives.value.push(data);
            showAlert("success", "Objective created.");
        }
        objectiveDialog.value = false;
    } catch (err) {
        showAlert(
            "error",
            err.response?.data?.message || "Failed to save objective.",
        );
    } finally {
        saving.value = false;
    }
}

onMounted(async () => {
    try {
        const [kpiRes, objRes] = await Promise.all([
            axios.get("/api/kpis"),
            axios.get("/api/objectives"),
        ]);
        kpis.value = kpiRes.data;
        objectives.value = objRes.data;
    } catch {
        showAlert("error", "Failed to load data.");
    } finally {
        loading.value = false;
    }
});
</script>
