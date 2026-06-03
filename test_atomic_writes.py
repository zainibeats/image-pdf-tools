from __future__ import annotations

import importlib.util
import io
import sys
import tempfile
import unittest
from contextlib import redirect_stderr
from pathlib import Path


def load_script_module(name: str, filename: str) -> object:
    spec = importlib.util.spec_from_file_location(name, Path(__file__).with_name(filename))
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load {filename}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


append_image_page = load_script_module("append_image_page", "append-image-page.py")
make_image_grid = load_script_module("make_image_grid", "make-image-grid.py")


class BytesWriter:
    def __init__(self, data: bytes) -> None:
        self.data = data

    def write(self, file_obj: object) -> None:
        file_obj.write(self.data)


class BytesImage:
    def __init__(self, data: bytes) -> None:
        self.data = data

    def save(self, file_obj: object, image_format: str, **save_kwargs: object) -> None:
        file_obj.write(self.data)


class AtomicWriteTests(unittest.TestCase):
    def test_pdf_write_without_overwrite_refuses_existing_destination(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            destination = Path(temp_dir) / "output.pdf"
            destination.write_bytes(b"existing")

            with redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                append_image_page.write_pdf_atomically(
                    BytesWriter(b"new"),
                    destination,
                    overwrite=False,
                )

            self.assertEqual(destination.read_bytes(), b"existing")
            self.assertFalse(list(Path(temp_dir).glob(".output.pdf.*")))

    def test_pdf_write_with_overwrite_replaces_existing_destination(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            destination = Path(temp_dir) / "output.pdf"
            destination.write_bytes(b"existing")

            append_image_page.write_pdf_atomically(
                BytesWriter(b"new"),
                destination,
                overwrite=True,
            )

            self.assertEqual(destination.read_bytes(), b"new")

    def test_image_write_without_overwrite_refuses_existing_destination(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            destination = Path(temp_dir) / "output.jpg"
            destination.write_bytes(b"existing")

            with redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                make_image_grid.save_image_atomically(
                    BytesImage(b"new"),
                    destination,
                    "JPEG",
                    overwrite=False,
                )

            self.assertEqual(destination.read_bytes(), b"existing")
            self.assertFalse(list(Path(temp_dir).glob(".output.jpg.*")))

    def test_image_write_with_overwrite_replaces_existing_destination(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            destination = Path(temp_dir) / "output.jpg"
            destination.write_bytes(b"existing")

            make_image_grid.save_image_atomically(
                BytesImage(b"new"),
                destination,
                "JPEG",
                overwrite=True,
            )

            self.assertEqual(destination.read_bytes(), b"new")


if __name__ == "__main__":
    unittest.main()
