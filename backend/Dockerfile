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

WORKDIR /opt/app

COPY ./pyproject.toml ./poetry.lock ./
RUN poetry install --no-root --no-interaction --no-ansi --only main

COPY ./alembic.ini ./run.sh ./
COPY ./alembic ./alembic

EXPOSE 80


FROM base AS dev

RUN poetry install --no-root --no-interaction --no-ansi --with dev

COPY ./backend ./backend
COPY ./tests ./tests

RUN poetry install --only-root --no-interaction --no-ansi

CMD ["./run.sh", "--reload"]


FROM base as prod

COPY ./backend ./backend

RUN poetry install --only-root --no-interaction --no-ansi

CMD ["./run.sh"]
