@echo off
REM Menu principal - Elije que deseas hacer

setlocal enabledelayedexpansion
cls

:MENU
echo.
echo ════════════════════════════════════════════════════════════════
echo             CELLSITE - MENU PRINCIPAL
echo ════════════════════════════════════════════════════════════════
echo.
echo [1] Iniciar CellSite (ejecutable compilado)
echo [2] Iniciar CellSite en modo desarrollo (necesita Python)
echo [3] Construir ejecutable portable para USB
echo [4] Verificar ambiente de construccion
echo [5] Abrir carpeta de datos
echo [6] Abrir documentacion
echo [7] Instalar inicio automatico con Windows
echo [8] Quitar inicio automatico con Windows
echo [9] Salir
echo.
set /p CHOICE="Elige una opcion (1-9): "

if "%CHOICE%"=="1" goto START_APP
if "%CHOICE%"=="2" goto START_DEV
if "%CHOICE%"=="3" goto BUILD_PORTABLE
if "%CHOICE%"=="4" goto VERIFY_BUILD
if "%CHOICE%"=="5" goto OPEN_DATA
if "%CHOICE%"=="6" goto OPEN_DOCS
if "%CHOICE%"=="7" goto INSTALL_AUTOSTART
if "%CHOICE%"=="8" goto UNINSTALL_AUTOSTART
if "%CHOICE%"=="9" exit /b 0

echo.
echo ERROR: Opcion no valida
timeout /t 2 /nobreak
cls
goto MENU

REM ──────────────────────────────────────────────────────────────
:START_APP
cls
echo.
echo Iniciando CellSite desde ejecutable compilado...
echo.
if exist "start_app.bat" (
    call start_app.bat
) else if exist "dist\CellSite_portable\start_app.bat" (
    cd /d dist\CellSite_portable
    call start_app.bat
) else (
    echo ERROR: No se encontro start_app.bat
    echo Primero ejecuta la opcion [3] para compilar
    pause
    goto MENU
)
goto MENU

REM ──────────────────────────────────────────────────────────────
:START_DEV
cls
echo.
echo Iniciando en modo desarrollo...
echo.
if exist "start.bat" (
    call start.bat
) else (
    echo ERROR: start.bat no encontrado
    pause
)
goto MENU

REM ──────────────────────────────────────────────────────────────
:BUILD_PORTABLE
cls
echo.
echo Construyendo ejecutable portable...
echo.
if exist "build_portable.bat" (
    call build_portable.bat
) else (
    echo ERROR: build_portable.bat no encontrado
    pause
)
goto MENU

REM ──────────────────────────────────────────────────────────────
:VERIFY_BUILD
cls
echo.
echo Verificando ambiente...
echo.
if exist "verify_build_ready.bat" (
    call verify_build_ready.bat
) else (
    echo ERROR: verify_build_ready.bat no encontrado
    pause
)
goto MENU

REM ──────────────────────────────────────────────────────────────
:OPEN_DATA
echo.
echo Abriendo carpeta de datos...
if exist "data" (
    start "" "data"
) else if exist "dist\CellSite_portable\data" (
    start "" "dist\CellSite_portable\data"
) else (
    echo ERROR: Carpeta data no encontrada
    pause
)
goto MENU

REM ──────────────────────────────────────────────────────────────
:OPEN_DOCS
cls
echo.
echo Documentacion disponible:
echo.
echo [1] INSTRUCCIONES_USB_PORTABLE.txt
echo [2] WORKFLOW_CONSTRUCCION_USB.txt
echo [3] README.md
echo [4] LEEME_PRIMERO.txt
echo [5] Volver al menu
echo.
set /p DOC="Elige documento (1-5): "

if "%DOC%"=="1" (
    if exist "INSTRUCCIONES_USB_PORTABLE.txt" start "" "INSTRUCCIONES_USB_PORTABLE.txt"
) else if "%DOC%"=="2" (
    if exist "WORKFLOW_CONSTRUCCION_USB.txt" start "" "WORKFLOW_CONSTRUCCION_USB.txt"
) else if "%DOC%"=="3" (
    if exist "README.md" start "" "README.md"
) else if "%DOC%"=="4" (
    if exist "LEEME_PRIMERO.txt" start "" "LEEME_PRIMERO.txt"
) else if "%DOC%"=="5" (
    goto MENU
)
goto MENU

REM ──────────────────────────────────────────────────────────────
:INSTALL_AUTOSTART
cls
echo.
echo Instalando inicio automatico...
echo.
if exist "install_autostart.bat" (
    call install_autostart.bat
) else if exist "dist\CellSite_portable\install_autostart.bat" (
    cd /d dist\CellSite_portable
    call install_autostart.bat
) else (
    echo ERROR: install_autostart.bat no encontrado
    echo Primero ejecuta la opcion [3] para compilar
    pause
)
goto MENU

REM ──────────────────────────────────────────────────────────────
:UNINSTALL_AUTOSTART
cls
echo.
echo Quitando inicio automatico...
echo.
if exist "uninstall_autostart.bat" (
    call uninstall_autostart.bat
) else if exist "dist\CellSite_portable\uninstall_autostart.bat" (
    cd /d dist\CellSite_portable
    call uninstall_autostart.bat
) else (
    echo ERROR: uninstall_autostart.bat no encontrado
    pause
)
goto MENU
