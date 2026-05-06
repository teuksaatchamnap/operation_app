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
                    primary: '#1976d2',
                    secondary: '#424242',
                    success: '#4caf50',
                    error: '#ff5252',
                    info: '#2196f3',
                    warning: '#fb8c00',
                },
            },
            dark: {
                colors: {
                    background: '#0f0f1a',
                    primary: '#90caf9',
                    secondary: '#a0a0a0',
                    success: '#66bb6a',
                    error: '#ef5350',
                    info: '#64b5f6',
                    warning: '#ffa726',
                },
            },
        },
    },
});

export default vuetify;
