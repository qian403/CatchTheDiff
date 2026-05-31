import { createApp } from 'vue';
import { createPinia } from 'pinia';
import App from './App.vue';
import router from './router';

// Vuetify
import 'vuetify/styles'
import { createVuetify } from 'vuetify'
import { aliases, mdi } from 'vuetify/iconsets/mdi'
import '@mdi/font/css/materialdesignicons.css'

import './styles/global.css';

const vuetify = createVuetify({
    icons: {
        defaultSet: 'mdi',
        aliases,
        sets: {
            mdi,
        },
    },
    theme: {
        defaultTheme: 'light',
        themes: {
            light: {
                dark: false,
                colors: {
                    background: '#f7f4ed',
                    surface: '#fefdfb',
                    primary: '#c41e3a',
                    secondary: '#5c5344',
                    accent: '#2d6a4f',
                    error: '#c41e3a',
                    info: '#2c2416',
                    success: '#2d6a4f',
                    warning: '#b7791f',
                },
            },
        },
    },
})

const app = createApp(App);

app.use(createPinia());
app.use(router);
app.use(vuetify);

app.mount('#app');
