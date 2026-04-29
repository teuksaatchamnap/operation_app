import 'vuetify/styles';
import '@mdi/font/css/materialdesignicons.css';
import { createVuetify } from 'vuetify';
import * as components from 'vuetify/components';
import * as directives from 'vuetify/directives';

const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;

const vuetify = createVuetify({
    components,
    directives,
    theme: {
        defaultTheme: prefersDark ? 'dark' : 'light',
        themes: {
            light: {
                colors: {
                    background: '#f5f9fc',
                },
            },
            dark: {
                colors: {
                    background: '#0f0f1a',
                },
            },
        },
    },
});

export default vuetify;
