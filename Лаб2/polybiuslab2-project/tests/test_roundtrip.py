"""Зворотність Dk(Ek(x)) = x для кожного режиму, обох мов, у тому числі випадкових."""

import random
import unittest

from polybiuslab2 import service
from polybiuslab2.alphabets import get_alphabet
from polybiuslab2.textprep import normalize_text

COORD, SHIFT, GRON = service.POLYBIUS_COORDINATES, service.POLYBIUS_ROW_SHIFT, service.GRONSFELD

# Повідомлення для режимів, що зберігають сторонні символи
FREE_TEXT = {
    "ua": ["СЛАВА УКРАЇНІ", "Привіт, світе!", "ҐЄІЇ ґєії", "Тест 2026: так/ні.", "один\nдва\nтри\n",
           "А", "", "Тире — довге, «лапки» та ʼапострофʼ", "Hello перемішано з текстом 123",
           "Довге речення з багатьма літерами: щука, юшка, їжак, цвях, фея, шість.",
           "ЄВРОПА", "Ґанок і ґрунт"],
    "en": ["HELLO WORLD", "Hello, world!", "AZ az", "Test 2026: yes/no.", "one\ntwo\nthree\n",
           "A", "", "Dash — long, «quotes» and 'apostrophes'", "Привіт перемішано with text 123",
           "The quick brown fox jumps over the lazy dog 0123456789.", "ZEBRA", "Quizzical"],
}
KEYWORDS = {"ua": "БЕЗПЕКА", "en": "SECURITY"}
DIGIT_KEYS = ["31415", "0123", "9", "2718", "1000000", "90210"]


def expected_prepared(algorithm, language, text):
    alphabet = get_alphabet(language)
    supported = alphabet.letters if algorithm == GRON else alphabet.base
    return normalize_text(text, supported)


class RoundtripTests(unittest.TestCase):
    def test_row_shift_and_gronsfeld_all_messages(self):
        for lang in ("ua", "en"):
            for message in FREE_TEXT[lang]:
                for algo, keys in ((SHIFT, [KEYWORDS[lang]]), (GRON, DIGIT_KEYS)):
                    for key in keys:
                        with self.subTest(algo=algo, lang=lang, key=key, message=message):
                            encrypted = service.encrypt(algo, lang, message, key)
                            self.assertEqual(service.decrypt(algo, lang, encrypted, key),
                                             expected_prepared(algo, lang, message))

    def test_coordinates_all_square_messages(self):
        for lang in ("ua", "en"):
            base = get_alphabet(lang).base
            messages = ["", base[0], base[-1], base, base[::-1], base.lower(),
                        base[:5] * 3, "".join(reversed(base[:10]))]
            messages.append("ҐЄІЇ" if lang == "ua" else "AZ")
            for key in (KEYWORDS[lang], base[3], base[::-1]):
                for message in messages:
                    with self.subTest(lang=lang, key=key, message=message):
                        encrypted = service.encrypt(COORD, lang, message, key)
                        self.assertEqual(service.decrypt(COORD, lang, encrypted, key),
                                         expected_prepared(COORD, lang, message))

    def test_random_keys_and_messages(self):
        """Генеративний тест із фіксованим зерном (відтворюваний)."""
        rng = random.Random(2026)
        for _ in range(600):
            lang = rng.choice(("ua", "en"))
            alphabet = get_alphabet(lang)
            algo = rng.choice((COORD, SHIFT, GRON))
            if algo == GRON:
                key = "".join(rng.choice("0123456789") for _ in range(rng.randint(1, 15)))
                if set(key) == {"0"}:
                    key += "7"
                pool = alphabet.letters + alphabet.letters.lower() + " 0123456789.,;!?-—«»\n"
            else:
                key = rng.choice(alphabet.letters) + "".join(
                    rng.choice(alphabet.base) for _ in range(rng.randint(0, 12)))
                if algo == COORD:
                    pool = alphabet.base + alphabet.base.lower()
                else:
                    pool = alphabet.base + alphabet.base.lower() + " 3456789.,;!?-—«»\n"
            text = "".join(rng.choice(pool) for _ in range(rng.randint(0, 80)))
            with self.subTest(algo=algo, lang=lang, key=key, text=text):
                encrypted = service.encrypt(algo, lang, text, key)
                self.assertEqual(service.decrypt(algo, lang, encrypted, key),
                                 expected_prepared(algo, lang, text))

    def test_every_symbol_of_square_survives_row_shift_both_directions(self):
        for lang in ("ua", "en"):
            base = get_alphabet(lang).base
            with self.subTest(lang=lang):
                shifted = service.encrypt(SHIFT, lang, base, KEYWORDS[lang])
                self.assertEqual(sorted(shifted), sorted(base))
                self.assertEqual(service.decrypt(SHIFT, lang, shifted, KEYWORDS[lang]), base)


if __name__ == "__main__":
    unittest.main()
