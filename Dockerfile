# syntax=docker/dockerfile:1
FROM python:3.13.5-slim-bookworm@sha256:4c2cf9917bd1cbacc5e9b07320025bdb7cdf2df7b0ceaccb55e9dd7e30987419

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FIRSTRING_DATABASE=/app/runtime/firstring.sqlite3

RUN addgroup --system app && adduser --system --ingroup app --home /app app
WORKDIR /app

COPY vendor/deliveryguard-0.1.0-py3-none-any.whl /tmp/deliveryguard-0.1.0-py3-none-any.whl
RUN python -m pip install --no-cache-dir /tmp/deliveryguard-0.1.0-py3-none-any.whl \
    && rm /tmp/deliveryguard-0.1.0-py3-none-any.whl

COPY pyproject.toml README.md ./
COPY src ./src
RUN python -m pip install --no-cache-dir . && mkdir -p /app/runtime && chown -R app:app /app

USER app
EXPOSE 8000
HEALTHCHECK --interval=10s --timeout=3s --start-period=15s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=2)"

CMD ["python", "-m", "uvicorn", "firstring.app:app", "--host", "0.0.0.0", "--port", "8000"]
