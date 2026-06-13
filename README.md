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

## Docker

Build a reproducible Python 3.12 image with Pillow, pillow-heif, and the project
dependencies installed:

```bash
docker compose build app
docker compose run --rm app python -m pytest
```

Run the receipt processor against a model server on the host machine:

```bash
docker compose run --rm app receipt-process image-tests
```

Inside the container, `host.docker.internal` points back to the host. The
Compose defaults use `http://host.docker.internal:8000/v1` for an
OpenAI-compatible local server. Set `DOCKER_RECEIPT_VISION_BASE_URL` in `.env`
when your host model server uses a different port.

To run with the optional Ollama sidecar:

```bash
docker compose --profile ollama up -d ollama
docker compose --profile ollama run --rm app-ollama receipt-process image-tests
```

Pull the model into the sidecar before processing receipts:

```bash
docker compose --profile ollama exec ollama ollama pull qwen3-vl:8b
```

Set `PYTHON_VERSION`, `OLLAMA_TAG`, or `OLLAMA_MODEL` in `.env` when you need
to pin different container or model versions.

## Menu Wrappers

For manual use without remembering commands, run the wrapper for your platform
from the project folder:

```bash
./run-image-pdf-tools.sh
```

On Windows, double-click `run-image-pdf-tools.bat`.

The wrappers create a local `.venv`, install `requirements.txt`, and show a
menu for making an image grid, appending an image to a PDF, or doing both in one
flow. They require Python 3.12 or 3.13.

## Tools

- [`scripts/make-image-grid.py`](docs/image-grid.md): combines HEIC, HEIF, JPG,
  JPEG, and PNG images into one balanced JPG grid.
- [`scripts/append-image-page.py`](docs/append-image-page.md): appends a
  JPG/JPEG image as a US Letter page at the end of an existing PDF.
- [`receipt-process`](docs/receipt-processor.md): extracts receipt dates and
  totals from HEIC, HEIF, JPG, JPEG, PNG, TIFF, BMP, and WebP images with a
  configured local vision model.

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
