"""Робота з UTF-8 файлами. Запис атомарний: результат або повністю є, або його немає."""

from __future__ import annotations

import os
import tempfile

from .errors import FileIOError


def read_text(path: str) -> str:
    """Прочитати UTF-8 файл (BOM ігнорується, переноси рядків зводяться до \\n)."""
    try:
        with open(path, "r", encoding="utf-8-sig") as handle:
            return handle.read()
    except FileNotFoundError:
        raise FileIOError(f"Файл не знайдено: {path}") from None
    except UnicodeDecodeError as error:
        raise FileIOError(f"Файл {path} не є коректним UTF-8 ({error.reason}).") from None
    except OSError as error:
        raise FileIOError(f"Не вдалося прочитати {path}: {error.strerror or error}.") from None


def write_text_atomic(path: str, text: str) -> None:
    """Записати у тимчасовий файл поруч і підмінити цільовий одним os.replace."""
    directory = os.path.dirname(os.path.abspath(path))
    temp_path = None
    try:
        handle, temp_path = tempfile.mkstemp(dir=directory, prefix=".tmp_", suffix=".part")
        with os.fdopen(handle, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(text)
        os.replace(temp_path, path)
        temp_path = None
    except OSError as error:
        raise FileIOError(f"Не вдалося записати {path}: {error.strerror or error}.") from None
    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)
