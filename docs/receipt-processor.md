# Receipt Processor

`receipt-process` sends receipt images to a configured local vision model,
extracts transaction dates and totals, and writes daily summary JSON.

## Usage

Process receipt images directly with the configured local vision model:

```bash
receipt-process path/to/receipts
```

Supported input formats include HEIC, HEIF, JPG, JPEG, PNG, TIFF, BMP, and WebP.
Images are resized and sent to the vision model as JPEG payloads.

For best results, use one receipt per image. The current receipt extraction
flow appears to handle only one receipt from each image reliably.

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

The processor rejects remote HTTP endpoints by default so receipt images stay on
local or private-network model servers. Pass `--vision-llm-allow-remote` only
when sending receipt images to a remote endpoint is intentional.

## Docker Model URLs

When `receipt-process` runs in Docker, `127.0.0.1` is the app container, not the
host. Use `http://host.docker.internal:8000/v1` for an OpenAI-compatible server
running on the host machine. In Compose, set `DOCKER_RECEIPT_VISION_BASE_URL`
when the host model server uses a different port or path.

The Compose file also includes an optional Ollama sidecar. Start it with:

```bash
docker compose --profile ollama up -d ollama
docker compose --profile ollama exec ollama ollama pull qwen3-vl:8b
docker compose --profile ollama run --rm app-ollama receipt-process image-tests
```

`app-ollama` sets `RECEIPT_VISION_BASE_URL=http://ollama:11434` so the app
container talks to the sidecar over the Docker network.

## Providers

- `openai-compatible`: calls a local OpenAI-compatible chat completions
  endpoint.
- `ollama`: calls Ollama's local generate endpoint.
- `command`: runs a local command and sends JSON with the prompt and base64 JPEG
  image on stdin.

## Outputs

`daily_totals.json` contains accepted receipt totals summed by ISO date.

`receipt_results.json` contains:

- `receipts`: accepted receipt records with file, date, total, confidence, and
  method.
- `failures`: image paths that could not be extracted or failed validation.

See [receipt processor internals](receipt-processor-internals.md) for the code
layout and processing flow.
