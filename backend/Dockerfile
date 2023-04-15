FROM python:3.11-slim AS base

ENV PYTHONUNBUFFERED 1

RUN apt-get update \
    && apt-get install -y curl \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --upgrade pip

RUN curl -sSL https://install.python-poetry.org | python - \
    && ln -s ~/.local/bin/poetry /usr/local/bin/poetry \
    && poetry config virtualenvs.create false

WORKDIR /app

COPY app/pyproject.toml app/poetry.lock /app/

EXPOSE 80


FROM base AS dev

RUN poetry install --no-root --no-interaction --no-ansi

COPY app /app

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "80", "--reload"]


FROM base AS prod

RUN poetry install --no-root --no-dev --no-interaction --no-ansi

COPY app /app

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "80"]
