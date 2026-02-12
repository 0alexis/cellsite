#!/usr/bin/env bash
# Lanzador simple: si existe `dist/MiApp` la ejecuta, si no ejecuta con Python (requiere venv activado)
HERE="$(cd "$(dirname "$0")" && pwd)"
if [ -x "$HERE/dist/MiApp" ]; then
  "$HERE/dist/MiApp" &
  exit 0
fi

if [ -f "$HERE/.venv/bin/activate" ]; then
  source "$HERE/.venv/bin/activate"
fi
python3 "$HERE/app.py" &
exit 0
