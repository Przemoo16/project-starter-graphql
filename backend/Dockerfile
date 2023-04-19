FROM python:3.11-slim AS base

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

ENV PYTHONUNBUFFERED 1


RUN apt-get update \
    && apt-get install --no-install-recommends -y curl=7.74.0-1.3+deb11u7 \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir --upgrade pip==23.1

RUN curl -sSL https://install.python-poetry.org | python - \
    && ln -s ~/.local/bin/poetry /usr/local/bin/poetry \
    && poetry config virtualenvs.create false

WORKDIR /app

COPY app/pyproject.toml app/poetry.lock /app/

EXPOSE 80


FROM base AS prod

RUN poetry install --no-root --no-interaction --no-ansi --only main

COPY app /app

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "80"]


FROM base AS test

RUN poetry install --no-root --no-interaction --no-ansi --with test

COPY app /app

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "80"]


FROM base AS dev

RUN poetry install --no-root --no-interaction --no-ansi --with test --with dev

COPY app /app

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "80", "--reload"]
