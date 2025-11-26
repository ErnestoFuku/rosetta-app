@echo off
echo ========================================
echo Instalacion del Frontend - Rosetta App
echo ========================================
echo.

REM Verificar si Node.js esta instalado
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js no encontrado. Por favor instala Node.js 16 o superior.
    echo Descarga Node.js desde: https://nodejs.org/
    pause
    exit /b 1
)

echo [OK] Node.js encontrado
node --version
echo.

REM Verificar si npm esta instalado
npm --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] npm no encontrado.
    pause
    exit /b 1
)

echo [OK] npm encontrado
npm --version
echo.

REM Instalar dependencias
echo [1/1] Instalando dependencias de Node.js...
call npm install
if errorlevel 1 (
    echo [ERROR] No se pudieron instalar las dependencias
    pause
    exit /b 1
)
echo [OK] Dependencias instaladas
echo.

echo ========================================
echo Instalacion completada!
echo ========================================
echo.
echo Para iniciar el frontend, ejecuta:
echo   npm run dev
echo.
echo El frontend estara disponible en: http://localhost:3000
echo.
pause

