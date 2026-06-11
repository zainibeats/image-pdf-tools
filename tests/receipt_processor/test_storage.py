import json

from receipt_processor.models import ExtractedReceipt, ProcessingFailure
from receipt_processor.storage import write_processing_details_json


def test_writes_processing_details_json(tmp_path) -> None:
    output_path = tmp_path / "details.json"

    write_processing_details_json(
        output_path,
        [ExtractedReceipt("a.jpg", "2026-06-01", 12.34, 0.9, "vision_llm")],
        [ProcessingFailure("b.jpg", "failed")],
    )

    assert json.loads(output_path.read_text(encoding="utf-8")) == {
        "failures": [{"file": "b.jpg", "reason": "failed"}],
        "receipts": [
            {
                "confidence": 0.9,
                "date": "2026-06-01",
                "file": "a.jpg",
                "method": "vision_llm",
                "total": 12.34,
            }
        ],
    }
