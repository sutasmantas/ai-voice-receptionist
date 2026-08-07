# syntax=docker/dockerfile:1
FROM python:3.14.0-slim-bookworm@sha256:d13fa0424035d290decef3d575cea23d1b7d5952cdf429df8f5542c71e961576

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FIRSTRING_DATABASE=/app/runtime/firstring.sqlite3

RUN addgroup --system app && adduser --system --ingroup app --home /app app
WORKDIR /app

COPY vendor/deliveryguard-0.2.0-py3-none-any.whl /tmp/deliveryguard-0.2.0-py3-none-any.whl
RUN python -m pip install --no-cache-dir /tmp/deliveryguard-0.2.0-py3-none-any.whl \
    && rm /tmp/deliveryguard-0.2.0-py3-none-any.whl

COPY pyproject.toml README.md ./
COPY src ./src
RUN python -m pip install --no-cache-dir . && mkdir -p /app/runtime && chown -R app:app /app

USER app
EXPOSE 8000
HEALTHCHECK --interval=10s --timeout=3s --start-period=15s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=2)"

CMD ["python", "-m", "uvicorn", "firstring.app:app", "--host", "0.0.0.0", "--port", "8000"]
