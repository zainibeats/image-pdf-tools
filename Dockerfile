ARG PYTHON_VERSION=3.12
FROM python:${PYTHON_VERSION}-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /work

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libheif1 \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml README.md ./
COPY src ./src
COPY tests ./tests
COPY scripts ./scripts

RUN python -m pip install --upgrade pip \
    && python -m pip install -e ".[dev]" \
    && python - <<'PY'
from PIL import Image
from pillow_heif import register_heif_opener

register_heif_opener()
print(f"Pillow {Image.__version__} with pillow-heif support is available")
PY

CMD ["receipt-process", "--help"]
