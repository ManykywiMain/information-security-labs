"""Єдина точка входу: перевірка алгоритму, алфавіту та ключа -> обробка тексту."""

from __future__ import annotations

from . import coordinates, gronsfeld, row_shift
from .alphabets import get_alphabet
from .errors import ModeError
from .square import build_square

POLYBIUS_COORDINATES = "polybius-coordinates"
POLYBIUS_ROW_SHIFT = "polybius-row-shift"
GRONSFELD = "gronsfeld"
ALGORITHMS = (POLYBIUS_COORDINATES, POLYBIUS_ROW_SHIFT, GRONSFELD)


def _check_algorithm(algorithm: str) -> None:
    if algorithm not in ALGORITHMS:
        raise ModeError(
            f"Непідтримуваний алгоритм {algorithm!r}; доступні: {', '.join(ALGORITHMS)}."
        )


def encrypt(algorithm: str, language: str, text: str, key: str) -> str:
    """Зашифрувати. Ключ перевіряється до початку обробки тексту.

    ``key`` - ключове слово для алгоритмів Полібія і рядок цифр для Гронсфельда.
    """
    _check_algorithm(algorithm)
    alphabet = get_alphabet(language)
    if algorithm == GRONSFELD:
        return gronsfeld.encrypt(text, alphabet, key)
    square = build_square(language, key)
    if algorithm == POLYBIUS_COORDINATES:
        return coordinates.encrypt(text, square)
    return row_shift.encrypt(text, square)


def decrypt(algorithm: str, language: str, text: str, key: str) -> str:
    _check_algorithm(algorithm)
    alphabet = get_alphabet(language)
    if algorithm == GRONSFELD:
        return gronsfeld.decrypt(text, alphabet, key)
    square = build_square(language, key)
    if algorithm == POLYBIUS_COORDINATES:
        return coordinates.decrypt(text, square)
    return row_shift.decrypt(text, square)


def get_square(language: str, keyword: str):
    """Активний квадрат (для показу в інтерфейсі)."""
    return build_square(language, keyword)
