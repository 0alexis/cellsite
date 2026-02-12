@echo off
REM Script para crear ejecutable portable en Windows
REM Ejecutar: build.bat

echo.
echo ==================================================
echo   Creando ejecutable CellSite para Windows
echo ==================================================
echo.

echo [1/4] Creando entorno virtual...
python -m venv .venv
if errorlevel 1 (
    echo ERROR: No se pudo crear el entorno virtual
    echo Asegurate de tener Python 3.8+ instalado
    pause
    exit /b 1
)

echo [2/4] Activando entorno virtual...
call .venv\Scripts\activate.bat

echo [3/4] Instalando dependencias...
python -m pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet
pip install pyinstaller --quiet

echo [4/4] Empaquetando aplicacion...
pyinstaller --onedir --add-data "templates;templates" --add-data "static;static" --name CellSite --windowed --noconfirm app.py

if errorlevel 1 (
    echo.
    echo ERROR: Fallo el empaquetado
    pause
    exit /b 1
)

echo.
echo [+] Creando estructura portable...
if not exist "dist\CellSite\data" mkdir dist\CellSite\data
copy DATOS_UBICACION.txt dist\CellSite\ >nul 2>&1
copy README.md dist\CellSite\ >nul 2>&1

echo.
echo ==================================================
echo   BUILD COMPLETO!
echo ==================================================
echo.
echo Tu aplicacion esta en: dist\CellSite\
echo.
echo PARA USAR EN OTRO PC:
echo   1. Copia toda la carpeta dist\CellSite\ a tu USB
echo   2. En el otro PC, ejecuta: CellSite\CellSite.exe
echo   3. Los datos se guardan en: CellSite\data\app.db
echo.
echo Tamano aproximado: ~50-60 MB
echo.
pause
