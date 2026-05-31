<template>
  <div class="diff-viewer paper-card">
    <div class="diff-header">
      <div class="diff-tabs">
        <button 
          class="tab-btn" 
          :class="{ active: activeTab === 'title' }"
          @click="activeTab = 'title'"
        >
          標題差異
        </button>
        <button 
          class="tab-btn" 
          :class="{ active: activeTab === 'body' }"
          @click="activeTab = 'body'"
        >
          內文差異
        </button>
      </div>
    </div>

    <div class="diff-content-wrapper">
      <div v-if="loading" class="loading-container">
        <LoadingSpinner />
      </div>
      
      <div v-else-if="diffFile" class="git-diff-container">
        <DiffView 
          :diffFile="diffFile" 
          :diffViewTheme="'light'" 
          :diffViewMode="'unified'" 
          :diffViewHighlight="true"
          :diffViewWrap="true"
        />
      </div>
      
      <div v-else class="empty-state">
        無差異資料
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { DiffView } from '@git-diff-view/vue';
import { generateDiffFile } from '@git-diff-view/file';
import '@git-diff-view/vue/styles/diff-view.css';

import type { NewsDiff } from '../types';
import LoadingSpinner from './LoadingSpinner.vue';

const props = defineProps<{
  diff: NewsDiff | null;
  loading: boolean;
}>();

const activeTab = ref<'title' | 'body'>('body');

const diffFile = computed(() => {
  if (!props.diff) return null;

  const rawDiff = activeTab.value === 'title' ? props.diff.diff_title : props.diff.diff_body;
  if (!rawDiff) return null;

  // Reconstruct old and new strings from diff-match-patch data
  let oldStr = '';
  let newStr = '';

  try {
    const diffData = typeof rawDiff === 'string' ? JSON.parse(rawDiff) : rawDiff;

    for (const [op, text] of diffData) {
      if (op === 0) {
        oldStr += text;
        newStr += text;
      } else if (op === -1) {
        oldStr += text;
      } else if (op === 1) {
        newStr += text;
      }
    }
    
    const fileName = activeTab.value === 'title' ? 'Title' : 'Body';
    
    // If there's no difference, return null
    if (oldStr === newStr) {
      return null;
    }
    
    // Use generateDiffFile to create the diff - this is the recommended approach
    const file = generateDiffFile(
      fileName,
      oldStr,
      fileName,
      newStr,
      'plaintext',
      'plaintext'
    );
    
    file.initTheme('light');
    file.init();

    return file;
  } catch (e) {
    console.error('Error generating diff:', e);
    return null;
  }
});
</script>

<style scoped>
.diff-viewer {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
}

.diff-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-sm) var(--spacing-lg);
  background: var(--color-bg-tertiary);
  border-bottom: 1px solid var(--color-border);
}

.diff-tabs {
  display: flex;
  gap: 2px;
}

.tab-btn {
  padding: 6px 14px;
  border-radius: var(--radius-sm);
  color: var(--color-text-secondary);
  font-size: 0.8rem;
  font-weight: 500;
  transition: all var(--transition-fast);
  cursor: pointer;
}

.tab-btn:hover {
  background-color: var(--color-bg-primary);
  color: var(--color-text-primary);
}

.tab-btn.active {
  background-color: var(--color-accent-primary);
  color: white;
}

.diff-content-wrapper {
  flex: 1;
  overflow: hidden;
  position: relative;
}

.git-diff-container {
  height: 100%;
  overflow-y: auto;
}

.loading-container, .empty-state {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  color: var(--color-text-secondary);
  font-size: 0.9rem;
}

:deep(.diff-view-container) {
  background-color: transparent !important;
}
</style>
