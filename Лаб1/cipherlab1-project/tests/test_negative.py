"""Негативні сценарії: некоректні ключі, символи, режими, шифротекст."""

import unittest

from cipherlab1 import service
from cipherlab1.errors import (CipherError, KeyValidationError, ModeError,
                               TextValidationError)
from cipherlab1.keys import parse_permutation
from cipherlab1.substitution import build_table, validate_table
from cipherlab1.textprep import ALPHABET, prepare_text


class KeyValidationTests(unittest.TestCase):
    def test_empty_keys_rejected(self):
        for algorithm in service.ALGORITHMS:
            with self.subTest(algorithm=algorithm):
                with self.assertRaises(KeyValidationError):
                    service.encrypt(algorithm, "АБВ", "")

    def test_substitution_keyword_with_foreign_letter(self):
        for bad in ("KEY", "СЛОВО1", "Є Ж", "СЛОВО!", "Ы"):
            with self.subTest(key=bad):
                with self.assertRaises(KeyValidationError):
                    build_table(bad)

    def test_vigenere_keyword_with_foreign_symbol(self):
        with self.assertRaises(KeyValidationError):
            service.encrypt(service.VIGENERE, "АБВ", "КЛЮЧ2")

    def test_permutation_repeated_number(self):
        with self.assertRaises(KeyValidationError) as ctx:
            parse_permutation("1 2 2 4")
        self.assertIn("повторюється", str(ctx.exception))

    def test_permutation_number_out_of_range(self):
        for bad in ("1 2 5", "0 1 2", "1 2 3 7"):
            with self.subTest(key=bad):
                with self.assertRaises(KeyValidationError) as ctx:
                    parse_permutation(bad)
                self.assertIn("діапазоном", str(ctx.exception))

    def test_compact_and_spaced_notation_agree(self):
        self.assertEqual(parse_permutation("32514"), (3, 2, 5, 1, 4))
        self.assertEqual(parse_permutation("3 2 5 1 4"), (3, 2, 5, 1, 4))
        self.assertEqual(parse_permutation("3,2,5,1,4"), (3, 2, 5, 1, 4))
        self.assertEqual(parse_permutation("1 2 3 4 5 6 7 8 9 10"), tuple(range(1, 11)))

    def test_compact_notation_is_still_validated(self):
        for bad in ("11234", "1234568", "32517", "30214"):
            with self.subTest(key=bad):
                with self.assertRaises(KeyValidationError):
                    parse_permutation(bad)

    def test_permutation_not_numbers(self):
        for bad in ("a b c", "1 2 -3", "1.5 2", "   "):
            with self.subTest(key=bad):
                with self.assertRaises(KeyValidationError):
                    parse_permutation(bad)

    def test_table_validation(self):
        validate_table(ALPHABET[::-1])  # коректна таблиця не викликає помилки
        for bad in (ALPHABET[:-1],             # 32 літери
                    ALPHABET + "А",            # 34 літери
                    "А" * 33,                  # повтори
                    "A" + ALPHABET[1:]):       # латинська A замість А
            with self.subTest(table=bad):
                with self.assertRaises(KeyValidationError):
                    validate_table(bad)

    def test_columnar_decrypt_requires_valid_pad(self):
        with self.assertRaises(KeyValidationError):
            service.decrypt(service.COLUMNAR, "АБВГ", "1 2", None)
        for bad_pad in (-1, 2, 4):
            with self.subTest(pad=bad_pad):
                with self.assertRaises(KeyValidationError):
                    service.decrypt(service.COLUMNAR, "АБВГ", "1 2", bad_pad)

    def test_columnar_decrypt_rejects_corrupted_ciphertext(self):
        with self.assertRaises(TextValidationError):
            service.decrypt(service.COLUMNAR, "АБВ", "1 2", 0)  # довжина не кратна 2
        with self.assertRaises(TextValidationError):
            service.decrypt(service.COLUMNAR, "АБВГ", "1 2", 1)  # немає службового символу

    def test_key_checked_before_text(self):
        # і ключ, і текст некоректні: помилка має стосуватися ключа
        with self.assertRaises(KeyValidationError):
            service.encrypt(service.VIGENERE, "Hello", "")


class TextAndModeTests(unittest.TestCase):
    def test_unsupported_symbols_report_position(self):
        for bad in ("Hello", "АБВ😀", "Ы", "ё", "АБ́"):
            with self.subTest(text=bad):
                with self.assertRaises(TextValidationError) as ctx:
                    prepare_text(bad)
                self.assertIn("позиції", str(ctx.exception))

    def test_unknown_algorithm_and_mode(self):
        with self.assertRaises(ModeError):
            service.encrypt("caesar", "АБВ", "1")
        with self.assertRaises(ModeError):
            service.decrypt("caesar", "АБВ", "1")
        with self.assertRaises(ModeError):
            service.encrypt(service.VIGENERE, "АБВ", "А", mode="weird")

    def test_errors_are_cipher_errors_not_crashes(self):
        with self.assertRaises(CipherError):
            service.encrypt(service.BLOCK, "АБВ", "1 1")


if __name__ == "__main__":
    unittest.main()
