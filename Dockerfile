FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY pyproject.toml README.md LICENSE ./
COPY algoquant ./algoquant

RUN python -m pip install --upgrade pip \
    && python -m pip install .

USER 65532:65532

ENTRYPOINT ["algoquant-backtest"]
CMD ["--rows", "1000", "--seed", "20260828"]
