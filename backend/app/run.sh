#!/bin/bash

set -euo pipefail

APP=src.main:app
HOST=0.0.0.0
PORT=80

alembic upgrade head

uvicorn "$APP" --host "$HOST" --port "$PORT" "$@"
