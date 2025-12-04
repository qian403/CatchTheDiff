<template>
  <div class="news-card glass-panel" @click="$emit('click')">
    <div class="news-header">
      <div class="source-badge" :style="{ backgroundColor: sourceInfo.color }">
        {{ sourceInfo.name }}
      </div>
      <span class="news-time">{{ formattedTime }}</span>
    </div>
    
    <h3 class="news-title">{{ news.versions[news.versions.length - 1]?.title || '無標題' }}</h3>
    
    <div class="news-footer">
      <div class="version-badge">
        <span class="material-icons">history</span>
        {{ news.versions.length }} 個版本
      </div>
      
      <div class="update-info" v-if="news.last_changed_at > 0">
        <span class="material-icons">update</span>
        {{ formatRelativeTime(news.last_changed_at) }} 更新
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import type { News } from '../types';
import { getSourceInfo } from '../constants/sources';
import { formatTimestamp, formatRelativeTime } from '../utils/formatters';

const props = defineProps<{
  news: News;
}>();

defineEmits<{
  (e: 'click'): void
}>();

const sourceInfo = computed(() => getSourceInfo(props.news.source));
const formattedTime = computed(() => formatTimestamp(props.news.created_at));
</script>

<style scoped>
.news-card {
  padding: var(--spacing-lg);
  border-radius: var(--radius-lg);
  cursor: pointer;
  transition: all var(--transition-fast);
  display: flex;
  flex-direction: column;
  height: 100%;
}

.news-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-glow);
  border-color: rgba(59, 130, 246, 0.3);
}

.news-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-md);
}

.source-badge {
  padding: 4px 8px;
  border-radius: var(--radius-sm);
  font-size: 0.75rem;
  font-weight: 600;
  color: white;
}

.news-time {
  font-size: 0.875rem;
  color: var(--color-text-tertiary);
}

.news-title {
  font-size: 1.125rem;
  font-weight: 600;
  line-height: 1.4;
  margin-bottom: var(--spacing-lg);
  flex-grow: 1;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.news-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: var(--spacing-md);
  border-top: 1px solid rgba(255, 255, 255, 0.05);
}

.version-badge, .update-info {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 0.75rem;
  color: var(--color-text-secondary);
}

.material-icons {
  font-size: 16px;
}
</style>
