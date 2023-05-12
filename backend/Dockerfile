FROM python:3.11-slim AS base

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

ENV PYTHONUNBUFFERED=1

RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install --no-install-recommends -y curl \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir --upgrade pip

RUN curl -sSL https://install.python-poetry.org | python - \
    # Upgrade setuptools, which is poetry dependency to non-vulnerable version (reported by Trivy)
    # FIXME: Remove after poetry resolves it on their own
    && ~/.local/share/pypoetry/venv/bin/pip install "setuptools>=65.5.1" \
    && ln -s ~/.local/bin/poetry /usr/local/bin/poetry \
    && poetry config virtualenvs.create false

WORKDIR /app

COPY ./app/pyproject.toml ./app/poetry.lock ./
RUN poetry install --no-root --no-interaction --no-ansi --only main

EXPOSE 80

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "80"]


FROM base AS test

RUN poetry install --no-root --no-interaction --no-ansi --with test

COPY ./app .


FROM base AS dev

RUN poetry install --no-root --no-interaction --no-ansi --with test --with dev

COPY ./app .

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "80", "--reload"]


FROM base as prod

COPY ./app .
