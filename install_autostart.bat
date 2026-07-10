@echo off
REM Instala CellSite para iniciar automaticamente al iniciar sesion en Windows.
REM No requiere permisos de administrador porque usa el registro del usuario actual.

setlocal enabledelayedexpansion

set SCRIPT_DIR=%~dp0
set START_SCRIPT=%SCRIPT_DIR%start_app.bat
set VBS_SCRIPT=%SCRIPT_DIR%start_cellsite_hidden.vbs
set RUN_KEY=HKCU\Software\Microsoft\Windows\CurrentVersion\Run
set APP_NAME=CellSite
set AUTOSTART_CMD=wscript.exe "%VBS_SCRIPT%"

cd /d "%SCRIPT_DIR%"

echo.
echo ==================================================
echo   INSTALAR INICIO AUTOMATICO - CELLSITE
echo ==================================================
echo.

if not exist "CellSite.exe" (
    echo ERROR: No se encontro CellSite.exe en esta carpeta.
    echo Ejecuta este archivo desde la carpeta portable de CellSite.
    pause
    exit /b 1
)

if not exist "start_app.bat" (
    echo ERROR: No se encontro start_app.bat en esta carpeta.
    pause
    exit /b 1
)

echo Set shell = CreateObject("WScript.Shell") > "%VBS_SCRIPT%"
echo shell.CurrentDirectory = "%SCRIPT_DIR%" >> "%VBS_SCRIPT%"
echo shell.Run """%START_SCRIPT%""", 0, False >> "%VBS_SCRIPT%"

reg add "%RUN_KEY%" /v "%APP_NAME%" /t REG_SZ /d "%AUTOSTART_CMD%" /f >nul
if errorlevel 1 (
    echo ERROR: No se pudo registrar el inicio automatico.
    pause
    exit /b 1
)

echo [+] Inicio automatico instalado correctamente.
echo.
echo CellSite se iniciara solo despues de apagar/prender,
echo reiniciar o cerrar y volver a iniciar sesion en Windows.
echo.
echo IMPORTANTE: Manten esta carpeta en la misma ubicacion.
echo Si la mueves o cambia la letra del USB, ejecuta este instalador otra vez.
echo.
pause
endlocal