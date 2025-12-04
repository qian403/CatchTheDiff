<template>
  <div class="dashboard">
    <!-- Header with Search -->
    <header class="dashboard-header">
      <div>
        <h1 class="page-title">所有新聞</h1>
        <p class="page-subtitle">即時監控 18 家新聞媒體的版本變更</p>
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

const SOURCES: Record<number, string> = {
  1: "中央廣播電台",
  2: "中時新聞網",
  3: "中央社",
  4: "ETtoday新聞雲",
  5: "自由時報",
  6: "新頭殼",
  7: "NOWnews今日新聞",
  8: "聯合新聞網",
  9: "TVBS新聞",
  10: "中廣新聞網",
  11: "公視新聞網",
  12: "台視新聞",
  13: "華視新聞",
  14: "民視新聞",
  15: "三立新聞",
  16: "風傳媒",
  17: "關鍵評論網",
  18: "報導者"
};

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

const handleApplyFilters = (newFilters: any) => {
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
  padding-bottom: var(--spacing-2xl);
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-xl);
}

.page-title {
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 4px;
}

.page-subtitle {
  color: var(--color-text-tertiary);
}

.header-actions {
  display: flex;
  gap: var(--spacing-md);
  align-items: center;
}

.search-box {
  position: relative;
  width: 300px;
}

.search-icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--color-text-tertiary);
}

.search-input {
  width: 100%;
  padding: 10px 16px 10px 40px;
  background: rgba(0, 0, 0, 0.2);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  color: var(--color-text-primary);
  font-size: 0.875rem;
  transition: all var(--transition-fast);
}

.search-input:focus {
  outline: none;
  border-color: var(--color-accent-primary);
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
}

.filter-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  background: rgba(0, 0, 0, 0.2);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  color: var(--color-text-primary);
  font-size: 0.875rem;
  cursor: pointer;
  transition: all var(--transition-fast);
  height: 42px;
  /* Match search input height */
}

.filter-btn:hover {
  background: rgba(255, 255, 255, 0.05);
  border-color: var(--color-text-secondary);
}

.filter-btn.active {
  background: rgba(59, 130, 246, 0.1);
  border-color: var(--color-accent-primary);
  color: var(--color-accent-primary);
}

.filter-badge {
  background: var(--color-accent-primary);
  color: white;
  font-size: 0.75rem;
  padding: 2px 6px;
  border-radius: 10px;
  min-width: 18px;
  text-align: center;
}

.active-filters {
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-sm);
  margin-bottom: var(--spacing-lg);
  align-items: center;
}

.filter-tag {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 12px;
  background: rgba(59, 130, 246, 0.1);
  border: 1px solid rgba(59, 130, 246, 0.2);
  border-radius: 100px;
  color: var(--color-accent-primary);
  font-size: 0.875rem;
}

.close-icon {
  font-size: 16px;
  cursor: pointer;
  opacity: 0.7;
  transition: opacity var(--transition-fast);
}

.close-icon:hover {
  opacity: 1;
}

.clear-all-btn {
  background: none;
  border: none;
  color: var(--color-text-tertiary);
  font-size: 0.875rem;
  cursor: pointer;
  text-decoration: underline;
  padding: 4px 8px;
}

.clear-all-btn:hover {
  color: var(--color-text-primary);
}

.news-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  column-gap: var(--spacing-lg);
  row-gap: var(--spacing-4xl);
  margin-bottom: var(--spacing-xl);
}

.loading-state,
.error-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-2xl);
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
  border-radius: var(--radius-md);
  font-weight: 600;
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
}
</style>
