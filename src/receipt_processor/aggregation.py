from __future__ import annotations

from collections import defaultdict

from receipt_processor.models import ExtractedReceipt


def aggregate_daily_totals(receipts: list[ExtractedReceipt]) -> dict[str, float]:
    """Sum accepted receipt totals by ISO date."""
    daily_totals: defaultdict[str, float] = defaultdict(float)
    for receipt in receipts:
        daily_totals[receipt.date] += receipt.total

    return {date: round(total, 2) for date, total in sorted(daily_totals.items())}
