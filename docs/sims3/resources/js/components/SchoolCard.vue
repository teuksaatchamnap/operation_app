<script setup>

const props = defineProps({
    site: {
        type: [String, Number],
        required: true,
    },
    year: {
        type: [Number],
        required: true,
    },
    schools: {
        type: [Object],
        required: true,
    },
});
</script>

<template>
    <v-card elevation="0" class="my-2 mx-2 school-card">
        <template #text>
            <h4 class="text-center">Validated Schools for {{ site }} </h4>
            <table class="school-table">
                <tbody>
                    <tr>
                        <th rowspan="2">
                            code
                        </th>
                        <th rowspan="2">
                            name
                        </th>
                        <th rowspan="2">
                            director
                        </th>
                        <th colspan="3">
                            bottles approved
                        </th>
                    </tr>
                    <tr>
                        <th>{{ (year -  2) + '-' + (year - 1) }}</th>
                        <th>{{ (year - 1) + '-' + year }}</th>
                        <th>{{ year + '-' + (year + 1) }}</th>
                    </tr>
                    <tr v-for="(years, schoolCode) in schools" :key="schoolCode">
                        <td class="school-code">
                            {{ schoolCode }}
                        </td>
                        <td class="truncate-cell" :title="years[year -  2]?.[0].school_name_english ?? years[year - 1]?.[0].school_name_english ?? years[year]?.[0].school_name_english">
                            {{ years[year -  2]?.[0].school_name_english ?? years[year - 1]?.[0].school_name_english ?? years[year]?.[0].school_name_english }}
                        </td>
                        <td class="truncate-cell" :title="years[year -  2]?.[0].school_director_name_english ?? years[year - 1]?.[0].school_director_name_english ?? years[year]?.[0].school_director_name_english">
                            {{ years[year -  2]?.[0].school_director_name_english ?? years[year - 1]?.[0].school_director_name_english ?? years[year]?.[0].school_director_name_english }}
                        </td>
                        <td class="number-cell">
                            {{ years[year -  2]?.[0].bottle_approved ?? 0 }}
                        </td>
                        <td class="number-cell">
                            {{ years[year - 1]?.[0].bottle_approved ?? 0 }}
                        </td>
                        <td class="number-cell">
                            {{ years[year]?.[0].bottle_approved ?? 0 }}
                        </td>
                    </tr>
                    <tr>
                        <th colspan="3" class="text-right number-cell">
                            Total
                        </th>
                        <th class="number-cell">
                            {{ Object.values(schools).reduce((acc, years) => acc + (years[year -  2]?.[0].bottle_approved ?? 0), 0) }}
                        </th>
                        <th class="number-cell">
                            {{ Object.values(schools).reduce((acc, years) => acc + (years[year - 1]?.[0].bottle_approved ?? 0), 0) }}
                        </th>
                        <th class="number-cell">
                            {{ Object.values(schools).reduce((acc, years) => acc + (years[year]?.[0].bottle_approved ?? 0), 0) }}
                        </th>
                    </tr>
                </tbody>
            </table>
        </template>
    </v-card>
</template>
<style scoped>
.school-card {
    max-width: 600px;
    border: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
    box-shadow: 0 2px 4px rgba(0,0,0,0.05) !important;
}
.school-table {
    width: 100%;
    border-collapse: collapse;
    text-align: center;
    table-layout: fixed;
    margin-top: 8px;
}
.school-table th {
    border: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
    font-size: 0.75rem;
    font-weight: 600;
    padding: 0.25rem;
    background-color: rgba(var(--v-theme-on-surface), 0.05); /* Adaptive header bg */
    color: rgba(var(--v-theme-on-surface), 0.87);
    text-transform: uppercase;
    letter-spacing: 0.05em;
}
.school-table td {
    border: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
    font-size: 0.7rem;
    padding: 0.25rem;
    color: rgba(var(--v-theme-on-surface), 0.6);
}

/* Hover effect for rows */
.school-table tbody tr:hover td {
    background-color: rgba(var(--v-theme-on-surface), 0.05);
}

/* School code column - narrow */
.school-code {
    width: 15%;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    font-weight: 500;
    color: rgb(var(--v-theme-primary));
}

/* Truncatable cells (name and director) */
.truncate-cell {
    max-width: 150px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    position: relative;
    cursor: help;
}

/* Hover tooltip effect */
.truncate-cell:hover::after {
    content: attr(title);
    position: absolute;
    left: 50%;
    bottom: 100%;
    transform: translateX(-50%);
    background-color: rgb(var(--v-theme-surface-variant));
    color: rgb(var(--v-theme-on-surface-variant));
    padding: 0.5rem 0.75rem;
    border-radius: 4px;
    white-space: normal;
    width: max-content;
    max-width: 250px;
    z-index: 1000;
    font-size: 0.75rem;
    line-height: 1.4;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    margin-bottom: 0.5rem;
    pointer-events: none;
}

/* Arrow for tooltip */
.truncate-cell:hover::before {
    content: '';
    position: absolute;
    left: 50%;
    bottom: 100%;
    transform: translateX(-50%);
    border: 6px solid transparent;
    border-top-color: rgb(var(--v-theme-surface-variant));
    z-index: 1000;
    pointer-events: none;
    margin-bottom: -1px; /* Align with tooltip bottom margin */
}

/* Number cells - narrow */
.number-cell {
    width: 12%;
    font-family: 'Roboto Mono', monospace; /* Monospace for numbers */
    color: rgba(var(--v-theme-on-surface), 0.87);
}
</style>

