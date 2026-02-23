<template>
  <div class="stats-bar">
    <div class="stat-item">
      <div class="stat-label">{{ t('stats_total') }}</div>
      <div class="stat-value">{{ total }}</div>
    </div>
    <div class="stat-item">
      <div class="stat-label">{{ t('stats_prob') }}</div>
      <div class="stat-value highlight">{{ formattedProbability }}%</div>
    </div>
    <div class="stat-item">
      <div class="stat-label">{{ t('stats_country') }}</div>
      <div class="stat-value">{{ topRegion }}</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useTranslation } from '../composables/useTranslation';
import type { PlateCalculationResult } from '../types/plate';

const props = defineProps<{
  total: number;
  maxProbability: number;
  results: PlateCalculationResult[];
}>();

const { t } = useTranslation();

const formattedProbability = computed(() => {
  // Бэкенд возвращает 0-100, просто форматируем
  return props.maxProbability < 0.01 && props.maxProbability > 0
    ? '< 0.01'
    : props.maxProbability.toFixed(2);
});

const topRegion = computed(() => {
  if (!props.results.length) return 'N/A';
  // Результаты уже отсортированы бэкендом
  return props.results[0].country_name.toUpperCase();
});
</script>

<style scoped>
.stats-bar {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
  background: rgba(20, 20, 22, 0.6);
  backdrop-filter: blur(12px);
  border: 1px solid var(--border-subtle);
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 4rem;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.2);
}

.stat-item {
  text-align: center;
  border-right: 1px solid var(--border-subtle);
}

.stat-item:last-child {
  border-right: none;
}

.stat-label {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.65rem;
  color: var(--text-dim);
  margin-bottom: 0.5rem;
  text-transform: uppercase;
}

.stat-value {
  font-family: 'Inter', sans-serif;
  font-size: 1.2rem;
  font-weight: 600;
  color: var(--text-main);
}

.highlight {
  color: var(--color-primary);
}

@media (max-width: 640px) {
  .stats-bar {
    grid-template-columns: 1fr;
    gap: 1.5rem;
    margin-bottom: 2rem; /* Уменьшаем отступ на мобильных, чтобы избежать наложений */
  }
  .stat-item {
    border-right: none;
    border-bottom: 1px solid var(--border-subtle);
    padding-bottom: 1rem;
  }
  .stat-item:last-child {
    border-bottom: none;
    padding-bottom: 0;
  }
}
</style>