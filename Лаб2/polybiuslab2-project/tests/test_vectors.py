"""Шість контрольних векторів з розділу 7: прямий результат і відновлення."""

import unittest

from polybiuslab2 import service

# (назва, алгоритм, мова, ключ, відкритий текст, очікуваний результат)
VECTORS = [
    ("Полібій coordinates, укр.", service.POLYBIUS_COORDINATES, "ua", "БЕЗПЕКА",
     "СЛАВА", "44 35 16 21 16"),
    ("Полібій coordinates, лат.", service.POLYBIUS_COORDINATES, "en", "SECURITY",
     "HELLO", "32 12 35 35 42"),
    ("Полібій row shift, укр.", service.POLYBIUS_ROW_SHIFT, "ua", "БЕЗПЕКА",
     "СЛАВА", "ЧТЖИЖ"),
    ("Полібій row shift, лат.", service.POLYBIUS_ROW_SHIFT, "en", "SECURITY",
     "HELLO", "OYVVZ"),
    ("Гронсфельд, укр.", service.GRONSFELD, "ua", "31415",
     "СЛАВА УКРАЇНІ", "ФМҐГД ЦЛФБНРЇ"),
    ("Гронсфельд, лат.", service.GRONSFELD, "en", "2718",
     "HELLO WORLD", "JLMTQ DPZNK"),
]


class ReferenceVectorTests(unittest.TestCase):
    def test_encrypt_matches_expected(self):
        for name, algo, lang, key, plain, expected in VECTORS:
            with self.subTest(vector=name):
                self.assertEqual(service.encrypt(algo, lang, plain, key), expected)

    def test_decrypt_restores_plaintext(self):
        for name, algo, lang, key, plain, expected in VECTORS:
            with self.subTest(vector=name):
                self.assertEqual(service.decrypt(algo, lang, expected, key), plain)

    def test_lowercase_input_gives_same_results(self):
        for name, algo, lang, key, plain, expected in VECTORS:
            with self.subTest(vector=name):
                self.assertEqual(service.encrypt(algo, lang, plain.lower(), key.lower()
                                                 if algo != service.GRONSFELD else key), expected)


if __name__ == "__main__":
    unittest.main()
