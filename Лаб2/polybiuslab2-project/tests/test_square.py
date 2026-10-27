"""Ключовий квадрат: розмір, унікальність, дедуплікація, перевірка ключового слова."""

import unittest

from polybiuslab2.alphabets import ALPHABETS, get_alphabet
from polybiuslab2.errors import KeyValidationError, ModeError
from polybiuslab2.square import build_square, validate_cells

UA_ROWS = ("БЕЗПКА", "ВГҐДЄЖ", "ИІЇЙЛМ", "НОРСТУ", "ФХЦЧШЩ", "ЬЮЯ012")
EN_ROWS = ("SECURI", "TYABDF", "GHJKLM", "NOPQVW", "XZ0123", "456789")


class SquareConstructionTests(unittest.TestCase):
    def test_reference_squares(self):
        self.assertEqual(build_square("ua", "БЕЗПЕКА").rows, UA_ROWS)
        self.assertEqual(build_square("en", "SECURITY").rows, EN_ROWS)

    def test_size_and_uniqueness_for_both_languages(self):
        for lang, key in (("ua", "БЕЗПЕКА"), ("en", "SECURITY"), ("ua", "А"), ("en", "Z9")):
            with self.subTest(lang=lang, key=key):
                square = build_square(lang, key)
                self.assertEqual(len(square.rows), 6)
                self.assertTrue(all(len(row) == 6 for row in square.rows))
                self.assertEqual(len(set(square.cells)), 36)
                self.assertEqual(set(square.cells), set(get_alphabet(lang).base))

    def test_duplicates_removed_keeping_first_occurrence(self):
        square = build_square("ua", "БЕЗПЕКА")
        self.assertEqual(square.cells[:6], "БЕЗПКА")
        self.assertEqual(build_square("en", "BANANA").cells[:3], "BAN")

    def test_keyword_is_normalised(self):
        self.assertEqual(build_square("ua", "безпека").cells, build_square("ua", "БЕЗПЕКА").cells)
        # і + діарезис (NFD) має стати Ї
        self.assertEqual(build_square("ua", "ї").cells[0], "Ї")

    def test_digits_allowed_in_keyword_if_in_square(self):
        self.assertEqual(build_square("ua", "А1").cells[:2], "А1")
        self.assertEqual(build_square("en", "A9").cells[:2], "A9")

    def test_keyword_may_use_all_symbols(self):
        base = get_alphabet("en").base
        self.assertEqual(build_square("en", base[::-1]).cells, base[::-1])

    def test_coordinates_are_inverse_of_symbols(self):
        square = build_square("ua", "БЕЗПЕКА")
        for symbol, position in square.coords.items():
            self.assertEqual(square.symbols[position], symbol)
        self.assertEqual(square.coords["Б"], (1, 1))
        self.assertEqual(square.coords["2"], (6, 6))

    def test_render_contains_all_rows(self):
        text = build_square("en", "SECURITY").render()
        for row in EN_ROWS:
            self.assertIn(" ".join(row), text)


class KeywordValidationTests(unittest.TestCase):
    def test_empty_keyword(self):
        with self.assertRaises(KeyValidationError):
            build_square("ua", "")

    def test_foreign_symbols_in_keyword(self):
        for lang, bad in (("ua", "SECURITY"), ("ua", "БЕЗ ПЕКА"), ("ua", "БЕЗПЕКА3"),
                          ("ua", "Ы"), ("en", "БЕЗПЕКА"), ("en", "SEC-URITY"), ("en", "Ä")):
            with self.subTest(lang=lang, key=bad):
                with self.assertRaises(KeyValidationError):
                    build_square(lang, bad)

    def test_keyword_without_letters(self):
        for lang, bad in (("ua", "012"), ("en", "2026"), ("ua", "0")):
            with self.subTest(lang=lang, key=bad):
                with self.assertRaises(KeyValidationError) as ctx:
                    build_square(lang, bad)
                self.assertIn("літеру", str(ctx.exception))

    def test_language_is_never_guessed(self):
        # українське слово з латинським алфавітом - помилка, а не автоматична зміна мови
        with self.assertRaises(KeyValidationError):
            build_square("en", "СЛАВА")
        with self.assertRaises(ModeError):
            build_square("de", "KEY")

    def test_validate_cells_rejects_broken_squares(self):
        alphabet = ALPHABETS["en"]
        good = alphabet.base
        validate_cells(good, alphabet)
        for bad in (good[:-1], good + "A", "A" * 36, good[:-1] + "Б"):
            with self.subTest(cells=bad):
                with self.assertRaises(KeyValidationError):
                    validate_cells(bad, alphabet)


if __name__ == "__main__":
    unittest.main()
