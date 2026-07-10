@echo off
REM Script para crear ejecutable USB PORTABLE para Windows
REM Ejecutar: build_portable.bat
REM Resultado: dist\CellSite_portable\CellSite.exe (totalmente autocontenido)

setlocal enabledelayedexpansion
cls

echo.
echo ==================================================
echo   CONSTRUCCION DE CELLSITE - USB PORTABLE
echo ==================================================
echo.
echo Este proceso creara un ejecutable autocontenido
echo que funciona desde USB sin necesidad de Python
echo.

REM Verificar que Python este disponible
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no encontrado
    echo Por favor instala Python 3.8+ desde python.org
    echo y asegurate de marcar "Add Python to PATH"
    pause
    exit /b 1
)

echo [1/6] Limpiando construcciones anteriores...
if exist "build" rmdir /s /q build >nul 2>&1
if exist "dist\CellSite_portable" rmdir /s /q dist\CellSite_portable >nul 2>&1

echo [2/6] Creando entorno virtual...
if exist ".venv" (
    echo Usando entorno virtual existente...
) else (
    python -m venv .venv
    if errorlevel 1 (
        echo ERROR: No se pudo crear el entorno virtual
        pause
        exit /b 1
    )
)

echo [3/6] Activando entorno virtual e instalando dependencias...
call .venv\Scripts\activate.bat

python -m pip install --upgrade pip --quiet --disable-pip-version-check
pip install -r requirements.txt --quiet --disable-pip-version-check
pip install pyinstaller --quiet --disable-pip-version-check

echo [4/6] Generando archivo de especificacion PyInstaller...
python -c "
import PyInstaller.__main__
import sys
" >nul 2>&1

echo [5/6] Empaquetando aplicacion (esto puede tomar 1-2 minutos)...
REM Crear el ejecutable de una sola pieza (--onefile)
REM --windowed: sin ventana de consola
REM --add-data: incluir plantillas y archivos estaticos
REM --hidden-import: importaciones que PyInstaller no detecta automaticamente
pyinstaller ^
    --onefile ^
    --windowed ^
    --icon=ICON_CELLSITE.ico ^
    --name CellSite ^
    --distpath dist\CellSite_portable ^
    --buildpath build ^
    --add-data "templates;templates" ^
    --add-data "static;static" ^
    --hidden-import=werkzeug.security ^
    --hidden-import=flask_sqlalchemy ^
    --noconfirm ^
    app.py

if errorlevel 1 (
    echo.
    echo ERROR: Fallo el empaquetado con PyInstaller
    echo Por favor verifica que todos los archivos esten presentes
    pause
    exit /b 1
)

echo [6/6] Creando estructura portable...

REM Crear carpeta de datos
if not exist "dist\CellSite_portable\data" mkdir dist\CellSite_portable\data

REM Copiar archivos de configuracion y documentacion
copy /Y app.py dist\CellSite_portable\ >nul 2>&1
copy /Y start_app.bat dist\CellSite_portable\ >nul 2>&1
copy /Y install_autostart.bat dist\CellSite_portable\ >nul 2>&1
copy /Y uninstall_autostart.bat dist\CellSite_portable\ >nul 2>&1
copy /Y README.md dist\CellSite_portable\ >nul 2>&1
copy /Y requirements.txt dist\CellSite_portable\ >nul 2>&1
copy /Y INSTRUCCIONES_USB_PORTABLE.txt dist\CellSite_portable\ >nul 2>&1
copy /Y LEEME_PRIMERO.txt dist\CellSite_portable\ >nul 2>&1
copy /Y DATOS_UBICACION.txt dist\CellSite_portable\ >nul 2>&1

REM Crear base de datos de ejemplo si no existe
if not exist "data\app.db" (
    echo Inicializando base de datos...
    .venv\Scripts\python -c "from app import app, db; app.app_context().push(); db.create_all()"
)

copy /Y data\app.db dist\CellSite_portable\data\ >nul 2>&1

echo.
echo ==================================================
echo   BUILD COMPLETO - APLICACION LISTA PARA USB!
echo ==================================================
echo.
echo Carpeta de distribucion: dist\CellSite_portable\
echo Archivo ejecutable:      CellSite.exe
echo.
echo Para usar en USB:
echo   1. Copia la carpeta dist\CellSite_portable\ a tu USB
echo   2. Abre start_app.bat desde la carpeta del USB
echo   3. La aplicacion se abrira en tu navegador
echo   4. Al abrirse una vez, CellSite queda registrado para iniciar con Windows
echo      Si quieres forzarlo manualmente, abre install_autostart.bat una vez
echo.
echo NOTA: La primera vez que inicies, la app creara
echo los datos iniciales. Esto es normal.
echo.
echo Tamaño del ejecutable: ~80-100 MB
echo Tiempo de inicio: ~5-10 segundos (normal)
echo.
pause
