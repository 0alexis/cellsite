# CellSite — Sistema de Ventas de Celulares

Sistema completo para gestión de ventas de celulares con pagos en cuotas, control de deudores, dashboard financiero y exportación de reportes.

## 🚀 Inicio Rápido

### 🪟 Windows:

**Crear ejecutable:**
```cmd
build.bat
```
El ejecutable estará en: `dist\CellSite\CellSite.exe`

**Modo desarrollo (sin build):**
```cmd
start.bat
```

### 🐧 Linux:

**Crear ejecutable:**
```bash
bash build.sh
```
El ejecutable estará en: `dist/CellSite/CellSite`

**Modo desarrollo (sin build):**
```bash
bash start.sh
```

## � USB Portable para Windows (NUEVO!)

**Para crear un ejecutable completamente portable en USB:**

```cmd
REM Verifica que todo este listo
verify_build_ready.bat

REM Construye el ejecutable
build_portable.bat

REM Resultado: dist\CellSite_portable\CellSite.exe
```

**Características del USB portable:**
- ✅ Funciona en **cualquier Windows 7+**
- ✅ **Sin instalación** de Python o dependencias
- ✅ Funciona en **cualquier computadora**
- ✅ Funciona desde **USB**, carpeta local o red
- ✅ Tus datos en `data/app.db` completamente portátil

**Usar desde USB:**
1. Copia carpeta `dist\CellSite_portable\` a tu USB
2. Haz doble-clic en `start_app.bat`
3. Se abre automáticamente en navegador

📖 **Más información:** Lee `INSTRUCCIONES_USB_PORTABLE.txt` y `WORKFLOW_CONSTRUCCION_USB.txt`

## �📋 Archivos de ayuda

- **LEEME_PRIMERO.txt** - Resumen rápido
- **INSTRUCCIONES_WINDOWS.txt** - Guía completa para Windows con solución de problemas
- **INSTRUCCIONES_EJECUTABLE.txt** - Información sobre ejecutables
- **DATOS_UBICACION.txt** - Dónde se guardan los datos y respaldos
- **README_CONSTRUCCION_USB.txt** - Resumen rápido del workflow USB (EMPIEZA AQUI)
- **INSTRUCCIONES_USB_PORTABLE.txt** - Guía para usar CellSite desde USB
- **WORKFLOW_CONSTRUCCION_USB.txt** - Procedimiento técnico para construir ejecutable USB
## 📂 ¿Dónde se guardan los datos?

La aplicación usa una base de datos SQLite que se guarda en:

**Durante desarrollo:**
- Linux: `/home/usuario/CellSite/data/app.db`
- Windows: `C:\Users\Usuario\CellSite\data\app.db`

**Ejecutable empaquetado:**
Los datos se guardan en la misma carpeta donde está el ejecutable:
- Linux: `dist/CellSite/data/app.db`
- Windows: `dist\CellSite\data\app.db`

### Cómo acceder a tus datos:

1. **Ver la base de datos:** Abre el archivo `app.db` con [DB Browser for SQLite](https://sqlitebrowser.org/)
2. **Respaldar:** Copia el archivo `app.db` a otra ubicación segura (USB, nube, etc.)
3. **Restaurar:** Reemplaza el archivo `app.db` con tu respaldo
4. **Exportar:** Usa el botón "Descargar Excel" desde la app (sección Caja)

⚠️ **IMPORTANTE:** Si desinstalas o borras la aplicación, asegúrate de hacer una copia del archivo `data/app.db` primero para no perder tus ventas, clientes y pagos.

## 🎯 Características

- ✅ Gestión de clientes (crear, ver, editar)
- ✅ Registro de ventas de celulares con datos de producto
- ✅ Sistema de pagos en cuotas
- ✅ Control de deudores con alertas automáticas (>3 días)
- ✅ Dashboard de caja diaria con desglose por método de pago
- ✅ Exportación a Excel (clientes y ventas completas)
- ✅ Generación de facturas PDF personalizadas
- ✅ Gestión de devoluciones con cálculo de reembolso
- ✅ Configuración de empresa con carga de logo
- ✅ Múltiples usuarios con autenticación
- ✅ 100% portable - no necesita instalación
- ✅ Funciona sin conexión a internet

## 💰 Formato de moneda

La aplicación usa **pesos colombianos (COP)** sin decimales:
- Todos los valores se ingresan como números enteros (Ej: 500000, 1000000)
- Los reportes y pantallas muestran el formato: COP 1.000.000

## 👤 Primer uso

Usuario por defecto:
- **Usuario:** `admin`
- **Contraseña:** `admin`

Puedes crear usuarios adicionales desde la aplicación (botón "Crear usuario" en login).

## 🔧 Requisitos técnicos

**Para crear el ejecutable:**
- Python 3.8 o superior
- Conexión a internet (solo para descargar dependencias)

**Para usar el ejecutable:**
- ❌ NO necesita Python
- ❌ NO necesita internet
- ✅ Funciona directo desde USB o cualquier carpeta

## �️ Scripts disponibles

**Windows:**
- `verify_build_ready.bat` - Verifica que todo este listo para construir
- `build.bat` - Construye ejecutable estándar (modo directorio)
- `build_portable.bat` - Construye ejecutable USB portable (en un solo archivo)
- `start.bat` - Ejecuta en modo desarrollo (necesita Python)
- `start_app.bat` - Ejecuta el aplicativo compilado

**Linux:**
- `build.sh` - Construye ejecutable para Linux
- `start.sh` - Ejecuta en modo desarrollo

## �📦 Distribución

Una vez creado el ejecutable, puedes:

1. **Copiar a USB** - Toda la carpeta `dist/CellSite/`
2. **Ejecutar en otro PC** - Sin instalación, doble clic y listo
3. **Llevar tus datos** - El archivo `data/app.db` contiene todo
4. **Compartir** - Copia la carpeta a otros usuarios

**Compatibilidad:**
- Windows → Crear en Windows
- Linux → Crear en Linux
- Mac → Crear en Mac

(El ejecutable solo funciona en el sistema donde se creó)

