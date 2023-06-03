#!/bin/bash

set -euo pipefail

alembic upgrade head

uvicorn backend.main:get_app --factory --host 0.0.0.0 --port 80 "$@"
