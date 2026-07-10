#!/usr/bin/env bash
set -euo pipefail

# Script para crear un ejecutable portable con PyInstaller
# Ejecutar desde la carpeta del proyecto: ./build.sh

echo "🔧 Preparando entorno virtual..."
python3 -m venv .venv
source .venv/bin/activate

echo "📦 Instalando dependencias..."
pip install --upgrade pip -q
pip install -r requirements.txt -q
pip install pyinstaller -q

echo "🏗️ Empaquetando aplicación..."
# --onedir: Crea carpeta con ejecutable y dependencias (mejor para USB)
# --windowed: Sin ventana de consola
pyinstaller --onedir \
  --add-data "templates:templates" \
  --add-data "static:static" \
  --name CellSite \
  --windowed \
  --noconfirm \
  app.py

echo "📁 Creando estructura portable..."
# Crear carpeta data dentro del dist para que sea portable
mkdir -p dist/CellSite/data

# Copiar archivos de documentación
cp DATOS_UBICACION.txt dist/CellSite/ 2>/dev/null || true
cp README.md dist/CellSite/ 2>/dev/null || true
cp run_cellsite.sh dist/CellSite/ 2>/dev/null || true
cp install_local_service.sh dist/CellSite/ 2>/dev/null || true
cp uninstall_local_service.sh dist/CellSite/ 2>/dev/null || true
chmod +x dist/CellSite/run_cellsite.sh dist/CellSite/install_local_service.sh dist/CellSite/uninstall_local_service.sh 2>/dev/null || true

echo ""
echo "✅ ¡Build completo!"
echo ""
echo "📂 Tu aplicación está en: dist/CellSite/"
echo ""
echo "Para usar en otro PC:"
echo "  1. Copia toda la carpeta dist/CellSite/ a tu USB"
echo "  2. En el otro PC, ejecuta: CellSite/CellSite"
echo "  3. Los datos se guardarán en CellSite/data/app.db"
echo "  4. Para inicio local continuo en Linux: ./install_local_service.sh"
echo ""
