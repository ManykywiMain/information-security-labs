"""Циклічний зсув за рядками (polybius row shift).

Символ замінюється символом із наступного рядка того самого стовпця; після
шостого рядка - перехід до першого. Розшифрування - зсув на рядок угору.
Символи поза квадратом зберігаються без змін. Це проста одноалфавітна
підстановка, а не координатне кодування.
"""

from __future__ import annotations

from .square import SIZE, Square
from .textprep import normalize_text


def _shift(text: str, square: Square, step: int) -> str:
    result = []
    for ch in normalize_text(text, square.coords):
        coordinate = square.coords.get(ch)
        if coordinate is None:
            result.append(ch)
            continue
        row, column = coordinate
        result.append(square.symbols[((row - 1 + step) % SIZE + 1, column)])
    return "".join(result)


def encrypt(text: str, square: Square) -> str:
    return _shift(text, square, +1)


def decrypt(text: str, square: Square) -> str:
    return _shift(text, square, -1)
