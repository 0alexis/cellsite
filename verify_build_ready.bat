@echo off
REM Script para verificar que el entorno esta listo para construir el ejecutable USB
REM Ejecutar: verify_build_ready.bat

setlocal enabledelayedexpansion
cls

echo.
echo ==================================================
echo  VERIFICACION PRE-CONSTRUCCION
echo ==================================================
echo.

set ERRORS=0
set WARNINGS=0

REM ─────────────────────────────────────────────────────────────────
REM 1. Verificar Python
REM ─────────────────────────────────────────────────────────────────
echo [1] Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python NO encontrado en PATH
    echo Solucion: Instala Python 3.8+ desde python.org
    echo           Marca "Add Python to PATH" durante instalacion
    set /a ERRORS+=1
) else (
    for /f "tokens=*" %%i in ('python --version') do set PYTHON_VERSION=%%i
    echo [OK] !PYTHON_VERSION! encontrado
)

REM ─────────────────────────────────────────────────────────────────
REM 2. Verificar archivos necesarios
REM ─────────────────────────────────────────────────────────────────
echo.
echo [2] Verificando archivos necesarios...

if not exist "app.py" (
    echo [ERROR] app.py NO encontrado
    set /a ERRORS+=1
) else (
    echo [OK] app.py existe
)

if not exist "requirements.txt" (
    echo [ERROR] requirements.txt NO encontrado
    set /a ERRORS+=1
) else (
    echo [OK] requirements.txt existe
)

if not exist "templates" (
    echo [ERROR] Carpeta templates/ NO encontrada
    set /a ERRORS+=1
) else (
    echo [OK] Carpeta templates/ existe
)

if not exist "static" (
    echo [ERROR] Carpeta static/ NO encontrada
    set /a ERRORS+=1
) else (
    echo [OK] Carpeta static/ existe
)

if not exist "build_portable.bat" (
    echo [WARNING] build_portable.bat NO encontrado
    set /a WARNINGS+=1
)

REM ─────────────────────────────────────────────────────────────────
REM 3. Verificar dependencias importantes
REM ─────────────────────────────────────────────────────────────────
echo.
echo [3] Verificando dependencias necesarias...

echo Analizando requirements.txt...

findstr "Flask" requirements.txt >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Flask no esta en requirements.txt
    set /a WARNINGS+=1
) else (
    echo [OK] Flask esta en requirements.txt
)

findstr "Flask-SQLAlchemy" requirements.txt >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Flask-SQLAlchemy no esta en requirements.txt
    set /a WARNINGS+=1
) else (
    echo [OK] Flask-SQLAlchemy esta en requirements.txt
)

findstr "reportlab" requirements.txt >nul 2>&1
if errorlevel 1 (
    echo [WARNING] reportlab no esta en requirements.txt
    set /a WARNINGS+=1
) else (
    echo [OK] reportlab esta en requirements.txt
)

REM ─────────────────────────────────────────────────────────────────
REM 4. Verificar espacio en disco
REM ─────────────────────────────────────────────────────────────────
echo.
echo [4] Verificando espacio en disco...

for /f "tokens=3" %%A in ('dir /-C ^| findstr "bytes free"') do set FREE_SPACE=%%A

if errorlevel 1 (
    echo [WARNING] No se pudo verificar espacio disponible
    set /a WARNINGS+=1
) else (
    echo [OK] Espacio disponible: !FREE_SPACE! bytes
    echo     (Recomendado: 500 MB o mas)
)

REM ─────────────────────────────────────────────────────────────────
REM 5. Verificar carpeta build anterior
REM ─────────────────────────────────────────────────────────────────
echo.
echo [5] Verificando construcciones anteriores...

if exist "build" (
    echo [INFO] Carpeta build/ encontrada
    echo Sera limpiada durante la construccion
) else (
    echo [OK] Primera construccion
)

if exist "dist\CellSite_portable" (
    echo [INFO] Construccion anterior encontrada en dist\CellSite_portable\
    echo Sera reemplazada durante la construccion
)

REM ─────────────────────────────────────────────────────────────────
REM 6. Verificar sintaxis de app.py
REM ─────────────────────────────────────────────────────────────────
echo.
echo [6] Verificando sintaxis de app.py...

python -m py_compile app.py >nul 2>&1
if errorlevel 1 (
    echo [ERROR] app.py tiene errores de sintaxis
    set /a ERRORS+=1
    python -m py_compile app.py
) else (
    echo [OK] app.py sintaxis correcta
)

REM ─────────────────────────────────────────────────────────────────
REM RESUMEN
REM ─────────────────────────────────────────────────────────────────
echo.
echo ==================================================
echo  RESUMEN
echo ==================================================
echo.

if %ERRORS% EQU 0 (
    if %WARNINGS% EQU 0 (
        echo [SUCCESS] Todo esta listo para construir!
        echo.
        echo Proximos pasos:
        echo 1. Ejecuta: build_portable.bat
        echo 2. Espera 1-2 minutos
        echo 3. El ejecutable estara en: dist\CellSite_portable\
        echo.
        echo Informacion de construccion:
        echo - Tamaño esperado: ~80-100 MB
        echo - Tiempo: 1-2 minutos (primera vez mas lento)
        echo - Resultado: dist\CellSite_portable\CellSite.exe
        echo.
    ) else (
        echo [WARNING] Hay %WARNINGS% advertencia(s), pero puedes continuar
        echo.
        echo Se recomienda revisar los WARNING arriba antes de construir
        echo.
    )
) else (
    echo [ERROR] Hay %ERRORS% error(es) que deben corregirse!
    echo.
    echo Por favor revisa los errores arriba y corrige antes de construir
    echo.
)

echo ==================================================
echo.
pause
