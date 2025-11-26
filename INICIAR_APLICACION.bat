@echo off
echo ========================================
echo    ROSETTA APP - Inicio Completo
echo ========================================
echo.

REM Verificar Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js no encontrado en el PATH.
    echo.
    echo Por favor:
    echo 1. Asegurate de que Node.js este instalado
    echo 2. Reinicia esta terminal
    echo 3. O ejecuta este script desde una nueva terminal
    echo.
    pause
    exit /b 1
)

echo [OK] Node.js encontrado
node --version
npm --version
echo.

REM Navegar al directorio frontend
cd /d "%~dp0frontend"
if not exist "package.json" (
    echo [ERROR] No se encontro el directorio frontend
    pause
    exit /b 1
)

echo [INFO] Directorio: %CD%
echo.

REM Verificar si node_modules existe
if not exist "node_modules" (
    echo [1/2] Instalando dependencias del frontend...
    call npm install
    if errorlevel 1 (
        echo [ERROR] No se pudieron instalar las dependencias
        pause
        exit /b 1
    )
    echo [OK] Dependencias instaladas
    echo.
) else (
    echo [INFO] Dependencias ya instaladas
    echo.
)

echo [2/2] Iniciando servidor de desarrollo del frontend...
echo.
echo ========================================
echo   Frontend: http://localhost:3000
echo   Backend:  http://localhost:8000
echo ========================================
echo.
echo Presiona Ctrl+C para detener el servidor
echo.

call npm run dev

