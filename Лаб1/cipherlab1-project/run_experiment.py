"""Відтворюваний експеримент: власний текст -> шифротекст -> розшифрований текст.

Запуск:  python run_experiment.py
Результат: results/experiment.json (читає звіт) і results/experiment.txt.
"""

import json
import os
import platform
import sys

from cipherlab1 import __version__, service
from cipherlab1.fileio import read_text, write_text_atomic
from cipherlab1.textprep import MODE_LETTERS_ONLY, MODE_PRESERVE, prepare_text

HERE = os.path.dirname(os.path.abspath(__file__))

# навчальні ключі (вигадані, у реальних системах так робити не можна)
EXPERIMENTS = [
    ("Проста підстановка", service.SUBSTITUTION, "ЗАХИСТ", MODE_PRESERVE),
    ("Шифр Віженера", service.VIGENERE, "ШИФР", MODE_PRESERVE),
    ("Блокова перестановка", service.BLOCK, "3 2 5 1 4", MODE_PRESERVE),
    ("Вертикальна перестановка", service.COLUMNAR, "3 1 4 2", MODE_PRESERVE),
]


def main() -> int:
    source = read_text(os.path.join(HERE, "data", "own_text.txt"))
    prepared = prepare_text(source)
    letters = len(prepare_text(source, MODE_LETTERS_ONLY))
    report = {
        "program_version": __version__,
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "source_text": source.strip(),
        "prepared_text": prepared.strip(),
        "letters_count": letters,
        "experiments": [],
    }
    lines = [f"cipherlab1 {__version__}, Python {report['python']}",
             f"Літер у тексті: {letters}", ""]
    for title, algo, key, mode in EXPERIMENTS:
        encrypted = service.encrypt(algo, prepared, key, mode)
        decrypted = service.decrypt(algo, encrypted.text, key, encrypted.pad)
        ok = decrypted.text == prepared
        report["experiments"].append({
            "title": title, "algorithm": algo, "key": key, "mode": mode,
            "ciphertext": encrypted.text, "pad": encrypted.pad,
            "decrypted": decrypted.text, "restored": ok,
        })
        lines += [f"== {title} (ключ: {key}) ==", encrypted.text.strip(),
                  f"розшифровано коректно: {ok}", ""]
        if not ok:
            print(f"ПОМИЛКА: {title} не відновив текст", file=sys.stderr)
            return 1
    out_dir = os.path.join(HERE, "results")
    os.makedirs(out_dir, exist_ok=True)
    write_text_atomic(os.path.join(out_dir, "experiment.json"),
                      json.dumps(report, ensure_ascii=False, indent=2))
    write_text_atomic(os.path.join(out_dir, "experiment.txt"), "\n".join(lines))
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
