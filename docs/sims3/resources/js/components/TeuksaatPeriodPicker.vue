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
                label="Select a period"
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
                    setWeekFromDate(parseDateToUTC(newVal));
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

            const year = selectedDate.getUTCFullYear();
            const month = selectedDate.getUTCMonth();
            const day = selectedDate.getUTCDate();

            // Calculate start day of period
            // Periods: 1-7, 8-14, 15-21, 22-End of month
            let startDay;
            if (day <= 7) {
                startDay = 1;
            } else if (day <= 14) {
                startDay = 8;
            } else if (day <= 21) {
                startDay = 15;
            } else {
                startDay = 22; // Last chunk always starts on day 22
            }

            const startOfWeek = new Date(Date.UTC(year, month, startDay));
            internalStartDate.value = startOfWeek
                .toISOString()
                .substring(0, 10);

            // Calculate end day
            const daysInMonth = new Date(Date.UTC(year, month + 1, 0)).getUTCDate();
            let endDay;
            if (startDay === 1) {
                endDay = 7;
            } else if (startDay === 8) {
                endDay = 14;
            } else if (startDay === 15) {
                endDay = 21;
            } else {
                endDay = daysInMonth; // Last chunk always goes to end of month
            }
            
            const endOfWeek = new Date(Date.UTC(year, month, endDay));
            internalEndDate.value = endOfWeek.toISOString().substring(0, 10);

            pickerDate.value = new Date(year, month, startDay);

            emit("select-week", {
                start: internalStartDate.value,
                end: internalEndDate.value,
            });
        };

        const handleDateSelection = (date) => {
            setWeekFromDate(parseDateToUTC(date));
            menu.value = false;
        };

        const goToPreviousWeek = () => {
            if (!internalStartDate.value) return;
            const parts = internalStartDate.value.split("-");
            // Treat as UTC components
            const year = parseInt(parts[0], 10);
            const month = parseInt(parts[1], 10) - 1; // 0-indexed
            const day = parseInt(parts[2], 10);

            let targetDate;
            if (day === 1) {
                // If currently at start of month (Period 1), go to end of previous month
                // New Date(year, month, 0) gives last day of previous month
                targetDate = new Date(Date.UTC(year, month, 0));
            } else {
                // Otherwise just subtract 7 days to jump to previous period start
                targetDate = new Date(Date.UTC(year, month, day - 7));
            }
            setWeekFromDate(targetDate);
        };

        const goToNextWeek = () => {
            if (!internalStartDate.value) return;
            const parts = internalStartDate.value.split("-");
            const year = parseInt(parts[0], 10);
            const month = parseInt(parts[1], 10) - 1; 
            const day = parseInt(parts[2], 10);
            let targetDate;
            if(day >= 22){
                targetDate = new Date(Date.UTC(year, month + 1, 1));
            }else{
                targetDate = new Date(Date.UTC(year, month, day + 7));
            }
            setWeekFromDate(targetDate);
        };

        // Initialize the component with the prop values if they exist
        if (props.startDate) {
            setWeekFromDate(parseDateToUTC(props.startDate));
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
