<template>
  <div class="chart-container glass-panel">
    <h3 class="chart-title">新聞來源分佈</h3>
    <div class="chart-wrapper">
      <Doughnut v-if="chartData.datasets[0].data.length > 0" :data="chartData" :options="chartOptions" />
      <div v-else class="no-data">暫無數據</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js';
import { Doughnut } from 'vue-chartjs';
import { getSourceInfo } from '../constants/sources';

ChartJS.register(ArcElement, Tooltip, Legend);

const props = defineProps<{
  sourceStats: Record<number, number>;
}>();

const chartData = computed(() => {
  const sourceIds = Object.keys(props.sourceStats).map(Number);
  const data = Object.values(props.sourceStats);
  const labels = sourceIds.map(id => getSourceInfo(id).name);
  const backgroundColors = sourceIds.map(id => getSourceInfo(id).color);

  return {
    labels,
    datasets: [
      {
        backgroundColor: backgroundColors,
        data: data,
        borderWidth: 0
      }
    ]
  };
});

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'right' as const,
      labels: {
        color: '#cbd5e1',
        font: {
          family: "'Inter', sans-serif",
          size: 12
        },
        usePointStyle: true,
        padding: 20
      }
    }
  },
  cutout: '70%'
};
</script>

<style scoped>
.chart-container {
  padding: var(--spacing-lg);
  border-radius: var(--radius-lg);
  height: 100%;
  display: flex;
  flex-direction: column;
}

.chart-title {
  font-size: 1.125rem;
  font-weight: 600;
  margin-bottom: var(--spacing-lg);
  color: var(--color-text-primary);
}

.chart-wrapper {
  flex: 1;
  position: relative;
  min-height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.no-data {
  color: var(--color-text-tertiary);
}
</style>
