<template>
  <div class="result-grid">
    <div
      v-for="(result, index) in results"
      :key="`${result.country_code}-${index}`"
      class="result-card"
      :class="{ 'best-match': isBestMatch(result.probability) }"
    >
      <div class="card-header">
        <div class="country-info">
          <span class="country-name">{{ result.country_name }}</span>
        </div>
        <div class="probability">
          {{ formatProb(result.probability) }}%
        </div>
      </div>

      <LicensePlate
        :result="result"
        :isHighLighted="isBestMatch(result.probability)"
      />
      
      <div class="card-footer">
        <div class="pattern-info">{{ t('pattern') }}: {{ result.pattern }}</div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useTranslation } from '../composables/useTranslation';
import type { PlateCalculationResult } from '../types/plate';
import LicensePlate from './LicensePlate.vue';

interface Props {
  results: PlateCalculationResult[];
  maxProbability: number;
}

const props = defineProps<Props>();
const { t } = useTranslation();

const isBestMatch = (probability: number): boolean => {
  return probability === props.maxProbability && props.maxProbability > 0;
};

const formatProb = (prob: number) => {
  if (prob === 0) return '0';
  if (prob < 0.01) return '< 0.01';
  return prob.toFixed(2);
};
</script>

<style scoped>
.result-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: 1.5rem;
}

.result-card {
  background: var(--bg-surface);
  border: 1px solid var(--border-subtle);
  border-radius: 8px;
  padding: 1.5rem;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.result-card:hover {
  transform: translateY(-2px);
  border-color: var(--text-dim);
}

.result-card.best-match {
  border: 1px solid var(--color-primary);
  box-shadow: 0 0 0 1px var(--color-primary-dim);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.country-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.country-name {
  font-family: 'Inter', sans-serif;
  font-weight: 600;
  font-size: 0.85rem;
  color: var(--text-main);
  text-transform: uppercase;
}

.probability {
  font-family: 'JetBrains Mono', monospace;
  font-weight: 600;
  color: var(--color-primary);
  font-size: 0.9rem;
}

.card-footer {
  margin-top: 1rem;
  display: flex;
  justify-content: space-between;
  font-size: 0.7rem;
  color: var(--text-dim);
  font-family: 'JetBrains Mono', monospace;
}

@media (max-width: 768px) {
  .result-grid {
    grid-template-columns: 1fr;
  }
}
</style>