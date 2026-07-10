#!/usr/bin/env bash
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
cd "$HERE"

export FLASK_ENV=production
export CELLSITE_PORT="${CELLSITE_PORT:-8765}"

if [ -x "$HERE/CellSite" ]; then
  exec "$HERE/CellSite"
fi

if [ -f "$HERE/.venv/bin/activate" ]; then
  source "$HERE/.venv/bin/activate"
fi

if [ -f "$HERE/app.py" ]; then
  exec python3 "$HERE/app.py"
fi

if [ -x "$HERE/dist/CellSite/CellSite" ]; then
  cd "$HERE/dist/CellSite"
  exec "$HERE/dist/CellSite/CellSite"
fi

echo "ERROR: No se encontro app.py ni el ejecutable CellSite."
exit 1