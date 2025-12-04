import { createRouter, createWebHistory } from 'vue-router';
import DashboardView from '../views/DashboardView.vue';

const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes: [
        {
            path: '/',
            name: 'dashboard',
            component: DashboardView
        },
        {
            path: '/stats',
            name: 'stats',
            component: () => import('../views/StatsView.vue')
        },
        {
            path: '/recent',
            name: 'recent',
            component: () => import('../views/RecentChangesView.vue')
        },
        {
            path: '/news/:id',
            name: 'news-detail',
            // Lazy load the detail view
            component: () => import('../views/NewsDetailView.vue')
        }
    ],
    scrollBehavior(to, from, savedPosition) {
        if (savedPosition) {
            return savedPosition;
        } else {
            return { top: 0 };
        }
    }
});

export default router;
