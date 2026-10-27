"""Алфавіт і підготовка тексту (єдина специфікація обробки, розділ 5 методички).

Правила:
  1. працюємо з Unicode-рядками (не з байтами);
  2. спочатку нормалізація NFC;
  3. літери переводяться у верхній регістр посимвольно;
  4. допустимі символи: літери українського алфавіту, пробільні символи,
     цифри 0-9 та розділові знаки (ASCII + типографські « » „ “ ” ‘ ’ ʼ — – … №);
  5. будь-який інший символ відхиляється з повідомленням про позицію.
"""

from __future__ import annotations

import string
import unicodedata

from .errors import ModeError, TextValidationError

ALPHABET = "АБВГҐДЕЄЖЗИІЇЙКЛМНОПРСТУФХЦЧШЩЬЮЯ"
ALPHABET_SIZE = len(ALPHABET)  # m = 33
INDEX = {letter: i for i, letter in enumerate(ALPHABET)}

MODE_PRESERVE = "preserve"
MODE_LETTERS_ONLY = "letters-only"
MODES = (MODE_PRESERVE, MODE_LETTERS_ONLY)

_DIGITS = frozenset("0123456789")
_PUNCTUATION = frozenset(string.punctuation) | frozenset("«»„“”‘’ʼ—–…№")


def nfc(text: str) -> str:
    """Канонічна нормалізація Unicode (форма NFC)."""
    return unicodedata.normalize("NFC", text)


def to_upper(text: str) -> str:
    """NFC + верхній регістр посимвольно (довжина рядка не змінюється)."""
    result = []
    for ch in nfc(text):
        upper = ch.upper()
        result.append(upper if len(upper) == 1 else ch)
    return nfc("".join(result))


def is_supported(ch: str) -> bool:
    return ch in INDEX or ch.isspace() or ch in _DIGITS or ch in _PUNCTUATION


def check_mode(mode: str) -> None:
    if mode not in MODES:
        raise ModeError(
            f"Непідтримуваний режим обробки тексту {mode!r}; "
            f"доступні: {', '.join(MODES)}."
        )


def prepare_text(text: str, mode: str = MODE_PRESERVE) -> str:
    """Підготувати текст: NFC, верхній регістр, перевірка символів.

    preserve     - усі допустимі символи зберігаються (режим зворотний).
    letters-only - залишаються лише літери алфавіту (історичний режим;
                   пробіли, цифри й знаки безповоротно втрачаються).
    """
    check_mode(mode)
    prepared = to_upper(text)
    for position, ch in enumerate(prepared, start=1):
        if not is_supported(ch):
            raise TextValidationError(
                f"Непідтримуваний символ {ch!r} (U+{ord(ch):04X}) на позиції "
                f"{position} нормалізованого тексту. Дозволені: літери "
                "українського алфавіту, пробіли, цифри та розділові знаки."
            )
    if mode == MODE_LETTERS_ONLY:
        return "".join(ch for ch in prepared if ch in INDEX)
    return prepared
