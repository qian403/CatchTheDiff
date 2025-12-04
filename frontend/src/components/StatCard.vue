<template>
  <div class="stat-card glass-panel">
    <div class="stat-icon" :style="{ backgroundColor: iconBgColor }">
      <span class="material-icons">{{ icon }}</span>
    </div>
    <div class="stat-content">
      <h3 class="stat-value">{{ value }}</h3>
      <p class="stat-label">{{ label }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  icon: string;
  value: string | number;
  label: string;
  iconBgColor?: string;
}>();
</script>

<style scoped>
.stat-card {
  display: flex;
  align-items: center;
  padding: var(--spacing-lg);
  border-radius: var(--radius-lg);
  transition: transform var(--transition-fast);
}

.stat-card:hover {
  transform: translateY(-2px);
}

.stat-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  border-radius: var(--radius-md);
  margin-right: var(--spacing-md);
  background-color: rgba(59, 130, 246, 0.1);
  color: white;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--color-text-primary);
  line-height: 1.2;
}

.stat-label {
  font-size: 0.875rem;
  color: var(--color-text-tertiary);
  margin-top: 2px;
}
</style>
