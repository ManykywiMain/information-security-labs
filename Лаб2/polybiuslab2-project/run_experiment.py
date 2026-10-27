"""Відтворюваний експеримент: власні тексти -> шифротекст -> розшифрований текст.

Запуск:  python run_experiment.py
Результат: results/experiment.json (читає звіт) і results/experiment.txt.
"""

import json
import os
import platform
import sys

from polybiuslab2 import __version__, service
from polybiuslab2.alphabets import get_alphabet
from polybiuslab2.fileio import read_text, write_text_atomic
from polybiuslab2.textprep import normalize_text, strip_whitespace

HERE = os.path.dirname(os.path.abspath(__file__))

# навчальні ключі (вигадані; у реальних системах так робити не можна)
CONFIG = {
    "ua": {"file": "own_text_ua.txt", "keyword": "ІНФОРМАЦІЯ", "digits": "0517",
           "coordinates_text": "ҐАНОК ЄНОТ ЇЖАК ІВАН 2012"},
    "en": {"file": "own_text_en.txt", "keyword": "CRYPTOGRAPHY", "digits": "4096",
           "coordinates_text": "AZ HELLO WORLD 2026"},
}


def main() -> int:
    report = {"program_version": __version__, "python": sys.version.split()[0],
              "platform": platform.platform(), "runs": []}
    lines = [f"polybiuslab2 {__version__}, Python {report['python']}", ""]
    for lang, cfg in CONFIG.items():
        free_text = read_text(os.path.join(HERE, "data", cfg["file"])).strip()
        coord_text, removed = strip_whitespace(cfg["coordinates_text"])  # видима операція
        square = service.get_square(lang, cfg["keyword"])
        lines += [f"##### Алфавіт: {lang}, ключове слово: {cfg['keyword']} #####", square.render(), ""]
        runs = [
            ("Полібій coordinates", service.POLYBIUS_COORDINATES, cfg["keyword"], coord_text,
             f"{cfg['coordinates_text']!r} -> без пробільних символів (видалено {removed})"),
            ("Полібій row shift", service.POLYBIUS_ROW_SHIFT, cfg["keyword"], free_text, ""),
            ("Гронсфельд", service.GRONSFELD, cfg["digits"], free_text, ""),
        ]
        for title, algo, key, plain, note in runs:
            encrypted = service.encrypt(algo, lang, plain, key)
            decrypted = service.decrypt(algo, lang, encrypted, key)
            ok = decrypted == _prepared(plain, lang, algo)
            report["runs"].append({
                "language": lang, "title": title, "algorithm": algo, "key": key,
                "keyword": cfg["keyword"], "plaintext": plain, "note": note,
                "ciphertext": encrypted, "decrypted": decrypted, "restored": ok,
                "square_rows": list(square.rows),
            })
            lines += [f"== {title} (ключ: {key}) ==", f"відкритий:   {plain}",
                      f"шифротекст:  {encrypted}", f"розшифровано: {decrypted}",
                      f"відновлено коректно: {ok}", ""]
            if not ok:
                print(f"ПОМИЛКА: {title} ({lang}) не відновив текст", file=sys.stderr)
                return 1
    out_dir = os.path.join(HERE, "results")
    os.makedirs(out_dir, exist_ok=True)
    write_text_atomic(os.path.join(out_dir, "experiment.json"),
                      json.dumps(report, ensure_ascii=False, indent=2))
    write_text_atomic(os.path.join(out_dir, "experiment.txt"), "\n".join(lines))
    print("\n".join(lines))
    return 0


def _prepared(text: str, lang: str, algorithm: str) -> str:
    """Підготовлений відкритий текст: NFC і верхній регістр підтримуваних символів."""
    alphabet = get_alphabet(lang)
    supported = alphabet.letters if algorithm == service.GRONSFELD else alphabet.base
    return normalize_text(text, supported)


if __name__ == "__main__":
    sys.exit(main())
