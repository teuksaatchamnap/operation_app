<template>
    <div class="cal-grid mb-1">
        <div v-for="d in ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']" :key="d"
            class="text-center text-caption font-weight-bold text-medium-emphasis py-1">{{ d }}
        </div>
    </div>

    <div class="cal-grid">
        <div v-for="(cell, idx) in calendarGrid" :key="idx" class="cal-cell rounded" :class="[
            cell.isWeekend ? 'cal-weekend' : '',
            cell.isToday ? 'cal-today' : '',
            cell.isSelected ? 'cal-selected' : '',
            cell.day ? 'cal-clickable' : '',
        ]" @click="cell.day && selectDay(cell.day)">
            <template v-if="cell.day">
                <div class="cal-day-num" :class="cell.isToday ? 'cal-today-num' : ''">{{ cell.day }}
                </div>
                <div class="cal-events">
                    <div v-for="(ev, ei) in cell.events.slice(0, 2)" :key="ei" class="cal-pill"
                        :class="ev.colorClass">{{ ev.label }}</div>
                    <div v-if="cell.events.length > 2" class="cal-pill cal-more">+{{
                        cell.events.length - 2 }}</div>
                </div>
            </template>
        </div>
    </div>

    <!-- Legend -->
    <div class="mt-4 pt-3 d-flex flex-wrap ga-3" style="border-top:1px solid #e0e0e0">
        <div v-for="leg in legend" :key="leg.label" class="d-flex align-center ga-1">
            <div class="legend-swatch" :class="leg.colorClass"></div>
            <span class="text-caption text-medium-emphasis">{{ leg.label }}</span>
        </div>
    </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
    monthOffset: { type: Number, default: 0 }, // offset from May 2026
})

const TODAY_DAY = 6

const selectedDay = ref(TODAY_DAY)
const selectDay = (d) => { selectedDay.value = d }

const calendarEvents = {
    5: [{ label: 'RC', colorClass: 'pill-grey' }, { label: 'WS', colorClass: 'pill-cyan' }],
    6: [{ label: 'SA', colorClass: 'pill-purple' }, { label: 'Issue', colorClass: 'pill-red' }, { label: 'RC', colorClass: 'pill-grey' }],
    7: [{ label: 'RC', colorClass: 'pill-grey' }],
    8: [{ label: 'WS', colorClass: 'pill-cyan' }, { label: 'SA', colorClass: 'pill-purple' }],
    12: [{ label: 'RC', colorClass: 'pill-grey' }, { label: 'Issue', colorClass: 'pill-red' }],
    15: [{ label: 'WS', colorClass: 'pill-cyan' }],
    19: [{ label: 'SA', colorClass: 'pill-purple' }],
    21: [{ label: 'RC', colorClass: 'pill-grey' }, { label: 'WS', colorClass: 'pill-cyan' }],
    26: [{ label: 'Issue', colorClass: 'pill-red' }],
    28: [{ label: 'RC', colorClass: 'pill-grey' }],
}

const calendarGrid = computed(() => {
    const base = new Date(2026, 4 + props.monthOffset, 1)
    const year = base.getFullYear()
    const month = base.getMonth()
    const daysInMonth = new Date(year, month + 1, 0).getDate()
    const firstDow = new Date(year, month, 1).getDay()

    const isCurrentMonth = props.monthOffset === 0

    const cells = []
    for (let i = 0; i < firstDow; i++) cells.push({ day: null })
    for (let d = 1; d <= daysInMonth; d++) {
        const dow = new Date(year, month, d).getDay()
        cells.push({
            day: d,
            isWeekend: dow === 0 || dow === 6,
            isToday: isCurrentMonth && d === TODAY_DAY,
            isSelected: isCurrentMonth && d === selectedDay.value,
            events: (isCurrentMonth ? calendarEvents[d] : []) ?? [],
        })
    }
    return cells
})

const legend = [
    { label: 'Issue', colorClass: 'pill-red' },
    { label: 'Routine Check', colorClass: 'pill-grey' },
    { label: 'Water Sample', colorClass: 'pill-cyan' },
    { label: 'Site Assessment', colorClass: 'pill-purple' },
]
</script>

<style scoped>
.cal-grid {
    display: grid;
    grid-template-columns: repeat(7, 1fr);
    gap: 3px;
}

.cal-cell {
    min-height: 72px;
    padding: 4px 5px;
    background: #fff;
    border: 1px solid #f0f0f0;
    transition: background 0.15s;
}

.cal-clickable {
    cursor: pointer;
}

.cal-clickable:hover {
    background: #f5f8ff;
}

.cal-weekend {
    background: #fafafa;
}

.cal-today {
    border-color: #1976D2 !important;
    background: #e3f2fd !important;
}

.cal-selected {
    border-color: #1565C0 !important;
    background: #dce8fc !important;
}

.cal-day-num {
    font-weight: 600;
    font-size: 12px;
    color: #424242;
    line-height: 1.4;
}

.cal-today-num {
    color: #1565C0;
}

.cal-events {
    margin-top: 3px;
}

.cal-pill {
    display: block;
    font-size: 10px;
    padding: 1px 4px;
    border-radius: 3px;
    margin-top: 2px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.pill-red {
    background: #ffebee;
    color: #c62828;
}

.pill-grey {
    background: #f5f5f5;
    color: #424242;
}

.pill-cyan {
    background: #e0f7fa;
    color: #00695c;
}

.pill-purple {
    background: #f3e5f5;
    color: #6a1b9a;
}

.cal-more {
    background: #eeeeee;
    color: #757575;
}

.legend-swatch {
    width: 14px;
    height: 14px;
    border-radius: 3px;
    flex-shrink: 0;
}
</style>
