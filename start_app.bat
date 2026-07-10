@echo off
REM Script para iniciar CellSite desde USB o carpeta local
REM Ejecutar: start_app.bat

setlocal enabledelayedexpansion

REM Obtener la carpeta actual (donde esta este script)
set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

echo.
echo ==================================================
echo   INICIANDO CELLSITE
echo ==================================================
echo.

REM Verificar si existe el ejecutable
if not exist "CellSite.exe" (
    echo ERROR: No se encontro CellSite.exe
    echo Por favor asegurate de estar en la carpeta correcta
    echo y que hayas ejecutado build_portable.bat primero
    pause
    exit /b 1
)

REM Crear carpeta data si no existe
if not exist "data" mkdir data

REM Establecer puerto local de CellSite
set PORT=8765
set CELLSITE_PORT=%PORT%

REM Si CellSite ya esta activo en este puerto, no iniciar otra copia
powershell -NoProfile -ExecutionPolicy Bypass -Command "try { $r = Invoke-WebRequest -UseBasicParsing -Uri 'http://127.0.0.1:%PORT%/login' -TimeoutSec 2; if ($r.StatusCode -ge 200 -and $r.StatusCode -lt 500) { exit 0 } else { exit 1 } } catch { exit 1 }" >nul 2>&1
if not errorlevel 1 (
    echo [*] CellSite ya esta en ejecucion.
    start "" http://127.0.0.1:%PORT%
    exit /b 0
)

echo [*] Iniciando CellSite...
echo [*] Puerto: http://127.0.0.1:%PORT%
echo.
echo Abriendo navegador en 5 segundos...
echo (Si el navegador no se abre, ingresa a: http://127.0.0.1:%PORT%)
echo.

REM Esperar un poco antes de abrir el navegador
timeout /t 5 /nobreak

REM Iniciar el ejecutable con variables de entorno
set FLASK_ENV=production
set FLASK_APP=CellSite.exe
start "" http://127.0.0.1:%PORT%

REM Ejecutar la aplicacion
"%SCRIPT_DIR%CellSite.exe"

if errorlevel 1 (
    echo.
    echo ERROR: La aplicacion encontro un error
    echo Por favor verifica que tengas permisos de lectura/escritura
    echo en la carpeta: %SCRIPT_DIR%data\
    pause
)

endlocal
