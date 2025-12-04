<template>
  <div class="news-detail">
    <div v-if="loading && !currentNews" class="loading-screen">
      <LoadingSpinner />
    </div>

    <div v-else-if="error" class="error-screen">
      <p>{{ error }}</p>
      <button @click="loadNewsDetail" class="retry-btn">重試</button>
    </div>

    <div v-else-if="currentNews" class="detail-layout">
      <!-- Sidebar: Version Timeline -->
      <aside class="sidebar">
        <VersionTimeline :versions="currentNews.versions" :selected-version-id="selectedVersionId"
          :compare-source-id="compareSourceId" :compare-target-id="compareTargetId" @select="handleVersionSelect"
          @compare="handleCompareSelect" />
      </aside>

      <!-- Main Content -->
      <main class="main-content">
        <!-- Metadata Header -->
        <div class="meta-header glass-panel">
          <div class="meta-top">
            <div class="source-tag" :style="{ backgroundColor: sourceInfo.color }">
              {{ sourceInfo.name }}
            </div>
            <div class="header-actions">
              <v-switch v-model="showGitDiff" label="顯示變更 (Git Mode)" color="primary" hide-details density="compact"
                class="git-switch"></v-switch>
              <a :href="currentNews.url" target="_blank" class="original-link">
                原始連結 <span class="material-icons">open_in_new</span>
              </a>
            </div>
          </div>

          <h1 class="news-title">{{ displayTitle }}</h1>

          <!-- Title diff comparison (shown below title if changed) -->
          <div v-if="titleHasChanged" class="title-diff-section">
            <div class="diff-label">標題變更對比</div>
            <div class="title-comparison">
              <div class="old-title">
                <span class="diff-marker">舊</span>
                <!-- eslint-disable-next-line vue/no-v-html -- Safe: sanitized with DOMPurify -->
                <span v-html="highlightTitleDiff(previousTitle, displayTitle, 'old')"></span>
              </div>
              <div class="arrow-separator">→</div>
              <div class="new-title">
                <span class="diff-marker">新</span>
                <!-- eslint-disable-next-line vue/no-v-html -- Safe: sanitized with DOMPurify -->
                <span v-html="highlightTitleDiff(previousTitle, displayTitle, 'new')"></span>
              </div>
            </div>
          </div>

          <div class="meta-info">
            <span>首次發布: {{ formatTimestamp(currentNews.created_at) }}</span>
            <span>最後更新: {{ formatTimestamp(currentNews.last_fetch_at) }}</span>
            <span>共 {{ currentNews.versions.length }} 個版本</span>
          </div>
        </div>

        <!-- Content Area -->
        <div class="content-area">
          <!-- Diff View Mode -->
          <div v-if="isComparing" class="diff-mode">
            <div class="mode-header">
              <h2>版本比對</h2>
            </div>
            <DiffViewer :diff="currentDiff" :loading="loading" />
          </div>

          <!-- Single Version Mode -->
          <div v-else class="single-mode glass-panel">
            <div class="version-indicator">
              當前顯示版本: {{ formatTimestamp(selectedVersion?.time || 0) }}
            </div>
            <div class="article-body">
              {{ displayBody }}
            </div>
          </div>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue';
import { useRoute } from 'vue-router';
import { storeToRefs } from 'pinia';
import { useNewsStore } from '../stores/news';
import { getSourceInfo } from '../constants/sources';
import { formatTimestamp } from '../utils/formatters';
import VersionTimeline from '../components/VersionTimeline.vue';
import DiffViewer from '../components/DiffViewer.vue';
import LoadingSpinner from '../components/LoadingSpinner.vue';
import DOMPurify from 'dompurify';

const route = useRoute();
const newsStore = useNewsStore();
const { currentNews, currentDiff, loading, error } = storeToRefs(newsStore);

const selectedVersionId = ref<number | null>(null);
const compareSourceId = ref<number | null>(null);
const compareTargetId = ref<number | null>(null);
const showGitDiff = ref(false);

const newsId = computed(() => Number(route.params.id));
const sourceInfo = computed(() => currentNews.value ? getSourceInfo(currentNews.value.source) : { name: '', color: '' });

const selectedVersion = computed(() => {
  if (!currentNews.value || !selectedVersionId.value) return null;
  return currentNews.value.versions.find(v => v.id === selectedVersionId.value);
});


// Memoize sorted versions for better performance
const sortedVersions = computed(() => {
  if (!currentNews.value) return [];
  return [...currentNews.value.versions].sort((a, b) => b.time - a.time);
});

const displayTitle = computed(() => selectedVersion.value?.title || '');
const displayBody = computed(() => selectedVersion.value?.body || '');

// Check if title has changed from previous version
const previousVersion = computed(() => {
  if (!selectedVersionId.value) return null;
  const currentIndex = sortedVersions.value.findIndex(v => v.id === selectedVersionId.value);
  if (currentIndex !== -1 && currentIndex < sortedVersions.value.length - 1) {
    return sortedVersions.value[currentIndex + 1];
  }
  return null;
});

const previousTitle = computed(() => previousVersion.value?.title || '');
const titleHasChanged = computed(() => {
  return previousVersion.value && previousTitle.value !== displayTitle.value;
});

// Simple character-level diff highlighting
function highlightTitleDiff(oldText: string, newText: string, mode: 'old' | 'new'): string {
  if (!oldText || !newText) return DOMPurify.sanitize(mode === 'old' ? oldText : newText);

  // Simple word-level diff for readability
  const oldWords = oldText.split('');
  const newWords = newText.split('');

  if (mode === 'old') {
    // Highlight deletions in red
    let result = '';
    let i = 0, j = 0;
    while (i < oldWords.length || j < newWords.length) {
      if (i < oldWords.length && j < newWords.length && oldWords[i] === newWords[j]) {
        result += oldWords[i];
        i++;
        j++;
      } else if (i < oldWords.length) {
        result += `<del class="diff-del">${oldWords[i]}</del>`;
        i++;
      } else {
        j++;
      }
    }
    // Sanitize the generated HTML to prevent XSS
    return DOMPurify.sanitize(result);
  } else {
    // Highlight additions in green
    let result = '';
    let i = 0, j = 0;
    while (i < oldWords.length || j < newWords.length) {
      if (i < oldWords.length && j < newWords.length && oldWords[i] === newWords[j]) {
        result += newWords[j];
        i++;
        j++;
      } else if (j < newWords.length) {
        result += `<ins class="diff-ins">${newWords[j]}</ins>`;
        j++;
      } else {
        i++;
      }
    }
    // Sanitize the generated HTML to prevent XSS
    return DOMPurify.sanitize(result);
  }
}

const isComparing = computed(() => compareSourceId.value !== null && compareTargetId.value !== null);

// Watch for Git Mode toggle
watch(showGitDiff, (val) => {
  if (val) {
    updateGitDiff();
  } else {
    exitCompareMode();
  }
});

// Watch for selected version change to update Git Diff if active
watch(selectedVersionId, () => {
  if (showGitDiff.value) {
    updateGitDiff();
  }
});

onMounted(() => {
  loadNewsDetail();
});

async function loadNewsDetail() {
  await newsStore.loadNewsDetail(newsId.value);
  if (currentNews.value && currentNews.value.versions.length > 0) {
    // Select latest version by default
    selectedVersionId.value = sortedVersions.value[0]?.id || null;
  }
}

function updateGitDiff() {
  if (!currentNews.value || !selectedVersionId.value) return;

  const currentIndex = sortedVersions.value.findIndex(v => v.id === selectedVersionId.value);

  if (currentIndex !== -1 && currentIndex < sortedVersions.value.length - 1) {
    const prevVersion = sortedVersions.value[currentIndex + 1];
    // Compare: Source (Old) -> Target (New)
    compareSourceId.value = prevVersion.id;
    compareTargetId.value = selectedVersionId.value;
    fetchDiff();
  } else {
    // No previous version (Initial commit)
    compareSourceId.value = null;
    compareTargetId.value = null;
    newsStore.currentDiff = null;
  }
}

function handleVersionSelect(id: number) {
  // If Git Mode is on, just change selection and let watcher handle diff
  if (showGitDiff.value) {
    selectedVersionId.value = id;
    return;
  }

  if (compareSourceId.value) {
    // If we are in "select target for compare" mode
    compareTargetId.value = id;
    fetchDiff();
  } else {
    // Just viewing a version
    selectedVersionId.value = id;
    exitCompareMode();
  }
}

function handleCompareSelect(id: number) {
  showGitDiff.value = false; // Disable Git Mode if manual compare is triggered
  compareSourceId.value = selectedVersionId.value; // Current view is source
  compareTargetId.value = id; // Selected is target
  fetchDiff();
}

async function fetchDiff() {
  if (!compareSourceId.value || !compareTargetId.value || !currentNews.value) return;

  const v1 = currentNews.value.versions.find(v => v.id === compareSourceId.value);
  const v2 = currentNews.value.versions.find(v => v.id === compareTargetId.value);

  if (v1 && v2) {
    await newsStore.loadDiff(newsId.value, v1.time, v2.time);
  }
}

function exitCompareMode() {
  showGitDiff.value = false;
  compareSourceId.value = null;
  compareTargetId.value = null;
  newsStore.currentDiff = null;
}
</script>

<style scoped>
.news-detail {
  padding-bottom: var(--spacing-2xl);
}

.loading-screen,
.error-screen {
  height: 50vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.detail-layout {
  display: grid;
  grid-template-columns: 300px 1fr;
  gap: var(--spacing-xl);
  align-items: start;
}

.sidebar {
  position: sticky;
  top: 100px;
  max-height: calc(100vh - 120px);
}

.meta-header {
  padding: var(--spacing-xl);
  border-radius: var(--radius-lg);
  margin-bottom: var(--spacing-xl);
}

.meta-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-lg);
}

.source-tag {
  padding: 4px 12px;
  border-radius: var(--radius-full);
  font-weight: 600;
  font-size: 0.875rem;
  color: white;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: var(--spacing-lg);
}

.git-switch {
  display: flex;
  align-items: center;
}

.original-link {
  display: flex;
  align-items: center;
  gap: 4px;
  color: var(--color-accent-primary);
  font-size: 0.875rem;
  font-weight: 500;
}

.original-link:hover {
  text-decoration: underline;
}


.news-title {
  font-size: 2rem;
  font-weight: 700;
  line-height: 1.3;
  margin-bottom: var(--spacing-md);
}

.title-diff-section {
  margin-top: var(--spacing-md);
  margin-bottom: var(--spacing-lg);
  padding: var(--spacing-md) var(--spacing-lg);
  border-radius: var(--radius-md);
}

.diff-label {
  font-size: 0.875rem;
  color: var(--color-text-secondary);
  margin-bottom: var(--spacing-sm);
  font-weight: 600;
}

.title-comparison {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  gap: var(--spacing-md);
  align-items: center;
}

.arrow-separator {
  color: var(--color-text-tertiary);
  font-size: 1.25rem;
  font-weight: bold;
}

.old-title,
.new-title {
  display: flex;
  align-items: flex-start;
  gap: var(--spacing-sm);
  line-height: 1.5;
  font-size: 0.95rem;
}

.diff-marker {
  flex-shrink: 0;
  font-size: 0.75rem;
  font-weight: 700;
  padding: 2px 6px;
  border-radius: var(--radius-sm);
  text-align: center;
  min-width: 32px;
}

.old-title .diff-marker {
  background-color: rgba(239, 68, 68, 0.15);
  color: #EF4444;
}

.new-title .diff-marker {
  background-color: rgba(16, 185, 129, 0.15);
  color: #10B981;
}

.diff-del {
  background-color: rgba(239, 68, 68, 0.25);
  color: #EF4444;
  text-decoration: line-through;
  padding: 1px 3px;
  border-radius: 2px;
}

.diff-ins {
  background-color: rgba(16, 185, 129, 0.25);
  color: #10B981;
  text-decoration: none;
  padding: 1px 3px;
  border-radius: 2px;
  font-weight: 600;
}

@media (max-width: 768px) {
  .title-comparison {
    grid-template-columns: 1fr;
    gap: var(--spacing-sm);
  }

  .arrow-separator {
    display: none;
  }
}

.meta-info {
  display: flex;
  gap: var(--spacing-xl);
  color: var(--color-text-tertiary);
  font-size: 0.875rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  padding-top: var(--spacing-md);
}

.content-area {
  min-height: 400px;
}

.single-mode {
  padding: var(--spacing-2xl);
  border-radius: var(--radius-lg);
}

.version-indicator {
  display: inline-block;
  padding: 4px 12px;
  background-color: rgba(59, 130, 246, 0.1);
  color: var(--color-accent-primary);
  border-radius: var(--radius-full);
  font-size: 0.875rem;
  margin-bottom: var(--spacing-xl);
}

.article-body {
  font-size: 1.125rem;
  line-height: 1.8;
  color: var(--color-text-secondary);
  white-space: pre-wrap;
}

.mode-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-lg);
}



@media (max-width: 1024px) {
  .detail-layout {
    grid-template-columns: 1fr;
  }

  .sidebar {
    position: static;
    max-height: 400px;
    margin-bottom: var(--spacing-xl);
  }
}
</style>
