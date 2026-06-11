<template>
    <div v-if="!loading" class="pa-4">
        <h3 class="mb-4">
            <v-btn color="primary" class="mx-5" icon="mdi-arrow-left" @click="$router.go(-1)" />Site {{ site }}
        </h3>
        <v-data-table v-model:items-per-page="itemsPerPage" :headers="headers" :items="samples" density="compact"
            item-value="sample_date" class="elevation-1">
            <template #item.sample_date="{ item }">
                {{item.sample_date? item.sample_date.substring(0, 10): item}}
            </template>
            <template #item.action_done="{ item }">
                {{ item.action_done ? "yes" : "no" }}
            </template>
            <template #item.comment="{ item }">
                <span v-if="item.comment && item.comment.length < 40">
                {{ item.comment }}</span>
                <span v-else-if="item.comment">
                    {{ item.comment.substring(0, 40) }}
                    <v-tooltip :text="item.comment" location="top">
                        <template #activator="{ props }">
                            <v-btn v-bind="props" density="compact" icon="mdi-dots-horizontal" />
                        </template>
                    </v-tooltip>
                </span>
            </template>
            <template #item.actions="{ item }">
                <v-btn v-if="
                    $store.state.user.permissions.includes('quality_edit')
                " icon="mdi-pencil" density="compact" color="primary" variant="tonal" size="small" class="me-2"
                    @click="
                        $router.push({ path: '/quality/sample/' + item.id })
                        " />
                <v-btn icon="mdi-printer" density="compact" class="me-2" color="success" size="small" variant="tonal"
                    @click="printCertificate(item.id)" />
                <v-btn v-if="
                    $store.state.user.permissions.includes(
                        'edit_permissions'
                    )
                " icon="mdi-delete" density="compact" class="me-2" color="red" size="small" variant="tonal"
                    @click="deleteItem(item.id)" />
            </template>
        </v-data-table>
    </div>
    <div v-if="loading" class="d-flex justify-center mt-10">
        <v-progress-circular indeterminate color="primary" :size="60" />
    </div>
</template>

<script>
// import { VDataTable } from 'vuetify/labs/VDataTable'

export default {
    name: "QualitySiteDetails",
    components: {

    },
    data: function () {
        return {
            loading: true,
            site: "",
            samples: [],
            itemsPerPage: 10,
            headers: [
                { title: "Date", align: "start", key: "sample_date" },
                {
                    title: "Coliform (machine)",
                    align: "center",
                    key: "total_coliform",
                },
                {
                    title: "Ecoli (machine)",
                    align: "center",
                    key: "escherichia",
                },
                {
                    title: "Coliform (bottle)",
                    align: "center",
                    key: "total_coliform_bottle",
                },
                {
                    title: "Ecoli (bottle)",
                    align: "center",
                    key: "escherichia_bottle",
                },
                { title: "Safe", align: "center", key: "safe" },
                { title: "Root cause", align: "center", key: "root_cause" },
                { title: "Comment", key: "comment" },
                { title: "Action done", align: "center", key: "action_done" },
                { title: "", align: "center", key: "actions" },
            ],
        };
    },
    computed: {},
    watch: {
        site() {
            this.getSamples();
        },
    },
    mounted() {
        this.site = this.$route.params.site;
    },
    methods: {
        getSamples() {
            this.loading = true;
            window.axios
                .get("/api/samplesForSite/" + this.site)
                .then((response) => {
                    this.samples = response.data;
                    console.log(this.samples);
                    this.loading = false;
                });
        },
        deleteItem(id) {
            this.loading = true;
            window.axios.delete("/api/sample/" + id).then((response) => {
                console.log(response.data);
                this.loading = false;
            });
        },
        printCertificate(id) {
            const i = id;
            this.$router.push({
                path: "/labCertificate",
                query: {
                    id: i,
                },
            });
        },
        printItem(item) {
            window.axios
                .get("/api/samplePrint?id=" + item.id, {
                    responseType: "blob",
                })
                .then((response) => {
                    const url = URL.createObjectURL(
                        new Blob([response.data], {
                            type: "application/vnd.ms-excel",
                        })
                    );
                    const link = document.createElement("a");
                    link.href = url;
                    link.setAttribute(
                        "download",
                        "quality_" +
                        item.site +
                        "_" +
                        item.sample_date +
                        ".xlsx"
                    );
                    document.body.appendChild(link);
                    link.click();
                    link.remove();
                });
        },
    },
};
</script>

<style scoped></style>
