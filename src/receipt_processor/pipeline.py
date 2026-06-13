from __future__ import annotations

from datetime import date
from pathlib import Path

from receipt_processor.aggregation import aggregate_daily_totals
from receipt_processor.models import ExtractedReceipt, ProcessingFailure
from receipt_processor.validation import is_valid_receipt
from receipt_processor.vision_llm import VisionExtractor

IMAGE_EXTENSIONS = {".heic", ".heif", ".jpg", ".jpeg", ".png", ".tif", ".tiff", ".bmp", ".webp"}


def process_directory(
    input_dir: Path,
    vision_extractor: VisionExtractor,
    *,
    max_total: float = 1000.0,
    min_date: date | None = None,
    max_date: date | None = None,
) -> tuple[dict[str, float], list[ExtractedReceipt], list[ProcessingFailure]]:
    """Process receipt images and return daily totals, accepted receipts, and failures."""
    receipts: list[ExtractedReceipt] = []
    failures: list[ProcessingFailure] = []

    for image_path in iter_image_files(input_dir):
        try:
            extraction = vision_extractor.extract(image_path)
        except Exception as exc:
            failures.append(ProcessingFailure.from_path(image_path, str(exc)))
            continue

        if extraction is None:
            failures.append(ProcessingFailure.from_path(image_path, "Vision model did not return valid JSON"))
            continue
        if not is_valid_receipt(
            extraction.date,
            extraction.total,
            max_total=max_total,
            min_date=min_date,
            max_date=max_date,
        ):
            failures.append(ProcessingFailure.from_path(image_path, "Vision model returned invalid date or total"))
            continue

        receipts.append(
            ExtractedReceipt(
                file=str(image_path),
                date=extraction.date,
                total=round(extraction.total, 2),
                confidence=round(extraction.confidence, 3),
                method="vision_llm",
            )
        )

    return aggregate_daily_totals(receipts), receipts, failures


def iter_image_files(input_dir: Path) -> list[Path]:
    """Return supported image files in deterministic order."""
    return sorted(path for path in input_dir.iterdir() if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS)
