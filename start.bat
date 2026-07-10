@echo off
REM Script para ejecutar la aplicacion en modo desarrollo (Windows)
REM No crea ejecutable, solo ejecuta el servidor Flask

echo.
echo Iniciando CellSite en modo desarrollo...
echo.

if not exist ".venv\Scripts\activate.bat" (
    echo Creando entorno virtual...
    python -m venv .venv
    call .venv\Scripts\activate.bat
    echo Instalando dependencias...
    pip install -r requirements.txt --quiet
) else (
    call .venv\Scripts\activate.bat
)

echo.
echo Servidor iniciado en: http://127.0.0.1:8765
echo.
echo Presiona Ctrl+C para detener el servidor
echo.

python app.py
