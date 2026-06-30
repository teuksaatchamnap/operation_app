<template>
    <div class="kpi-scroll-wrapper">
        <v-btn
            v-show="canScrollLeft"
            icon="mdi-chevron-left"
            class="kpi-scroll-btn kpi-scroll-btn-left"
            density="comfortable"
            size="large"
            variant="tonal"
            @click="scroll('left')"
        />
        <div
            ref="scroller"
            class="kpi-scroller"
            :class="{ 'kpi-scroller--dragging': isDragging }"
            @scroll="updateScrollState"
            @mousedown="onDragStart"
            @mousemove="onDragMove"
            @mouseup="onDragEnd"
            @mouseleave="onDragEnd"
            @touchstart.prevent="onTouchStart"
            @touchmove.prevent="onTouchMove"
            @touchend="onDragEnd"
        >
            <slot />
        </div>
        <v-btn
            v-show="canScrollRight"
            icon="mdi-chevron-right"
            class="kpi-scroll-btn kpi-scroll-btn-right"
            density="comfortable"
            size="large"
            variant="tonal"
            @click="scroll('right')"
        />
    </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from "vue";

const scroller = ref(null);
const canScrollLeft = ref(false);
const canScrollRight = ref(false);
const isDragging = ref(false);
let resizeObserver = null;
let dragStartX = 0;
let dragScrollLeft = 0;

function onDragStart(e) {
    isDragging.value = true;
    dragStartX = e.pageX - scroller.value.offsetLeft;
    dragScrollLeft = scroller.value.scrollLeft;
}

function onDragMove(e) {
    if (!isDragging.value) return;
    e.preventDefault();
    const x = e.pageX - scroller.value.offsetLeft;
    const walk = (x - dragStartX) * 1.5;
    scroller.value.scrollLeft = dragScrollLeft - walk;
}

function onTouchStart(e) {
    isDragging.value = true;
    dragStartX = e.touches[0].pageX - scroller.value.offsetLeft;
    dragScrollLeft = scroller.value.scrollLeft;
}

function onTouchMove(e) {
    if (!isDragging.value) return;
    const x = e.touches[0].pageX - scroller.value.offsetLeft;
    const walk = (x - dragStartX) * 1.5;
    scroller.value.scrollLeft = dragScrollLeft - walk;
}

function onDragEnd() {
    isDragging.value = false;
}

function updateScrollState() {
    const el = scroller.value;
    if (!el) return;
    canScrollLeft.value = el.scrollLeft > 0;
    canScrollRight.value = el.scrollLeft + el.clientWidth < el.scrollWidth - 1;
}

function scroll(direction) {
    const el = scroller.value;
    if (!el) return;
    el.scrollBy({
        left: direction === "left" ? -300 : 300,
        behavior: "smooth",
    });
}

onMounted(async () => {
    await nextTick();
    updateScrollState();
    if (scroller.value) {
        resizeObserver = new ResizeObserver(updateScrollState);
        resizeObserver.observe(scroller.value);
    }
});

onUnmounted(() => {
    if (resizeObserver) {
        resizeObserver.disconnect();
    }
});
</script>

<style scoped>
.kpi-scroll-wrapper {
    position: relative;
}

.kpi-scroller {
    display: flex;
    gap: 16px;
    overflow-x: auto;
    scroll-behavior: smooth;
    padding: 10px 10px 10px 10px;
    cursor: grab;
    user-select: none;
}

.kpi-scroller--dragging {
    cursor: grabbing;
    scroll-behavior: auto;
}

.kpi-scroller::-webkit-scrollbar {
    display: none;
}

.kpi-scroller {
    -ms-overflow-style: none;
    scrollbar-width: none;
}

.kpi-scroll-btn {
    position: absolute;
    top: 50%;
    transform: translateY(-50%);
    z-index: 1;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.kpi-scroll-btn-left {
    left: 4px;
}

.kpi-scroll-btn-right {
    right: 4px;
}
</style>
