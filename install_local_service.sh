#!/usr/bin/env bash
set -euo pipefail

APP_NAME="CellSite"
SERVICE_NAME="cellsite.service"
HERE="$(cd "$(dirname "$0")" && pwd)"
SERVICE_DIR="$HOME/.config/systemd/user"
SERVICE_FILE="$SERVICE_DIR/$SERVICE_NAME"
RUNNER="$HERE/run_cellsite.sh"

if ! command -v systemctl >/dev/null 2>&1; then
  echo "ERROR: systemctl no esta disponible en este sistema."
  exit 1
fi

if [ ! -f "$RUNNER" ]; then
  echo "ERROR: No se encontro run_cellsite.sh en: $HERE"
  exit 1
fi

chmod +x "$RUNNER"
mkdir -p "$SERVICE_DIR"

cat > "$SERVICE_FILE" <<EOF
[Unit]
Description=$APP_NAME local
After=graphical-session.target network.target

[Service]
Type=simple
WorkingDirectory=$HERE
ExecStart=$RUNNER
Restart=always
RestartSec=5
Environment=CELLSITE_PORT=8765

[Install]
WantedBy=default.target
EOF

systemctl --user daemon-reload
systemctl --user enable --now "$SERVICE_NAME"

echo ""
echo "[+] CellSite quedo instalado de manera local y continua."
echo "[+] Se iniciara automaticamente al iniciar sesion en este usuario."
echo "[+] Si se cierra por error, systemd intentara levantarlo de nuevo."
echo ""
echo "Abrir en el navegador: http://127.0.0.1:8765"
echo "Ver estado: systemctl --user status $SERVICE_NAME"
echo "Detener: systemctl --user stop $SERVICE_NAME"
echo "Quitar instalacion: ./uninstall_local_service.sh"