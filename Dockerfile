FROM python:3.13-slim AS builder  

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN mkdir /app
 
WORKDIR /app
 
ENV UV_COMPILE_BYTECODE=1 

COPY pyproject.toml uv.lock /app/

RUN uv sync --frozen --no-dev

FROM python:3.13-slim AS prod

COPY --from=ghcr.io/astral-sh/uv:0.9.8 /uv /uvx /bin/
 
RUN useradd -m -r appuser && \
   mkdir /app && \
   chown -R appuser /app
 
COPY --from=builder --chown=appuser:appuser /app/.venv /app/.venv
 
WORKDIR /app
 
COPY --chown=appuser:appuser . .

ENV PATH="/app/.venv/bin:$PATH"

USER appuser
 
EXPOSE 8000

ENV DEBUG=0

COPY --chown=appuser:appuser entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh
ENTRYPOINT ["/app/entrypoint.sh"]

CMD ["gunicorn", "app.asgi:application", "-k", "uvicorn_worker.UvicornWorker", "-b", "0.0.0.0:8000"]