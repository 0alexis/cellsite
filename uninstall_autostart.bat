@echo off
REM Quita CellSite del inicio automatico del usuario actual.

setlocal

set SCRIPT_DIR=%~dp0
set VBS_SCRIPT=%SCRIPT_DIR%start_cellsite_hidden.vbs
set RUN_KEY=HKCU\Software\Microsoft\Windows\CurrentVersion\Run
set APP_NAME=CellSite

echo.
echo ==================================================
echo   QUITAR INICIO AUTOMATICO - CELLSITE
echo ==================================================
echo.

reg delete "%RUN_KEY%" /v "%APP_NAME%" /f >nul 2>&1
if exist "%VBS_SCRIPT%" del /f /q "%VBS_SCRIPT%" >nul 2>&1

echo [+] Inicio automatico eliminado.
echo.
pause
endlocal