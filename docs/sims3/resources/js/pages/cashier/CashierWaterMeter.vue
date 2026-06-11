<script setup>
import { useRoute, useRouter } from "vue-router";
import { usePermissions } from "../../composables/usePermissions";
import { ref } from "vue";
const route = useRoute();
const siteId = route.params.site;
const router = useRouter();
const endDate = route.params.endDate;
const startDate = route.params.startDate;
const files = ref([]);
const existingFiles = ref([]);
const queryParams = {
    start_date: startDate,
    end_date: endDate,
    site: siteId,
};
const loading = ref(true);
const consumption = ref(0);
const saving = ref(false);
const readOnly = ref(true);
const lastWaterMeter = defineModel("lastWaterMeter", { type: Number });
const currentWaterMeter = defineModel("currentWaterMeter", { type: Number });
const errors = ref({});
const { isCashierAdmin } = usePermissions();

const createObjectURL = (file) => {
    return URL.createObjectURL(file);
};

const uploadFiles = async () => {
    if (files.value.length === 0) {
        return;
    }
    const formData = new FormData();
    files.value.forEach((file) => {
        formData.append("files[]", file);
    });
    formData.append("site", siteId);
    formData.append("related_date", endDate);
    formData.append("type", "water_meter");
    try {
        await window.axios.post("/api/cashier/upload", formData, {
            headers: { "Content-Type": "multipart/form-data" },
        });
        console.log("Files uploaded successfully in the background.");
        files.value = [];
    } catch (error) {
        console.error("Error uploading files:", error);
    }
};

window.axios
    .get("/api/cashier/water", {
        params: queryParams,
    })
    .then((response) => {
        lastWaterMeter.value = response.data.previous;
        currentWaterMeter.value = response.data.current;
        existingFiles.value = response.data.images;
        consumption.value = response.data.consumption;
        loading.value = false;
        if(isCashierAdmin.value || response.data.current == null) {
            readOnly.value = false;
        }
    });

const save = async () => {
    if(readOnly.value == true) {
        return;
    }
    saving.value = true;
    errors.value = {}; // Clear previous errors
    try {
        await window.axios.post("/api/cashier/water", {
            site: siteId,
            end_date: endDate,
            value: currentWaterMeter.value,
        });
        await uploadFiles();
    } catch (error) {
        if (
            error.response &&
            error.response.data &&
            error.response.data.errors
        ) {
            errors.value = error.response.data.errors;
            console.error("Validation errors:", errors.value);
        } else if (
            error.response &&
            error.response.data &&
            error.response.data.message
        ) {
            errors.value = { general: [error.response.data.message] };
            console.error(
                "Error saving water meter data:",
                error.response.data.message
            );
        } else {
            console.error("An unexpected error occurred:", error);
        }
        throw error;
    } finally {
        saving.value = false;
    }
};

defineExpose({ save });

</script>

<template>
    <div>
        <div v-if="loading" class="d-flex justify-center mt-10 pt-10">
            <v-progress-circular indeterminate :size="60" color="primary" />
        </div>
        <div v-else class="pt-2">
            <v-row align="center" justify="center">
                <v-col cols="12" md="6">
                    <v-table>
                        <thead>
                            <tr>
                                <th class="text-left">Metric</th>
                                <th class="text-left">Value</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr class="previous-reading">
                                <td>Previous Week Reading</td>
                                <td class="pl-5">
                                    {{ lastWaterMeter }}
                                </td>
                            </tr>
                            <tr>
                                <td>Current Week Reading</td>
                                <td>
                                    <v-number-input
                                        v-if="!readOnly"
                                        v-model="currentWaterMeter"
                                        density="compact"
                                        hide-details
                                        control-variant="hidden"
                                        :min="0"
                                        autocomplete="off"
                                    />
                                    <span v-else>
                                        {{ currentWaterMeter }}
                                    </span>
                                    <div
                                        v-if="errors.value"
                                        class="v-input__details"
                                    >
                                        <div
                                            class="v-messages__message text-error"
                                        >
                                            {{ errors.value }}
                                        </div>
                                    </div>
                                </td>
                            </tr>
                        </tbody>
                    </v-table>
                </v-col>
            </v-row>

            <v-row>
                <v-col
                    v-for="(file, index) in existingFiles"
                    :key="'existingFiles' + index"
                    class="pic-scroll"
                >
                    <v-img
                        :src="file.path.replace('public/', 'storage/')"
                        style="max-height: 200px"
                    >
                        <template #placeholder>
                            <v-row
                                class="fill-height ma-0"
                                align="center"
                                justify="center"
                            >
                                <v-progress-circular
                                    indeterminate
                                    color="grey-lighten-5"
                                />
                            </v-row>
                        </template>
                    </v-img>
                </v-col>
            </v-row>

            <v-row justify="center" align="center">
                <v-col
                    v-if="!files.length"
                    class="px-5"
                    cols="auto"
                >
                    <div class="text-center">
                        <v-file-input
                            v-model="files"
                            label="Add picture from entrepreneur"
                            multiple
                            placeholder="Add picture from entrepreneur"
                            prepend-icon="mdi-paperclip"
                            variant="outlined"
                            accept="image/*"
                            class="w-300"
                        />
                    </div>
                </v-col>
                <v-col
                    v-for="(file, index) in files"
                    v-else
                    :key="index"
                    class="pic-scroll"
                >
                    <v-img
                        :src="createObjectURL(file)"
                        style="min-height: 500px; width: 100%"
                    >
                        <template #placeholder>
                            <v-row
                                class="fill-height ma-0"
                                align="center"
                                justify="center"
                            >
                                <v-progress-circular
                                    indeterminate
                                    color="grey-lighten-5"
                                />
                            </v-row>
                        </template>
                    </v-img>
                    <div class="text-center">
                        <v-btn
                            class="mt-2 text-center"
                            @click="files.splice(index, 1)"
                        >
                            delete picture
                        </v-btn>
                    </div>
                </v-col>
            </v-row>
        </div>
    </div>
</template>

<style scoped>
.previous-reading {
    background-color: #f5f5f5; /* A light gray color */
    color: #555;
}
.text-center :deep(input) {
    text-align: center;
}
.w-300 {
    width: 300px;
}
.pic-scroll {
    max-height: 200px;
    overflow-y: scroll;
    max-width: 95%;
}
</style>
