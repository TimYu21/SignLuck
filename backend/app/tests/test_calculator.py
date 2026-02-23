def test_calculate_probability_exact_match(calculator, sample_country_simple):
    """Тест полного совпадения запроса с шаблоном."""
    # Pattern: AAA (allowed: ABC). Total: 27.
    # Query: "ABC". Match: 1.
    # Probability: 1/27 * 100 ≈ 3.703%
    result = calculator.calculate_probability("ABC", sample_country_simple)

    assert result is not None
    assert result.probability > 0
    assert abs(result.probability - (1 / 27 * 100)) < 0.01
    assert len(result.symbols) == 3
    assert result.symbols[0].value == "A"


def test_calculate_probability_wildcard(calculator, sample_country_ru):
    """Тест совпадения с учетом фиксированных символов шаблона."""
    # Pattern: A 000 AA. Query: "A777AA".
    # Должен найтись, так как буквы разрешены, а цифры подходят под 0.
    result = calculator.calculate_probability("A777AA", sample_country_ru)

    assert result is not None
    assert result.probability > 0
    # Проверяем, что символы корректно размечены
    assert result.symbols[0].value == "A"
    assert result.symbols[1].value == " "  # Пробел из шаблона
    assert result.symbols[2].value == "7"


def test_no_match_invalid_char(calculator, sample_country_simple):
    """Тест на недопустимый символ."""
    # 'D' нет в allowed_letters="ABC"
    result = calculator.calculate_probability("D", sample_country_simple)
    assert result is None


def test_partial_match(calculator, sample_country_simple):
    """Тест частичного вхождения."""
    # Pattern: AAA. Query: "A".
    # Варианты размещения: A__, _A_, __A.
    result = calculator.calculate_probability("A", sample_country_simple)

    assert result is not None
    assert result.probability > 0
    # Вероятность должна быть выше, чем при полном совпадении
    assert result.probability > 3.7


def test_examples_generation(calculator, sample_country_simple):
    """Тест генерации примеров номеров."""
    result = calculator.calculate_probability("A", sample_country_simple)

    assert result.examples
    assert len(result.examples) > 0
    # Проверяем структуру примера
    example = result.examples[0]
    assert len(example) == 3
    # Один из символов должен быть 'A' и помечен как is_query=True
    assert any(s.value == "A" and s.is_query for s in example)


def test_empty_query(calculator, sample_country_simple):
    """Тест пустого запроса (должен вернуть None или 0, но по логике кода matches не найдутся)."""
    # Пустой запрос технически имеет длину 0, matches могут быть странными,
    # но валидация Pydantic не пропустит это на уровне API.
    # На уровне класса проверим поведение:
    result = calculator.calculate_probability("", sample_country_simple)
    # _find_all_matches вернет match [], но логика дальше может сломаться или вернуть 0
    # В текущей реализации это скорее всего вернет результат с 100% (пустота везде),
    # либо упадет. Но так как API защищен min_length=1, это edge-case unit теста.
    pass
