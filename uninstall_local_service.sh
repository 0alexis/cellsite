#!/usr/bin/env bash
set -euo pipefail

SERVICE_NAME="cellsite.service"
SERVICE_FILE="$HOME/.config/systemd/user/$SERVICE_NAME"

if command -v systemctl >/dev/null 2>&1; then
  systemctl --user disable --now "$SERVICE_NAME" >/dev/null 2>&1 || true
  systemctl --user daemon-reload || true
fi

rm -f "$SERVICE_FILE"

echo "[+] Servicio local de CellSite eliminado."