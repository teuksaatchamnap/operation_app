import { defineStore } from 'pinia';
import axios from 'axios';

export const useAuthStore = defineStore('auth', {
    state: () => ({
        user: null,
        initialRoute: null,
    }),
    getters: {
        isLoggedIn: (state) => !!state.user,
    },
    actions: {
        login(userData) {
            this.user = userData;
        },
        logout() {
            this.user = null;
        },
        setInitialRoute(route) {
            if (!this.initialRoute && route !== '/login') {
                this.initialRoute = route;
            }
        },
        async getAuth() {
            try {
                const response = await axios.get('/api/getAuth');
                this.login(response.data);
                return response.data;
            } catch {
                this.logout();
                throw new Error('Unauthenticated');
            }
        },
        async fetchCsrfAndAuth() {
            await axios.get('/sanctum/csrf-cookie');
            return this.getAuth();
        },
    },
});
