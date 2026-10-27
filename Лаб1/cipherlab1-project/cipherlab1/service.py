"""Єдина точка входу: перевірка ключа -> підготовка тексту -> алгоритм."""

from __future__ import annotations

from dataclasses import dataclass

from . import permutations, substitution, vigenere
from .errors import KeyValidationError, ModeError
from .keys import parse_permutation
from .textprep import MODE_PRESERVE, check_mode, prepare_text

SUBSTITUTION = "substitution"
VIGENERE = "vigenere"
BLOCK = "block"
COLUMNAR = "columnar"
ALGORITHMS = (SUBSTITUTION, VIGENERE, BLOCK, COLUMNAR)


@dataclass(frozen=True)
class Result:
    """Результат операції. ``pad`` значущий лише для вертикальної перестановки."""

    text: str
    pad: int = 0


def _check_algorithm(algorithm: str) -> None:
    if algorithm not in ALGORITHMS:
        raise ModeError(
            f"Непідтримуваний алгоритм {algorithm!r}; доступні: {', '.join(ALGORITHMS)}."
        )


def encrypt(algorithm: str, text: str, key: str, mode: str = MODE_PRESERVE) -> Result:
    """Зашифрувати. Ключ і режим перевіряються до початку обробки тексту."""
    _check_algorithm(algorithm)
    check_mode(mode)
    if algorithm == SUBSTITUTION:
        table = substitution.build_table(key)
        return Result(substitution.encrypt(prepare_text(text, mode), table))
    if algorithm == VIGENERE:
        vigenere.encrypt("", key)  # лише перевірка ключа
        return Result(vigenere.encrypt(prepare_text(text, mode), key))
    perm = parse_permutation(key)
    prepared = prepare_text(text, mode)
    if algorithm == BLOCK:
        return Result(permutations.block_encrypt(prepared, perm))
    cipher, pad = permutations.columnar_encrypt(prepared, perm)
    return Result(cipher, pad)


def decrypt(algorithm: str, text: str, key: str, pad: int | None = None) -> Result:
    """Розшифрувати. Шифротекст уже підготовлений, тому режим не потрібен.

    Для вертикальної перестановки обов'язково потрібен ``pad``.
    """
    _check_algorithm(algorithm)
    if algorithm == SUBSTITUTION:
        table = substitution.build_table(key)
        return Result(substitution.decrypt(prepare_text(text), table))
    if algorithm == VIGENERE:
        vigenere.decrypt("", key)
        return Result(vigenere.decrypt(prepare_text(text), key))
    perm = parse_permutation(key)
    prepared = prepare_text(text)
    if algorithm == BLOCK:
        return Result(permutations.block_decrypt(prepared, perm))
    if pad is None:
        raise KeyValidationError(
            "Для розшифрування вертикальної перестановки потрібно вказати кількість "
            "доданих символів (параметр --pad), яку вивела операція шифрування."
        )
    return Result(permutations.columnar_decrypt(prepared, perm, pad), pad)
