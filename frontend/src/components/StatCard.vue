<template>
  <div class="stat-card paper-card">
    <div class="stat-icon" :style="{ backgroundColor: props.iconBgColor }">
      <span class="material-icons">{{ props.icon }}</span>
    </div>
    <div class="stat-content">
      <h3 class="stat-value">{{ props.value }}</h3>
      <p class="stat-label">{{ props.label }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  icon: string;
  value: string | number;
  label: string;
  iconBgColor?: string;
}

const props = withDefaults(defineProps<Props>(), {
  iconBgColor: 'rgba(59, 130, 246, 0.1)'
});
</script>

<style scoped>
.stat-card {
  display: flex;
  align-items: center;
  padding: var(--spacing-lg);
  transition: box-shadow var(--transition-fast);
}

.stat-card:hover {
  box-shadow: var(--shadow-md);
}

.stat-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
  border-radius: var(--radius-sm);
  margin-right: var(--spacing-md);
  color: white;
}

.stat-icon .material-icons {
  font-size: 20px;
}

.stat-value {
  font-family: var(--font-family-serif);
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--color-text-primary);
  line-height: 1.2;
}

.stat-label {
  font-size: 0.8rem;
  color: var(--color-text-tertiary);
  margin-top: 2px;
}
</style>
