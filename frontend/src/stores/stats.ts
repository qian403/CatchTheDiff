import { defineStore } from 'pinia';
import { ref } from 'vue';
import type { StatsOverview, EditFrequencyItem, TimelineData } from '../types';
import { fetchStatsOverview, fetchEditFrequency, fetchTimeline } from '../api/stats';
import { logger } from '../utils/logger';

export const useStatsStore = defineStore('stats', () => {
  const overview = ref<StatsOverview | null>(null);
  const editFrequency = ref<EditFrequencyItem[]>([]);
  const timeline = ref<TimelineData | null>(null);
  const loading = ref(false);
  const error = ref<string | null>(null);

  async function loadAll(days = 30): Promise<void> {
    loading.value = true;
    error.value = null;
    try {
      const [o, f, t] = await Promise.all([
        fetchStatsOverview(),
        fetchEditFrequency(),
        fetchTimeline(days),
      ]);
      overview.value = o;
      editFrequency.value = f;
      timeline.value = t;
    } catch (e) {
      error.value = e instanceof Error ? e.message : '載入統計失敗';
      logger.error('Failed to load statistics:', e);
    } finally {
      loading.value = false;
    }
  }

  return { overview, editFrequency, timeline, loading, error, loadAll };
});
