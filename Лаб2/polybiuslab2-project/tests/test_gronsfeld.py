"""Шифр Гронсфельда: ключі, просування ключа, модуль алфавіту, форматування."""

import unittest

from polybiuslab2 import service
from polybiuslab2.errors import KeyValidationError

G = service.GRONSFELD


class KeyTests(unittest.TestCase):
    def test_leading_zero_is_preserved(self):
        # ключ "0123": зсуви 0,1,2,3
        self.assertEqual(service.encrypt(G, "ua", "АААА", "0123"), "АБВГ")
        # ключ - рядок, а не число: "01" і "1" - різні ключі
        self.assertEqual(service.encrypt(G, "ua", "АА", "01"), "АБ")
        self.assertEqual(service.encrypt(G, "ua", "АА", "1"), "ББ")

    def test_key_nine(self):
        self.assertEqual(service.encrypt(G, "ua", "Я", "9"), "Ж")      # 32 + 9 = 41 -> 8
        self.assertEqual(service.encrypt(G, "en", "Z", "9"), "I")      # 25 + 9 = 34 -> 8
        self.assertEqual(service.decrypt(G, "ua", "Ж", "9"), "Я")

    def test_key_longer_than_text(self):
        key = "12345678901234567890"
        self.assertEqual(service.encrypt(G, "en", "ABC", key), "BDF")
        self.assertEqual(service.decrypt(G, "en", "BDF", key), "ABC")

    def test_key_shorter_than_text_repeats(self):
        self.assertEqual(service.encrypt(G, "en", "AAAAA", "12"), "BCBCB")

    def test_invalid_keys(self):
        for bad in ("", "000", "0", "12a", "1 2", "-1", "1.5", "１２", "²", "٣"):
            with self.subTest(key=bad):
                with self.assertRaises(KeyValidationError):
                    service.encrypt(G, "ua", "СЛАВА", bad)
                with self.assertRaises(KeyValidationError):
                    service.decrypt(G, "ua", "СЛАВА", bad)

    def test_key_error_precedes_text_processing(self):
        with self.assertRaises(KeyValidationError):
            service.encrypt(G, "ua", "\ud800", "000")


class AlphabetModuloTests(unittest.TestCase):
    def test_wrap_modulo_33_and_26(self):
        self.assertEqual(service.encrypt(G, "ua", "Я", "1"), "А")
        self.assertEqual(service.encrypt(G, "en", "Z", "1"), "A")
        self.assertEqual(service.decrypt(G, "ua", "А", "1"), "Я")
        self.assertEqual(service.decrypt(G, "en", "A", "1"), "Z")

    def test_special_ukrainian_letters_are_in_alphabet(self):
        self.assertEqual(service.encrypt(G, "ua", "Г", "1"), "Ґ")
        self.assertEqual(service.encrypt(G, "ua", "Д", "3"), "Ж")  # Д(5) + 3 = Ж(8)
        self.assertEqual(service.encrypt(G, "ua", "Ґ", "1"), "Д")  # Ґ(4) + 1 = Д(5)
        self.assertEqual(service.encrypt(G, "ua", "ЄІЇ", "111"), "ЖЇЙ")

    def test_language_is_explicit_foreign_letters_untouched(self):
        self.assertEqual(service.encrypt(G, "ua", "HELLO", "31415"), "HELLO")
        self.assertEqual(service.encrypt(G, "en", "СЛАВА", "31415"), "СЛАВА")


class FormattingTests(unittest.TestCase):
    def test_foreign_symbols_do_not_advance_the_key(self):
        self.assertEqual(service.encrypt(G, "en", "A A", "12"), "B C")
        self.assertEqual(service.encrypt(G, "en", "A, 1 A!", "12"), "B, 1 C!")
        self.assertEqual(service.encrypt(G, "ua", "А\nА", "12"), "Б\nВ")

    def test_digits_and_punctuation_unchanged(self):
        self.assertEqual(service.encrypt(G, "ua", "СЛАВА, 2026!", "31415"), "ФМҐГД, 2026!")

    def test_lowercase_is_uppercased(self):
        self.assertEqual(service.encrypt(G, "ua", "слава", "31415"), "ФМҐГД")
        self.assertEqual(service.encrypt(G, "en", "hello", "2718"), "JLMTQ")

    def test_nfc_composed_before_processing(self):
        self.assertEqual(service.encrypt(G, "ua", "ї", "1"), service.encrypt(G, "ua", "Ї", "1"))

    def test_empty_text(self):
        self.assertEqual(service.encrypt(G, "ua", "", "31415"), "")
        self.assertEqual(service.decrypt(G, "en", "", "2718"), "")


if __name__ == "__main__":
    unittest.main()
