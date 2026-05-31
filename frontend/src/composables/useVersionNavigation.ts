import { computed, type ComputedRef, type Ref } from 'vue';
import type { News, NewsVersion } from '../types';

export interface UseVersionNavigationReturn {
  sortedVersions: ComputedRef<NewsVersion[]>;
  selectedVersion: ComputedRef<NewsVersion | null>;
  previousVersion: ComputedRef<NewsVersion | null>;
  titleHasChanged: ComputedRef<boolean>;
}

/**
 * Derive sorted version list and previous/current version navigation from a
 * News object and the currently selected version id.
 *
 * Versions are sorted newest-first (descending by `time`). "previous" means
 * the version immediately older than the selected one.
 */
export function useVersionNavigation(
  news: Ref<News | null>,
  selectedVersionId: Ref<number | null>,
): UseVersionNavigationReturn {
  const sortedVersions = computed<NewsVersion[]>(() =>
    news.value ? [...news.value.versions].sort((a, b) => b.time - a.time) : [],
  );

  const selectedVersion = computed<NewsVersion | null>(() => {
    if (selectedVersionId.value === null) return null;
    return sortedVersions.value.find(v => v.id === selectedVersionId.value) ?? null;
  });

  const previousVersion = computed<NewsVersion | null>(() => {
    if (selectedVersionId.value === null) return null;
    const idx = sortedVersions.value.findIndex(v => v.id === selectedVersionId.value);
    if (idx === -1 || idx >= sortedVersions.value.length - 1) return null;
    return sortedVersions.value[idx + 1];
  });

  const titleHasChanged = computed<boolean>(
    () =>
      previousVersion.value !== null &&
      selectedVersion.value !== null &&
      previousVersion.value.title !== selectedVersion.value.title,
  );

  return { sortedVersions, selectedVersion, previousVersion, titleHasChanged };
}
