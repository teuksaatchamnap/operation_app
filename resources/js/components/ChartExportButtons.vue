<template>
    <div class="d-flex justify-end ga-1 mt-1">
        <v-btn
            variant="text"
            size="small"
            prepend-icon="mdi-file-image"
            @click="exportChart('png')"
        >
            PNG
        </v-btn>
        <v-btn
            variant="text"
            size="small"
            prepend-icon="mdi-file-document"
            @click="exportChart('svg')"
        >
            SVG
        </v-btn>
        <v-btn
            variant="text"
            size="small"
            prepend-icon="mdi-file-delimited"
            @click="exportChart('csv')"
        >
            CSV
        </v-btn>
    </div>
</template>

<script setup>
const props = defineProps({
    chart: {
        type: Object,
        default: null,
    },
    filename: {
        type: String,
        default: "chart",
    },
});

function exportChart(format) {
    const chart = props.chart;
    if (!chart) return;

    if (format === "csv") {
        if (typeof chart.exports?.csv === "function") {
            chart.exports.csv();
        } else if (typeof chart.exportToCSV === "function") {
            chart.exportToCSV();
        }
        return;
    }

    const type = format === "svg" ? "svg" : undefined;
    chart.dataURI({ scale: 1, type }).then(({ imgURI }) => {
        const link = document.createElement("a");
        link.href = imgURI;
        link.download = `${props.filename}.${format}`;
        link.click();
    });
}
</script>
