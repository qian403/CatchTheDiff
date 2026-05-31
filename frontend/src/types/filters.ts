export type SortBy = 'newest' | 'recently_changed';

export interface NewsFilters {
  sortBy: SortBy;
  date: string;
  selectedSources: number[];
}

export const DEFAULT_FILTERS: NewsFilters = {
  sortBy: 'newest',
  date: '',
  selectedSources: [],
};
