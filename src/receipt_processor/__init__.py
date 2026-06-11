"""Receipt processing package."""

from receipt_processor.aggregation import aggregate_daily_totals
from receipt_processor.models import ExtractedReceipt
from receipt_processor.pipeline import process_directory

__all__ = ["ExtractedReceipt", "aggregate_daily_totals", "process_directory"]
