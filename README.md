# Weekly Receipt Tools

> **Note**: This project contains AI-generated code

Separate command line tools for weekly receipt work:

- build a JPG grid from receipt images
- append a receipt image page to an expense-report PDF
- extract receipt dates and totals with a local vision LLM

The tools are intentionally separate. Use only the action needed for the current
step. Original images and PDFs are always preserved.

## Setup

```bash
python -m pip install -e ".[dev]"
```

Copy `.env.example` to `.env` and point it at your local AI server if you use
`receipt-process`.

## Tools

- [`scripts/make-image-grid.py`](docs/image-grid.md): combines HEIC, HEIF, JPG,
  JPEG, and PNG images into one balanced JPG grid.
- [`scripts/append-image-page.py`](docs/append-image-page.md): appends a
  JPG/JPEG image as a US Letter page at the end of an existing PDF.
- [`receipt-process`](docs/receipt-processor.md): extracts receipt dates and
  totals with a configured local vision model.

## Quick Examples

```bash
python scripts/make-image-grid.py ~/Pictures/receipts
python scripts/append-image-page.py ~/Pictures/receipts/image-grid.jpg --pdf ~/Downloads/input.pdf
receipt-process ~/Pictures/receipts
```

## Project Docs

- [Image grid usage](docs/image-grid.md)
- [Append image to PDF usage](docs/append-image-page.md)
- [Receipt processor usage](docs/receipt-processor.md)
- [Receipt processor internals](docs/receipt-processor-internals.md)

## Tests

```bash
python -m pytest
```
