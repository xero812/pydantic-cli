#!/usr/bin/env bash
set -euo pipefail

PY=python3
VENV=.venv
PIP=$VENV/bin/pip
PYTHON=$VENV/bin/python

cmd=${1:-help}

venv() {
    if [ ! -d "$VENV" ]; then
        $PY -m venv "$VENV"
    fi
}

install() {
    venv
    $PIP install --upgrade pip
    $PIP install -r requirements.txt
}

run() {
    if [ -z "${OPENAI_API_KEY:-}" ]; then
        echo "Error: OPENAI_API_KEY not set" >&2
        exit 1
    fi
    $PYTHON main.py
}

versions() {
    venv
    $PYTHON - << 'EOF'
import sys
for n in ['pydantic_ai','openai','pydantic']:
    try:
        m=__import__(n)
        print(n, getattr(m,'__version__','(no __version__)'))
    except Exception as e:
        print(n, 'not installed:', e)
print('python', sys.version)
EOF
}

clean() {
    rm -rf "$VENV" __pycache__ .pytest_cache .mypy_cache .ruff_cache
}

case "$cmd" in
    venv|install|run|versions|clean)
        "$cmd"
        ;;
    *)
        echo "Usage: $0 {venv|install|run|versions|clean}"
        ;;
esac
