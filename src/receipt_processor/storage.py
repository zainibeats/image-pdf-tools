from __future__ import annotations

import json
from pathlib import Path

from receipt_processor.models import ExtractedReceipt, ProcessingFailure


def write_processing_details_json(
    path: Path,
    receipts: list[ExtractedReceipt],
    failures: list[ProcessingFailure],
) -> None:
    """Write accepted receipts and failed receipt paths."""
    payload = {
        "receipts": [receipt.to_dict() for receipt in receipts],
        "failures": [failure.__dict__ for failure in failures],
    }
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
