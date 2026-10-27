"""Ключовий квадрат Полібія 6 на 6.

Побудова: ключове слово -> NFC + верхній регістр -> перевірка за квадратом ->
унікальні символи за першою появою -> решта базового набору -> 6 рядків по 6.
Прямі та обернені відображення будуються один раз при створенні квадрата.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache

from .alphabets import Alphabet, get_alphabet
from .errors import KeyValidationError
from .textprep import to_upper

SIZE = 6
CELLS = SIZE * SIZE  # 36


@dataclass(frozen=True, eq=False)
class Square:
    language: str
    keyword: str                              # нормалізоване ключове слово
    cells: str                                # 36 символів по рядках
    coords: dict[str, tuple[int, int]]        # символ -> (рядок, стовпець), з 1
    symbols: dict[tuple[int, int], str]       # (рядок, стовпець) -> символ

    @property
    def rows(self) -> tuple[str, ...]:
        return tuple(self.cells[i:i + SIZE] for i in range(0, CELLS, SIZE))

    def render(self) -> str:
        """Текстове подання квадрата з номерами рядків і стовпців."""
        header = "    " + " ".join(str(c) for c in range(1, SIZE + 1))
        body = [f"{r}   " + " ".join(row) for r, row in enumerate(self.rows, start=1)]
        return "\n".join([header, *body])


def normalize_keyword(keyword: str, alphabet: Alphabet) -> str:
    """Не порожнє; лише символи квадрата; щонайменше одна літера."""
    if not isinstance(keyword, str) or keyword == "":
        raise KeyValidationError("Ключове слово не може бути порожнім.")
    normalized = to_upper(keyword)
    allowed = set(alphabet.base)
    for position, ch in enumerate(normalized, start=1):
        if ch not in allowed:
            raise KeyValidationError(
                f"Ключове слово містить символ {ch!r} на позиції {position}, якого немає в "
                f"{alphabet.name} квадраті (літери й цифри: {alphabet.base})."
            )
    if not any(ch in alphabet.letters for ch in normalized):
        raise KeyValidationError("Ключове слово має містити щонайменше одну літеру.")
    return normalized


def validate_cells(cells: str, alphabet: Alphabet) -> None:
    """Квадрат: рівно 36 унікальних символів, кожен символ базового набору один раз."""
    if len(cells) != CELLS:
        raise KeyValidationError(f"Квадрат має містити {CELLS} символів, а містить {len(cells)}.")
    if len(set(cells)) != CELLS:
        raise KeyValidationError("У квадраті є повторювані символи.")
    if set(cells) != set(alphabet.base):
        raise KeyValidationError("Квадрат не збігається з базовим набором символів.")


@lru_cache(maxsize=64)
def build_square(language: str, keyword: str) -> Square:
    alphabet = get_alphabet(language)
    key = normalize_keyword(keyword, alphabet)
    unique = "".join(dict.fromkeys(key))
    used = set(unique)
    cells = unique + "".join(ch for ch in alphabet.base if ch not in used)
    validate_cells(cells, alphabet)
    coords = {ch: (i // SIZE + 1, i % SIZE + 1) for i, ch in enumerate(cells)}
    symbols = {position: ch for ch, position in coords.items()}
    return Square(language, key, cells, coords, symbols)
