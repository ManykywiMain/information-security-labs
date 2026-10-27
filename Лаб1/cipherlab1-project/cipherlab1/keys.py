"""Перевірка та розбір ключів (виконується до початку обробки тексту)."""

from __future__ import annotations

from typing import Iterable, Sequence

from .errors import KeyValidationError
from .textprep import INDEX, to_upper


def normalize_letter_key(key: str, name: str = "Ключ") -> str:
    """Ключове слово: не порожнє, лише літери алфавіту (після NFC і верхнього регістру)."""
    if not isinstance(key, str) or key == "":
        raise KeyValidationError(f"{name} не може бути порожнім.")
    normalized = to_upper(key)
    for position, ch in enumerate(normalized, start=1):
        if ch not in INDEX:
            raise KeyValidationError(
                f"{name} містить символ {ch!r} на позиції {position}, "
                "якого немає в українському алфавіті (допустимі лише літери А-Я, Ґ, Є, І, Ї)."
            )
    return normalized


def validate_permutation(perm: Sequence[int], name: str = "Перестановка") -> tuple[int, ...]:
    """Перестановка довжини n має містити кожне число від 1 до n рівно один раз."""
    if len(perm) == 0:
        raise KeyValidationError(f"{name} не може бути порожньою.")
    n = len(perm)
    seen: set[int] = set()
    for value in perm:
        if not 1 <= value <= n:
            raise KeyValidationError(
                f"{name}: число {value} поза діапазоном 1..{n} (довжина ключа {n})."
            )
        if value in seen:
            raise KeyValidationError(f"{name}: число {value} повторюється.")
        seen.add(value)
    return tuple(perm)


def parse_permutation(key: str | Iterable[int], name: str = "Перестановка") -> tuple[int, ...]:
    """Розібрати ключ перестановки і перевірити його.

    Підтримуються обидва записи з методички: ``"3 2 5 1 4"`` (або ``"3,2,5,1,4"``)
    та компактний ``"32514"``. Рядок з одних цифр без роздільників читається
    як послідовність окремих цифр, тому так можна записати лише ключі до 9 стовпців
    (довші записують через пробіл).
    """
    if isinstance(key, str):
        tokens = key.replace(",", " ").split()
        if not tokens:
            raise KeyValidationError(f"{name} не може бути порожньою.")
        if len(tokens) == 1 and len(tokens[0]) > 1 and tokens[0].isascii() and tokens[0].isdigit():
            tokens = list(tokens[0])  # компактний запис: кожна цифра - окремий елемент
        values = []
        for token in tokens:
            if not (token.isascii() and token.isdigit()):
                raise KeyValidationError(
                    f"{name}: {token!r} не є натуральним числом."
                )
            values.append(int(token))
    else:
        values = list(key)
    return validate_permutation(values, name)


def inverse_permutation(perm: Sequence[int]) -> tuple[int, ...]:
    """Обернена перестановка: для (3,2,5,1,4) це (4,2,1,5,3)."""
    inverse = [0] * len(perm)
    for position, value in enumerate(perm, start=1):
        inverse[value - 1] = position
    return tuple(inverse)
