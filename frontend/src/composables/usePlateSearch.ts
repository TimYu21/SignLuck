import { ref, watch, type Ref } from 'vue';
import type { PlateCalculationResult } from '../types/plate';

export interface TripSegment {
    country_name: string;
    country_code: string;
    probability: number;
    booking_url: string;
    lat: number;
    lng: number;
}

export function usePlateSearch(lang: Ref<'ru' | 'en'>) {
    const query = ref('');
    const results = ref<PlateCalculationResult[]>([]);
    const routeSegments = ref<TripSegment[]>([]);
    const loading = ref(false);
    const routeLoading = ref(false);
    const maxProbability = ref(0);
    const totalResults = ref(0);
    let debounceTimer: ReturnType<typeof setTimeout> | null = null;

    const search = async () => {
        if (!query.value) {
            results.value = [];
            maxProbability.value = 0;
            totalResults.value = 0;
            return;
        }

        loading.value = true;
        try {
            // Передаем параметр lang на бэкенд
            const response = await fetch(`/api/check?lang=${lang.value}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ query: query.value }),
            });

            const data = await response.json();
            results.value = data.results;
            maxProbability.value = data.max_probability;
            totalResults.value = data.total_results;
        } catch (e) {
            console.error(e);
            results.value = [];
        } finally {
            loading.value = false;
        }
    };

    const fetchRoute = async () => {
        if (!query.value) return;

        routeLoading.value = true;

        // Пытаемся получить геопозицию пользователя
        let coords = {};
        try {
            const pos = await new Promise<GeolocationPosition>((resolve, reject) => {
                navigator.geolocation.getCurrentPosition(resolve, reject, { timeout: 5000 });
            });
            coords = {
                user_lat: pos.coords.latitude,
                user_lng: pos.coords.longitude
            };
        } catch (e) {
            console.warn('Geolocation denied or failed', e);
        }

        try {
            const response = await fetch(`/api/route?lang=${lang.value}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query: query.value, ...coords }),
            });
            const data = await response.json();
            routeSegments.value = data.segments;
        } catch (e) {
            console.error(e);
            routeSegments.value = [];
        } finally {
            routeLoading.value = false;
        }
    };

    const clearSearch = () => {
        query.value = '';
        results.value = [];
        routeSegments.value = [];
    };

    watch(query, () => {
        if (debounceTimer) clearTimeout(debounceTimer);
        debounceTimer = setTimeout(search, 500);
    });

    // При смене языка перезапрашиваем данные, если есть запрос
    watch(lang, () => {
        if (query.value) {
            search();
        }
    });

    return {
        query,
        results,
        loading,
        routeSegments,
        routeLoading,
        maxProbability,
        totalResults,
        clearSearch,
        fetchRoute
    };
}