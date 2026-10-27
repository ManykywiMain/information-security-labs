"""Файли UTF-8 та консольний інтерфейс (коди завершення, атомарний запис, квадрат)."""

import contextlib
import io
import os
import tempfile
import unittest

from polybiuslab2 import fileio
from polybiuslab2.cli import main
from polybiuslab2.errors import FileIOError


def run_cli(*argv):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        try:
            code = main(list(argv))
        except SystemExit as exit_info:  # argparse
            code = exit_info.code
    return code, out.getvalue(), err.getvalue()


class TempDirCase(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.dir.cleanup)

    def path(self, name):
        return os.path.join(self.dir.name, name)


class FileTests(TempDirCase):
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


class CliTests(TempDirCase):
    def test_vectors_through_cli(self):
        cases = [
            (["--algo", "polybius-coordinates", "--lang", "ua", "--key", "БЕЗПЕКА"], "СЛАВА", "44 35 16 21 16"),
            (["--algo", "polybius-row-shift", "--lang", "en", "--key", "SECURITY"], "HELLO", "OYVVZ"),
            (["--algo", "gronsfeld", "--lang", "ua", "--key", "31415"], "СЛАВА УКРАЇНІ", "ФМҐГД ЦЛФБНРЇ"),
        ]
        for options, plain, expected in cases:
            with self.subTest(options=options):
                self.assertEqual(run_cli("encrypt", *options, "--text", plain), (0, expected, ""))
                self.assertEqual(run_cli("decrypt", *options, "--text", expected), (0, plain, ""))

    def test_square_command_and_show_square(self):
        code, out, _ = run_cli("square", "--lang", "ua", "--key", "БЕЗПЕКА")
        self.assertEqual(code, 0)
        self.assertIn("Б Е З П К А", out)
        self.assertIn("Ь Ю Я 0 1 2", out)
        code, out, err = run_cli("encrypt", "--algo", "polybius-coordinates", "--lang", "en",
                                 "--key", "SECURITY", "--text", "HELLO", "--show-square")
        self.assertEqual((code, out), (0, "32 12 35 35 42"))
        self.assertIn("S E C U R I", err)

    def test_strip_spaces_is_explicit_and_visible(self):
        base = ["--algo", "polybius-coordinates", "--lang", "ua", "--key", "БЕЗПЕКА"]
        code, out, err = run_cli("encrypt", *base, "--text", "СЛАВА УКРАЇНІ")
        self.assertEqual((code, out), (1, ""))
        self.assertIn("--strip-spaces", err)
        code, out, err = run_cli("encrypt", *base, "--text", "СЛАВА УКРАЇНІ", "--strip-spaces")
        self.assertEqual(code, 0)
        # СЛАВА УКРАЇНІ без пробілу; координати звірено вручну за квадратом БЕЗПЕКА
        self.assertEqual(out, "44 35 16 21 16 46 15 43 16 33 41 32")
        self.assertIn("Видалено пробільних символів: 1", err)
        code, out, _ = run_cli("decrypt", *base, "--text", out)
        self.assertEqual(out, "СЛАВАУКРАЇНІ")

    def test_file_roundtrip_multiline(self):
        original = "Перший рядок.\nДругий рядок із цифрами 2026.\nҐЄІЇ\n"
        fileio.write_text_atomic(self.path("in.txt"), original)
        for algo, lang, key in (("polybius-row-shift", "ua", "БЕЗПЕКА"), ("gronsfeld", "ua", "0517")):
            with self.subTest(algo=algo):
                self.assertEqual(run_cli("encrypt", "--algo", algo, "--lang", lang, "--key", key,
                                         "--input", self.path("in.txt"), "--output", self.path("e.txt"))[0], 0)
                self.assertEqual(run_cli("decrypt", "--algo", algo, "--lang", lang, "--key", key,
                                         "--input", self.path("e.txt"), "--output", self.path("d.txt"))[0], 0)
                self.assertEqual(fileio.read_text(self.path("d.txt")), original.upper())

    def test_coordinate_file_roundtrip_with_trailing_newline(self):
        fileio.write_text_atomic(self.path("plain.txt"), "СЛАВА\n")
        base = ["--algo", "polybius-coordinates", "--lang", "ua", "--key", "БЕЗПЕКА"]
        code, _, _ = run_cli("encrypt", *base, "--input", self.path("plain.txt"),
                             "--output", self.path("c.txt"), "--strip-spaces")
        self.assertEqual(code, 0)
        self.assertEqual(fileio.read_text(self.path("c.txt")), "44 35 16 21 16")
        fileio.write_text_atomic(self.path("c.txt"), "44 35 16 21 16\n")
        code, _, _ = run_cli("decrypt", *base, "--input", self.path("c.txt"),
                             "--output", self.path("p.txt"))
        self.assertEqual((code, fileio.read_text(self.path("p.txt"))), (0, "СЛАВА"))

    def test_errors_give_nonzero_code_and_message(self):
        cases = [
            ["encrypt", "--algo", "gronsfeld", "--lang", "ua", "--key", "000", "--text", "А"],
            ["encrypt", "--algo", "polybius-row-shift", "--lang", "ua", "--key", "KEY", "--text", "А"],
            ["decrypt", "--algo", "polybius-coordinates", "--lang", "ua", "--key", "БЕЗПЕКА", "--text", "67"],
        ]
        for argv in cases:
            with self.subTest(argv=argv):
                code, out, err = run_cli(*argv)
                self.assertEqual((code, out), (1, ""))
                self.assertIn("Помилка:", err)

    def test_failed_run_leaves_no_partial_output_and_keeps_existing_file(self):
        out_path = self.path("result.txt")
        run_cli("encrypt", "--algo", "gronsfeld", "--lang", "ua", "--key", "0", "--text", "АБВ",
                "--output", out_path)
        self.assertFalse(os.path.exists(out_path))
        fileio.write_text_atomic(out_path, "СТАРИЙ")
        code, _, _ = run_cli("decrypt", "--algo", "polybius-coordinates", "--lang", "ua",
                             "--key", "БЕЗПЕКА", "--text", "44 35 99", "--output", out_path)
        self.assertEqual(code, 1)
        self.assertEqual(fileio.read_text(out_path), "СТАРИЙ")
        self.assertEqual(os.listdir(self.dir.name), ["result.txt"])

    def test_option_conflicts(self):
        code, _, err = run_cli("encrypt", "--algo", "gronsfeld", "--lang", "ua", "--key", "31415",
                               "--text", "А", "--show-square")
        self.assertEqual(code, 1)
        code, _, err = run_cli("encrypt", "--algo", "polybius-row-shift", "--lang", "ua",
                               "--key", "БЕЗПЕКА", "--text", "А", "--strip-spaces")
        self.assertEqual(code, 1)
        fileio.write_text_atomic(self.path("same.txt"), "АБВ")
        code, _, err = run_cli("encrypt", "--algo", "gronsfeld", "--lang", "ua", "--key", "1",
                               "--input", self.path("same.txt"), "--output", self.path("same.txt"))
        self.assertEqual(code, 1)
        self.assertIn("збігаються", err)

    def test_usage_errors_help_and_rules(self):
        self.assertEqual(run_cli("encrypt", "--algo", "caesar", "--lang", "ua", "--key", "1",
                                 "--text", "А")[0], 2)
        self.assertEqual(run_cli("encrypt", "--algo", "gronsfeld", "--lang", "auto", "--key", "1",
                                 "--text", "А")[0], 2)  # автоматичного вибору мови немає
        code, out, _ = run_cli("--help")
        self.assertEqual(code, 0)
        self.assertIn("encrypt", out)
        code, out, _ = run_cli("rules")
        self.assertEqual(code, 0)
        self.assertIn("NFC", out)


if __name__ == "__main__":
    unittest.main()
