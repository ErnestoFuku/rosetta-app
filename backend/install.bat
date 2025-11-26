@echo off
echo ========================================
echo Instalacion del Backend - Rosetta App
echo ========================================
echo.

REM Verificar si Python esta instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python no encontrado. Por favor instala Python 3.8 o superior.
    echo Descarga Python desde: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [OK] Python encontrado
python --version
echo.

REM Crear entorno virtual
echo [1/3] Creando entorno virtual...
if exist venv (
    echo [INFO] El entorno virtual ya existe. Se omitira este paso.
) else (
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] No se pudo crear el entorno virtual
        pause
        exit /b 1
    )
    echo [OK] Entorno virtual creado
)
echo.

REM Activar entorno virtual e instalar dependencias
echo [2/3] Instalando dependencias...
call venv\Scripts\activate.bat
pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] No se pudieron instalar las dependencias
    pause
    exit /b 1
)
echo [OK] Dependencias instaladas
echo.

REM Verificar configuracion
echo [3/3] Verificando configuracion...
if exist config.env (
    echo [OK] Archivo config.env encontrado
) else (
    echo [ADVERTENCIA] Archivo config.env no encontrado
    echo Por favor crea el archivo .env o config.env con tu OPENAI_API_KEY
)
echo.

echo ========================================
echo Instalacion completada!
echo ========================================
echo.
echo Para iniciar el servidor, ejecuta:
echo   start.bat
echo.
echo O manualmente:
echo   venv\Scripts\activate
echo   uvicorn app:app --host 0.0.0.0 --port 8000 --reload
echo.
pause

