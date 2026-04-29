<template>
    <v-app>
        <DashboardLayout v-if="route.path !== '/login'">
            <router-view />
        </DashboardLayout>
        <v-main v-else>
            <router-view />
        </v-main>
    </v-app>
</template>

<script setup>
import { useRoute } from "vue-router";
import DashboardLayout from "../layouts/DashboardLayout.vue";

const route = useRoute();
</script>
