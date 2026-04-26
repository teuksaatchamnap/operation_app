<template>
    <div class="login-box">
        <h1 class="text-2xl font-bold mb-2">Teuksaat 1001</h1>
        <p class="text-sm text-gray-500 mb-6">Sims 3 Command Center</p>

        <v-card v-if="loading" color="primary" class="mb-4">
            <v-card-text>
                Please stand by
                <v-progress-linear indeterminate color="white" class="mb-0" />
            </v-card-text>
        </v-card>

        <div v-if="!loading">
            <p class="mb-2">
                Access to this application is restricted to TeukSaat employees.
            </p>
            <p class="mb-4 text-sm text-gray-600">
                Please login using your Google @teuksaat1001.com or
                @1001fontaines.com account.
            </p>
            <GoogleSignInButton @success="onGoogleAuthSuccess" />
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import { GoogleSignInButton } from "vue3-google-signin";
import { useAuthStore } from "../stores/auth";
import axios from "axios";

const router = useRouter();
const authStore = useAuthStore();
const loading = ref(true);

function onGoogleAuthSuccess(response) {
    console.log("Google Auth Success", response);
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
    axios.get("/sanctum/csrf-cookie").then(() => {
        fetchAuth();
    });
});
</script>

<style scoped>
.login-box {
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
    margin-top: 30px;
}
</style>
