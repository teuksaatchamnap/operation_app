<template>
    <div class="page-wrapper">

        <!-- Above the fold: loaded with the page -->
        <TechHeader />
        <KpiSlider />
        <ScheduleCard />
        <QuickActions />

        <!-- Below the fold: code is fetched and rendered only when scrolled into view -->
        <v-lazy min-height="480" :options="{ threshold: 0.1 }" transition="fade-transition">
            <IssuesTable />
        </v-lazy>

        <v-lazy min-height="320" :options="{ threshold: 0.1 }" transition="fade-transition">
            <VisitHistory />
        </v-lazy>

    </div>
</template>
<!-- send data -->
<script setup>
import { defineAsyncComponent } from 'vue'
import TechHeader from '../../components/Technical/TechHeader.vue'
import KpiSlider from '../../components/Technical/KpiSlider.vue'
import ScheduleCard from '../../components/Technical/ScheduleCard.vue'
import QuickActions from '../../components/Technical/QuickActions.vue'

const IssuesTable = defineAsyncComponent(() => import('../../components/Technical/IssuesTable.vue'))
const VisitHistory = defineAsyncComponent(() => import('../../components/Technical/VisitHistory.vue'))
</script>

<style scoped>
.page-wrapper {
    min-height: 100vh;
    background: #f4f6f9;
}
</style>
