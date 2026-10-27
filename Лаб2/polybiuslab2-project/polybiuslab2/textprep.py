"""Нормалізація тексту: NFC і верхній регістр підтримуваних символів."""

from __future__ import annotations

import unicodedata
from typing import Container


def nfc(text: str) -> str:
    """Канонічна нормалізація Unicode (форма NFC)."""
    return unicodedata.normalize("NFC", text)


def to_upper(text: str) -> str:
    """NFC + верхній регістр усіх символів (для ключових слів)."""
    out = []
    for ch in nfc(text):
        upper = ch.upper()
        out.append(upper if len(upper) == 1 else ch)
    return nfc("".join(out))


def normalize_text(text: str, supported: Container[str]) -> str:
    """NFC, потім до верхнього регістру лише ті символи, що мають верхню форму
    з набору ``supported``. Сторонні символи не змінюються."""
    out = []
    for ch in nfc(text):
        upper = ch.upper()
        out.append(upper if len(upper) == 1 and upper in supported else ch)
    return nfc("".join(out))


def strip_whitespace(text: str) -> tuple[str, int]:
    """Окрема видима операція підготовки: прибрати пробільні символи.

    Повертає (текст без пробілів, кількість видалених символів).
    """
    kept = "".join(ch for ch in text if not ch.isspace())
    return kept, len(text) - len(kept)
