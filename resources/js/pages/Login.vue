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
                        <v-btn
                            variant="elevated"
                            rounded="lg"
                            size="large"
                            :disabled="!isReady"
                            class="google-btn"
                            @click="login"
                        >
                            <template #prepend>
                                <svg
                                    class="google-logo"
                                    width="18"
                                    height="18"
                                    viewBox="0 0 48 48"
                                    xmlns="http://www.w3.org/2000/svg"
                                >
                                    <path
                                        fill="#EA4335"
                                        d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z"
                                    />
                                    <path
                                        fill="#4285F4"
                                        d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z"
                                    />
                                    <path
                                        fill="#FBBC05"
                                        d="M10.53 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24c0 3.88.92 7.54 2.56 10.78l7.97-6.19z"
                                    />
                                    <path
                                        fill="#34A853"
                                        d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.15 1.45-4.92 2.3-8.16 2.3-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z"
                                    />
                                </svg>
                            </template>
                            <span class="google-btn-text">
                                Sign in with Google
                            </span>
                        </v-btn>
                    </div>
                    <v-alert
                        v-if="isBrave"
                        type="warning"
                        density="compact"
                        variant="tonal"
                        class="mt-4 mb-4"
                        title="Brave Shield Detected"
                        text="Brave Shields may block the one-tap sign-in. If you experience issues, try disabling Shields for this site or use another browser."
                    />
                </div>
            </div>
        </v-sheet>
    </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from "vue";
import { useRouter } from "vue-router";
import { useTheme } from "vuetify";
import { useOneTap } from "vue3-google-signin";
import { useAuthStore } from "../stores/auth";
import axios from "axios";

const router = useRouter();
const authStore = useAuthStore();
const theme = useTheme();
const loading = ref(true);
const manualOverride = ref(false);
const isBrave = ref(false);

const isDark = computed(() => theme.global.current.value.dark);

const { isReady, login } = useOneTap({
    autoSelect: true,
    disableAutomaticPrompt: true,
    onSuccess: onGoogleAuthSuccess,
});

const systemMediaQuery = window.matchMedia("(prefers-color-scheme: dark)");

function applySystemPreference() {
    if (!manualOverride.value) {
        theme.change(systemMediaQuery.matches ? "dark" : "light");
    }
}

function toggleTheme() {
    manualOverride.value = true;
    theme.change(isDark.value ? "light" : "dark");
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
    if (navigator.brave?.isBrave) {
        navigator.brave.isBrave().then((brave) => {
            isBrave.value = brave;
        });
    }
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

.google-btn {
    text-transform: none;
    letter-spacing: normal;
    font-weight: 500;
    font-size: 14px;
    border: 1px solid rgb(var(--v-theme-primary));
}

.google-btn-text {
    color: rgb(var(--v-theme-on-background));
}

:root {
    --login-glow-color: 37, 99, 235;
}

:root.dark {
    --login-glow-color: 99, 102, 241;
}

.login-card {
    background-color: rgb(var(--v-theme-surface)) !important;
    border: 1px solid transparent;
    transition:
        border-color 0.3s,
        box-shadow 0.3s;
}

.dark .login-card,
:root.dark .login-card {
    border-color: rgba(var(--login-glow-color), 0.15);
    box-shadow:
        0 0 20px rgba(var(--login-glow-color), 0.08),
        0 0 60px rgba(var(--login-glow-color), 0.04),
        0 8px 32px rgba(0, 0, 0, 0.4);
}
</style>
