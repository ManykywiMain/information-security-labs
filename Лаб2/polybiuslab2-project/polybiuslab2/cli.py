"""Консольний інтерфейс: encrypt, decrypt, square, rules. Помилка -> stderr і код 1."""

from __future__ import annotations

import argparse
import os
import sys

from . import __version__, fileio, service
from .alphabets import ALPHABETS
from .errors import CipherError
from .textprep import strip_whitespace

RULES = """\
Правила (єдина специфікація):
  * кодування файлів UTF-8; текст обробляється як Unicode-рядок; перед усім - NFC;
  * мова (--lang ua|en) обирається явно, автоматичного вгадування немає;
  * українська: 33 літери АБВГҐДЕЄЖЗИІЇЙКЛМНОПРСТУФХЦЧШЩЬЮЯ; квадрат = літери + 0 1 2;
    латинська: 26 літер A-Z; квадрат = літери + 0-9;
  * підтримувані літери переводяться у верхній регістр;
  * квадрат будується з ключового слова: унікальні символи за першою появою, потім решта
    набору, запис по рядках 6 на 6; координати - (рядок, стовпець) з 1 до 6;
  * polybius-coordinates (strict): приймає лише символи квадрата, результат - токени
    рядок-стовпець через пробіл; пробіли треба прибрати окремо (--strip-spaces);
    розшифрування відхиляє будь-який токен, що не є двома цифрами 1-6;
  * polybius-row-shift: символ -> символ наступного рядка того самого стовпця (після 6 - 1);
    символи поза квадратом зберігаються;
  * gronsfeld: ключ - рядок цифр (початкові нулі зберігаються, не лише нулі);
    змінюються лише літери вибраного алфавіту, інші символи не просувають ключ.
"""


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="polybiuslab2",
        description="Квадрат Полібія та шифр Гронсфельда (лабораторна робота 2). "
                    "Навчальні шифри; не використовувати для захисту реальних даних.",
        epilog=RULES,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--version", action="version", version=f"polybiuslab2 {__version__}")
    subparsers = parser.add_subparsers(dest="command", required=True)

    for name, help_text in (("encrypt", "зашифрувати"), ("decrypt", "розшифрувати")):
        sub = subparsers.add_parser(name, help=help_text, epilog=RULES,
                                    formatter_class=argparse.RawDescriptionHelpFormatter)
        sub.add_argument("--algo", required=True, choices=service.ALGORITHMS, help="алгоритм")
        sub.add_argument("--lang", required=True, choices=tuple(ALPHABETS), help="алфавіт")
        sub.add_argument("--key", required=True,
                         help="ключове слово (Полібій) або рядок цифр (Гронсфельд)")
        source = sub.add_mutually_exclusive_group()
        source.add_argument("--text", help="текст у командному рядку")
        source.add_argument("--input", metavar="FILE", help="UTF-8 файл із текстом")
        sub.add_argument("--output", metavar="FILE", help="записати результат у UTF-8 файл")
        sub.add_argument("--show-square", action="store_true",
                         help="показати активний квадрат (лише алгоритми Полібія)")
        if name == "encrypt":
            sub.add_argument("--strip-spaces", action="store_true",
                             help="перед polybius-coordinates видалити пробільні символи")

    square = subparsers.add_parser("square", help="показати ключовий квадрат 6 на 6")
    square.add_argument("--lang", required=True, choices=tuple(ALPHABETS))
    square.add_argument("--key", required=True, help="ключове слово")

    subparsers.add_parser("rules", help="показати правила обробки")
    return parser


def _read_source(args: argparse.Namespace) -> str:
    if args.text is not None:
        return args.text
    if args.input is not None:
        return fileio.read_text(args.input)
    return sys.stdin.read()


def _check_options(args: argparse.Namespace) -> None:
    if args.input and args.output and os.path.exists(args.output) \
            and os.path.exists(args.input) and os.path.samefile(args.input, args.output):
        raise CipherError("Вхідний і вихідний файли збігаються; вкажіть інший --output.")
    if args.show_square and args.algo == service.GRONSFELD:
        raise CipherError("--show-square застосовується лише до алгоритмів Полібія.")
    if getattr(args, "strip_spaces", False) and args.algo != service.POLYBIUS_COORDINATES:
        raise CipherError("--strip-spaces застосовується лише до polybius-coordinates.")


def _emit(text: str, output: str | None) -> None:
    if output:
        fileio.write_text_atomic(output, text)
        print(f"Результат збережено у {output}", file=sys.stderr)
        return
    sys.stdout.write(text)
    if sys.stdout.isatty() and not text.endswith("\n"):
        sys.stdout.write("\n")


def run(args: argparse.Namespace) -> None:
    if args.command == "rules":
        print(RULES)
        return
    if args.command == "square":
        print(service.get_square(args.lang, args.key).render())
        return
    _check_options(args)
    if args.show_square:  # квадрат перевіряється до читання тексту
        print(service.get_square(args.lang, args.key).render(), file=sys.stderr)
    source = _read_source(args)
    if args.command == "encrypt":
        if args.strip_spaces:
            source, removed = strip_whitespace(source)
            print(f"Видалено пробільних символів: {removed}", file=sys.stderr)
        result = service.encrypt(args.algo, args.lang, source, args.key)
    else:
        result = service.decrypt(args.algo, args.lang, source, args.key)
    _emit(result, args.output)


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)  # некоректні аргументи: argparse завершується з кодом 2
    try:
        run(args)
    except CipherError as error:
        print(f"Помилка: {error}", file=sys.stderr)
        return 1
    return 0
