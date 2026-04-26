<template>
    <v-container>
        <div class="flex justify-between items-center mb-6">
            <h1 class="text-2xl font-bold">Application</h1>
            <v-btn color="error" variant="outlined" prepend-icon="mdi-logout" @click="logout">
                Logout
            </v-btn>
        </div>

        <v-alert type="success" variant="tonal" class="mb-6">
            Welcome, {{ authStore.user?.name }}!
        </v-alert>

        <v-row>
            <v-col cols="12" md="6">
                <v-card>
                    <v-card-title>Card 1</v-card-title>
                    <v-card-text>A sample card component.</v-card-text>
                </v-card>
            </v-col>
            <v-col cols="12" md="6">
                <v-card>
                    <v-card-title>Card 2</v-card-title>
                    <v-card-text>Another sample card.</v-card-text>
                </v-card>
            </v-col>
        </v-row>
    </v-container>
</template>

<script setup>
import { useRouter } from 'vue-router';
import { useAuthStore } from '../stores/auth';
import axios from 'axios';

const router = useRouter();
const authStore = useAuthStore();

function logout() {
    axios.post('/api/logout').then(() => {
        authStore.logout();
        router.push('/login');
    });
}
</script>
