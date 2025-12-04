<template>
  <div class="stats-view">
    <h1 class="page-title">統計資訊</h1>

    <!-- Loading state -->
    <div v-if="loading" class="loading">載入中...</div>

    <!-- Overview cards -->
    <div v-else-if="stats" class="stats-grid">
      <StatCard icon="article" :value="stats.totalNews" label="追蹤新聞總數" iconBgColor="#3B82F6" />
      <StatCard icon="edit" :value="stats.totalEdits" label="累計修改次數" iconBgColor="#F59E0B" />
      <StatCard icon="source" :value="stats.mostActiveSource?.name || 'N/A'"
        :label="`最常偷改: ${stats.mostActiveSource?.editCount || 0}次`" iconBgColor="#10B981" />
      <StatCard icon="history" :value="stats.mostEditedNews?.versionCount || 0"
        :label="stats.mostEditedNews?.title?.substring(0, 20) + '...' || '最多版本新聞'" iconBgColor="#8B5CF6" />
    </div>

    <!-- Edit Frequency Ranking -->
    <div v-if="editFrequency.length > 0" class="section">
      <h2 class="section-title">🏆 偷改王排行榜</h2>
      <div class="ranking-table">
        <table>
          <thead>
            <tr>
              <th>排名</th>
              <th>媒體來源</th>
              <th>新聞數</th>
              <th>修改次數</th>
              <th>修改比率</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(item, index) in editFrequency" :key="item.sourceId">
              <td class="rank">
                <span v-if="index === 0" class="medal gold">🥇</span>
                <span v-else-if="index === 1" class="medal silver">🥈</span>
                <span v-else-if="index === 2" class="medal bronze">🥉</span>
                <span v-else>{{ index + 1 }}</span>
              </td>
              <td class="source-name">{{ item.sourceName }}</td>
              <td>{{ item.newsCount }}</td>
              <td class="edit-count">{{ item.editCount }}</td>
              <td>
                <span class="ratio" :class="getRatioClass(item.editRatio)">
                  {{ item.editRatio.toFixed(2) }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Publication Timeline Chart -->
    <div v-if="timelineData" class="section">
      <h2 class="section-title">📰 新聞發布動態 (最近30天)</h2>
      <div class="chart-container">
        <Line :data="publicationChartData" :options="chartOptions" />
      </div>
    </div>

    <!-- Edit Timeline Chart -->
    <div v-if="timelineData" class="section">
      <h2 class="section-title">✏️ 新聞修改動態 (最近30天)</h2>
      <div class="chart-container">
        <Line :data="editChartData" :options="chartOptions" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { Line } from 'vue-chartjs';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js';
import StatCard from '../components/StatCard.vue';
import apiClient from '../api/client';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

// Colors for different sources
const sourceColors = [
  '#3B82F6', // Blue
  '#F59E0B', // Orange  
  '#10B981', // Green
  '#8B5CF6', // Purple
  '#EF4444', // Red
  '#EC4899', // Pink
  '#14B8A6'  // Teal
];

const loading = ref(true);
const stats = ref<any>(null);
const editFrequency = ref<any[]>([]);
const timelineData = ref<any>(null);

const publicationChartData = computed(() => {
  if (!timelineData.value) return null;

  const datasets = timelineData.value.sources.map((source: any, index: number) => ({
    label: source.sourceName,
    data: timelineData.value.dates.map((date: string) => source.data[date].newNews),
    borderColor: sourceColors[index % sourceColors.length],
    backgroundColor: sourceColors[index % sourceColors.length] + '20',
    tension: 0.4,
    fill: false
  }));

  return {
    labels: timelineData.value.dates,
    datasets
  };
});

const editChartData = computed(() => {
  if (!timelineData.value) return null;

  const datasets = timelineData.value.sources.map((source: any, index: number) => ({
    label: source.sourceName,
    data: timelineData.value.dates.map((date: string) => source.data[date].edits),
    borderColor: sourceColors[index % sourceColors.length],
    backgroundColor: sourceColors[index % sourceColors.length] + '20',
    tension: 0.4,
    fill: false
  }));

  return {
    labels: timelineData.value.dates,
    datasets
  };
});

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  interaction: {
    mode: 'index' as const,
    intersect: false,
  },
  plugins: {
    legend: {
      position: 'top' as const,
      labels: {
        usePointStyle: true,
        padding: 15
      }
    },
    tooltip: {
      mode: 'index' as const,
      intersect: false,
    }
  },
  scales: {
    y: {
      beginAtZero: true,
      ticks: {
        precision: 0
      }
    }
  }
};

const getRatioClass = (ratio: number) => {
  if (ratio >= 2) return 'high';
  if (ratio >= 1) return 'medium';
  return 'low';
};

const loadStats = async () => {
  try {
    loading.value = true;

    const [statsRes, freqRes, timelineRes] = await Promise.all([
      apiClient.get('/stats'),
      apiClient.get('/stats/edit-frequency'),
      apiClient.get('/stats/timeline?days=30')
    ]);

    stats.value = statsRes.data;
    editFrequency.value = freqRes.data;
    timelineData.value = timelineRes.data;
  } catch (error) {
    console.error('Failed to load statistics:', error);
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  loadStats();
});
</script>

<style scoped>
.stats-view {
  padding-bottom: var(--spacing-2xl);
}

.page-title {
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: var(--spacing-xl);
}

.loading {
  text-align: center;
  padding: var(--spacing-2xl);
  color: var(--color-text-secondary);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: var(--spacing-lg);
  margin-bottom: var(--spacing-2xl);
}

.section {
  margin-bottom: var(--spacing-2xl);
}

.section-title {
  font-size: 1.5rem;
  font-weight: 600;
  margin-bottom: var(--spacing-lg);
  color: var(--color-text-primary);
}

.ranking-table {
  background: var(--color-bg-secondary);
  border-radius: var(--radius-lg);
  overflow: hidden;
  box-shadow: var(--shadow-sm);
}

table {
  width: 100%;
  border-collapse: collapse;
}

thead {
  background: var(--color-bg-tertiary);
}

th {
  padding: var(--spacing-md);
  text-align: left;
  font-weight: 600;
  color: var(--color-text-secondary);
  font-size: 0.875rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

td {
  padding: var(--spacing-md);
  border-top: 1px solid var(--color-border);
}

.rank {
  font-weight: 600;
  text-align: center;
  width: 80px;
}

.medal {
  font-size: 1.5rem;
}

.source-name {
  font-weight: 500;
}

.edit-count {
  color: var(--color-warning);
  font-weight: 600;
}

.ratio {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: var(--radius-md);
  font-weight: 600;
  font-size: 0.875rem;
}

.ratio.high {
  background: rgba(239, 68, 68, 0.1);
  color: #EF4444;
}

.ratio.medium {
  background: rgba(245, 158, 11, 0.1);
  color: #F59E0B;
}

.ratio.low {
  background: rgba(16, 185, 129, 0.1);
  color: #10B981;
}

.chart-container {
  background: var(--color-bg-secondary);
  border-radius: var(--radius-lg);
  padding: var(--spacing-xl);
  box-shadow: var(--shadow-sm);
  height: 400px;
}
</style>
