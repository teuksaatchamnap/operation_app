<script setup>
import { ref } from "vue";

const props = defineProps({
    site: {
        type: [String, Number], // Adjust type based on what `site` is (e.g., String for a slug, Number for an ID)
        required: true,
    },
});

const entrepreneur = ref({});
const loading = ref(true);
window.axios.get("/api/cashier/site/" + props.site).then((response) => {
    entrepreneur.value = response.data;
    loading.value = false;
});
</script>

<template>
    <v-card v-if="!loading" elevation="0" class="my-2 mx-2 entrepreneur-card">
        <template #text>
            <table class="entrepreneur-table">
                <tbody>
                    <tr>
                        <td class="label-cell">Entrepreneur Name</td>
                        <td class="value-cell">
                            <div class="english-name">{{ entrepreneur.Entrepreneur_English_Name }}</div>
                            <div v-if="entrepreneur.Entrepreneur_Khmer_Name" class="khmer-name">{{ entrepreneur.Entrepreneur_Khmer_Name }}</div>
                        </td>
                    </tr>
                    <tr v-if="entrepreneur.Phone_Number">
                        <td class="label-cell">Phone Number</td>
                        <td class="value-cell">
                            <a
                                :href="'https://t.me/+855' + entrepreneur.Phone_Number"
                                target="_blank"
                                class="phone-link"
                            >
                                +855 {{ entrepreneur.Phone_Number }}
                                <v-icon size="small" class="ms-1">mdi-chat</v-icon>
                            </a>
                        </td>
                    </tr>
                    <tr v-if="entrepreneur.Advisor">
                        <td class="label-cell">Advisor</td>
                        <td class="value-cell">
                            {{
                                entrepreneur.Advisor.split("_")
                                    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
                                    .join(" ")
                            }}
                        </td>
                    </tr>
                    <tr v-if="entrepreneur.telegram_invite_url">
                        <td class="label-cell">Telegram Group</td>
                        <td class="value-cell">
                            <a
                                :href="entrepreneur.telegram_invite_url"
                                target="_blank"
                                rel="noopener noreferrer"
                                class="phone-link"
                            >
                                Site telegram Group
                                <v-icon size="small" class="ms-1">mdi-chat</v-icon>
                            </a>
                        </td>
                    </tr>
                </tbody>
            </table>
        </template>
    </v-card>
    <div v-else>...</div>
</template>
<style scoped>
.entrepreneur-card {
    max-width: 500px;
    border: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
    box-shadow: 0 2px 4px rgba(0,0,0,0.05) !important;
}

.entrepreneur-table {
    width: 100%;
    border-collapse: collapse;
}

.entrepreneur-table td {
    padding: 0.3rem;
    border-bottom: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
    vertical-align: top;
}

.entrepreneur-table tr:last-child td {
    border-bottom: none;
}

.label-cell {
    width: 35%;
    font-weight: 600;
    color: rgba(var(--v-theme-on-surface), 0.7);
    background-color: rgba(var(--v-theme-on-surface), 0.04);
    font-size: 0.8rem;
    white-space: nowrap;
}

.value-cell {
    color: rgba(var(--v-theme-on-surface), 0.87);
    font-size: 0.95rem;
}

.phone-link {
    color: rgb(var(--v-theme-primary));
    text-decoration: none;
    font-weight: 500;
    display: inline-flex;
    align-items: center;
}

.phone-link:hover {
    text-decoration: underline;
}

.english-name {
    font-weight: 500;
    font-size: 0.9rem;
}

.khmer-name {
    font-size: 0.9rem;
    color: rgba(var(--v-theme-on-surface), 0.6);
    margin-top: 4px;
}
</style>
