# Append Image To PDF

`scripts/append-image-page.py` appends a JPG/JPEG image as a US Letter page at
the end of an existing PDF.

Original images and PDFs are always preserved. Default input PDF limits are 10
pages, 25 MiB, and a 15-second PDF parsing/rewrite timeout.

## Usage

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

By default, appended PDF outputs must stay inside either the image folder or the
source PDF folder. Pass `--allow-risky-output-path` only when an unusual
destination is intentional.

## Notes

- Source pages and simple string metadata are preserved.
- Encryption, permission restrictions, signatures, forms, outlines, attachments,
  document-level JavaScript, and tagged-PDF structure are not preserved.
- Owner-restricted PDFs that open with an empty password are accepted by
  default, but output PDF permissions are not preserved.
- Pass `--refuse-unrestricted-output` to stop instead of writing an unrestricted
  output PDF from an owner-restricted input.
