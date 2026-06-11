<template>
    <v-container fluid class="pa-4" style="max-width: 900px">
        <h2 class="mb-4">Province Report</h2>

        <v-card class="pa-4">
            <v-row dense>
                <v-col cols="12" sm="6" md="4">
                    <v-text-field
                        v-model="selectedMonth"
                        label="Month"
                        type="month"
                        density="compact"
                        hide-details
                    />
                </v-col>
                <v-col cols="12" sm="6" md="4">
                    <v-select
                        v-model="selectedProvince"
                        :items="provinces"
                        item-title="display"
                        item-value="name"
                        label="Province"
                        density="compact"
                        hide-details
                        :loading="loadingProvinces"
                        :disabled="!provinces.length"
                    />
                </v-col>
                <v-col cols="12" sm="6" md="4">
                    <v-select
                        v-model="selectedFormat"
                        :items="formatOptions"
                        item-title="title"
                        item-value="value"
                        label="Format"
                        density="compact"
                        hide-details
                    />
                </v-col>
            </v-row>

            <v-row dense class="mt-4">
                <v-col cols="12">
                    <v-btn
                        color="success"
                        :loading="loadingDownload"
                        :disabled="!canDownload"
                        @click="download"
                        block
                    >
                        <v-icon start>mdi-download</v-icon>
                        Download report
                    </v-btn>
                </v-col>
            </v-row>

            <v-alert
                v-if="errorMessage"
                type="error"
                density="compact"
                class="mt-3"
                closable
                @click:close="errorMessage = ''"
            >
                {{ errorMessage }}
            </v-alert>
        </v-card>
    </v-container>
</template>

<script>
export default {
    name: "ProvinceReport",
    data() {
        const now = new Date();
        now.setDate(1);
        now.setMonth(now.getMonth() - 1);
        const yyyy = now.getFullYear();
        const mm = String(now.getMonth() + 1).padStart(2, "0");
        return {
            selectedMonth: `${yyyy}-${mm}`,
            provinces: [],
            selectedProvince: null,
            loadingProvinces: false,
            loadingDownload: false,
            errorMessage: "",
            selectedFormat: "docx",
            formatOptions: [
                { title: "Microsoft Word (.docx)", value: "docx" },
                { title: "LibreOffice (.odt)",     value: "odt"  },
            ],
        };
    },
    computed: {
        monthDate() {
            return this.selectedMonth ? `${this.selectedMonth}-01` : null;
        },
        canDownload() {
            return !!this.selectedProvince && !!this.monthDate;
        },
    },
    watch: {
        selectedMonth: {
            immediate: true,
            handler() {
                this.loadProvinces();
            },
        },
    },
    methods: {
        async loadProvinces() {
            if (!this.monthDate) return;
            this.loadingProvinces = true;
            try {
                const { data } = await window.axios.get(
                    "/api/provinceReport/provinces",
                    { params: { month: this.monthDate } }
                );
                this.provinces = (data.provinces ?? []).map((p) => ({
                    ...p,
                    display: `${p.name} (${p.name_khmer})`,
                }));
                if (
                    this.selectedProvince &&
                    !this.provinces.find((p) => p.name === this.selectedProvince)
                ) {
                    this.selectedProvince = null;
                }
            } catch (e) {
                this.errorMessage = "Failed to load provinces.";
            } finally {
                this.loadingProvinces = false;
            }
        },
        async download() {
            if (!this.canDownload) return;
            this.errorMessage = "";
            this.loadingDownload = true;
            try {
                const response = await window.axios.get(
                    "/api/provinceReport/download",
                    {
                        params: {
                            month:    this.monthDate,
                            province: this.selectedProvince,
                            format:   this.selectedFormat,
                        },
                        responseType: "blob",
                    }
                );

                // Server may return JSON error with 200 only if mime detection is wrong;
                // otherwise axios throws on 4xx/5xx and we land in catch.
                const blob = new Blob([response.data], {
                    type: response.headers["content-type"],
                });

                const [, mm] = this.selectedMonth.split("-");
                const yyyy   = this.selectedMonth.split("-")[0];
                const url    = URL.createObjectURL(blob);
                const link   = document.createElement("a");
                link.href     = url;
                link.download = `Province Report - ${this.selectedProvince} - ${yyyy}-${mm}.${this.selectedFormat}`;
                document.body.appendChild(link);
                link.click();
                link.remove();
                URL.revokeObjectURL(url);
            } catch (e) {
                this.errorMessage = await this.extractError(e);
            } finally {
                this.loadingDownload = false;
            }
        },
        async extractError(err) {
            const resp = err?.response;
            if (!resp) return err?.message || "Download failed.";
            if (resp.data instanceof Blob) {
                try {
                    const text = await resp.data.text();
                    const json = JSON.parse(text);
                    return json.message || json.error || text;
                } catch {
                    return `Download failed (HTTP ${resp.status}).`;
                }
            }
            return resp.data?.message || `Download failed (HTTP ${resp.status}).`;
        },
    },
};
</script>
