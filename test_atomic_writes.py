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


class EmptyPasswordEncryptedReader:
    is_encrypted = True

    def __init__(self) -> None:
        self.decrypt_calls: list[str] = []

    def decrypt(self, password: str) -> int:
        self.decrypt_calls.append(password)
        return 1


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

    def test_encrypted_pdf_requires_explicit_unrestricted_output_consent(self) -> None:
        reader = EmptyPasswordEncryptedReader()

        with redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            append_image_page.decrypt_reader_if_needed(
                reader,
                Path("restricted.pdf"),
                allow_unrestricted_output=False,
            )

        self.assertEqual(reader.decrypt_calls, [])

    def test_encrypted_pdf_consent_warns_about_lost_restrictions(self) -> None:
        reader = EmptyPasswordEncryptedReader()
        stderr = io.StringIO()

        with redirect_stderr(stderr):
            append_image_page.decrypt_reader_if_needed(
                reader,
                Path("restricted.pdf"),
                allow_unrestricted_output=True,
            )

        self.assertEqual(reader.decrypt_calls, [""])
        self.assertIn("will not preserve input encryption", stderr.getvalue())

    def test_grid_output_path_must_stay_inside_input_folder_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            input_dir = root / "images"
            input_dir.mkdir()
            output = root / "outside.jpg"

            with redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                make_image_grid.validate_output_path_safety(
                    output,
                    input_dir,
                    allow_risky_output_path=False,
                )

            make_image_grid.validate_output_path_safety(
                output,
                input_dir,
                allow_risky_output_path=True,
            )

    def test_grid_output_path_refuses_multiple_new_parent_folders(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            input_dir = Path(temp_dir)
            output = input_dir / "new" / "nested" / "grid.jpg"

            with redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                make_image_grid.validate_output_path_safety(
                    output,
                    input_dir,
                    allow_risky_output_path=False,
                )

    def test_append_output_path_allows_image_or_pdf_folder(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            image_dir = root / "images"
            pdf_dir = root / "pdfs"
            image_dir.mkdir()
            pdf_dir.mkdir()

            append_image_page.validate_output_path_safety(
                image_dir / "output.pdf",
                [image_dir, pdf_dir],
                allow_risky_output_path=False,
            )
            append_image_page.validate_output_path_safety(
                pdf_dir / "output.pdf",
                [image_dir, pdf_dir],
                allow_risky_output_path=False,
            )

    def test_append_output_path_refuses_reserved_windows_device_names(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "CON.pdf"

            with redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                append_image_page.validate_output_path_safety(
                    output,
                    [Path(temp_dir)],
                    allow_risky_output_path=False,
                )


if __name__ == "__main__":
    unittest.main()
