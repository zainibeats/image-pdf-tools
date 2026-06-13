from pathlib import Path

from receipt_processor.pipeline import process_directory
from receipt_processor.vision_llm import VisionExtraction


class StubVisionExtractor:
    def __init__(self, results: dict[str, VisionExtraction | None]) -> None:
        self.results = results
        self.calls: list[Path] = []

    def extract(self, image_path: Path) -> VisionExtraction | None:
        self.calls.append(image_path)
        return self.results.get(image_path.name)


def test_pipeline_uses_vision_llm(tmp_path) -> None:
    receipt_dir = tmp_path / "receipts"
    receipt_dir.mkdir()
    (receipt_dir / "a.jpg").write_bytes(b"fake")
    (receipt_dir / "b.jpg").write_bytes(b"fake")
    vision = StubVisionExtractor(
        {
            "a.jpg": VisionExtraction(date="2026-06-01", total=12.34, confidence=0.8),
            "b.jpg": VisionExtraction(date="2026-06-01", total=7.66, confidence=0.7),
        }
    )

    daily_totals, receipts, failures = process_directory(receipt_dir, vision)

    assert daily_totals == {"2026-06-01": 20.0}
    assert [receipt.method for receipt in receipts] == ["vision_llm", "vision_llm"]
    assert failures == []
    assert [path.name for path in vision.calls] == ["a.jpg", "b.jpg"]


def test_pipeline_includes_heic_and_heif_images(tmp_path) -> None:
    receipt_dir = tmp_path / "receipts"
    receipt_dir.mkdir()
    (receipt_dir / "a.HEIC").write_bytes(b"fake")
    (receipt_dir / "b.heif").write_bytes(b"fake")
    (receipt_dir / "c.txt").write_text("not an image", encoding="utf-8")
    vision = StubVisionExtractor(
        {
            "a.HEIC": VisionExtraction(date="2026-06-01", total=12.34, confidence=0.8),
            "b.heif": VisionExtraction(date="2026-06-02", total=7.66, confidence=0.7),
        }
    )

    daily_totals, receipts, failures = process_directory(receipt_dir, vision)

    assert daily_totals == {"2026-06-01": 12.34, "2026-06-02": 7.66}
    assert [receipt.file for receipt in receipts] == [
        str(receipt_dir / "a.HEIC"),
        str(receipt_dir / "b.heif"),
    ]
    assert failures == []
    assert [path.name for path in vision.calls] == ["a.HEIC", "b.heif"]


def test_pipeline_rejects_invalid_vision_results(tmp_path) -> None:
    receipt_dir = tmp_path / "receipts"
    receipt_dir.mkdir()
    (receipt_dir / "bad.jpg").write_bytes(b"fake")
    vision = StubVisionExtractor({"bad.jpg": VisionExtraction(date="not-a-date", total=12.34)})

    daily_totals, receipts, failures = process_directory(receipt_dir, vision)

    assert daily_totals == {}
    assert receipts == []
    assert len(failures) == 1
