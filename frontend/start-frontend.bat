@echo off
echo ========================================
echo Iniciando Frontend - Rosetta App
echo ========================================
echo.

REM Verificar Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js no encontrado.
    echo Por favor:
    echo 1. Instala Node.js desde https://nodejs.org/
    echo 2. Reinicia esta terminal
    echo 3. Ejecuta este script nuevamente
    pause
    exit /b 1
)

echo [OK] Node.js encontrado
node --version
npm --version
echo.

REM Verificar si node_modules existe
if not exist "node_modules" (
    echo [INFO] Instalando dependencias por primera vez...
    call npm install
    if errorlevel 1 (
        echo [ERROR] No se pudieron instalar las dependencias
        pause
        exit /b 1
    )
    echo [OK] Dependencias instaladas
    echo.
)

echo [INFO] Iniciando servidor de desarrollo...
echo [INFO] El frontend estara disponible en: http://localhost:3000
echo.
call npm run dev

