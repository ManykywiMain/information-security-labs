"""Координатний режим і циклічний зсув за рядками."""

import unittest

from polybiuslab2 import service
from polybiuslab2.errors import TextValidationError

COORD = service.POLYBIUS_COORDINATES
SHIFT = service.POLYBIUS_ROW_SHIFT


class CoordinateTests(unittest.TestCase):
    def test_first_and_last_cells(self):
        # у квадраті БЕЗПЕКА перший символ - Б (11), останній - цифра 2 (66)
        self.assertEqual(service.encrypt(COORD, "ua", "Б2", "БЕЗПЕКА"), "11 66")
        self.assertEqual(service.decrypt(COORD, "ua", "11 66", "БЕЗПЕКА"), "Б2")
        self.assertEqual(service.encrypt(COORD, "en", "S9", "SECURITY"), "11 66")

    def test_first_and_last_rows(self):
        first_row = "БЕЗПКА"
        last_row = "ЬЮЯ012"
        self.assertEqual(service.encrypt(COORD, "ua", first_row, "БЕЗПЕКА"),
                         "11 12 13 14 15 16")
        self.assertEqual(service.encrypt(COORD, "ua", last_row, "БЕЗПЕКА"),
                         "61 62 63 64 65 66")

    def test_row_comes_before_column(self):
        # Л лежить у рядку 3, стовпці 5 -> 35, а не 53
        self.assertEqual(service.encrypt(COORD, "ua", "Л", "БЕЗПЕКА"), "35")

    def test_invalid_tokens_are_rejected_not_skipped(self):
        # Увага: 61 тут немає навмисно - (6,1) є допустимою клітинкою квадрата (див. наступний тест)
        for bad in ("00", "17", "67", "07", "71", "7", "123", "AB", "4 4", "44,35", "44-35",
                    "44 xx", "44 35 7", "0", "٤٤", "44\n35", "44  35"):
            with self.subTest(ciphertext=bad):
                with self.assertRaises(TextValidationError):
                    service.decrypt(COORD, "ua", bad, "БЕЗПЕКА")

    def test_token_61_is_a_valid_cell_unlike_67(self):
        """Методичка називає 61 серед помилкових, але за її ж правилом (дві цифри 1-6) це
        рядок 6, стовпець 1, тобто Ь. Інакше шифрування само створювало б недешифровний токен."""
        self.assertEqual(service.decrypt(COORD, "ua", "61", "БЕЗПЕКА"), "Ь")
        self.assertEqual(service.encrypt(COORD, "ua", "Ь", "БЕЗПЕКА"), "61")
        with self.assertRaises(TextValidationError):
            service.decrypt(COORD, "ua", "67", "БЕЗПЕКА")

    def test_error_names_the_bad_token_and_position(self):
        with self.assertRaises(TextValidationError) as ctx:
            service.decrypt(COORD, "ua", "44 35 67 21", "БЕЗПЕКА")
        message = str(ctx.exception)
        self.assertIn("'67'", message)
        self.assertIn("3", message)

    def test_trailing_newline_from_file_is_not_a_token(self):
        self.assertEqual(service.decrypt(COORD, "ua", "44 35 16 21 16\n", "БЕЗПЕКА"), "СЛАВА")

    def test_empty_text(self):
        self.assertEqual(service.encrypt(COORD, "ua", "", "БЕЗПЕКА"), "")
        self.assertEqual(service.decrypt(COORD, "ua", "", "БЕЗПЕКА"), "")

    def test_strict_mode_rejects_spaces_punctuation_and_foreign_letters(self):
        for text in ("СЛАВА УКРАЇНІ", "СЛАВА!", "СЛАВА\n", "SLAVA", "Ы"):
            with self.subTest(text=text):
                with self.assertRaises(TextValidationError):
                    service.encrypt(COORD, "ua", text, "БЕЗПЕКА")

    def test_space_error_mentions_explicit_strip_operation(self):
        with self.assertRaises(TextValidationError) as ctx:
            service.encrypt(COORD, "ua", "А Б", "БЕЗПЕКА")
        self.assertIn("--strip-spaces", str(ctx.exception))

    def test_language_is_not_guessed_for_text(self):
        with self.assertRaises(TextValidationError):
            service.encrypt(COORD, "en", "СЛАВА", "SECURITY")
        with self.assertRaises(TextValidationError):
            service.encrypt(COORD, "ua", "HELLO", "БЕЗПЕКА")

    def test_digits_outside_ukrainian_square_are_rejected_but_latin_digits_work(self):
        with self.assertRaises(TextValidationError):
            service.encrypt(COORD, "ua", "3", "БЕЗПЕКА")  # у квадраті лише 0 1 2
        self.assertEqual(service.encrypt(COORD, "en", "3", "SECURITY"), "56")


class RowShiftTests(unittest.TestCase):
    def test_wrap_from_row_six_to_row_one_and_back(self):
        self.assertEqual(service.encrypt(SHIFT, "ua", "Ь", "БЕЗПЕКА"), "Б")  # (6,1) -> (1,1)
        self.assertEqual(service.decrypt(SHIFT, "ua", "Б", "БЕЗПЕКА"), "Ь")
        self.assertEqual(service.encrypt(SHIFT, "en", "9", "SECURITY"), "I")  # (6,6) -> (1,6)
        self.assertEqual(service.decrypt(SHIFT, "en", "I", "SECURITY"), "9")

    def test_ordinary_shift_down(self):
        self.assertEqual(service.encrypt(SHIFT, "ua", "Б", "БЕЗПЕКА"), "В")  # (1,1) -> (2,1)

    def test_whole_square_is_a_permutation_with_period_six(self):
        text = "БЕЗПКАВГҐДЄЖИІЇЙЛМНОРСТУФХЦЧШЩЬЮЯ012"
        current = text
        for _ in range(6):
            current = service.encrypt(SHIFT, "ua", current, "БЕЗПЕКА")
        self.assertEqual(current, text)

    def test_foreign_symbols_are_preserved(self):
        self.assertEqual(service.encrypt(SHIFT, "ua", "СЛАВА, СЛАВА!\n", "БЕЗПЕКА"),
                         "ЧТЖИЖ, ЧТЖИЖ!\n")
        # цифра 3 лежить поза українським квадратом, а 0 - усередині
        self.assertEqual(service.encrypt(SHIFT, "ua", "3", "БЕЗПЕКА"), "3")
        self.assertEqual(service.encrypt(SHIFT, "ua", "0", "БЕЗПЕКА"), "П")  # (6,4) -> (1,4)

    def test_latin_letters_are_foreign_for_ukrainian_square(self):
        self.assertEqual(service.encrypt(SHIFT, "ua", "HELLO", "БЕЗПЕКА"), "HELLO")

    def test_differs_from_coordinates_mode(self):
        self.assertNotEqual(service.encrypt(SHIFT, "ua", "СЛАВА", "БЕЗПЕКА"),
                            service.encrypt(COORD, "ua", "СЛАВА", "БЕЗПЕКА"))


class SpecialLettersTests(unittest.TestCase):
    def test_ukrainian_special_letters_and_latin_edges(self):
        for algo in (COORD, SHIFT):
            for lang, key, text in (("ua", "БЕЗПЕКА", "ҐЄІЇ"), ("en", "SECURITY", "AZ")):
                with self.subTest(algo=algo, lang=lang):
                    encrypted = service.encrypt(algo, lang, text, key)
                    self.assertEqual(service.decrypt(algo, lang, encrypted, key), text)

    def test_special_letters_coordinates(self):
        # Ґ (2,3), Є (2,5), І (3,2), Ї (3,3)
        self.assertEqual(service.encrypt(COORD, "ua", "ҐЄІЇ", "БЕЗПЕКА"), "23 25 32 33")
        # Latin A (2,3), Z (5,2)
        self.assertEqual(service.encrypt(COORD, "en", "AZ", "SECURITY"), "23 52")


if __name__ == "__main__":
    unittest.main()
