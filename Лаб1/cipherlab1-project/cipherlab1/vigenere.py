"""Шифр Віженера: Ci = (Pi + K(j mod l)) mod 33.

Ключ просувається лише на літерах алфавіту; пробіли, цифри та знаки
зберігаються і ключ не споживають.
"""

from __future__ import annotations

from .keys import normalize_letter_key
from .textprep import ALPHABET, ALPHABET_SIZE, INDEX


def _shift_text(text: str, key: str, direction: int) -> str:
    shifts = [INDEX[ch] for ch in key]
    period = len(shifts)
    result = []
    letters_seen = 0  # j - номер оброблюваної літери без урахування сторонніх символів
    for ch in text:
        index = INDEX.get(ch)
        if index is None:
            result.append(ch)
            continue
        shift = shifts[letters_seen % period]
        result.append(ALPHABET[(index + direction * shift) % ALPHABET_SIZE])
        letters_seen += 1
    return "".join(result)


def encrypt(text: str, key: str) -> str:
    return _shift_text(text, normalize_letter_key(key, "Ключ Віженера"), +1)


def decrypt(text: str, key: str) -> str:
    # Python повертає невід'ємну остачу, тому від'ємні значення окремо не обробляємо.
    return _shift_text(text, normalize_letter_key(key, "Ключ Віженера"), -1)
