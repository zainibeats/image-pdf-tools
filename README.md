# Weekly Receipt Tools

> **Note**: This project contains AI-generated code

Separate command line tools for weekly receipt work:

- build a JPG grid from receipt images
- append a receipt image page to an expense-report PDF
- extract receipt dates and totals with a local vision LLM

The tools are intentionally separate. Use only the action needed for the current
step.

## Tools

- `scripts/make-image-grid.py`: combines HEIC, HEIF, JPG, JPEG, and PNG images
  into one balanced JPG grid. Default image limit is 24.
- `scripts/append-image-page.py`: appends a JPG/JPEG image as a US Letter page
  at the end of an existing PDF. Default input PDF limits are 10 pages, 25 MiB,
  and a 15-second PDF parsing/rewrite timeout.
- `receipt-process`: sends receipt images to a configured local vision model,
  extracts transaction dates and totals, and writes daily summary JSON.

Original images and PDFs are always preserved.

## Setup

```bash
python -m pip install -e ".[dev]"
```

Copy `.env.example` to `.env` and point it at your local AI server if you use
`receipt-process`.

## Image Grid

Create a grid from a folder of images:

```bash
python scripts/make-image-grid.py ~/Pictures/receipts
```

This writes `image-grid.jpg` inside the input folder by default.

Common options:

```bash
python scripts/make-image-grid.py ~/Pictures/receipts -o named-image-grid.jpg
python scripts/make-image-grid.py ~/Pictures/receipts --max-images 60
python scripts/make-image-grid.py ~/Pictures/receipts --max-output-pixels 100000000
```

## Append Image To PDF

Append a JPG/JPEG image to an existing PDF:

```bash
python scripts/append-image-page.py ~/Pictures/receipts/image-grid.jpg --pdf ~/Downloads/input.pdf
```

This writes a PDF next to the image by default:

```text
~/Pictures/receipts/image-grid.pdf
```

Common options:

```bash
python scripts/append-image-page.py ~/Pictures/receipts/image-grid.jpg --pdf ~/Downloads/input.pdf -o ~/Pictures/receipts/final.pdf
python scripts/append-image-page.py ~/Desktop/image-grid.jpg --pdf ~/Downloads/input.pdf --max-pdf-pages 20
python scripts/append-image-page.py ~/Desktop/image-grid.jpg --pdf ~/Downloads/input.pdf --max-pdf-mb 50
python scripts/append-image-page.py ~/Desktop/image-grid.jpg --pdf ~/Downloads/input.pdf --pdf-timeout 30
python scripts/append-image-page.py ~/Desktop/image-grid.jpg --pdf ~/Downloads/input.pdf --refuse-unrestricted-output
```

Existing output files are not replaced unless `--overwrite` is passed.

By default, grid outputs must stay inside the input image folder, and appended
PDF outputs must stay inside either the image folder or the source PDF folder.
Pass `--allow-risky-output-path` only when an unusual destination is intentional.

## Receipt Total Extraction

Process receipt images directly with the configured local vision model:

```bash
receipt-process path/to/receipts
```

By default this writes:

- `daily_totals.json`
- `receipt_results.json`

Override output paths when needed:

```bash
receipt-process path/to/receipts --output daily_totals.json --details receipt_results.json
```

Constrain accepted receipt dates:

```bash
receipt-process path/to/receipts --min-date 2026-06-01 --max-date 2026-06-30
```

## Local Model Config

Example `.env` values:

```bash
RECEIPT_VISION_PROVIDER=openai-compatible
RECEIPT_VISION_BASE_URL=http://127.0.0.1:8000/v1
RECEIPT_VISION_MODEL=mistralai/ministral-3-3b
RECEIPT_VISION_TIMEOUT=90
RECEIPT_VISION_MAX_IMAGE_EDGE=768
```

Use `RECEIPT_VISION_PROVIDER=ollama` with
`RECEIPT_VISION_BASE_URL=http://127.0.0.1:11434` for Ollama.

## Tests

```bash
python -m pytest
```

## Notes

- `scripts/make-image-grid.py` only scans files directly inside the input
  folder. Subfolders are ignored.
- Unreadable image files are skipped and reported. If no readable images remain,
  the grid job fails.
- `scripts/append-image-page.py` preserves source pages and simple string
  metadata, but does not preserve encryption, permission restrictions,
  signatures, forms, outlines, attachments, document-level JavaScript, or
  tagged-PDF structure.
- Owner-restricted PDFs that open with an empty password are accepted by
  default, but output PDF permissions are not preserved. Pass
  `--refuse-unrestricted-output` to stop instead.
