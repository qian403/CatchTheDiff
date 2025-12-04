import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import type { News, NewsDiff } from '../types';
import { fetchNewsList, fetchNewsDetail, fetchNewsDiff } from '../api/news';

export const useNewsStore = defineStore('news', () => {
    // State
    const newsList = ref<News[]>([]);
    const currentNews = ref<News | null>(null);
    const currentDiff = ref<NewsDiff | null>(null);
    const loading = ref(false);
    const error = ref<string | null>(null);
    const hasMore = ref(true);
    const page = ref(0);
    const limit = 30;

    // Getters
    const totalNewsCount = computed(() => newsList.value.length);

    const sourceStats = computed(() => {
        const stats: Record<number, number> = {};
        newsList.value.forEach(news => {
            stats[news.source] = (stats[news.source] || 0) + 1;
        });
        return stats;
    });

    // Actions
    async function loadNews(reset = false, query?: string, sources?: number[], date?: string, sortBy?: string) {
        if (reset) {
            page.value = 0;
            newsList.value = [];
            hasMore.value = true;
        }

        if (!hasMore.value && !reset) return;

        loading.value = true;
        error.value = null;

        try {
            const data = await fetchNewsList(page.value * limit, limit, query, sources, date, sortBy);

            if (data.length < limit) {
                hasMore.value = false;
            }

            if (reset) {
                newsList.value = data;
            } else {
                newsList.value = [...newsList.value, ...data];
            }

            page.value++;
        } catch (err: any) {
            error.value = err.message || 'Failed to load news';
            console.error(err);
        } finally {
            loading.value = false;
        }
    }

    async function loadNewsDetail(id: number) {
        loading.value = true;
        error.value = null;
        currentNews.value = null;

        try {
            const data = await fetchNewsDetail(id);
            currentNews.value = data;
        } catch (err: any) {
            error.value = err.message || 'Failed to load news detail';
            console.error(err);
        } finally {
            loading.value = false;
        }
    }

    async function loadDiff(newsId: number, v1: number, v2: number) {
        loading.value = true;
        error.value = null;
        currentDiff.value = null;

        try {
            const data = await fetchNewsDiff(newsId, v1, v2);
            currentDiff.value = data;
        } catch (err: any) {
            error.value = err.message || 'Failed to load diff';
            console.error(err);
        } finally {
            loading.value = false;
        }
    }

    return {
        newsList,
        currentNews,
        currentDiff,
        loading,
        error,
        hasMore,
        totalNewsCount,
        sourceStats,
        loadNews,
        loadNewsDetail,
        loadDiff
    };
});
