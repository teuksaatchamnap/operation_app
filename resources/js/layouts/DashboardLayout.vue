<template>
    <v-navigation-drawer
        v-model="drawer"
        :rail="rail"
        permanent
        @click="rail = false"
    >
        <v-list-item :title="rail ? '' : 'Operations App'" nav class="px-2">
            <template v-slot:append>
                <v-btn
                    variant="text"
                    :icon="rail ? 'mdi-chevron-right' : 'mdi-chevron-left'"
                    @click.stop="rail = !rail"
                ></v-btn>
            </template>
        </v-list-item>

        <v-divider></v-divider>

        <v-list density="compact" nav>
            <v-list-item
                prepend-icon="mdi-view-dashboard"
                title="Command Center"
                value="dashboard"
                to="/application"
                color="primary"
            ></v-list-item>
            <v-list-item
                prepend-icon="mdi-file-chart"
                title="Technical"
                value="reports"
                disabled
            ></v-list-item>
            <v-list-item
                prepend-icon="mdi-chart-line"
                title="Tech manager"
                value="analytics"
                disabled
            ></v-list-item>
            <v-list-item
                prepend-icon="mdi-cog"
                title="Laboratory"
                value="settings"
                disabled
            ></v-list-item>
            <v-list-item
                prepend-icon="mdi-bullseye-arrow"
                title="Kpis"
                value="kpis"
                to="/kpis"
                color="primary"
            ></v-list-item>
            <v-list-item
                prepend-icon="mdi-bullseye-arrow"
                title="Advisor"
                value="Advisor"
                to="/Advisor"
                color="primary"
            ></v-list-item>
        </v-list>
    </v-navigation-drawer>

    <v-app-bar elevation="1">
        <template v-slot:prepend>
            <span class="text-h6 ml-2">📡 Command Center</span>
        </template>

        <v-spacer></v-spacer>

        <v-tooltip location="bottom" text="Toggle dark mode">
            <template v-slot:activator="{ props }">
                <v-btn
                    :icon="isDark ? 'mdi-weather-night' : 'mdi-weather-sunny'"
                    variant="text"
                    v-bind="props"
                    @click="toggleDarkMode"
                ></v-btn>
            </template>
        </v-tooltip>

        <v-tooltip location="bottom" text="Logout">
            <template v-slot:activator="{ props }">
                <v-btn
                    icon="mdi-logout"
                    variant="text"
                    v-bind="props"
                    @click="logout"
                ></v-btn>
            </template>
        </v-tooltip>
    </v-app-bar>

    <v-main class="bg-background mt-2 ml-1 mr-1">
        <slot></slot>
    </v-main>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { useRouter } from "vue-router";
import { useTheme } from "vuetify";
import { useAuthStore } from "../stores/auth";
import axios from "axios";

const router = useRouter();
const authStore = useAuthStore();
const theme = useTheme();

const drawer = ref(true);
const rail = ref(false);

const isDark = computed(() => theme.global.current.value.dark);

function toggleDarkMode() {
    theme.change(isDark.value ? "light" : "dark");
    localStorage.setItem("darkMode", isDark.value ? "true" : "false");
}

if (
    localStorage.getItem("darkMode") === "true" ||
    (!localStorage.getItem("darkMode") &&
        window.matchMedia("(prefers-color-scheme: dark)").matches)
) {
    theme.change("dark");
}

function logout() {
    axios.post("/api/logout").then(() => {
        authStore.logout();
        router.push("/login");
    });
}
</script>
