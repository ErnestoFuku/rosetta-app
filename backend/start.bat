@echo off
echo Iniciando servidor FastAPI...
echo.
echo Asegurate de haber activado el entorno virtual primero:
echo   venv\Scripts\activate
echo.
echo Y de haber configurado el archivo .env con tu OPENAI_API_KEY
echo.
pause
uvicorn app:app --host 0.0.0.0 --port 8000 --reload

