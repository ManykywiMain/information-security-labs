"""Координатний режим Полібія (strict).

Символ -> два цифри: номер рядка, потім номер стовпця (нумерація з 1).
Токени розділяються одним пробілом: СЛАВА -> "44 35 16 21 16".
"""

from __future__ import annotations

import re

from .errors import TextValidationError
from .square import Square
from .textprep import normalize_text

_TOKEN = re.compile(r"[1-6]{2}")


def encrypt(text: str, square: Square) -> str:
    """Приймає лише символи квадрата; пробіли та знаки - помилка (strict)."""
    tokens = []
    for position, ch in enumerate(normalize_text(text, square.coords), start=1):
        coordinate = square.coords.get(ch)
        if coordinate is None:
            hint = " Пробіли слід видаляти окремою операцією (--strip-spaces)." if ch.isspace() else ""
            raise TextValidationError(
                f"Символ {ch!r} (U+{ord(ch):04X}) на позиції {position} не входить до квадрата "
                f"(літери й цифри: {''.join(sorted(square.coords))}).{hint}"
            )
        tokens.append(f"{coordinate[0]}{coordinate[1]}")
    return " ".join(tokens)


def parse_tokens(ciphertext: str) -> list[tuple[int, int]]:
    """Суворий розбір: кожен токен - рівно дві цифри від 1 до 6, нічого не пропускається."""
    stripped = ciphertext.strip()  # кінцевий перенос рядка з файлу не є токеном
    if stripped == "":
        return []
    parsed = []
    for position, token in enumerate(stripped.split(" "), start=1):
        if token == "":
            raise TextValidationError(
                f"Порожній токен на позиції {position}: токени розділяються рівно одним пробілом."
            )
        if not _TOKEN.fullmatch(token):
            raise TextValidationError(
                f"Некоректний токен {token!r} на позиції {position}: "
                "очікуються дві цифри, кожна від 1 до 6."
            )
        parsed.append((int(token[0]), int(token[1])))
    return parsed


def decrypt(ciphertext: str, square: Square) -> str:
    return "".join(square.symbols[coordinate] for coordinate in parse_tokens(ciphertext))
