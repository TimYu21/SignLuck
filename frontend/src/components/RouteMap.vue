<template>
  <div class="route-map-wrapper">
    <div id="route-map" class="map-container"></div>
  </div>
</template>

<script setup lang="ts">
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { onMounted, onUnmounted, watch } from 'vue';
import type { TripSegment } from '../composables/usePlateSearch';
import { useTranslation } from '../composables/useTranslation';

const props = defineProps<{
  segments: TripSegment[];
  lang: 'ru' | 'en';
}>();

const { t, currentLang } = useTranslation();
let map: L.Map | null = null;
let layerGroup: L.LayerGroup | null = null;

const formatProb = (prob: number) => {
  if (prob === 0) return '0';
  if (prob < 0.01) return '< 0.01';
  return prob.toFixed(2);
};

const initMap = () => {
  if (map) return;
  
  // Инициализация карты (центр мира)
  map = L.map('route-map').setView([30, 0], 2);

  // Убираем префикс Leaflet (может содержать флаг в attribution)
  map.attributionControl.setPrefix('');

  L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
    attribution: '&copy; OpenStreetMap contributors &copy; CARTO',
    subdomains: 'abcd',
    maxZoom: 19
  }).addTo(map);

  layerGroup = L.layerGroup().addTo(map);
};

const drawRoute = () => {
  if (!map || !layerGroup) return;
  layerGroup.clearLayers();

  const points: L.LatLngExpression[] = [];

  props.segments.forEach((segment, index) => {
    const latLng: L.LatLngExpression = [segment.lat, segment.lng];
    points.push(latLng);

    // Создаем кастомный маркер
    const markerHtml = `
      <div style="
        background: var(--color-primary);
        width: 24px; height: 24px;
        border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        font-weight: bold; color: black;
        box-shadow: 0 0 10px var(--color-primary);
        border: 2px solid white;
      ">${index + 1}</div>
    `;

    const icon = L.divIcon({
      html: markerHtml,
      className: 'custom-route-marker',
      iconSize: [24, 24],
      iconAnchor: [12, 12]
    });

    const btnText = t('buy_ticket');
    
    const popupContent = `
      <div style="text-align: center; font-family: 'JetBrains Mono', monospace;">
        <h3 style="margin: 0 0 5px 0; color: #333;">${segment.country_name}</h3>
        <div style="color: #666; margin-bottom: 8px;">${t('prob_label')}: ${formatProb(segment.probability)}%</div>
        <a href="${segment.booking_url}" target="_blank" rel="noopener noreferrer" 
           style="display: inline-block; background: #28a745; color: white; padding: 5px 10px; text-decoration: none; border-radius: 4px; font-size: 12px;">
           ${btnText} ✈️
        </a>
      </div>
    `;

    L.marker(latLng, { icon })
      .bindPopup(popupContent)
      .addTo(layerGroup!);
  });

  // Рисуем линии маршрута
  if (points.length > 1) {
    // 1. Фоновая линия для свечения (Glow effect)
    L.polyline(points, {
      color: 'var(--color-primary)',
      weight: 8,
      opacity: 0.2,
      className: 'route-line-glow'
    }).addTo(layerGroup!);

    // 2. Основная анимированная пунктирная линия
    L.polyline(points, {
      color: 'var(--color-primary)',
      weight: 3,
      className: 'route-line-animated'
    }).addTo(layerGroup!);
  }

  // Подгоняем зум под маршрут
  if (points.length > 0) {
    map.fitBounds(L.latLngBounds(points).pad(0.2));
  }
};

onMounted(() => {
  initMap();
  drawRoute();
});

watch(() => props.segments, drawRoute, { deep: true });
watch(currentLang, drawRoute);

onUnmounted(() => {
  if (map) {
    map.remove();
    map = null;
  }
});
</script>

<style scoped>
.route-map-wrapper {
  margin-top: 2rem;
  border: 1px solid var(--border-subtle);
  border-radius: 12px;
  overflow: hidden;
  height: 400px;
  position: relative;
  margin-bottom: 4rem;
}

.map-container {
  width: 100%;
  height: 100%;
  z-index: 1;
}

/* Анимация линий маршрута */
:deep(.route-line-animated) {
  stroke-dasharray: 10, 15;
  stroke-linecap: round;
  animation: dash-flow 2s linear infinite;
  filter: drop-shadow(0 0 2px var(--color-primary));
}

:deep(.route-line-glow) {
  filter: blur(3px);
}

@keyframes dash-flow {
  from { stroke-dashoffset: 25; }
  to { stroke-dashoffset: 0; }
}
</style>