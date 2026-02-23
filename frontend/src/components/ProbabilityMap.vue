<template>
  <div class="map-wrapper">
    <div id="map" ref="mapContainer"></div>
  </div>
</template>

<script setup lang="ts">
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { onMounted, onUnmounted, ref, watch } from 'vue';
import { useTranslation } from '../composables/useTranslation';
import type { PlateCalculationResult } from '../types/plate';

const props = defineProps<{
  results: PlateCalculationResult[];
}>();

const { t } = useTranslation();
const mapContainer = ref<HTMLElement | null>(null);
let map: L.Map | null = null;
let geoJsonLayer: L.GeoJSON | null = null;
let geoJsonData: any = null;

// URL для GeoJSON с границами стран (Natural Earth low res)
const GEOJSON_URL = 'https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_110m_admin_0_countries.geojson';

// Функция для получения цвета заливки в зависимости от вероятности
const getColor = (probability: number) => {
  if (probability >= 0.8) return '#f59e0b';
  if (probability >= 0.6) return '#cc8b1f';
  if (probability >= 0.4) return '#a37833';
  if (probability >= 0.2) return '#7a6547';
  return '#52525b';
};

const initMap = async () => {
  if (!mapContainer.value) return;

  map = L.map(mapContainer.value, {
    zoomControl: false,
    attributionControl: false,
    center: [20, 0],
    zoom: 2
  });

  // Добавляем атрибуцию (хороший тон)
  L.control.attribution({ prefix: false }).addAttribution('&copy; OpenStreetMap, &copy; CARTO, &copy; Natural Earth').addTo(map);

  // Используем темную тему карты (CartoDB Dark Matter) для соответствия стилю сайта
  L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
    subdomains: 'abcd',
    maxZoom: 19
  }).addTo(map);

  // Добавляем легенду
  const Legend = L.Control.extend({
    onAdd: () => {
      const div = L.DomUtil.create('div', 'map-legend');
      div.innerHTML = `
        <div class="legend-title">${t('map_legend')}</div>
        <div class="legend-item">
          <span class="legend-dot" style="background: #f59e0b"></span>
          <span>> 0.8%</span>
        </div>
        <div class="legend-item">
          <span class="legend-dot" style="background: #cc8b1f"></span>
          <span>0.6 - 0.8%</span>
        </div>
        <div class="legend-item">
          <span class="legend-dot" style="background: #a37833"></span>
          <span>0.4 - 0.6%</span>
        </div>
        <div class="legend-item">
          <span class="legend-dot" style="background: #7a6547"></span>
          <span>0.2 - 0.4%</span>
        </div>
        <div class="legend-item">
          <span class="legend-dot" style="background: #52525b"></span>
          <span>< 0.2%</span>
        </div>
      `;
      return div;
    }
  });
  new Legend({ position: 'bottomright' }).addTo(map);

  try {
    const response = await fetch(GEOJSON_URL);
    if (!response.ok) throw new Error('Failed to load GeoJSON');
    geoJsonData = await response.json();
    updateMapLayer();
  } catch (e) {
    console.error('Error loading map data:', e);
  }
};

const updateMapLayer = () => {
  if (!map || !geoJsonData) return;

  // Удаляем старый слой если есть
  if (geoJsonLayer) {
    map.removeLayer(geoJsonLayer);
  }

  geoJsonLayer = L.geoJSON(geoJsonData, {
    style: (feature) => {
      const isoCode = feature?.properties?.ISO_A2;
      const result = props.results.find(r => r.country_code === isoCode);

      if (result) {
        return {
          fillColor: getColor(result.probability),
          weight: 1,
          opacity: 1,
          color: 'rgba(255, 255, 255, 0.2)',
          fillOpacity: 0.6
        };
      }

      // Для стран без совпадений - делаем их прозрачными
      return {
        fillColor: 'transparent',
        weight: 0,
        opacity: 0,
        fillOpacity: 0
      };
    },
    onEachFeature: (feature, layer) => {
      const isoCode = feature?.properties?.ISO_A2;
      const result = props.results.find(r => r.country_code === isoCode);

      if (result) {
        const { probability, country_name, flag_emoji } = result;
        
        const popupContent = `
          <div class="map-popup-content">
            <div class="popup-flag">${flag_emoji || ''}</div>
            <div class="popup-country">${country_name}</div>
            <div class="popup-prob">${t('prob_label')}: ${probability < 0.01 ? '< 0.01' : probability.toFixed(2)}%</div>
          </div>
        `;

        layer.bindTooltip(popupContent, {
          permanent: false,
          direction: 'top',
          className: 'map-tooltip',
          sticky: true,
          opacity: 1
        });
        
        layer.on('mouseover', function (this: L.Layer) {
          // @ts-ignore
          this.setStyle({ fillOpacity: 0.8, weight: 2, color: '#fff' });
        });
        layer.on('mouseout', function (this: L.Layer) {
          // @ts-ignore
          this.setStyle({ fillOpacity: 0.6, weight: 1, color: 'rgba(255, 255, 255, 0.2)' });
        });
      }
    }
  }).addTo(map);

  // Если есть результаты, зумим к ним
  if (props.results.length > 0) {
    const group = L.featureGroup();
    geoJsonLayer.eachLayer((layer: any) => {
       const isoCode = layer.feature?.properties?.ISO_A2;
       if (props.results.find(r => r.country_code === isoCode)) {
         group.addLayer(layer);
       }
    });
    
    if (group.getLayers().length > 0) {
      map.fitBounds(group.getBounds(), { padding: [50, 50], maxZoom: 6 });
    }
  } else {
    map.setView([20, 0], 2);
  }
};

watch(() => props.results, () => {
  updateMapLayer();
}, { deep: true });

onMounted(() => {
  initMap();
});

onUnmounted(() => {
  if (map) {
    map.remove();
    map = null;
  }
});
</script>

<style scoped>
.map-wrapper {
  height: 400px;
  width: 100%;
  border: 1px solid var(--border-subtle);
  border-radius: 8px;
  overflow: hidden;
  margin-bottom: 4rem;
  position: relative;
  z-index: 0; /* Чтобы карта была под модальными окнами, если они появятся */
}

#map {
  height: 100%;
  width: 100%;
  background: #050505;
}

/* Стилизация тултипов Leaflet */
:deep(.map-tooltip) {
  background: var(--bg-surface);
  color: var(--text-main);
  border: 1px solid var(--border-subtle);
  border-radius: 4px;
  font-family: 'JetBrains Mono', monospace;
  padding: 0.5rem 1rem;
  text-align: center;
  box-shadow: 0 4px 12px rgba(0,0,0,0.5);
}

:deep(.popup-flag) {
  font-size: 2rem;
  line-height: 1;
  margin-bottom: 0.2rem;
}

:deep(.popup-country) {
  font-weight: bold;
  text-transform: uppercase;
  color: var(--text-main);
  margin-bottom: 0.2rem;
}

:deep(.popup-prob) {
  font-size: 0.8rem;
  color: var(--color-primary);
  font-weight: bold;
}

:deep(.leaflet-control-attribution) {
  background: rgba(0,0,0,0.5) !important;
  color: #aaa;
  font-size: 0.6rem;
}
:deep(.leaflet-control-attribution a) {
  color: var(--text-dim);
  text-decoration: none;
}

:deep(.map-legend) {
  background: var(--bg-surface);
  border: 1px solid var(--border-subtle);
  border-radius: 4px;
  padding: 8px 12px;
  color: var(--text-main);
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.7rem;
  margin-right: 10px;
  margin-bottom: 10px;
}

:deep(.legend-title) {
  font-weight: bold;
  margin-bottom: 6px;
  color: var(--text-dim);
  text-align: center;
  letter-spacing: 1px;
}

:deep(.legend-item) {
  display: flex;
  align-items: center;
  margin-bottom: 4px;
}

:deep(.legend-dot) {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  margin-right: 8px;
  display: inline-block;
}

:deep(.legend-dot.high) { background-color: var(--color-primary); }
:deep(.legend-dot.low) { background-color: #52525b; }
</style>
