<template>
  <div class="plate-container" :class="{ 'highlighted': isHighLighted }">
    <div class="plate-frame">
      <div class="plate-content">
        <div class="plate-text">
          <!-- Если есть примеры, показываем их с анимацией -->
          <span v-if="currentExample.length > 0" class="dynamic-text">
            <span 
              v-for="(char, idx) in currentExample" 
              :key="idx"
              :class="{ 'dimmed': !char.is_query }"
            >{{ char.value }}</span>
          </span>
          <!-- Иначе показываем статический шаблон (fallback) -->
          <span v-else>
            <span 
              v-for="(symbol, idx) in result.symbols" 
              :key="idx"
              :class="{ 'fixed-char': symbol.is_fixed }"
            >
              {{ symbol.value }}
            </span>
          </span>
        </div>
        
        <!-- Унифицированный бейдж -->
        <div class="plate-badge">
          <span class="flag-emoji">{{ result.flag_emoji }}</span>
          <span class="country-code">{{ result.country_code }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref, watch } from 'vue';
import type { PlateCalculationResult } from '../types/plate';

const props = defineProps<{
  result: PlateCalculationResult;
  isHighLighted: boolean;
}>();

const currentExample = ref<Array<{ value: string; is_query: boolean }>>([]);
let intervalId: number | null = null;
let currentIndex = 0;

const startAnimation = () => {
  if (props.result.examples && props.result.examples.length > 0) {
    currentExample.value = props.result.examples[0];
    
    if (props.result.examples.length > 1) {
      intervalId = window.setInterval(() => {
        currentIndex = (currentIndex + 1) % props.result.examples.length;
        currentExample.value = props.result.examples[currentIndex];
      }, 800); // Меняем пример каждые 800мс
    }
  } else {
    // Fallback если примеров нет
    currentExample.value = [];
  }
};

watch(() => props.result, () => {
  if (intervalId) clearInterval(intervalId);
  currentIndex = 0;
  startAnimation();
});

onMounted(() => {
  startAnimation();
});

onUnmounted(() => {
  if (intervalId) clearInterval(intervalId);
});
</script>

<style scoped>
.plate-container {
  display: flex;
  justify-content: center;
  padding: 0.5rem 0;
}

.plate-frame {
  background: #f0f0f0;
  border: 2px solid #000;
  border-radius: 8px;
  padding: 2px;
  box-shadow: 0 2px 5px rgba(0,0,0,0.5);
  min-width: 200px;
  display: inline-block;
}

.highlighted .plate-frame {
  box-shadow: 0 0 15px var(--neon-cyan);
  border-color: var(--accent-blue);
}

.plate-content {
  border: 1px solid #333;
  border-radius: 4px;
  background: white;
  color: black;
  padding: 0.2rem 0.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  position: relative;
  min-width: 240px;
  height: 50px;
}

.plate-text {
  font-family: 'Courier New', monospace; /* В идеале нужен шрифт номера */
  font-weight: 900;
  font-size: 2rem;
  letter-spacing: 2px;
  text-transform: uppercase;
  flex-grow: 1;
  text-align: center;
}

.dynamic-text {
  animation: text-flicker 0.1s ease-in-out;
}

.fixed-char {
  color: #000;
}

.dimmed {
  color: rgba(0, 0, 0, 0.3);
}

.plate-badge {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 100%;
  padding: 0 5px;
  border-left: 2px solid #000;
  margin-left: 10px;
  min-width: 35px;
}

.country-code {
  font-size: 0.7rem;
  font-weight: bold;
  line-height: 1;
  margin-top: 2px;
}


.flag-emoji {
  font-size: 1.2rem;
  line-height: 1;
}
</style>