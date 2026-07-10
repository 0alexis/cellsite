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

**Instalacion local continua:**
```bash
./install_local_service.sh
```

Esto instala un servicio de usuario en:
```text
~/.config/systemd/user/cellsite.service
```

El servicio arranca CellSite automaticamente al iniciar sesion y lo vuelve a levantar si se cierra por error. La app queda disponible en:
```text
http://127.0.0.1:8765
```

**Actualizar una instalacion local existente:**
```bash
systemctl --user stop cellsite.service
bash build.sh
./install_local_service.sh
systemctl --user status cellsite.service
```

Si estas trabajando desde esta carpeta del proyecto, no es obligatorio reconstruir para tomar cambios de `app.py`, `templates/` o `static/`; puedes reiniciar el servicio:
```bash
systemctl --user restart cellsite.service
```

Si estas usando la carpeta empaquetada `dist/CellSite/`, si debes volver a correr `bash build.sh` y ejecutar `./install_local_service.sh` desde la carpeta actualizada.

La reinstalacion del servicio no borra la base de datos. Tus datos siguen en `data/app.db` cuando ejecutas desde el proyecto, o en `dist/CellSite/data/app.db` cuando ejecutas desde el paquete compilado. Antes de reemplazar carpetas completas, respalda ese archivo.

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
- `run_cellsite.sh` - Lanza CellSite para uso con servicio local
- `install_local_service.sh` - Instala inicio local continuo con systemd de usuario
- `uninstall_local_service.sh` - Quita el servicio local continuo

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

