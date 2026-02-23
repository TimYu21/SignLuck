<template>
  <div class="signluck-app">
    <div class="background-fx">
      <div class="grid-overlay"></div>
    </div>

    <header class="top-bar">
      <div class="container header-grid">
        <div class="brand">
          <div class="logo-group">
            <h1 class="logo">SIGNLUCK</h1>
            <div class="brand-slogan">
              <span>{{ t('slogan_top') }}</span>
              <span>{{ t('slogan_bottom') }}</span>
            </div>
          </div>
        </div>

        <div class="search-area">
          <SearchInput v-model="query" :loading="loading" @clear="clearSearch" />
          
          <!-- Блок подсказок -->
          <div class="suggestions-bar" v-if="suggestions.length > 0">
            <span class="suggestion-label">{{ t('try_also') || (currentLang === 'ru' ? 'Попробуйте также:' : 'Try also:') }}</span>
            <button v-for="s in suggestions" :key="s" class="suggestion-chip" @click="applySuggestion(s)">
              {{ s }}
            </button>
          </div>
        </div>

        <div class="header-controls">
          <button class="nav-btn" @click="showAbout = true">
            {{ t('about_btn') }}
          </button>

          <div class="lang-dropdown">
            <button class="lang-btn" @click="isLangMenuOpen = !isLangMenuOpen">
              {{ currentLang.toUpperCase() }} <span class="arrow">▼</span>
            </button>
            <div class="lang-menu" v-if="isLangMenuOpen">
              <div class="lang-option" :class="{ active: currentLang === 'ru' }" @click="setLang('ru')">RU</div>
              <div class="lang-option" :class="{ active: currentLang === 'en' }" @click="setLang('en')">EN</div>
            </div>
          </div>
        </div>
      </div>
    </header>

    <main class="content-wrapper">
      <div class="container">
        <SearchStats 
          v-if="results && results.length > 0"
          :total="totalResults"
          :max-probability="maxProbability"
          :results="results"
        />

        <div class="route-actions" v-if="results && results.length > 0">
          <div v-if="!isLocationDenied">
            <button class="action-btn" @click="handleRouteClick" :disabled="routeLoading">
              {{ t('build_route_btn') }} ✈️
            </button>
          </div>
          
          <div v-else class="manual-location-selector">
            <p class="manual-text">{{ t('geo_denied') }}</p>
            <div class="select-group">
              <select v-model="selectedCountryCode" class="country-select">
                <option value="" disabled selected>{{ t('select_country') }}</option>
                <option v-for="c in countries" :key="c.country_code" :value="c.country_code">
                  {{ c.flag_emoji }} {{ c.country_name }}
                </option>
              </select>
              <button class="action-btn small" @click="buildRouteManual" :disabled="!selectedCountryCode || manualLoading">
                {{ manualLoading ? '...' : t('go_btn') }}
              </button>
            </div>
          </div>
        </div>

        <TripRoute 
          v-if="routeSegments.length > 0 || routeLoading || manualLoading"
          :segments="routeSegments"
          :loading="routeLoading || manualLoading"
          :lang="currentLang"
        />

        <RouteMap
          v-if="routeSegments.length > 0"
          :segments="routeSegments"
          :lang="currentLang"
        />

        <ProbabilityMap 
          v-else-if="results && results.length > 0"
          :results="results"
        />

        <div class="results-container">
          <transition name="neon-fade" mode="out-in">
            <div v-if="loading" class="loading-state">
              <div class="loader-bar"></div>
              <p class="loading-text">{{ t('loading') }}</p>
            </div>
            
            <ResultGrid 
              v-else-if="results && results.length > 0"
              :results="results"
              :max-probability="maxProbability"
            />
            
            <div v-else-if="query" class="no-results">
              <div class="no-match-icon">⊘</div>
              <p class="error-sub">{{ t('no_match_desc') }}</p>
            </div>
          </transition>
        </div>
      </div>
    </main>

    <footer class="main-footer">
      <div class="container footer-content">
        <div class="version">SYSTEM V.1.0.0</div>
        <div class="author-tag">{{ t('footer_dev') }} <span class="highlight">TIM YU</span></div>
      </div>
    </footer>

    <AboutModal v-if="showAbout" @close="showAbout = false" />
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, watch } from 'vue';
import AboutModal from './components/AboutModal.vue';
import ProbabilityMap from './components/ProbabilityMap.vue';
import ResultGrid from './components/ResultGrid.vue';
import RouteMap from './components/RouteMap.vue';
import SearchInput from './components/SearchInput.vue';
import SearchStats from './components/SearchStats.vue';
import TripRoute from './components/TripRoute.vue';
import { usePlateSearch } from './composables/usePlateSearch';
import { useTranslation } from './composables/useTranslation';

const { t, currentLang } = useTranslation();

// Подключаем логику из твоего композабла
const { 
  query, 
  results, 
  loading, 
  routeSegments,
  routeLoading,
  maxProbability, 
  totalResults, 
  clearSearch,
  fetchRoute
} = usePlateSearch(currentLang);

// --- Логика ручного выбора страны (если нет гео) ---
interface Country {
  country_code: string;
  country_name: string;
  lat: number;
  lng: number;
  flag_emoji: string;
}

const countries = ref<Country[]>([]);
const isLocationDenied = ref(false);
const selectedCountryCode = ref('');
const manualLoading = ref(false);

const loadCountries = async () => {
  try {
    const res = await fetch('/api/countries');
    if (res.ok) {
      countries.value = await res.json();
      countries.value.sort((a, b) => a.country_name.localeCompare(b.country_name));
    }
  } catch (e) {
    console.error('Failed to load countries:', e);
  }
};

const handleRouteClick = () => {
  if (!navigator.geolocation) {
    isLocationDenied.value = true;
    if (countries.value.length === 0) loadCountries();
    return;
  }

  navigator.geolocation.getCurrentPosition(
    () => fetchRoute(),
    () => {
      isLocationDenied.value = true;
      if (countries.value.length === 0) loadCountries();
    }
  );
};

const buildRouteManual = async () => {
  if (!selectedCountryCode.value) return;
  const country = countries.value.find(c => c.country_code === selectedCountryCode.value);
  if (!country) return;

  manualLoading.value = true;
  try {
    const response = await fetch(`/api/route?lang=${currentLang.value}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query: query.value, user_lat: country.lat, user_lng: country.lng })
    });
    if (response.ok) {
      const data = await response.json();
      routeSegments.value = data.segments;
    }
  } catch (e) {
    console.error(e);
  } finally {
    manualLoading.value = false;
    isLocationDenied.value = false;
  }
};

// --- Логика подсказок (Suggestions) ---
const suggestions = ref<string[]>([]);

const generateSuggestions = (input: string) => {
  const replacements: Record<string, string> = {
    'O': '0', 'I': '1', 'Z': '2', 'E': '3', 'S': '5', 'B': '8'
  };
  
  const results = new Set<string>();
  
  const backtrack = (index: number, current: string) => {
    if (index === input.length) {
      if (current !== input) results.add(current);
      return;
    }
    const char = input[index];
    // Вариант 1: оставляем как есть
    backtrack(index + 1, current + char);
    // Вариант 2: заменяем, если есть на что
    if (replacements[char]) {
      backtrack(index + 1, current + replacements[char]);
    }
  };

  backtrack(0, '');
  return Array.from(results).sort().slice(0, 5);
};

watch(query, (newVal) => {
  suggestions.value = newVal ? generateSuggestions(newVal) : [];
});

watch(currentLang, (newLang, oldLang) => {
  // Если язык изменился и маршрут уже был построен, перезапрашиваем его
  if (newLang !== oldLang && routeSegments.value.length > 0) {
    fetchRoute();
  }
});

const applySuggestion = (s: string) => {
  query.value = s;
};

const showAbout = ref(false);
const isLangMenuOpen = ref(false);

const setLang = (lang: 'ru' | 'en') => {
  currentLang.value = lang;
  isLangMenuOpen.value = false;
};

const currentTime = ref('');

// Обновление времени для "бортового компьютера" и метаданных страницы
onMounted(() => {
  document.title = 'Sign Luck';

  // Установка favicon (клевер удачи)
  const link = document.querySelector("link[rel*='icon']") || document.createElement('link');
  (link as HTMLLinkElement).type = 'image/svg+xml';
  (link as HTMLLinkElement).rel = 'icon';
  (link as HTMLLinkElement).href = "data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>🍀</text></svg>";
  document.head.appendChild(link);

  currentTime.value = new Date().toLocaleTimeString('en-GB');
  setInterval(() => {
    currentTime.value = new Date().toLocaleTimeString('en-GB');
  }, 1000);
});
</script>

<style scoped>
.signluck-app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  position: relative;
  overflow-x: hidden;
}

.background-fx {
  position: fixed;
  inset: 0;
  z-index: 0;
  background: var(--bg-main);
  pointer-events: none;
}

.grid-overlay {
  position: absolute;
  inset: 0;
  background-image: 
    linear-gradient(rgba(255, 255, 255, 0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255, 255, 255, 0.03) 1px, transparent 1px);
  background-size: 40px 40px;
  mask-image: radial-gradient(circle at center, black 40%, transparent 100%);
}

.top-bar {
  position: sticky;
  top: 0;
  z-index: 100;
  background: rgba(9, 9, 11, 0.8);
  backdrop-filter: var(--glass-blur);
  border-bottom: 1px solid var(--border-subtle);
  padding: 0.8rem 0;
}

.header-grid {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  align-items: center;
  gap: 1rem;
}

.brand { justify-self: start; }
.search-area { width: 100%; max-width: 500px; min-width: 300px; justify-self: center; }
.header-controls { justify-self: end; align-self: start; padding-top: 10px; display: flex; gap: 1rem; align-items: center; }

.logo {
  font-family: 'JetBrains Mono', monospace;
  font-weight: 800;
  font-size: 1.2rem;
  margin: 0;
  letter-spacing: -1px;
  color: var(--text-main);
  text-shadow: 0 0 10px var(--color-primary);
}

.logo-group {
  display: flex;
  flex-direction: column;
  gap: 4px;
  text-align: left;
}

.brand-slogan {
  display: flex;
  flex-direction: column;
  font-size: 0.65rem;
  color: var(--color-primary);
  font-family: 'JetBrains Mono', monospace;
  font-weight: 600;
  line-height: 1.2;
  letter-spacing: 0.5px;
  text-shadow: 0 0 5px var(--color-primary);
}

.nav-btn {
  background: transparent;
  border: none;
  color: var(--text-dim);
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.8rem;
  cursor: pointer;
  transition: color 0.2s;
  padding: 0;
}

.nav-btn:hover {
  color: var(--color-primary);
  text-shadow: 0 0 8px var(--color-primary);
}

.lang-dropdown {
  position: relative;
}

.lang-btn {
  background: transparent;
  border: 1px solid var(--border-subtle);
  color: var(--text-dim);
  padding: 6px 10px;
  border-radius: 4px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.8rem;
  cursor: pointer;
  transition: all 0.2s;
  min-width: 60px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 6px;
}

/* Suggestions Styles */
.suggestions-bar {
  display: flex;
  gap: 8px;
  margin-top: 8px;
  flex-wrap: wrap;
  justify-content: center;
}

.suggestion-label {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.7rem;
  color: var(--text-dim);
  align-self: center;
}

.suggestion-chip {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid var(--border-subtle);
  color: var(--color-primary);
  padding: 2px 8px;
  border-radius: 12px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.75rem;
  cursor: pointer;
  transition: all 0.2s;
}

.suggestion-chip:hover {
  background: var(--color-primary-dim);
  border-color: var(--color-primary);
}

.arrow {
  font-size: 0.6rem;
}

.lang-menu {
  position: absolute;
  top: 100%;
  right: 0;
  margin-top: 4px;
  background: var(--bg-surface);
  border: 1px solid var(--border-subtle);
  border-radius: 4px;
  overflow: hidden;
  min-width: 100%;
  z-index: 10;
}

.lang-option {
  padding: 6px 12px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.8rem;
  color: var(--text-dim);
  cursor: pointer;
  text-align: center;
}

.lang-btn:hover {
  border-color: var(--color-primary);
  color: var(--color-primary);
}

.lang-option:hover, .lang-option.active {
  background: var(--border-subtle);
  color: var(--text-main);
}

.content-wrapper {
  position: relative;
  z-index: 1;
  flex: 1;
  padding: 3rem 0;
}

.loading-state {
  text-align: center;
  padding: 5rem 0;
  color: var(--text-dim);
}

.loader-bar {
  width: 40px;
  height: 4px;
  background: var(--color-primary);
  margin: 0 auto 1rem;
  animation: pulse 1s infinite alternate;
}

.loading-text {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.8rem;
  letter-spacing: 1px;
}

@keyframes pulse { 
  from { opacity: 0.4; width: 20px; } 
  to { opacity: 1; width: 60px; } 
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
}

.main-footer {
  padding: 1.5rem 0;
  border-top: 1px solid var(--border-subtle);
  background: var(--bg-main);
  position: relative;
  z-index: 10;
}

.footer-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.75rem;
  color: var(--text-dim);
  font-family: 'JetBrains Mono', monospace;
}

.clock {
  color: var(--text-main);
}

.highlight {
  color: var(--color-primary);
}

.no-results {
  text-align: center;
  padding: 4rem 2rem;
  border: 1px dashed var(--border-subtle);
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.01);
}

.no-match-icon {
  font-size: 3rem;
  color: var(--border-subtle);
  margin-bottom: 1rem;
}

.error-sub {
  color: var(--text-dim);
  font-size: 0.9rem;
}

.route-actions {
  display: flex;
  justify-content: center;
  margin: 1.5rem 0;
}

.action-btn {
  background: var(--color-primary);
  color: #000;
  border: none;
  padding: 0.8rem 1.5rem;
  font-family: 'JetBrains Mono', monospace;
  font-weight: bold;
  cursor: pointer;
  border-radius: 4px;
  transition: all 0.2s;
  text-transform: uppercase;
  letter-spacing: 1px;
  box-shadow: 0 0 10px var(--color-primary);
}

.action-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 0 20px var(--color-primary);
}

.action-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.manual-location-selector {
  background: rgba(255, 255, 255, 0.05);
  padding: 1rem;
  border-radius: 8px;
  border: 1px solid var(--border-subtle);
  text-align: center;
  animation: fadeIn 0.3s ease;
}

.manual-text {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.8rem;
  color: var(--text-dim);
  margin-bottom: 0.8rem;
}

.select-group {
  display: flex;
  gap: 0.5rem;
  justify-content: center;
  flex-wrap: wrap;
}

.country-select {
  background: var(--bg-surface);
  color: var(--text-main);
  border: 1px solid var(--border-subtle);
  padding: 0.5rem;
  border-radius: 4px;
  font-family: 'Inter', sans-serif;
  min-width: 200px;
}

.action-btn.small {
  padding: 0.5rem 1rem;
  font-size: 0.8rem;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-10px); }
  to { opacity: 1; transform: translateY(0); }
}

@media (max-width: 1024px) {
  .header-grid { 
    grid-template-columns: 1fr auto;
    grid-template-areas: 
      "brand controls"
      "search search";
    gap: 1rem; 
  }
  
  .brand { grid-area: brand; }
  .header-controls { grid-area: controls; justify-self: end; }
  .search-area { grid-area: search; width: 100%; max-width: none; min-width: 0; justify-self: stretch; }
}
</style>