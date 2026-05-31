import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import type { News, NewsDiff } from '../types';
import type { NewsFilters } from '../types/filters';
import { fetchNewsList, fetchNewsDetail, fetchNewsDiff } from '../api/news';
import { logger } from '../utils/logger';

const PAGE_SIZE = 30;

export interface LoadNewsOptions {
    reset?: boolean;
    query?: string;
    filters?: NewsFilters;
}

export const useNewsStore = defineStore('news', () => {
    // State
    const newsList = ref<News[]>([]);
    const currentNews = ref<News | null>(null);
    const currentDiff = ref<NewsDiff | null>(null);
    const loading = ref(false);
    const error = ref<string | null>(null);
    const hasMore = ref(true);
    const page = ref(0);

    // Getters
    const totalNewsCount = computed(() => newsList.value.length);

    const sourceStats = computed(() => {
        const stats: Record<number, number> = {};
        newsList.value.forEach(news => {
            stats[news.source] = (stats[news.source] ?? 0) + 1;
        });
        return stats;
    });

    // Actions
    async function loadNews(options: LoadNewsOptions = {}): Promise<void> {
        const { reset = false, query, filters } = options;

        if (reset) {
            page.value = 0;
            newsList.value = [];
            hasMore.value = true;
        }

        if (!hasMore.value && !reset) return;

        loading.value = true;
        error.value = null;

        try {
            const data = await fetchNewsList(
                page.value * PAGE_SIZE,
                PAGE_SIZE,
                query,
                filters?.selectedSources,
                filters?.date || undefined,
                filters?.sortBy,
            );

            if (data.length < PAGE_SIZE) {
                hasMore.value = false;
            }

            newsList.value = reset ? data : [...newsList.value, ...data];
            page.value += 1;
        } catch (err) {
            error.value = err instanceof Error ? err.message : 'Failed to load news';
            logger.error('loadNews failed:', err);
        } finally {
            loading.value = false;
        }
    }

    async function loadNewsDetail(id: number): Promise<void> {
        loading.value = true;
        error.value = null;
        currentNews.value = null;

        try {
            currentNews.value = await fetchNewsDetail(id);
        } catch (err) {
            error.value = err instanceof Error ? err.message : 'Failed to load news detail';
            logger.error('loadNewsDetail failed:', err);
        } finally {
            loading.value = false;
        }
    }

    async function loadDiff(newsId: number, v1: number, v2: number): Promise<void> {
        loading.value = true;
        error.value = null;
        currentDiff.value = null;

        try {
            currentDiff.value = await fetchNewsDiff(newsId, v1, v2);
        } catch (err) {
            error.value = err instanceof Error ? err.message : 'Failed to load diff';
            logger.error('loadDiff failed:', err);
        } finally {
            loading.value = false;
        }
    }

    function clearDiff(): void {
        currentDiff.value = null;
    }

    return {
        // state
        newsList,
        currentNews,
        currentDiff,
        loading,
        error,
        hasMore,
        // getters
        totalNewsCount,
        sourceStats,
        // actions
        loadNews,
        loadNewsDetail,
        loadDiff,
        clearDiff,
    };
});
