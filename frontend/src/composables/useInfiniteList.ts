import { ref, type Ref } from 'vue';
import { logger } from '../utils/logger';

export interface UseInfiniteListOptions<T> {
  fetcher: (skip: number, limit: number) => Promise<T[]>;
  limit?: number;
}

export interface UseInfiniteListReturn<T> {
  items: Ref<T[]>;
  loading: Ref<boolean>;
  error: Ref<string | null>;
  hasMore: Ref<boolean>;
  load: (reset?: boolean) => Promise<void>;
}

/**
 * Generic infinite-scroll list driver. Owns pagination state and exposes a
 * single `load(reset?)` action that either appends a page or resets the list.
 */
export function useInfiniteList<T>(
  options: UseInfiniteListOptions<T>,
): UseInfiniteListReturn<T> {
  const items = ref<T[]>([]) as Ref<T[]>;
  const loading = ref(false);
  const error = ref<string | null>(null);
  const hasMore = ref(true);
  const page = ref(0);
  const limit = options.limit ?? 30;

  async function load(reset = false): Promise<void> {
    if (reset) {
      page.value = 0;
      items.value = [];
      hasMore.value = true;
    }
    if (!hasMore.value && !reset) return;

    loading.value = true;
    error.value = null;
    try {
      const data = await options.fetcher(page.value * limit, limit);
      if (data.length < limit) hasMore.value = false;
      items.value = reset ? data : [...items.value, ...data];
      page.value += 1;
    } catch (e) {
      error.value = e instanceof Error ? e.message : '載入失敗';
      logger.error('useInfiniteList load failed:', e);
    } finally {
      loading.value = false;
    }
  }

  return { items, loading, error, hasMore, load };
}
