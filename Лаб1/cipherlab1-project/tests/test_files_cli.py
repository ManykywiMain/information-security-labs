"""Файли UTF-8 та консольний інтерфейс (коди завершення, атомарний запис)."""

import contextlib
import io
import os
import tempfile
import unittest

from cipherlab1 import fileio
from cipherlab1.cli import main
from cipherlab1.errors import FileIOError


def run_cli(*argv):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        try:
            code = main(list(argv))
        except SystemExit as exit_info:  # argparse
            code = exit_info.code
    return code, out.getvalue(), err.getvalue()


class FileTests(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.dir.cleanup)

    def path(self, name):
        return os.path.join(self.dir.name, name)

    def test_write_and_read_multiline_utf8_with_trailing_newline(self):
        text = "СЛАВА УКРАЇНІ\nҐЄІЇ\n"
        fileio.write_text_atomic(self.path("a.txt"), text)
        with open(self.path("a.txt"), "rb") as handle:
            self.assertEqual(handle.read(), text.encode("utf-8"))
        self.assertEqual(fileio.read_text(self.path("a.txt")), text)

    def test_bom_is_ignored_and_crlf_normalised(self):
        with open(self.path("b.txt"), "wb") as handle:
            handle.write(b"\xef\xbb\xbf" + "АБ\r\nВГ".encode("utf-8"))
        self.assertEqual(fileio.read_text(self.path("b.txt")), "АБ\nВГ")

    def test_invalid_utf8_and_missing_file(self):
        with open(self.path("c.txt"), "wb") as handle:
            handle.write("текст".encode("cp1251"))
        with self.assertRaises(FileIOError):
            fileio.read_text(self.path("c.txt"))
        with self.assertRaises(FileIOError):
            fileio.read_text(self.path("missing.txt"))

    def test_atomic_write_leaves_no_temporary_files(self):
        fileio.write_text_atomic(self.path("d.txt"), "ТЕСТ")
        self.assertEqual(os.listdir(self.dir.name), ["d.txt"])


class CliTests(FileTests):
    def test_encrypt_and_decrypt_text(self):
        code, out, _ = run_cli("encrypt", "--algo", "vigenere", "--key", "КЛЮЧ",
                               "--text", "СЛАВА УКРАЇНІ")
        self.assertEqual((code, out), (0, "ВЬЮЩК ДЇККЧЛД"))
        code, out, _ = run_cli("decrypt", "--algo", "vigenere", "--key", "КЛЮЧ",
                               "--text", "ВЬЮЩК ДЇККЧЛД")
        self.assertEqual((code, out), (0, "СЛАВА УКРАЇНІ"))

    def test_file_roundtrip_multiline_for_every_algorithm(self):
        original = "Перший рядок.\nДругий рядок із цифрами 123.\nҐЄІЇ\n"
        keys = {"substitution": "БЕЗПЕКА", "vigenere": "КЛЮЧ",
                "block": "3 2 5 1 4", "columnar": "3 1 4 2"}
        fileio.write_text_atomic(self.path("in.txt"), original)
        for algo, key in keys.items():
            with self.subTest(algo=algo):
                code, _, err = run_cli("encrypt", "--algo", algo, "--key", key,
                                       "--input", self.path("in.txt"),
                                       "--output", self.path("enc.txt"))
                self.assertEqual(code, 0)
                pad = ["--pad", err.split("--pad ")[1].split(" ")[0]] if algo == "columnar" else []
                code, _, _ = run_cli("decrypt", "--algo", algo, "--key", key,
                                     "--input", self.path("enc.txt"),
                                     "--output", self.path("dec.txt"), *pad)
                self.assertEqual(code, 0)
                self.assertEqual(fileio.read_text(self.path("dec.txt")), original.upper())

    def test_error_gives_nonzero_exit_code_and_message(self):
        code, out, err = run_cli("encrypt", "--algo", "block", "--key", "1 1", "--text", "АБВ")
        self.assertEqual(code, 1)
        self.assertEqual(out, "")
        self.assertIn("Помилка:", err)

    def test_failed_run_leaves_no_partial_output_and_keeps_existing_file(self):
        out_path = self.path("result.txt")
        run_cli("encrypt", "--algo", "vigenere", "--key", "", "--text", "АБВ", "--output", out_path)
        self.assertFalse(os.path.exists(out_path))
        fileio.write_text_atomic(out_path, "СТАРИЙ")
        code, _, _ = run_cli("encrypt", "--algo", "vigenere", "--key", "КЛЮЧ",
                             "--text", "Hello", "--output", out_path)
        self.assertEqual(code, 1)
        self.assertEqual(fileio.read_text(out_path), "СТАРИЙ")
        self.assertEqual(os.listdir(self.dir.name), ["result.txt"])

    def test_same_input_and_output_rejected(self):
        fileio.write_text_atomic(self.path("same.txt"), "АБВ")
        code, _, err = run_cli("encrypt", "--algo", "vigenere", "--key", "Б",
                               "--input", self.path("same.txt"), "--output", self.path("same.txt"))
        self.assertEqual(code, 1)
        self.assertIn("збігаються", err)

    def test_columnar_decrypt_without_pad_is_error(self):
        code, _, err = run_cli("decrypt", "--algo", "columnar", "--key", "1 2", "--text", "АБВГ")
        self.assertEqual(code, 1)
        self.assertIn("--pad", err)

    def test_usage_errors_and_help(self):
        code, _, _ = run_cli("encrypt", "--algo", "caesar", "--key", "1", "--text", "А")
        self.assertEqual(code, 2)
        code, out, _ = run_cli("--help")
        self.assertEqual(code, 0)
        self.assertIn("encrypt", out)
        code, out, _ = run_cli("rules")
        self.assertEqual(code, 0)
        self.assertIn("NFC", out)


if __name__ == "__main__":
    unittest.main()
