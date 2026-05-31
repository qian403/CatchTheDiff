<template>
  <div class="dashboard">
    <!-- Header with Search -->
    <header class="dashboard-header">
      <div>
        <h1 class="page-title">所有新聞</h1>
        <p class="page-subtitle">即時監控各家新聞媒體的版本變更</p>
      </div>

      <div class="header-actions">
        <!-- Search -->
        <div class="search-box">
          <span class="material-icons search-icon">search</span>
          <input type="text" v-model="searchQuery" @keyup.enter="handleSearch" placeholder="搜尋新聞..."
            class="search-input">
        </div>

        <!-- Filter Button -->
        <button class="filter-btn" @click="openFilterModal" :class="{ 'active': hasActiveFilters }">
          <span class="material-icons">tune</span>
          篩選
          <span v-if="activeFilterCount > 0" class="filter-badge">{{ activeFilterCount }}</span>
        </button>
      </div>
    </header>

    <!-- Active Filters Display -->
    <div v-if="hasActiveFilters" class="active-filters">
      <div v-if="filters.sortBy !== 'newest'" class="filter-tag">
        排序: {{ filters.sortBy === 'recently_changed' ? '最近變更' : '最新發布' }}
      </div>
      <div v-if="filters.date" class="filter-tag">
        日期: {{ filters.date }}
        <span class="material-icons close-icon" @click="clearDate">close</span>
      </div>
      <div v-for="sourceId in filters.selectedSources" :key="sourceId" class="filter-tag">
        {{ SOURCES[sourceId] }}
        <span class="material-icons close-icon" @click="removeSource(sourceId)">close</span>
      </div>
      <button class="clear-all-btn" @click="clearAllFilters">清除全部</button>
    </div>

    <!-- All News Section -->
    <section class="all-news-section">
      <div v-if="loading && newsList.length === 0" class="loading-state">
        <LoadingSpinner />
      </div>

      <div v-else-if="error" class="error-state">
        <span class="material-icons error-icon">error_outline</span>
        <p>{{ error }}</p>
        <button @click="loadNews(true)" class="retry-btn">重試</button>
      </div>

      <div v-else class="news-grid">
        <NewsCard v-for="news in newsList" :key="news.id" :news="news" @click="goToDetail(news.id)" />
      </div>

      <!-- Load More -->
      <div v-if="hasMore && !loading && newsList.length > 0" class="load-more">
        <button @click="loadNews()" class="load-more-btn">
          載入更多
        </button>
      </div>

      <div v-if="loading && newsList.length > 0" class="loading-more">
        <LoadingSpinner />
      </div>
    </section>

    <!-- Filter Modal -->
    <FilterModal :is-open="isFilterModalOpen" :sources="SOURCES" :current-filters="filters" @close="closeFilterModal"
      @apply="handleApplyFilters" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import { storeToRefs } from 'pinia';
import { useNewsStore } from '../stores/news';
import { NEWS_SOURCES } from '../constants/sources';
import NewsCard from '../components/NewsCard.vue';
import LoadingSpinner from '../components/LoadingSpinner.vue';
import FilterModal from '../components/FilterModal.vue';

const router = useRouter();
const newsStore = useNewsStore();
const { newsList, loading, error, hasMore } = storeToRefs(newsStore);

const searchQuery = ref('');
const isFilterModalOpen = ref(false);

const filters = ref({
  sortBy: 'newest',
  date: '',
  selectedSources: [] as number[]
});

const SOURCES: Record<number, string> = Object.fromEntries(
  Object.entries(NEWS_SOURCES).map(([id, src]) => [Number(id), src.name])
);

const hasActiveFilters = computed(() => {
  return filters.value.sortBy !== 'newest' ||
    filters.value.date !== '' ||
    filters.value.selectedSources.length > 0;
});

const activeFilterCount = computed(() => {
  let count = 0;
  if (filters.value.sortBy !== 'newest') count++;
  if (filters.value.date) count++;
  count += filters.value.selectedSources.length;
  return count;
});

onMounted(() => {
  if (newsList.value.length === 0) {
    loadNews(true);
  }
});

const handleSearch = () => {
  loadNews(true);
};

const openFilterModal = () => {
  isFilterModalOpen.value = true;
};

const closeFilterModal = () => {
  isFilterModalOpen.value = false;
};

const handleApplyFilters = (newFilters: { sortBy: string; date: string; selectedSources: number[] }) => {
  filters.value = newFilters;
  loadNews(true);
};

const clearDate = () => {
  filters.value.date = '';
  loadNews(true);
};

const removeSource = (id: number) => {
  filters.value.selectedSources = filters.value.selectedSources.filter(s => s !== id);
  loadNews(true);
};

const clearAllFilters = () => {
  filters.value = {
    sortBy: 'newest',
    date: '',
    selectedSources: []
  };
  loadNews(true);
};

const loadNews = (reset = false) => {
  newsStore.loadNews(
    reset,
    searchQuery.value,
    filters.value.selectedSources,
    filters.value.date || undefined,
    filters.value.sortBy
  );
};

const goToDetail = (id: number) => {
  router.push(`/news/${id}`);
};
</script>

<style scoped>
.dashboard {
  padding-bottom: var(--spacing-3xl);
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-xl);
}

.page-title {
  font-family: var(--font-family-serif);
  font-size: 1.75rem;
  font-weight: 700;
  color: var(--color-text-primary);
  margin-bottom: 2px;
}

.page-subtitle {
  color: var(--color-text-tertiary);
  font-size: 0.9rem;
}

.header-actions {
  display: flex;
  gap: var(--spacing-md);
  align-items: center;
}

.search-box {
  position: relative;
  width: 280px;
}

.search-icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--color-text-tertiary);
  font-size: 18px;
}

.search-input {
  width: 100%;
  padding: 9px 16px 9px 38px;
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  color: var(--color-text-primary);
  font-size: 0.875rem;
  transition: border-color var(--transition-fast);
}

.search-input:focus {
  outline: none;
  border-color: var(--color-accent-primary);
}

.search-input::placeholder {
  color: var(--color-text-tertiary);
}

.filter-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 9px 16px;
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  color: var(--color-text-secondary);
  font-size: 0.875rem;
  cursor: pointer;
  transition: all var(--transition-fast);
  height: 40px;
  white-space: nowrap;
}

.filter-btn:hover {
  border-color: var(--color-border-hover);
  color: var(--color-text-primary);
}

.filter-btn.active {
  background: rgba(196, 30, 58, 0.06);
  border-color: var(--color-accent-primary);
  color: var(--color-accent-primary);
}

.filter-badge {
  background: var(--color-accent-primary);
  color: white;
  font-size: 0.7rem;
  padding: 1px 6px;
  border-radius: 10px;
  min-width: 18px;
  text-align: center;
  font-weight: 600;
}

.active-filters {
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-sm);
  margin-bottom: var(--spacing-xl);
  align-items: center;
}

.filter-tag {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 3px 10px;
  background: rgba(196, 30, 58, 0.06);
  border: 1px solid rgba(196, 30, 58, 0.15);
  border-radius: var(--radius-sm);
  color: var(--color-accent-primary);
  font-size: 0.8rem;
}

.close-icon {
  font-size: 14px;
  cursor: pointer;
  opacity: 0.6;
  transition: opacity var(--transition-fast);
}

.close-icon:hover {
  opacity: 1;
}

.clear-all-btn {
  background: none;
  border: none;
  color: var(--color-text-tertiary);
  font-size: 0.8rem;
  cursor: pointer;
  padding: 3px 8px;
}

.clear-all-btn:hover {
  color: var(--color-accent-primary);
}

.news-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: var(--spacing-lg);
  margin-bottom: var(--spacing-xl);
}

.loading-state,
.error-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-3xl) var(--spacing-xl);
  color: var(--color-text-secondary);
}

.error-icon,
.empty-icon {
  font-size: 48px;
  margin-bottom: var(--spacing-md);
}

.error-icon {
  color: var(--color-accent-danger);
}

.empty-icon {
  color: var(--color-text-tertiary);
}

.empty-state p {
  margin: 4px 0;
}

.empty-hint {
  font-size: 0.875rem;
  color: var(--color-text-tertiary);
}

.retry-btn,
.load-more-btn {
  margin-top: var(--spacing-md);
  padding: 8px 24px;
  background: var(--color-accent-primary);
  color: white;
  border-radius: var(--radius-sm);
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: background var(--transition-fast);
}

.retry-btn:hover,
.load-more-btn:hover {
  background: var(--color-accent-secondary);
}

.load-more {
  display: flex;
  justify-content: center;
  margin-top: var(--spacing-xl);
}

.loading-more {
  display: flex;
  justify-content: center;
  margin-top: var(--spacing-lg);
}

@media (max-width: 768px) {
  .dashboard-header {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--spacing-md);
  }

  .header-actions {
    flex-direction: column;
    width: 100%;
    align-items: stretch;
  }

  .search-box,
  .filter-btn {
    width: 100%;
  }

  .filter-btn {
    justify-content: center;
  }

  .page-title {
    font-size: 1.5rem;
  }
}
</style>
