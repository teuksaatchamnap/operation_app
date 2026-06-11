<template>
    <v-menu
        v-model="menu"
        :close-on-content-click="false"
        transition="scale-transition"
        offset-y
        min-width="auto"
    >
        <template v-slot:activator="{ props }">
            <v-text-field
                v-model="dateRangeText"
                label="Select a week"
                readonly
                v-bind="props"
            >
                <template v-slot:append-inner>
                    <div v-if="internalStartDate" class="d-flex align-center">
                        <v-btn
                            variant="plain"
                            size="small"
                            icon="mdi-chevron-left"
                            @click.stop="goToPreviousWeek"
                        ></v-btn>
                        <v-btn
                            variant="plain"
                            size="small"
                            icon="mdi-chevron-right"
                            @click.stop="goToNextWeek"
                        ></v-btn>
                    </div>
                </template>
            </v-text-field>
        </template>
        <v-date-picker
            v-model="pickerDate"
            no-title
            @update:model-value="handleDateSelection"
            :first-day-of-week="1"
            show-week
        ></v-date-picker>
    </v-menu>
</template>

<script>
import { ref, computed, watch } from "vue";
import { parseDateToUTC, formatDateRange } from "../utils/dateUtils";

export default {
    props: {
        startDate: String,
        endDate: String,
    },
    setup(props, { emit }) {
        const menu = ref(false);
        const pickerDate = ref(null);
        const internalStartDate = ref(props.startDate);
        const internalEndDate = ref(props.endDate);

        watch(
            () => props.startDate,
            (newVal) => {
                internalStartDate.value = newVal;
                if (newVal) {
                    // To keep the picker in sync, you might want to update it
                    const newStartDate = new Date(newVal + "T07:00:00");
                    setWeekFromDate(newStartDate);
                }
            }
        );

        watch(
            () => props.endDate,
            (newVal) => {
                internalEndDate.value = newVal;
            }
        );

        const dateRangeText = computed(() => {
            return formatDateRange(internalStartDate.value, internalEndDate.value);
        });

        const setWeekFromDate = (date) => {
            if (!date) return;
            const selectedDate = new Date(date);
            selectedDate.setUTCHours(0, 0, 0, 0);

            const day = selectedDate.getUTCDay();
            const diff = selectedDate.getUTCDate() - (day === 0 ? 6 : day - 1);

            const startOfWeek = new Date(selectedDate.setUTCDate(diff));
            internalStartDate.value = startOfWeek
                .toISOString()
                .substring(0, 10);

            const endOfWeek = new Date(startOfWeek);
            endOfWeek.setUTCDate(startOfWeek.getUTCDate() + 6);
            internalEndDate.value = endOfWeek.toISOString().substring(0, 10);

            pickerDate.value = startOfWeek;

            emit("select-week", {
                start: internalStartDate.value,
                end: internalEndDate.value,
            });
        };

        const handleDateSelection = (date) => {
            setWeekFromDate(date);
            menu.value = false;
        };

        const goToPreviousWeek = () => {
            if (!internalStartDate.value) return;
            const currentStartDate = new Date(
                internalStartDate.value + "T07:00:00"
            );
            currentStartDate.setUTCDate(currentStartDate.getUTCDate() - 7);
            setWeekFromDate(currentStartDate);
        };

        const goToNextWeek = () => {
            if (!internalStartDate.value) return;
            const currentStartDate = new Date(
                internalStartDate.value + "T07:00:00"
            );
            currentStartDate.setUTCDate(currentStartDate.getUTCDate() + 7);
            setWeekFromDate(currentStartDate);
        };

        // Initialize the component with the prop values if they exist
        if (props.startDate) {
            setWeekFromDate(new Date(props.startDate + "T07:00:00"));
        }

        return {
            menu,
            pickerDate,
            internalStartDate,
            internalEndDate,
            dateRangeText,
            handleDateSelection,
            goToPreviousWeek,
            goToNextWeek,
        };
    },
};
</script>
