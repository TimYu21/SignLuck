<template>
  <div class="trip-route-container">
    <div v-if="loading" class="loading-state">
      ⏳
    </div>
    <transition-group v-else-if="segments.length" name="timeline-item-anim" tag="div" class="timeline">
      <div
        v-for="(segment, idx) in segments" 
        :key="segment.country_code" 
        class="timeline-item"
        :style="{ '--delay': `${idx * 0.1}s` }"
      >
        <div class="timeline-marker">
          <div class="dot"></div>
          <div v-if="idx < segments.length - 1" class="line"></div>
        </div>

        <div class="timeline-content">
          <div class="content-header">
            <span class="country-name">{{ segment.country_name }}</span>
            <span class="probability">{{ formatProb(segment.probability) }}%</span>
          </div>
          <a 
            :href="segment.booking_url" 
            target="_blank" 
            rel="noopener noreferrer" 
            class="buy-btn"
          >
            {{ t('find_tickets') }} <span>✈️</span>
          </a>
        </div>
      </div>
    </transition-group>
  </div>
</template>

<script setup lang="ts">
import type { TripSegment } from '../composables/usePlateSearch';
import { useTranslation } from '../composables/useTranslation';

defineProps<{
  segments: TripSegment[];
  loading: boolean;
  lang: 'ru' | 'en';
}>();

const { t } = useTranslation();

const formatProb = (prob: number) => {
  if (prob === 0) return '0';
  if (prob < 0.01) return '< 0.01';
  return prob.toFixed(2);
};
</script>

<style scoped>
.trip-route-container {
  margin-top: 2rem;
  padding: 0;
  background: rgba(255, 255, 255, 0.02);
  backdrop-filter: blur(10px);
  border: 1px solid var(--border-subtle);
  border-radius: 12px;
}

.loading-state {
  text-align: center;
  font-size: 2rem;
  padding: 2rem;
  color: var(--text-dim);
}

.timeline {
  display: flex;
  flex-direction: column;
}

.timeline-item {
  display: flex;
  position: relative;
  padding: 1rem 1.5rem;
  opacity: 0;
  transform: translateX(-20px);
  animation: slide-in 0.5s ease-out forwards;
  animation-delay: var(--delay);
}

.timeline-item:not(:last-child) {
  border-bottom: 1px solid var(--border-subtle);
}

.timeline-marker {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-right: 1.5rem;
}

.dot {
  width: 14px;
  height: 14px;
  background: var(--color-primary);
  border-radius: 50%;
  border: 2px solid var(--bg-main);
  box-shadow: 0 0 8px var(--color-primary);
  z-index: 1;
  flex-shrink: 0;
}

.line {
  flex-grow: 1;
  width: 2px;
  background: linear-gradient(to bottom, var(--color-primary), transparent);
}

.timeline-content {
  flex-grow: 1;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
}

.content-header {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.country-name {
  font-family: 'Inter', sans-serif;
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--text-main);
  text-transform: uppercase;
}

.probability {
  font-family: 'JetBrains Mono', monospace;
  font-weight: bold;
  color: var(--color-primary);
  font-size: 0.9rem;
}

.buy-btn {
  display: inline-block;
  padding: 8px 16px;
  background: var(--color-primary-dim);
  border: 1px solid var(--color-primary);
  color: var(--color-primary);
  text-decoration: none;
  border-radius: 4px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: uppercase;
  transition: all 0.2s;
  white-space: nowrap;
}

.buy-btn:hover {
  background: var(--color-primary);
  color: #000;
  box-shadow: 0 0 15px var(--color-primary);
  transform: scale(1.05);
}

.buy-btn span {
  display: inline-block;
  transition: transform 0.2s;
}

.buy-btn:hover span {
  transform: translateX(3px);
}

@keyframes slide-in {
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

@media (max-width: 600px) {
  .timeline-content {
    flex-direction: column;
    align-items: stretch;
  }

  .buy-btn {
    text-align: center;
  }
}
</style>