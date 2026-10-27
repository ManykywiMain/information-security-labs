"""Шифр Гронсфельда: Ci = (Pi + d(j mod t)) mod m.

Ключ - рядок цифр (початкові нулі зберігаються). Змінюються лише літери
вибраного алфавіту; пробіли, цифри й знаки не змінюються і ключ не споживають.
"""

from __future__ import annotations

from .alphabets import Alphabet, letter_index
from .errors import KeyValidationError
from .textprep import normalize_text

_ASCII_DIGITS = frozenset("0123456789")


def validate_key(key: str) -> list[int]:
    """Не порожній рядок ASCII-цифр з щонайменше однією ненульовою цифрою."""
    if not isinstance(key, str) or key == "":
        raise KeyValidationError("Цифровий ключ не може бути порожнім.")
    for position, ch in enumerate(key, start=1):
        if ch not in _ASCII_DIGITS:
            raise KeyValidationError(
                f"Цифровий ключ містить символ {ch!r} на позиції {position}; "
                "дозволені лише цифри 0-9."
            )
    if set(key) == {"0"}:
        raise KeyValidationError("Цифровий ключ не може складатися лише з нулів.")
    return [int(ch) for ch in key]


def _shift(text: str, alphabet: Alphabet, key: str, direction: int) -> str:
    digits = validate_key(key)
    index = letter_index(alphabet.letters)
    period, size = len(digits), alphabet.size
    result = []
    letters_seen = 0  # j(i): номер літери без урахування сторонніх символів
    for ch in normalize_text(text, index):
        position = index.get(ch)
        if position is None:
            result.append(ch)
            continue
        shift = digits[letters_seen % period]
        result.append(alphabet.letters[(position + direction * shift) % size])
        letters_seen += 1
    return "".join(result)


def encrypt(text: str, alphabet: Alphabet, key: str) -> str:
    return _shift(text, alphabet, key, +1)


def decrypt(text: str, alphabet: Alphabet, key: str) -> str:
    return _shift(text, alphabet, key, -1)
