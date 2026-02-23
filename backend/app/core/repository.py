import csv
import logging
from pathlib import Path
from typing import Dict, List, Optional

from app.schemas.plate import CountrySchema

logger = logging.getLogger(__name__)


class CountryRepository:
    """
    Репозиторий для управления данными о странах из CSV-хранилища

    Attributes:
        file_path (Path): Абсолютный путь к файлу данных CSV.
        _cache (Optional[List[CountrySchema]]): Внутренний кэш для хранения данных.
    """

    def __init__(self):
        self.file_path = Path(__file__).parent.parent.parent / "data" / "countries.csv"
        self._cache: Optional[List[CountrySchema]] = None

    def _get_flag_emoji(self, country_code: str) -> str:
        """Генерирует emoji флага из кода страны (ISO 3166-1 alpha-2)."""
        if len(country_code) != 2:
            return "🏳️"
        return "".join(chr(ord(c) + 127397) for c in country_code.upper())

    def get_all(self) -> List[CountrySchema]:
        """
        Читает CSV и возвращает все шаблоны стран.

        Использует ленивую загрузку с кэшированием в памяти.

        Returns:
            List[CountrySchema]: Список объектов стран.

        Raises:
            FileNotFoundError: Если CSV-файл отсутствует по указанному пути.
            IOError: Если возникла ошибка при чтении или обработке файла.
        """
        if self._cache is not None:
            return self._cache

        if not self.file_path.exists():
            logger.error(f"Data source not found: {self.file_path}")
            raise FileNotFoundError(f"CSV not found with path: {self.file_path}")

        try:
            with open(self.file_path, mode="r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                cleaned_data = []
                for row in reader:
                    if row.get("allowed_letters") is None:
                        row["allowed_letters"] = ""
                    row["flag_emoji"] = self._get_flag_emoji(row["country_code"])
                    cleaned_data.append(CountrySchema(**row))

                self._cache = cleaned_data
                return self._cache

        except Exception as e:
            logger.exception(f"Error with reading CSV: {e}")
            raise IOError(f"Error with processing countries data: {e}")
