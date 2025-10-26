# SPDX-License-Identifier: MPL-2.0

FROM python:3.11-slim

WORKDIR /workspace

ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apt-get update && apt-get install -y --no-install-recommends \
        ffmpeg \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .
COPY README.md .

RUN python -m pip install --upgrade pip && \
    python -m pip install --no-cache-dir -e .[dev]

COPY . .

CMD ["bash", "-lc", "scripts/dev"]
