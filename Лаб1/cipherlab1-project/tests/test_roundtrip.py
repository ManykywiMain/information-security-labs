"""Зворотність Dk(Ek(x)) = x, границі, українські літери, форматування, доповнення."""

import random
import unittest

from cipherlab1 import permutations, service
from cipherlab1.textprep import ALPHABET, MODE_LETTERS_ONLY, MODE_PRESERVE, prepare_text

MESSAGES = [
    "СЛАВА УКРАЇНІ",
    "Привіт, світе!",
    "ҐЕДЗЬ ЄЖАК ЇЖАК І ІВАН",
    "Тест 123 з цифрами та знаками: (так), «ні»; а також 5 % і №7.",
    "рядок один\nрядок два\nрядок три\n",
    "А",
    "",
    "Тире — довге, тире – коротке, апостроф ʼ і ’ та '",
    "Довге речення, яке перевіряє багато літер: щука, юшка, їжак, цвях, фея, шість.",
    "Табуляція\tта   кілька   пробілів підряд",
    "ЄВРОПА",
    "Ґанок і ґрунт",
]

KEYS = {
    service.SUBSTITUTION: "БЕЗПЕКА",
    service.VIGENERE: "КЛЮЧ",
    service.BLOCK: "3 2 5 1 4",
    service.COLUMNAR: "3 1 4 2",
}


def roundtrip(algorithm, text, key, mode=MODE_PRESERVE):
    encrypted = service.encrypt(algorithm, text, key, mode)
    return service.decrypt(algorithm, encrypted.text, key, encrypted.pad).text


class RoundtripTests(unittest.TestCase):
    def test_all_algorithms_all_messages_both_modes(self):
        for algorithm, key in KEYS.items():
            for mode in (MODE_PRESERVE, MODE_LETTERS_ONLY):
                for message in MESSAGES:
                    with self.subTest(algorithm=algorithm, mode=mode, message=message):
                        self.assertEqual(roundtrip(algorithm, message, key, mode),
                                         prepare_text(message, mode))

    def test_random_valid_keys_and_messages(self):
        """Генеративний тест із фіксованим зерном (відтворюваний)."""
        rng = random.Random(2026)
        pool = ALPHABET + ALPHABET.lower() + "  0123456789.,;:!?-—«»\n"
        for _ in range(400):
            algorithm = rng.choice(list(KEYS))
            if algorithm in (service.SUBSTITUTION, service.VIGENERE):
                key = "".join(rng.choice(ALPHABET) for _ in range(rng.randint(1, 12)))
            else:
                order = list(range(1, rng.randint(1, 8) + 1))
                rng.shuffle(order)
                key = " ".join(map(str, order))
            text = "".join(rng.choice(pool) for _ in range(rng.randint(0, 60)))
            mode = rng.choice((MODE_PRESERVE, MODE_LETTERS_ONLY))
            with self.subTest(algorithm=algorithm, key=key, text=text):
                self.assertEqual(roundtrip(algorithm, text, key, mode), prepare_text(text, mode))


class UkrainianLettersTests(unittest.TestCase):
    def test_special_letters_survive_every_algorithm(self):
        for algorithm, key in KEYS.items():
            with self.subTest(algorithm=algorithm):
                text = "ҐЄІЇ ґєії"
                encrypted = service.encrypt(algorithm, text, key).text
                self.assertNotIn("�", encrypted)
                self.assertEqual(roundtrip(algorithm, text, key), "ҐЄІЇ ҐЄІЇ")

    def test_substitution_maps_special_letters_through_table(self):
        # Ґ має індекс 4, Є - 7, І - 11, Ї - 12: у зворотному алфавіті це індекси 28, 25, 21, 20
        reverse = ALPHABET[::-1]
        self.assertEqual(service.encrypt(service.SUBSTITUTION, "ҐЄІЇ", reverse).text,
                         "".join(reverse[ALPHABET.index(c)] for c in "ҐЄІЇ"))


class BoundaryTests(unittest.TestCase):
    def test_block_boundaries(self):
        key = "3 2 5 1 4"  # блок 5
        for length in (0, 1, 4, 5, 6, 9, 10, 11):
            text = ALPHABET[:length]
            with self.subTest(length=length):
                self.assertEqual(roundtrip(service.BLOCK, text, key), text)

    def test_block_incomplete_tail_unchanged(self):
        self.assertEqual(service.encrypt(service.BLOCK, "АБВГ", "3 2 5 1 4").text, "АБВГ")
        self.assertEqual(service.encrypt(service.BLOCK, "АБВГДЕЖ", "3 2 5 1 4").text[5:], "ЕЖ")

    def test_columnar_boundaries_and_padding_counts(self):
        key = "3 1 4 2"  # 4 стовпці
        for length, expected_pad in ((0, 0), (1, 3), (3, 1), (4, 0), (5, 3), (8, 0)):
            text = ALPHABET[:length]
            with self.subTest(length=length):
                encrypted = service.encrypt(service.COLUMNAR, text, key)
                self.assertEqual(encrypted.pad, expected_pad)
                self.assertEqual(service.decrypt(service.COLUMNAR, encrypted.text, key,
                                                 encrypted.pad).text, text)

    def test_single_character_and_empty_text(self):
        for algorithm, key in KEYS.items():
            for text in ("", "Я"):
                with self.subTest(algorithm=algorithm, text=text):
                    self.assertEqual(roundtrip(algorithm, text, key), text)

    def test_single_column_key(self):
        self.assertEqual(service.encrypt(service.COLUMNAR, "АБВ", "1").text, "АБВ")
        self.assertEqual(service.encrypt(service.COLUMNAR, "АБВ", "1").pad, 0)


class FormattingTests(unittest.TestCase):
    def test_substitution_keeps_spaces_digits_punctuation_and_newlines(self):
        reverse = ALPHABET[::-1]
        out = service.encrypt(service.SUBSTITUTION, "а б, 12!\nв", reverse).text
        self.assertEqual(out, "Я Ю, 12!\nЬ")

    def test_vigenere_key_not_advanced_by_foreign_symbols(self):
        # ключ БВ: перша літера +1, друга +2, пробіл ключ не споживає
        self.assertEqual(service.encrypt(service.VIGENERE, "А А", "БВ").text, "Б В")
        self.assertEqual(service.encrypt(service.VIGENERE, "А, 1 А", "БВ").text, "Б, 1 В")

    def test_vigenere_wraps_around_alphabet(self):
        self.assertEqual(service.encrypt(service.VIGENERE, "Я", "Б").text, "А")
        self.assertEqual(service.decrypt(service.VIGENERE, "А", "Б").text, "Я")

    def test_block_preserve_includes_spaces_in_blocks(self):
        # у режимі preserve пробіл - звичайна позиція блока і може змінити місце
        text = "АБ ВГД"
        encrypted = service.encrypt(service.BLOCK, text, "3 2 5 1 4")
        self.assertEqual(service.decrypt(service.BLOCK, encrypted.text, "3 2 5 1 4").text, text)
        self.assertIn(" ", encrypted.text)

    def test_letters_only_drops_everything_except_letters(self):
        self.assertEqual(prepare_text("А, б; 1 В\n", MODE_LETTERS_ONLY), "АБВ")

    def test_lowercase_is_uppercased(self):
        self.assertEqual(service.encrypt(service.VIGENERE, "слава", "а").text, "СЛАВА")

    def test_nfc_composes_decomposed_letters(self):
        decomposed = "ї" + "й"  # і + діарезис, и + бревіс
        self.assertEqual(prepare_text(decomposed), "ЇЙ")


class PaddingTests(unittest.TestCase):
    def test_only_known_number_of_service_symbols_is_removed(self):
        # у відкритому тексті вже є символи '_' наприкінці - вони не мають зникнути
        text = "АБВ__"
        key = "3 1 4 2"
        encrypted = service.encrypt(service.COLUMNAR, text, key)
        self.assertEqual(encrypted.pad, 3)
        self.assertEqual(service.decrypt(service.COLUMNAR, encrypted.text, key, 3).text, text)

    def test_pad_char_constant(self):
        self.assertEqual(permutations.PAD_CHAR, "_")


if __name__ == "__main__":
    unittest.main()
