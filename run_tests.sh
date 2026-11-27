#!/bin/sh
set -eu

ROOT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
cd "$ROOT_DIR"

if [ -x ".venv/bin/python" ]; then
    exec .venv/bin/python -m pytest "$@"
fi

exec python3 -m pytest "$@"
