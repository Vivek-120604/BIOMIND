FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim

RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH \
    UV_CACHE_DIR=/home/user/.cache/uv \
    MPLCONFIGDIR=/tmp/matplotlib \
    PYTHONUNBUFFERED=1
WORKDIR /app

COPY --chown=user:user . /app
RUN mkdir -p /tmp/matplotlib && uv sync --frozen

EXPOSE 7860
CMD ["uv", "run", "python", "main.py"]
