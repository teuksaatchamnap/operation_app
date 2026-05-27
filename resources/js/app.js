import '../css/app.css';
import './bootstrap';
import { createApp } from 'vue';
import { createPinia } from 'pinia';
import GoogleSignInPlugin from 'vue3-google-signin';
import VueApexCharts from 'vue3-apexcharts';
import App from './components/App.vue';
import vuetify from './plugins/vuetify';
import router from './router';

const app = createApp(App);

app.use(createPinia());
app.use(vuetify);
app.use(router);
app.use(GoogleSignInPlugin, {
    clientId: import.meta.env.VITE_GOOGLE_CLIENT_ID,
});
app.use(VueApexCharts);

app.mount('#app');
