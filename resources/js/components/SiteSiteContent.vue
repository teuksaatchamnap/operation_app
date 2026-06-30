<template>
    <v-card flat>
        <v-tabs v-model="tab" density="compact" slider-color="primary">
            <v-tab value="site" prepend-icon="mdi-information-outline"
                >Site</v-tab
            >
            <v-tab
                value="entrepreneur-history"
                prepend-icon="mdi-account-switch"
                >Entrepreneur history</v-tab
            >
        </v-tabs>
        <v-divider />
        <v-card-text>
            <v-tabs-window v-model="tab">
                <v-tabs-window-item value="site">
                    <template v-if="loading">
                        <v-card variant="outlined" class="subtle-border">
                            <v-card-title
                                class="section-title d-flex align-center ga-2"
                            >
                                <v-icon size="small" color="primary"
                                    >mdi-account-details</v-icon
                                >
                                Site Profile
                            </v-card-title>
                            <v-card-text>
                                <v-row density="comfortable">
                                    <v-col v-for="i in 8" :key="i" cols="6" sm="4" md="3">
                                        <div class="skeleton skeleton-label" />
                                        <div
                                            class="skeleton skeleton-value mt-1"
                                        />
                                    </v-col>
                                </v-row>
                            </v-card-text>
                        </v-card>

                        <v-card variant="outlined" class="subtle-border mt-4">
                            <v-card-title
                                class="section-title d-flex align-center ga-2"
                            >
                                <v-icon size="small" color="primary"
                                    >mdi-map-marker</v-icon
                                >
                                Location Details
                            </v-card-title>
                            <v-card-text>
                                <v-row density="comfortable">
                                    <v-col v-for="i in 4" :key="i" cols="6" sm="4" md="3">
                                        <div class="skeleton skeleton-label" />
                                        <div
                                            class="skeleton skeleton-value mt-1"
                                        />
                                    </v-col>
                                </v-row>
                            </v-card-text>
                        </v-card>

                        <v-card variant="outlined" class="subtle-border mt-4">
                            <v-card-title
                                class="section-title d-flex align-center ga-2"
                            >
                                <v-icon size="small" color="primary"
                                    >mdi-account-group</v-icon
                                >
                                Demographics
                            </v-card-title>
                            <v-card-text>
                                <v-row density="comfortable">
                                    <v-col v-for="i in 4" :key="i" cols="6" sm="4" md="3">
                                        <div class="skeleton skeleton-label" />
                                        <div
                                            class="skeleton skeleton-value mt-1"
                                        />
                                    </v-col>
                                </v-row>
                            </v-card-text>
                        </v-card>

                        <v-card variant="outlined" class="subtle-border mt-4">
                            <v-card-title
                                class="section-title d-flex align-center ga-2"
                            >
                                <v-icon size="small" color="primary"
                                    >mdi-file-document-outline</v-icon
                                >
                                Project
                            </v-card-title>
                            <v-card-text>
                                <v-row density="comfortable">
                                    <v-col v-for="i in 3" :key="i" cols="6" sm="4" md="3">
                                        <div class="skeleton skeleton-label" />
                                        <div
                                            class="skeleton skeleton-value mt-1"
                                        />
                                    </v-col>
                                </v-row>
                            </v-card-text>
                        </v-card>

                        <v-card variant="outlined" class="subtle-border mt-4">
                            <v-card-title
                                class="section-title d-flex align-center ga-2"
                            >
                                <v-icon size="small" color="primary"
                                    >mdi-office-building-outline</v-icon
                                >
                                Infrastructure
                            </v-card-title>
                            <v-card-text>
                                <v-row density="comfortable">
                                    <v-col v-for="i in 8" :key="i" cols="6" sm="4" md="3">
                                        <div class="skeleton skeleton-label" />
                                        <div
                                            class="skeleton skeleton-value mt-1"
                                        />
                                    </v-col>
                                </v-row>
                            </v-card-text>
                        </v-card>
                    </template>

                    <v-row v-else-if="error" class="text-center">
                        <v-col>
                            <div class="text-medium-emphasis">
                                Failed to load site data
                            </div>
                        </v-col>
                    </v-row>

                    <template v-else-if="data">
                        <v-card variant="outlined" class="subtle-border">
                            <v-card-title
                                class="section-title d-flex align-center ga-2"
                            >
                                <v-icon size="small" color="primary"
                                    >mdi-account-details</v-icon
                                >
                                Site Profile
                            </v-card-title>
                            <v-card-text>
                                <v-row density="comfortable">
                                    <v-col cols="6" sm="4" md="3">
                                        <div
                                            class="caption-label text-medium-emphasis"
                                        >
                                            Location
                                        </div>
                                        <div class="text-body-1">
                                            <a
                                                v-if="googleMapsUrl"
                                                :href="googleMapsUrl"
                                                target="_blank"
                                                rel="noopener noreferrer"
                                                class="location-link"
                                                >{{ formattedLocation }}</a
                                            >
                                            <template v-else>{{
                                                formattedLocation
                                            }}</template>
                                        </div>
                                    </v-col>
                                    <v-col cols="6" sm="4" md="3">
                                        <div
                                            class="caption-label text-medium-emphasis"
                                        >
                                            Entrepreneur
                                        </div>
                                        <div class="text-body-1">
                                            {{
                                                data.profile.entrepreneur ?? "-"
                                            }}
                                        </div>
                                    </v-col>
                                    <v-col cols="6" sm="4" md="3">
                                        <div
                                            class="caption-label text-medium-emphasis"
                                        >
                                            Advisor
                                        </div>
                                        <div class="text-body-1">
                                            {{ data.profile.advisor ?? "-" }}
                                            <span class="text-medium-emphasis"
                                                >(TODO)</span
                                            >
                                        </div>
                                    </v-col>
                                    <v-col cols="6" sm="4" md="3">
                                        <div
                                            class="caption-label text-medium-emphasis"
                                        >
                                            ROM
                                        </div>
                                        <div class="text-body-1">
                                            {{ data.profile.rom ?? "-" }}
                                        </div>
                                    </v-col>
                                    <v-col cols="6" sm="4" md="3">
                                        <div
                                            class="caption-label text-medium-emphasis"
                                        >
                                            Technician
                                        </div>
                                        <div class="text-body-1">
                                            {{ data.profile.technician ?? "-" }}
                                            <span class="text-medium-emphasis"
                                                >(TODO)</span
                                            >
                                        </div>
                                    </v-col>
                                    <v-col cols="6" sm="4" md="3">
                                        <div
                                            class="caption-label text-medium-emphasis"
                                        >
                                            KOL (Key Opinion Leader)
                                        </div>
                                        <div class="text-body-1">
                                            <span class="text-medium-emphasis"
                                                >TODO</span
                                            >
                                        </div>
                                    </v-col>
                                    <v-col cols="6" sm="4" md="3">
                                        <div
                                            class="caption-label text-medium-emphasis"
                                        >
                                            Installation Date
                                        </div>
                                        <div class="text-body-1">
                                            {{
                                                data.profile
                                                    .installation_date ?? "-"
                                            }}
                                        </div>
                                    </v-col>
                                    <v-col cols="6" sm="4" md="3">
                                        <div
                                            class="caption-label text-medium-emphasis"
                                        >
                                            Phone
                                        </div>
                                        <div class="text-body-1">
                                            {{ data.profile.phone ?? "-" }}
                                        </div>
                                    </v-col>
                                    <v-col cols="6" sm="4" md="3">
                                        <div
                                            class="caption-label text-medium-emphasis"
                                        >
                                            Education
                                        </div>
                                        <div class="text-body-1">
                                            {{ data.profile.education ?? "-" }}
                                        </div>
                                    </v-col>
                                    <v-col cols="6" sm="4" md="3">
                                        <div
                                            class="caption-label text-medium-emphasis"
                                        >
                                            Previous Job
                                        </div>
                                        <div class="text-body-1">
                                            {{
                                                data.profile.previous_job ?? "-"
                                            }}
                                        </div>
                                    </v-col>
                                </v-row>
                            </v-card-text>
                        </v-card>

                        <v-card variant="outlined" class="subtle-border mt-4">
                            <v-card-title
                                class="section-title d-flex align-center ga-2"
                            >
                                <v-icon size="small" color="primary"
                                    >mdi-map-marker</v-icon
                                >
                                Location Details
                                <v-spacer />
                                <v-btn
                                    variant="text"
                                    color="primary"
                                    size="small"
                                    :loading="downloading"
                                    :disabled="!site?.id"
                                    @click="downloadCommuneContract"
                                    prepend-icon="mdi-download"
                                >
                                    Commune Contract
                                </v-btn>
                            </v-card-title>
                            <v-card-text>
                                <v-row density="comfortable">
                                    <v-col cols="6" sm="4" md="3">
                                        <div
                                            class="caption-label text-medium-emphasis"
                                        >
                                            Village
                                        </div>
                                        <div class="text-body-1">
                                            {{
                                                data.location.village.en ?? "-"
                                            }}
                                            <span
                                                v-if="data.location.village.km"
                                                class="text-medium-emphasis"
                                                >({{
                                                    data.location.village.km
                                                }})</span
                                            >
                                        </div>
                                    </v-col>
                                    <v-col cols="6" sm="4" md="3">
                                        <div
                                            class="caption-label text-medium-emphasis"
                                        >
                                            Commune
                                        </div>
                                        <div class="text-body-1">
                                            {{
                                                data.location.commune.en ?? "-"
                                            }}
                                            <span
                                                v-if="data.location.commune.km"
                                                class="text-medium-emphasis"
                                                >({{
                                                    data.location.commune.km
                                                }})</span
                                            >
                                        </div>
                                    </v-col>
                                    <v-col cols="6" sm="4" md="3">
                                        <div
                                            class="caption-label text-medium-emphasis"
                                        >
                                            District
                                        </div>
                                        <div class="text-body-1">
                                            {{
                                                data.location.district.en ?? "-"
                                            }}
                                            <span
                                                v-if="data.location.district.km"
                                                class="text-medium-emphasis"
                                                >({{
                                                    data.location.district.km
                                                }})</span
                                            >
                                        </div>
                                    </v-col>
                                    <v-col cols="6" sm="4" md="3">
                                        <div
                                            class="caption-label text-medium-emphasis"
                                        >
                                            Province
                                        </div>
                                        <div class="text-body-1">
                                            {{
                                                data.location.province.en ?? "-"
                                            }}
                                            <span
                                                v-if="data.location.province.km"
                                                class="text-medium-emphasis"
                                                >({{
                                                    data.location.province.km
                                                }})</span
                                            >
                                        </div>
                                    </v-col>
                                </v-row>
                            </v-card-text>
                        </v-card>

                        <v-card variant="outlined" class="subtle-border mt-4">
                            <v-card-title
                                class="section-title d-flex align-center ga-2"
                            >
                                <v-icon size="small" color="primary"
                                    >mdi-account-group</v-icon
                                >
                                Demographics
                            </v-card-title>
                            <v-card-text>
                                <v-row density="comfortable">
                                    <v-col cols="6" sm="4" md="3">
                                        <div
                                            class="caption-label text-medium-emphasis"
                                        >
                                            Villages in Commune
                                        </div>
                                        <div class="text-body-1">
                                            {{
                                                data.demographics
                                                    .villages_in_commune ?? "-"
                                            }}
                                        </div>
                                    </v-col>
                                    <v-col cols="6" sm="4" md="3">
                                        <div
                                            class="caption-label text-medium-emphasis"
                                        >
                                            Number of Families
                                        </div>
                                        <div class="text-body-1">
                                            {{ formattedFamilies }}
                                        </div>
                                    </v-col>
                                    <v-col cols="6" sm="4" md="3">
                                        <div
                                            class="caption-label text-medium-emphasis"
                                        >
                                            Households
                                        </div>
                                        <div class="text-body-1">
                                            {{ formattedHouseholds }}
                                        </div>
                                    </v-col>
                                    <v-col cols="6" sm="4" md="3">
                                        <div
                                            class="caption-label text-medium-emphasis"
                                        >
                                            Commune Population
                                        </div>
                                        <div class="text-body-1">
                                            {{ formattedPopulation }}
                                        </div>
                                    </v-col>
                                </v-row>
                            </v-card-text>
                        </v-card>

                        <v-card variant="outlined" class="subtle-border mt-4">
                            <v-card-title
                                class="section-title d-flex align-center ga-2"
                            >
                                <v-icon size="small" color="primary"
                                    >mdi-file-document-outline</v-icon
                                >
                                Project
                            </v-card-title>
                            <v-card-text>
                                <v-row density="comfortable">
                                    <v-col cols="6" sm="4" md="3">
                                        <div
                                            class="caption-label text-medium-emphasis"
                                        >
                                            Project Agreement Date
                                        </div>
                                        <div class="text-body-1">
                                            {{
                                                data.project?.agreement_date ??
                                                "-"
                                            }}
                                        </div>
                                    </v-col>
                                    <v-col cols="6" sm="4" md="3">
                                        <div
                                            class="caption-label text-medium-emphasis"
                                        >
                                            Wave
                                        </div>
                                        <div class="text-body-1">
                                            {{ data.project?.wave ?? "-" }}
                                        </div>
                                    </v-col>
                                    <v-col cols="6" sm="4" md="3">
                                        <div
                                            class="caption-label text-medium-emphasis"
                                        >
                                            Funders
                                        </div>
                                        <div class="text-body-1">
                                            {{ data.project?.funders ?? "-" }}
                                        </div>
                                    </v-col>
                                </v-row>
                            </v-card-text>
                        </v-card>

                        <v-card variant="outlined" class="subtle-border mt-4">
                            <v-card-title
                                class="section-title d-flex align-center ga-2"
                            >
                                <v-icon size="small" color="primary"
                                    >mdi-office-building-outline</v-icon
                                >
                                Infrastructure
                            </v-card-title>
                            <v-card-text>
                                <v-row density="comfortable">
                                    <v-col cols="6" sm="4" md="3">
                                        <div
                                            class="caption-label text-medium-emphasis"
                                        >
                                            Number of Pagodas
                                        </div>
                                        <div class="text-body-1">
                                            {{
                                                data.infrastructure
                                                    ?.number_of_pagodas ?? "-"
                                            }}
                                        </div>
                                    </v-col>
                                    <v-col cols="6" sm="4" md="3">
                                        <div
                                            class="caption-label text-medium-emphasis"
                                        >
                                            Number of Primary Schools
                                        </div>
                                        <div class="text-body-1">
                                            {{
                                                data.infrastructure
                                                    ?.number_of_primary_schools ??
                                                "-"
                                            }}
                                        </div>
                                    </v-col>
                                    <v-col cols="6" sm="4" md="3">
                                        <div
                                            class="caption-label text-medium-emphasis"
                                        >
                                            Kiosk Land
                                        </div>
                                        <div class="text-body-1">
                                            {{
                                                data.infrastructure
                                                    ?.kiosk_land ?? "-"
                                            }}
                                        </div>
                                    </v-col>
                                    <v-col cols="6" sm="4" md="3">
                                        <div
                                            class="caption-label text-medium-emphasis"
                                        >
                                            Kiosk Road Type
                                        </div>
                                        <div class="text-body-1">
                                            {{
                                                data.infrastructure
                                                    ?.kiosk_road_type ?? "-"
                                            }}
                                        </div>
                                    </v-col>
                                    <v-col cols="6" sm="4" md="3">
                                        <div
                                            class="caption-label text-medium-emphasis"
                                        >
                                            % Paved Asphalt
                                        </div>
                                        <div class="text-body-1">
                                            {{
                                                data.infrastructure
                                                    ?.paved_asphalt_pct ?? "-"
                                            }}
                                        </div>
                                    </v-col>
                                    <v-col cols="6" sm="4" md="3">
                                        <div
                                            class="caption-label text-medium-emphasis"
                                        >
                                            % Concrete Road
                                        </div>
                                        <div class="text-body-1">
                                            {{
                                                data.infrastructure
                                                    ?.concrete_road_pct ?? "-"
                                            }}
                                        </div>
                                    </v-col>
                                    <v-col cols="6" sm="4" md="3">
                                        <div
                                            class="caption-label text-medium-emphasis"
                                        >
                                            % Laterite Road
                                        </div>
                                        <div class="text-body-1">
                                            {{
                                                data.infrastructure
                                                    ?.laterite_road_pct ?? "-"
                                            }}
                                        </div>
                                    </v-col>
                                    <v-col cols="6" sm="4" md="3">
                                        <div
                                            class="caption-label text-medium-emphasis"
                                        >
                                            % White Soiled Road
                                        </div>
                                        <div class="text-body-1">
                                            {{
                                                data.infrastructure
                                                    ?.white_soiled_road_pct ??
                                                "-"
                                            }}
                                        </div>
                                    </v-col>
                                </v-row>
                            </v-card-text>
                        </v-card>
                    </template>
                </v-tabs-window-item>

                <v-tabs-window-item value="entrepreneur-history">
                    <div
                        v-if="entrepreneurLoading"
                        class="d-flex justify-center py-8"
                    >
                        <v-progress-circular indeterminate color="primary" />
                    </div>

                    <v-row v-else-if="entrepreneurError" class="text-center">
                        <v-col>
                            <div class="text-medium-emphasis">
                                Failed to load entrepreneur history
                            </div>
                        </v-col>
                    </v-row>

                    <v-row v-else-if="!entrepreneurItems.length" class="text-center">
                        <v-col>
                            <div class="text-medium-emphasis">
                                No entrepreneur records found for this site
                            </div>
                        </v-col>
                    </v-row>

                    <template v-else>
                    <div class="table-scroll">
                    <v-data-table
                        :headers="entrepreneurHeaders"
                        :items="entrepreneurItems"
                        density="compact"
                        :items-per-page="-1"
                        class="text-body-2"
                        hide-default-footer
                        :item-class="rowClass"
                    >
                        <template #item.name="{ item }">
                            <div class="d-flex align-center ga-2">
                                <div>
                                    <div>
                                        {{
                                            item.Entrepreneur_Khmer_name ?? "-"
                                        }}
                                    </div>
                                    <div>
                                        {{
                                            item.Entrepreneur_English_name ??
                                            "-"
                                        }}
                                    </div>
                                </div>
                                <v-chip
                                    v-if="item._isCurrent"
                                    color="success"
                                    size="x-small"
                                    variant="tonal"
                                >
                                    Current
                                </v-chip>
                            </div>
                        </template>
                        <template #item.Working_Date="{ value }">
                            {{
                                value
                                    ? new Date(value).toLocaleDateString(
                                          "en-GB",
                                      )
                                    : "-"
                            }}
                        </template>
                        <template #item.Resignation_Date="{ value }">
                            {{
                                value
                                    ? new Date(value).toLocaleDateString(
                                          "en-GB",
                                      )
                                    : "-"
                            }}
                        </template>
                        <template #item.Contract="{ item }">
                            <v-chip
                                v-if="item.Contract"
                                size="x-small"
                                color="primary"
                                variant="tonal"
                                @click="
                                    downloadEntrepreneurContract(item.Contract)
                                "
                            >
                                <v-icon start size="x-small"
                                    >mdi-cloud-download</v-icon
                                >
                                Download
                            </v-chip>
                            <span
                                v-else
                                class="text-medium-emphasis text-caption"
                                >—</span
                            >
                        </template>
                    </v-data-table>
                    </div>
                    </template>
                </v-tabs-window-item>
            </v-tabs-window>
        </v-card-text>
    </v-card>
</template>

<script setup>
import axios from "axios";
import { computed, ref, watchEffect } from "vue";

const props = defineProps({
    site: {
        type: Object,
        default: null,
    },
});

const tab = ref("site");

const loading = ref(false);
const error = ref(false);
const data = ref(null);
const downloading = ref(false);

const entrepreneurLoading = ref(false);
const entrepreneurError = ref(false);
const entrepreneurData = ref({ current: null, history: [] });

const entrepreneurHeaders = [
    { title: "Name", key: "name" },
    { title: "Sex", key: "Sex" },
    { title: "Start Date", key: "Working_Date" },
    { title: "Resign Date", key: "Resignation_Date" },
    { title: "Reason", key: "Reason_Resign" },
    { title: "Comment", key: "Detail_Resign" },
    { title: "Contract", key: "Contract", sortable: false },
];

const entrepreneurItems = computed(() => {
    const items = [];
    if (entrepreneurData.value?.current) {
        items.push(entrepreneurData.value.current);
    }
    if (entrepreneurData.value?.history) {
        items.push(...entrepreneurData.value.history);
    }
    return items;
});

function rowClass(item) {
    return item._isCurrent ? "current-entrepreneur-row" : "";
}

const formattedLocation = computed(() => {
    const { lat, lng } = data.value?.profile ?? {};
    if (lat == null && lng == null) return "-";
    return `${lat ?? "?"}°N, ${lng ?? "?"}°E`;
});

const googleMapsUrl = computed(() => {
    const { lat, lng } = data.value?.profile ?? {};
    if (lat == null || lng == null) return null;
    return `https://www.google.com/maps?q=${lat},${lng}`;
});

function formatNumber(num) {
    if (num === null || num === undefined) return "-";
    return Number(num).toLocaleString("en-US");
}

const formattedFamilies = computed(() =>
    formatNumber(data.value?.demographics?.families),
);
const formattedHouseholds = computed(() =>
    formatNumber(data.value?.demographics?.households),
);
const formattedPopulation = computed(() =>
    formatNumber(data.value?.demographics?.population),
);

watchEffect(async () => {
    if (!props.site?.id) return;

    loading.value = true;
    error.value = false;

    try {
        const res = await axios.get(`/api/sites/${props.site.id}/profile`);
        data.value = res.data;
    } catch {
        error.value = true;
        data.value = null;
    } finally {
        loading.value = false;
    }
});

watchEffect(async () => {
    if (!props.site?.id) return;

    entrepreneurLoading.value = true;
    entrepreneurError.value = false;

    try {
        const res = await axios.get(
            `/api/sites/${props.site.id}/entrepreneur-history`,
        );
        entrepreneurData.value = res.data;
    } catch {
        entrepreneurError.value = true;
        entrepreneurData.value = { current: null, history: [] };
    } finally {
        entrepreneurLoading.value = false;
    }
});

const downloadEntrepreneurContract = async (filename) => {
    try {
        const res = await axios.get(
            `/api/download-entrepreneur-contract/${filename}`,
            {
                responseType: "blob",
            },
        );
        const url = window.URL.createObjectURL(new Blob([res.data]));
        const link = document.createElement("a");
        link.href = url;
        link.setAttribute("download", filename);
        document.body.appendChild(link);
        link.click();
        link.remove();
        window.URL.revokeObjectURL(url);
    } catch {
        // silently fail
    }
};

const downloadCommuneContract = async () => {
    downloading.value = true;
    try {
        const res = await axios.get(
            `/api/sites/${props.site.id}/download-commune-contract`,
            {
                responseType: "blob",
            },
        );
        const url = window.URL.createObjectURL(new Blob([res.data]));
        const link = document.createElement("a");
        link.href = url;
        link.setAttribute("download", "commune_contract.pdf");
        document.body.appendChild(link);
        link.click();
        link.remove();
        window.URL.revokeObjectURL(url);
    } catch {
        // silently fail
    } finally {
        downloading.value = false;
    }
};
</script>

<style scoped>
.section-title {
    font-size: 1rem;
    font-weight: 600;
    letter-spacing: 0.0125em;
    padding-block: 14px;
    line-height: 1.5rem;
}

.caption-label {
    font-size: 0.75rem;
}

.subtle-border {
    border-color: rgba(var(--v-theme-on-surface), 0.12) !important;
}

.location-link {
    color: rgb(var(--v-theme-primary));
    text-decoration: none;
}

.location-link:hover {
    text-decoration: underline;
}

.table-scroll {
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
}

.skeleton {
    background: rgba(var(--v-theme-on-surface), 0.08);
    border-radius: 4px;
    animation: skeleton-pulse 1.5s ease-in-out infinite;
}

.skeleton-label {
    height: 10px;
    width: 55%;
}

.skeleton-value {
    height: 18px;
    width: 80%;
}

@keyframes skeleton-pulse {
    0%,
    100% {
        opacity: 1;
    }
    50% {
        opacity: 0.35;
    }
}

:deep(.current-entrepreneur-row td) {
    background-color: rgba(var(--v-theme-success), 0.06) !important;
}
</style>
