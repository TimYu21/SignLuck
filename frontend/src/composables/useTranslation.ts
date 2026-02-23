import { ref } from 'vue';

const currentLang = ref<'ru' | 'en'>('ru');

const translations = {
    ru: {
        slogan_top: 'ТВОЙ НОМЕР',
        slogan_bottom: 'ТВОЯ УДАЧА',
        status_online: 'СИСТЕМА АКТИВНА',
        search_placeholder: 'ВВЕДИТЕ НОМЕР...',
        search_label: 'ПОИСК',
        search_clear: 'СБРОС',
        stats_total: 'НАЙДЕНО ВАРИАНТОВ',
        stats_prob: 'МАКС. ВЕРОЯТНОСТЬ',
        stats_country: 'СТРАНА С НАИБОЛЬШЕЙ ВЕРОЯТНОСТЬЮ',
        loading: 'АНАЛИЗ ДАННЫХ...',
        no_match: 'НЕТ СОВПАДЕНИЙ',
        no_match_desc: 'НОМЕР НЕ ПОПАДАЕТ ПОД ИМЕЮЩИЕСЯ ПАТТЕРНЫ НОМЕРОВ',
        pattern: 'ФОРМАТ',
        map_legend: 'ВЕРОЯТНОСТЬ',
        prob_label: 'ВЕРОЯТНОСТЬ',
        footer_dev: 'РАЗРАБОТАНО',
        lang_switch: 'EN',
        find_tickets: 'НАЙТИ БИЛЕТЫ',
        buy_ticket: 'КУПИТЬ БИЛЕТ',
        build_route_btn: 'ПОСТРОИТЬ МАРШРУТ УДАЧИ',
        geo_denied: 'ГЕОЛОКАЦИЯ НЕДОСТУПНА. ВЫБЕРИТЕ СТРАНУ ОТПРАВЛЕНИЯ:',
        select_country: 'ВЫБЕРИТЕ СТРАНУ',
        go_btn: 'ПОЕХАЛИ',
        about_btn: 'О ПРОЕКТЕ',
        about_title: 'О ПРОЕКТЕ',
        about_dev: 'Проект разработан Tim Yu. Это Pet-проект, созданный исключительно ради веселья.',
        about_logic_title: 'КАК ЭТО РАБОТАЕТ?',
        about_prob_title: 'РАСЧЕТ ВЕРОЯТНОСТИ',
        about_prob_desc: 'Мы берем шаблон номера конкретной страны (например, 3 буквы и 3 цифры) и считаем общее количество возможных комбинаций. Затем математически вычисляем, сколько из них содержат введенные вами символы. Чем больше вариантов размещения вашего номера в шаблоне, тем выше процент.',
        about_route_title: 'ПОСТРОЕНИЕ МАРШРУТА',
        about_route_desc: 'Система выбирает топ-5 стран с самым высоким шансом встретить ваш номер. Если известна ваша геопозиция, алгоритм строит оптимальный путь: от вас к ближайшей стране, затем к следующей ближайшей ("Метод ближайшего соседа"), чтобы минимизировать расстояние.',
        close_btn: 'ЗАКРЫТЬ'
    },
    en: {
        slogan_top: 'YOUR PLATE',
        slogan_bottom: 'YOUR LUCK',
        status_online: 'SYSTEM ONLINE',
        search_placeholder: 'ENTER PLATE NUMBER...',
        search_label: 'SEARCH',
        search_clear: 'RESET',
        stats_total: 'VARIANTS FOUND',
        stats_prob: 'MAX PROBABILITY',
        stats_country: 'MOST PROBABLE COUNTRY',
        loading: 'ANALYZING DATA...',
        no_match: 'NO MATCH',
        no_match_desc: 'NUMBER NOT RECOGNIZED',
        pattern: 'FORMAT',
        map_legend: 'PROBABILITY',
        prob_label: 'PROBABILITY',
        footer_dev: 'DEV',
        lang_switch: 'RU',
        find_tickets: 'FIND TICKETS',
        buy_ticket: 'BUY TICKET',
        build_route_btn: 'BUILD LUCKY ROUTE',
        geo_denied: 'GEOLOCATION DENIED. SELECT DEPARTURE COUNTRY:',
        select_country: 'SELECT COUNTRY',
        go_btn: 'GO',
        about_btn: 'ABOUT',
        about_title: 'ABOUT PROJECT',
        about_dev: 'Developed by Tim Yu. This is a Pet-project created purely for fun.',
        about_logic_title: 'HOW IT WORKS?',
        about_prob_title: 'PROBABILITY CALCULATION',
        about_prob_desc: 'We take a country\'s license plate format (e.g., 3 letters and 3 digits) and calculate the total number of possible combinations. Then we mathematically count how many of them contain your characters. The more ways your number fits into the pattern, the higher the percentage.',
        about_route_title: 'ROUTE BUILDING',
        about_route_desc: 'The system selects the top 5 countries where you are most likely to see your number. If your location is known, the algorithm builds an optimal route: starting from the country closest to you, then to the next nearest one ("Nearest Neighbor" method) to minimize travel distance.',
        close_btn: 'CLOSE'
    }
};

export function useTranslation() {
    return {
        t: (key: keyof typeof translations['ru']) => translations[currentLang.value][key],
        currentLang,
        toggleLang: () => currentLang.value = currentLang.value === 'ru' ? 'en' : 'ru'
    };
}