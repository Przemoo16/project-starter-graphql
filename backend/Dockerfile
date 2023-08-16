FROM python:3.11-slim AS base

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

ENV PYTHONUNBUFFERED=1

RUN apt-get update \
    && apt-get upgrade -y \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/app

EXPOSE 80


FROM base as deps

RUN apt-get update \
    && apt-get install --no-install-recommends -y curl \
    && rm -rf /var/lib/apt/lists/*

# Shell has been set up in the parent stage
# hadolint ignore=DL4006
RUN curl -sSL https://install.python-poetry.org | python - \
    # Upgrade setuptools, which is poetry dependency to non-vulnerable version (reported by Trivy)
    # FIXME: Remove after poetry resolves it on their own
    && /root/.local/share/pypoetry/venv/bin/pip install "setuptools>=65.5.1" \
    && ln -s /root/.local/bin/poetry /usr/local/bin/poetry \
    && poetry config virtualenvs.create false


FROM deps AS dev

COPY ./pyproject.toml ./poetry.lock ./
RUN --mount=type=cache,target=/root/.cache/pypoetry/cache \
    --mount=type=cache,target=/root/.cache/pypoetry/artifacts \
    poetry install --no-root --no-interaction --no-ansi --with dev

COPY . .

RUN poetry install --only-root --no-interaction --no-ansi

CMD ["./run.sh", "--reload"]


FROM deps as build

COPY ./pyproject.toml ./poetry.lock ./
RUN poetry export -f requirements.txt --output requirements.txt


FROM base

COPY --from=build /opt/app/requirements.txt ./
RUN pip install --no-deps --no-cache-dir -r ./requirements.txt

COPY ./pyproject.toml ./alembic.ini ./run.sh ./
COPY ./alembic ./alembic
COPY ./backend ./backend

RUN pip install --no-deps --no-cache-dir .

CMD ["./run.sh"]
