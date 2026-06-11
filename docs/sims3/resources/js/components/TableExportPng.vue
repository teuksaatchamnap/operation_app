<script setup>
import { ref, onMounted } from "vue";
import html2canvas from "html2canvas";

const props = defineProps({
    tableRef: {
        type: Object,
        required: true,
    },
    siteId: {
        type: [String, Number],
        required: true,
    },
    filenamePrefix: {
        type: String,
        default: "table",
    },
    message: {
        type: Object,
        default: {},
    },
});

const emit = defineEmits(['telegram-sent']);

const exporting = ref(false);
const hasTelegramGroup = ref(false);
const checkingTelegramGroup = ref(true);

const checkTelegramGroup = async () => {
    try {
        const response = await window.axios.get('/api/telegram-groups', { params: { site: props.siteId } });
        hasTelegramGroup.value = response.data.chat_id != null;
    } catch (error) {
        console.error('Error checking telegram group:', error);
        hasTelegramGroup.value = false;
    } finally {
        checkingTelegramGroup.value = false;
    }
};

const exportToPng = async () => {
    if (!props.tableRef) return;
    exporting.value = true;
    const canvas = await html2canvas(props.tableRef, {
        scale: 2,
        backgroundColor: "#ffffff",
        useCORS: true,
        logging: false,
    });

    const dataUrl = canvas.toDataURL("image/png");
    const blob = await (await fetch(dataUrl)).blob();
    if (!blob) {
        alert("Failed to generate image");
        exporting.value = false;
        return;
    }

    const formData = new FormData();
    formData.append(
        "file",
        blob,
        `${props.filenamePrefix}-${props.siteId}-${props.relatedDate}.png`
    );
    formData.append("site", props.siteId);
    formData.append("message", props.message.message);
    formData.append("audio", props.message.audio ?? null);
    await window.axios.post("/api/telegram/sendImageToSite", formData, {
        headers: { "Content-Type": "multipart/form-data" },
    });
    emit('telegram-sent');
    exporting.value = false;
};

onMounted(() => {
    checkTelegramGroup();
});

defineExpose({
    exportToPng,
    exporting,
});
</script>

<template>
    <div>
        <v-btn
            :loading="exporting || checkingTelegramGroup"
            :disabled="exporting || checkingTelegramGroup || !hasTelegramGroup"
            prepend-icon="mdi-chat"
            color="success"
            @click="exportToPng"
        >
            {{ $t('cashier.send_to_site') }}
        </v-btn>
        <div v-if="!checkingTelegramGroup && !hasTelegramGroup" class="text-error text-caption mt-1">
            This site has no telegram group
        </div>
    </div>
</template>
