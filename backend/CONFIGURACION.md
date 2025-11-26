# Configuración de Variables de Entorno

## ⚠️ IMPORTANTE: Configura tu API Key y Modelo Fine-tuneado

Para que la aplicación funcione correctamente, necesitas crear un archivo `.env` en este directorio (`backend/`) con las siguientes variables:

## Pasos:

1. Crea un archivo llamado `.env` en el directorio `backend/`
2. Agrega las siguientes líneas (reemplaza con tus valores reales):

```env
OPENAI_API_KEY=sk-tu-clave-aqui
FT_MODEL_NAME=ft:gpt-4o-mini:astroquimico-2025
```

## Explicación de las variables:

- **OPENAI_API_KEY**: Tu clave de API de OpenAI. Obtén una en: https://platform.openai.com/api-keys
- **FT_MODEL_NAME**: El nombre de tu modelo fine-tuneado. Ejemplo: `ft:gpt-4o-mini:astroquimico-2025`

## Ejemplo completo:

```env
OPENAI_API_KEY=sk-proj-abc123def456ghi789jkl012mno345pqr678stu901vwx234yz
FT_MODEL_NAME=ft:gpt-4o-mini:astroquimico-2025
```

## ⚠️ SEGURIDAD

- **NUNCA** subas el archivo `.env` a un repositorio público
- El archivo `.env` ya está en `.gitignore` para proteger tus credenciales
- Si trabajas en equipo, comparte las instrucciones pero no el archivo `.env` completo

## Verificación

Una vez configurado, puedes verificar que funciona iniciando el servidor:

```bash
cd backend
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

Si visitas `http://localhost:8000`, deberías ver un mensaje con `"openai_configured": true` si todo está bien configurado.

