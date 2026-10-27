"""Блокова та вертикальна перестановки.

Політика неповного блока (частина специфікації):
  * блокова перестановка: неповний останній блок залишається без змін;
  * вертикальна перестановка: останній рядок доповнюється службовим символом
    PAD_CHAR, а кількість доданих символів повертається окремо і за нею
    ж вилучається під час розшифрування (а не за наявністю PAD_CHAR).
"""

from __future__ import annotations

from typing import Sequence

from .errors import KeyValidationError, TextValidationError
from .keys import inverse_permutation, validate_permutation

PAD_CHAR = "_"


# --------------------------------------------------------------- блокова


def _apply_blocks(text: str, perm: Sequence[int]) -> str:
    n = len(perm)
    parts = []
    for start in range(0, len(text), n):
        block = text[start:start + n]
        if len(block) < n:
            parts.append(block)  # неповний залишок не змінюється
        else:
            parts.append("".join(block[p - 1] for p in perm))
    return "".join(parts)


def block_encrypt(text: str, perm: Sequence[int]) -> str:
    """y = (x[pi1], x[pi2], ..., x[pin]) для кожного повного блока."""
    return _apply_blocks(text, validate_permutation(perm))


def block_decrypt(text: str, perm: Sequence[int]) -> str:
    """Той самий прохід з оберненою перестановкою, обчисленою один раз."""
    return _apply_blocks(text, inverse_permutation(validate_permutation(perm)))


# ------------------------------------------------------------- вертикальна


def columnar_encrypt(text: str, key: Sequence[int]) -> tuple[str, int]:
    """Запис по рядках, читання стовпців у порядку ключа.

    Повертає (шифротекст, кількість доданих службових символів).
    """
    key = validate_permutation(key, "Ключ вертикальної перестановки")
    columns = len(key)
    pad = (-len(text)) % columns
    padded = text + PAD_CHAR * pad
    # стовпець c (з нумерацією з 1) - це padded[c-1::columns]
    cipher = "".join(padded[c - 1::columns] for c in key)
    return cipher, pad


def columnar_decrypt(cipher: str, key: Sequence[int], pad: int) -> str:
    key = validate_permutation(key, "Ключ вертикальної перестановки")
    columns = len(key)
    if not isinstance(pad, int) or isinstance(pad, bool) or not 0 <= pad < columns:
        raise KeyValidationError(
            f"Кількість доданих символів має бути цілою у діапазоні 0..{columns - 1}, отримано {pad!r}."
        )
    if len(cipher) % columns != 0:
        raise TextValidationError(
            f"Довжина шифротексту ({len(cipher)}) не кратна кількості стовпців ({columns}); "
            "шифротекст пошкоджений або ключ неправильний."
        )
    if pad > len(cipher):
        raise KeyValidationError("Кількість доданих символів перевищує довжину шифротексту.")
    rows = len(cipher) // columns
    buffer = [""] * len(cipher)
    for order, column in enumerate(key):
        buffer[column - 1::columns] = list(cipher[order * rows:(order + 1) * rows])
    padded = "".join(buffer)
    if pad:
        if padded[-pad:] != PAD_CHAR * pad:
            raise TextValidationError(
                "Після розшифрування в кінці немає очікуваних службових символів; "
                "перевірте ключ і кількість доданих символів."
            )
        padded = padded[:-pad]
    return padded
