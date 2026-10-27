"""Узгоджені набори символів. Мова обирається явно і ніколи не вгадується."""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache

from .errors import ModeError

UKRAINIAN = "ua"
LATIN = "en"


@dataclass(frozen=True)
class Alphabet:
    code: str
    name: str
    letters: str   # базовий алфавіт для Гронсфельда (m = len(letters))
    extra: str     # додаткові символи, що доповнюють квадрат до 36

    @property
    def size(self) -> int:
        return len(self.letters)

    @property
    def base(self) -> str:
        """Базовий набір квадрата 6 на 6: літери, потім цифри."""
        return self.letters + self.extra


ALPHABETS = {
    UKRAINIAN: Alphabet(UKRAINIAN, "український", "АБВГҐДЕЄЖЗИІЇЙКЛМНОПРСТУФХЦЧШЩЬЮЯ", "012"),
    LATIN: Alphabet(LATIN, "латинський", "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "0123456789"),
}


def get_alphabet(language: str) -> Alphabet:
    try:
        return ALPHABETS[language]
    except (KeyError, TypeError):
        raise ModeError(
            f"Непідтримуваний алфавіт {language!r}; доступні: {', '.join(ALPHABETS)}."
        ) from None


@lru_cache(maxsize=None)
def letter_index(letters: str) -> dict[str, int]:
    """Відображення літера -> індекс, готується один раз для кожного алфавіту."""
    return {letter: i for i, letter in enumerate(letters)}
