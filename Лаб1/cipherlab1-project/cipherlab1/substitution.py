"""Проста одноалфавітна підстановка за ключовим словом."""

from __future__ import annotations

from collections import Counter

from .errors import KeyValidationError
from .keys import normalize_letter_key
from .textprep import ALPHABET, ALPHABET_SIZE, INDEX


def build_table(keyword: str) -> str:
    """Таблиця B: унікальні літери ключа (за першою появою) + решта алфавіту.

    Ключове слово, що вже є повною перестановкою алфавіту (наприклад,
    алфавіт у зворотному порядку), дає саме цю таблицю.
    """
    key = normalize_letter_key(keyword, "Ключове слово")
    unique = list(dict.fromkeys(key))
    used = set(unique)
    table = "".join(unique) + "".join(ch for ch in ALPHABET if ch not in used)
    validate_table(table)
    return table


def validate_table(table: str) -> None:
    """Таблиця: довжина 33, лише літери алфавіту, без повторів."""
    foreign = [ch for ch in table if ch not in INDEX]
    if foreign:
        raise KeyValidationError(f"Таблиця підстановки містить стороннього символа {foreign[0]!r}.")
    repeated = [ch for ch, count in Counter(table).items() if count > 1]
    if repeated:
        raise KeyValidationError(f"У таблиці підстановки літера {repeated[0]!r} повторюється.")
    if len(table) != ALPHABET_SIZE:
        raise KeyValidationError(
            f"Таблиця підстановки має містити {ALPHABET_SIZE} літер, а містить {len(table)}."
        )


def encrypt(text: str, table: str) -> str:
    """Літера з індексом i замінюється літерою таблиці з тим самим індексом."""
    return text.translate(str.maketrans(ALPHABET, table))


def decrypt(text: str, table: str) -> str:
    """Обернене відображення: літера таблиці -> літера алфавіту."""
    return text.translate(str.maketrans(table, ALPHABET))
