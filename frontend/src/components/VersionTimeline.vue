<template>
  <div class="version-timeline paper-card">
    <h3 class="timeline-header">版本歷史</h3>
    
    <v-timeline density="compact" side="end" line-color="grey-darken-2" truncate-line="both">
      <v-timeline-item
        v-for="version in sortedVersions"
        :key="version.id"
        :dot-color="getDotColor(version)"
        size="small"
        fill-dot
        class="timeline-item-cursor"
      >
        <div 
          class="timeline-content" 
          :class="{ 'active': selectedVersionId === version.id }"
          @click="$emit('select', version.id)"
        >
          <div class="version-time">{{ formatTimestamp(version.time) }}</div>
          <div class="version-title" :title="version.title">{{ version.title }}</div>
        </div>
      </v-timeline-item>
    </v-timeline>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import type { NewsVersion } from '../types';
import { formatTimestamp } from '../utils/formatters';

const props = defineProps<{
  versions: NewsVersion[];
  selectedVersionId: number | null;
  compareSourceId: number | null;
  compareTargetId: number | null;
}>();

defineEmits<{
  (e: 'select', id: number): void;
  (e: 'compare', id: number): void;
}>();

// Sort versions descending (newest first)
const sortedVersions = computed(() => {
  return [...props.versions].sort((a, b) => b.time - a.time);
});

const getDotColor = (version: NewsVersion) => {
  if (props.selectedVersionId === version.id) return 'primary';
  if (props.compareSourceId === version.id) return 'warning';
  if (props.compareTargetId === version.id) return 'secondary';
  return 'grey-darken-2';
};
</script>

<style scoped>
.version-timeline {
  padding: var(--spacing-lg);
  height: 100%;
  overflow-y: auto;
}

.timeline-header {
  font-family: var(--font-family-serif);
  font-size: 1rem;
  font-weight: 600;
  margin-bottom: var(--spacing-lg);
  padding-bottom: var(--spacing-sm);
  border-bottom: 1px solid var(--color-border);
  color: var(--color-text-primary);
}

.timeline-item-cursor {
  cursor: pointer;
}

.timeline-content {
  padding: var(--spacing-sm) var(--spacing-md);
  border-radius: var(--radius-sm);
  border: 1px solid transparent;
  transition: all var(--transition-fast);
}

.timeline-content:hover {
  background-color: var(--color-bg-tertiary);
}

.timeline-content.active {
  background-color: rgba(196, 30, 58, 0.06);
  border-color: rgba(196, 30, 58, 0.2);
}

.version-time {
  font-size: 0.75rem;
  color: var(--color-text-tertiary);
  margin-bottom: 2px;
}

.version-title {
  font-size: 0.85rem;
  font-weight: 500;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
