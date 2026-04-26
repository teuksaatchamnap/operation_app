<template>
    <div
        class="login-page bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 dark:from-slate-900 dark:via-slate-800 dark:to-slate-900 transition-colors duration-300"
    >
        <v-sheet :elevation="8" rounded="lg" class="login-card">
            <div class="flex justify-end mb-2">
                <v-btn
                    icon
                    variant="text"
                    density="comfortable"
                    size="small"
                    @click="toggleTheme"
                >
                    <v-icon>{{
                        isDark ? "mdi-weather-sunny" : "mdi-weather-night"
                    }}</v-icon>
                    <v-tooltip activator="parent" location="bottom">
                        {{
                            isDark
                                ? "Switch to light mode"
                                : "Switch to dark mode"
                        }}
                    </v-tooltip>
                </v-btn>
            </div>

            <div class="flex flex-col items-center text-center">
                <img class="max-w-20" src="/TS-1001-Logo.png" />
                <h1 class="text-2xl font-bold mb-1">Command Center</h1>
                <p class="text-sm text-gray-500 dark:text-gray-400 mb-8">
                    TeukSaat 1001 Analytics
                </p>

                <v-card v-if="loading" color="primary" class="mb-4 w-full">
                    <v-card-text class="text-white">
                        Please stand by
                        <v-progress-linear
                            indeterminate
                            color="white"
                            class="mb-0"
                        />
                    </v-card-text>
                </v-card>

                <div v-if="!loading" class="w-full">
                    <p class="mb-2 text-sm text-gray-700 dark:text-gray-300">
                        Access to this application is restricted to TeukSaat
                        employees.
                    </p>
                    <p class="mb-6 text-xs text-gray-500 dark:text-gray-400">
                        Please login using your Google
                        <span
                            class="font-medium text-gray-600 dark:text-gray-300"
                            >@teuksaat1001.com</span
                        >
                        or
                        <span
                            class="font-medium text-gray-600 dark:text-gray-300"
                            >@1001fontaines.com</span
                        >
                        account.
                    </p>

                    <div class="flex justify-center">
                        <GoogleSignInButton
                            :key="isDark ? 'dark' : 'light'"
                            :theme="isDark ? 'filled_black' : 'filled_blue'"
                            :auto-select="true"
                            @success="onGoogleAuthSuccess"
                        />
                    </div>
                </div>
            </div>
        </v-sheet>
    </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from "vue";
import { useRouter } from "vue-router";
import { useTheme } from "vuetify";
import { GoogleSignInButton } from "vue3-google-signin";
import { useAuthStore } from "../stores/auth";
import axios from "axios";

const router = useRouter();
const authStore = useAuthStore();
const theme = useTheme();
const loading = ref(true);
const manualOverride = ref(false);

const isDark = computed(() => theme.global.current.value.dark);

const systemMediaQuery = window.matchMedia("(prefers-color-scheme: dark)");

function applySystemPreference() {
    if (!manualOverride.value) {
        theme.global.name.value = systemMediaQuery.matches ? "dark" : "light";
    }
}

function toggleTheme() {
    manualOverride.value = true;
    theme.global.name.value = isDark.value ? "light" : "dark";
}

function onGoogleAuthSuccess(response) {
    const token = {
        ...response,
        client_id: import.meta.env.VITE_GOOGLE_CLIENT_ID,
    };
    axios.post("/api/login", { token }).then(() => {
        fetchAuth();
    });
}

function fetchAuth() {
    axios
        .get("/api/getAuth")
        .then((response) => {
            authStore.login(response.data);
            if (authStore.initialRoute) {
                router.push({ path: authStore.initialRoute });
            } else {
                router.push({ path: "/application" });
            }
        })
        .catch(() => {
            loading.value = false;
        });
}

onMounted(() => {
    systemMediaQuery.addEventListener("change", applySystemPreference);
    axios.get("/sanctum/csrf-cookie").then(() => {
        fetchAuth();
    });
});

onUnmounted(() => {
    systemMediaQuery.removeEventListener("change", applySystemPreference);
});
</script>

<style scoped>
.login-page {
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 100vh;
    padding: 1rem;
}

.login-card {
    width: 100%;
    max-width: 550px;
    padding: 2rem;
}
</style>
