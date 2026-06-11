from __future__ import annotations

from datetime import date, datetime


def parse_iso_date(value: str) -> date | None:
    """Parse YYYY-MM-DD dates without accepting alternate formats."""
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None


def is_valid_total(value: float, max_total: float = 1000.0) -> bool:
    """Accept positive totals up to the configured ceiling."""
    return 0.0 < value <= max_total


def is_valid_date(
    value: str,
    *,
    min_year: int = 2000,
    max_year: int = 2100,
    min_date: date | None = None,
    max_date: date | None = None,
) -> bool:
    """Validate receipt dates against broad year bounds and optional CLI bounds."""
    parsed = parse_iso_date(value)
    if parsed is None or not min_year <= parsed.year <= max_year:
        return False
    if min_date is not None and parsed < min_date:
        return False
    if max_date is not None and parsed > max_date:
        return False
    return True


def is_valid_receipt(
    date_value: str | None,
    total: float | None,
    max_total: float = 1000.0,
    *,
    min_date: date | None = None,
    max_date: date | None = None,
) -> bool:
    """Validate the required fields from a vision extraction."""
    return (
        date_value is not None
        and total is not None
        and is_valid_date(date_value, min_date=min_date, max_date=max_date)
        and is_valid_total(total, max_total)
    )
