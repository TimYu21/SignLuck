import logging
import random
from typing import Dict, List, Optional, Set

from app.schemas.country import CountrySchema
from app.schemas.plate import (
    PlateCalculationResult,
    PlateExampleSymbol,
    PlateVisualSymbol,
)

logger = logging.getLogger(__name__)


class PlateCalculator:
    """
    Сервис расчёта вероятности с поддержкой всех допустимых размещений запроса.

    Использует комбинаторику для подсчета общего числа вариантов номера
    и числа выигрышных вариантов, где встречается подстрока пользователя.
    """

    DIGITS_COUNT = 10

    def calculate_probability(
        self, query: str, country: CountrySchema
    ) -> PlateCalculationResult | None:
        """Основной метод расчета вероятности.

        Args:
            query: Строка запроса (например, "777").
            country: Объект страны с шаблоном номера.

        Returns:
            PlateCalculationResult или None, если совпадений нет.
        """
        query = query.upper()
        pattern = country.pattern.upper()
        allowed = country.allowed_letters.upper()

        matches = self._find_all_matches(query, pattern, allowed)
        if not matches:
            return None

        # Расчет общего количества комбинаций
        total_combinations = self._calculate_total_combinations(pattern, allowed)

        winning_combinations = 0
        examples = []
        seen_examples_str: Set[str] = set()

        for match in matches:
            # Подсчет вариантов для свободных слотов в текущем размещении
            match_combinations = self._calculate_match_combinations(
                match, pattern, allowed
            )
            winning_combinations += match_combinations

            if len(examples) < 5:
                ex_symbols = self._generate_example(match, query, pattern, allowed)
                ex_str = "".join(s.value for s in ex_symbols)
                if ex_str not in seen_examples_str:
                    examples.append(ex_symbols)
                    seen_examples_str.add(ex_str)

        # Генерация дополнительных примеров для визуализации, если их мало
        if matches and len(examples) < 5 and winning_combinations > len(matches):
            for _ in range(10):
                if len(examples) >= 5:
                    break
                random_match = random.choice(matches)
                new_ex_symbols = self._generate_example(
                    random_match, query, pattern, allowed
                )
                new_ex_str = "".join(s.value for s in new_ex_symbols)
                if new_ex_str not in seen_examples_str:
                    examples.append(new_ex_symbols)
                    seen_examples_str.add(new_ex_str)

        probability = (
            (winning_combinations / total_combinations * 100)
            if total_combinations > 0
            else 0.0
        )
        probability = min(probability, 100.0)

        # Карта соответствия индексов шаблона и запроса
        pattern_to_query_map: Dict[int, Set[int]] = {
            i: set() for i in range(len(pattern))
        }
        for match in matches:
            for query_idx, pattern_idx in enumerate(match):
                pattern_to_query_map[pattern_idx].add(query_idx)

        # Формирование визуального представления
        primary_match = matches[0]
        symbols: List[PlateVisualSymbol] = []
        for i, p_char in enumerate(pattern):
            is_fixed_in_primary = i in primary_match
            value = query[primary_match.index(i)] if is_fixed_in_primary else p_char

            symbols.append(
                PlateVisualSymbol(
                    value=value,
                    is_fixed=is_fixed_in_primary,
                    possible_query_indices=sorted(list(pattern_to_query_map[i])),
                )
            )

        return PlateCalculationResult(
            country_name=country.country_name,
            country_code=country.country_code,
            lat=country.lat,
            lng=country.lng,
            probability=probability,
            symbols=symbols,
            allowed_letters=allowed,
            pattern=pattern,
            flag_emoji=country.flag_emoji,
            examples=examples[:10],
        )

    def _get_options_count(self, char: str, allowed: str) -> int:
        """Возвращает количество вариантов для одного символа шаблона."""
        if char == "A":
            return len(allowed) if allowed else 26
        if char == "0":
            return self.DIGITS_COUNT
        return 1

    def _calculate_total_combinations(self, pattern: str, allowed: str) -> int:
        """Считает общее пространство вариантов для шаблона."""
        total = 1
        for char in pattern:
            total *= self._get_options_count(char, allowed)
        return total

    def _calculate_match_combinations(
        self, match_indices: List[int], pattern: str, allowed: str
    ) -> int:
        """
        Считает комбинации для конкретного наложения, варьируя только свободные слоты.

        Args:
            match_indices: Индексы шаблона, которые 'заняты' запросом.
        """
        combinations = 1
        for i, char in enumerate(pattern):
            if i not in match_indices:
                combinations *= self._get_options_count(char, allowed)
        return combinations

    def _generate_example(
        self, match_indices: List[int], query: str, pattern: str, allowed: str
    ) -> List[PlateExampleSymbol]:
        """Генерирует случайный валидный номер для данного совпадения."""
        result = []
        query_ptr = 0

        for i, p_char in enumerate(pattern):
            if i in match_indices:
                # Символ из запроса
                k = match_indices.index(i)
                result.append(PlateExampleSymbol(value=query[k], is_query=True))
            else:
                # Свободный слот, случайная генерация
                char_val = p_char
                if p_char == "A":
                    letters = allowed if allowed else "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
                    char_val = random.choice(letters)
                elif p_char == "0":
                    char_val = str(random.randint(0, 9))

                result.append(PlateExampleSymbol(value=char_val, is_query=False))

        return result

    def _is_char_matching(self, q_char: str, p_char: str, allowed: str) -> bool:
        if p_char == "A":
            return q_char.isalpha() and q_char in allowed
        if p_char == "0":
            return q_char.isdigit()
        return q_char == p_char

    def _find_all_matches(
        self, query: str, pattern: str, allowed: str
    ) -> List[List[int]]:
        """
        Находит ВСЕ допустимые размещения запроса в шаблоне.

        Алгоритм пытается "приложить" query к pattern, начиная с разных позиций,
        учитывая пропуски символов шаблона (например, пробелов или дефисов).

        Returns:
            List[List[int]]: Список вариантов. Каждый вариант - это список индексов
            шаблона, которые соответствуют символам запроса.
        """

        results: List[List[int]] = []

        def backtrack(q_idx: int, p_idx: int, current: List[int]) -> None:
            if q_idx == len(query):
                results.append(current.copy())
                return
            if p_idx == len(pattern):
                return

            # Попытка сопоставления
            if self._is_char_matching(query[q_idx], pattern[p_idx], allowed):
                backtrack(q_idx + 1, p_idx + 1, current + [p_idx])

            # Пропуск символа шаблона
            backtrack(q_idx, p_idx + 1, current)

        backtrack(0, 0, [])
        return results
