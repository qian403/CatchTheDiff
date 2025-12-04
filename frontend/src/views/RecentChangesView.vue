<template>
  <div class="recent-view">
    <header class="page-header">
      <div>
        <h1 class="page-title">變更紀錄</h1>
        <p class="page-subtitle">即時追蹤各家新聞媒體的內容變更</p>
      </div>
    </header>
    
    <section class="content-section">
      <div v-if="loading && newsList.length === 0" class="loading-state">
        <LoadingSpinner />
      </div>

      <div v-else-if="error" class="error-state">
        <span class="material-icons error-icon">error_outline</span>
        <p>{{ error }}</p>
        <button @click="loadChangeHistory(true)" class="retry-btn">重試</button>
      </div>

      <div v-else-if="newsList.length === 0" class="empty-state">
        <span class="material-icons empty-icon">history</span>
        <p>目前沒有變更記錄</p>
        <p class="empty-hint">當新聞內容被修改後，會在這裡顯示</p>
      </div>

      <div v-else class="news-grid">
        <NewsCard 
          v-for="news in newsList" 
          :key="news.id" 
          :news="news"
          @click="goToDetail(news.id)"
        />
      </div>

      <!-- Load More -->
      <div v-if="hasMore && !loading && newsList.length > 0" class="load-more">
        <button @click="loadChangeHistory()" class="load-more-btn">
          載入更多
        </button>
      </div>
      
      <div v-if="loading && newsList.length > 0" class="loading-more">
        <LoadingSpinner />
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import type { News } from '../types';
import { fetchChangedNews } from '../api/news';
import NewsCard from '../components/NewsCard.vue';
import LoadingSpinner from '../components/LoadingSpinner.vue';

const router = useRouter();

const newsList = ref<News[]>([]);
const loading = ref(false);
const error = ref<string | null>(null);
const hasMore = ref(true);
const page = ref(0);
const limit = 30;

onMounted(() => {
  loadChangeHistory(true);
});

async function loadChangeHistory(reset = false) {
  if (reset) {
    page.value = 0;
    newsList.value = [];
    hasMore.value = true;
  }

  if (!hasMore.value && !reset) return;

  loading.value = true;
  error.value = null;

  try {
    const data = await fetchChangedNews(page.value * limit, limit);

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
    error.value = err.message || '載入變更紀錄失敗';
    console.error(err);
  } finally {
    loading.value = false;
  }
}

const goToDetail = (id: number) => {
  router.push(`/news/${id}`);
};
</script>

<style scoped>
.recent-view {
  padding-bottom: var(--spacing-2xl);
}

.page-header {
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

.news-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  column-gap: var(--spacing-lg);
  row-gap: var(--spacing-4xl);
  margin-bottom: var(--spacing-xl);
}

.loading-state, .error-state, .empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-2xl);
  color: var(--color-text-secondary);
}

.error-icon, .empty-icon {
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

.retry-btn, .load-more-btn {
  margin-top: var(--spacing-md);
  padding: 8px 24px;
  background: var(--color-accent-primary);
  color: white;
  border-radius: var(--radius-md);
  font-weight: 600;
  transition: background var(--transition-fast);
}

.retry-btn:hover, .load-more-btn:hover {
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
</style>
