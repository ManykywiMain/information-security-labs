"""Контрольні вектори з розділу 7 методички: прямий результат і відновлення."""

import unittest

from cipherlab1 import service
from cipherlab1.keys import inverse_permutation
from cipherlab1.textprep import ALPHABET, MODE_LETTERS_ONLY, prepare_text

# (назва, алгоритм, ключ, режим, відкритий текст, очікуваний шифротекст)
VECTORS = [
    ("Зворотний алфавіт", service.SUBSTITUTION, ALPHABET[::-1], "preserve",
     "СЛАВА УКРАЇНІ", "ІНЯЬЯ ЗОЇЯРЛС"),
    ("Віженер", service.VIGENERE, "КЛЮЧ", "preserve",
     "СЛАВА УКРАЇНІ", "ВЬЮЩК ДЇККЧЛД"),
    ("Блокова перестановка", service.BLOCK, "3 2 5 1 4", MODE_LETTERS_ONLY,
     "СЛАВАУКРАЇНІ", "АЛАСВРКЇУАНІ"),
    ("Вертикальна перестановка", service.COLUMNAR, "3 1 4 2", "preserve",
     "КРИПТОГРАФІЯ", "ИГІКТАПРЯРОФ"),
]


class ReferenceVectorTests(unittest.TestCase):
    def test_encrypt_matches_expected(self):
        for name, algo, key, mode, plain, expected in VECTORS:
            with self.subTest(vector=name):
                self.assertEqual(service.encrypt(algo, plain, key, mode).text, expected)

    def test_decrypt_restores_prepared_plaintext(self):
        for name, algo, key, mode, plain, expected in VECTORS:
            with self.subTest(vector=name):
                encrypted = service.encrypt(algo, plain, key, mode)
                restored = service.decrypt(algo, expected, key, encrypted.pad)
                self.assertEqual(restored.text, prepare_text(plain, mode))

    def test_methodology_compact_key_notation(self):
        """У розділі 7 методички ключі записані компактно: 32514 і 3142."""
        self.assertEqual(service.encrypt(service.BLOCK, "СЛАВАУКРАЇНІ", "32514", MODE_LETTERS_ONLY).text,
                         "АЛАСВРКЇУАНІ")
        self.assertEqual(service.encrypt(service.COLUMNAR, "КРИПТОГРАФІЯ", "3142").text, "ИГІКТАПРЯРОФ")

    def test_block_vector_with_space_in_letters_only_mode(self):
        """Той самий вектор зі вхідним текстом із пробілом: letters-only його вилучає."""
        result = service.encrypt(service.BLOCK, "СЛАВА УКРАЇНІ", "3 2 5 1 4", MODE_LETTERS_ONLY)
        self.assertEqual(result.text, "АЛАСВРКЇУАНІ")

    def test_inverse_permutation_from_methodology(self):
        self.assertEqual(inverse_permutation((3, 2, 5, 1, 4)), (4, 2, 1, 5, 3))


if __name__ == "__main__":
    unittest.main()
