"""Консольний інтерфейс: encrypt, decrypt, rules. Помилка -> повідомлення у stderr і код 1."""

from __future__ import annotations

import argparse
import os
import sys

from . import __version__, fileio, service
from .errors import CipherError
from .textprep import MODE_PRESERVE, MODES

RULES = """\
Правила підготовки тексту (єдина специфікація):
  * кодування файлів UTF-8; текст обробляється як Unicode-рядок;
  * перед обробкою застосовується нормалізація NFC;
  * літери переводяться у верхній регістр;
  * алфавіт (m = 33): АБВГҐДЕЄЖЗИІЇЙКЛМНОПРСТУФХЦЧШЩЬЮЯ;
  * допустимі символи тексту: літери алфавіту, пробіли/переноси, цифри, розділові знаки;
    інші символи (латиниця, емодзі тощо) відхиляються з вказанням позиції;
  * substitution, vigenere: пробіли, цифри й знаки зберігаються; у Віженера вони
    не просувають ключ;
  * block, columnar: режим preserve (типовий) переставляє весь нормалізований текст;
    режим letters-only залишає лише літери (незворотний щодо пробілів);
  * block: неповний останній блок залишається без змін;
  * columnar: останній рядок доповнюється службовим символом '_', кількість доданих
    символів виводиться під час шифрування і передається в --pad під час розшифрування.

Ключі:
  substitution  ключове слово (ключ із 33 літер = готова таблиця, напр. алфавіт навпаки)
  vigenere      ключове слово з літер алфавіту
  block         перестановка, напр. "3 2 5 1 4"
  columnar      порядок читання стовпців, напр. "3 1 4 2"
"""


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cipherlab1",
        description="Навчальні шифри заміни та перестановки (лабораторна робота 1). "
                    "Не використовувати для захисту реальних даних.",
        epilog=RULES,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--version", action="version", version=f"cipherlab1 {__version__}")
    subparsers = parser.add_subparsers(dest="command", required=True)

    for name, help_text in (("encrypt", "зашифрувати"), ("decrypt", "розшифрувати")):
        sub = subparsers.add_parser(name, help=help_text, epilog=RULES,
                                    formatter_class=argparse.RawDescriptionHelpFormatter)
        sub.add_argument("--algo", required=True, choices=service.ALGORITHMS, help="алгоритм")
        sub.add_argument("--key", required=True, help="ключ (формат залежить від алгоритму)")
        source = sub.add_mutually_exclusive_group()
        source.add_argument("--text", help="текст у командному рядку")
        source.add_argument("--input", metavar="FILE", help="UTF-8 файл із текстом")
        sub.add_argument("--output", metavar="FILE", help="записати результат у UTF-8 файл")
        if name == "encrypt":
            sub.add_argument("--mode", choices=MODES, default=MODE_PRESERVE,
                             help="режим підготовки тексту (типово preserve)")
        else:
            sub.add_argument("--pad", type=int,
                             help="кількість доданих символів (обов'язково для columnar)")

    subparsers.add_parser("rules", help="показати правила підготовки тексту")
    return parser


def _read_source(args: argparse.Namespace) -> str:
    if args.text is not None:
        return args.text
    if args.input is not None:
        return fileio.read_text(args.input)
    return sys.stdin.read()


def _check_paths(args: argparse.Namespace) -> None:
    if args.input and args.output and os.path.exists(args.output) \
            and os.path.exists(args.input) and os.path.samefile(args.input, args.output):
        raise CipherError("Вхідний і вихідний файли збігаються; вкажіть інший --output.")


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
    _check_paths(args)
    source = _read_source(args)
    if args.command == "encrypt":
        result = service.encrypt(args.algo, source, args.key, args.mode)
        if args.algo == service.COLUMNAR:
            print(f"Додано службових символів: {result.pad} (передайте --pad {result.pad} "
                  "під час розшифрування)", file=sys.stderr)
    else:
        result = service.decrypt(args.algo, source, args.key, args.pad)
    _emit(result.text, args.output)


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)  # некоректні аргументи: argparse завершується з кодом 2
    try:
        run(args)
    except CipherError as error:
        print(f"Помилка: {error}", file=sys.stderr)
        return 1
    return 0
