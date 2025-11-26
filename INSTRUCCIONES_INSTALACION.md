# 🚀 Instrucciones de Instalación - Rosetta App

## ✅ Configuración Completada

Ya he configurado:
- ✅ API Key de OpenAI en `backend/config.env`
- ✅ Prompt ID configurado
- ✅ Código actualizado para usar el endpoint de responses
- ✅ Scripts de instalación automática creados

## 📋 Pasos para Ejecutar la Aplicación

### Opción 1: Instalación Automática (Recomendado)

#### Backend:

1. Abre una terminal en el directorio `backend`
2. Ejecuta:
   ```bash
   install.bat
   ```
   Este script:
   - Verificará que Python esté instalado
   - Creará el entorno virtual
   - Instalará todas las dependencias

3. Una vez completada la instalación, ejecuta:
   ```bash
   start.bat
   ```
   O manualmente:
   ```bash
   venv\Scripts\activate
   uvicorn app:app --host 0.0.0.0 --port 8000 --reload
   ```

#### Frontend:

1. Abre una terminal en el directorio `frontend`
2. Ejecuta:
   ```bash
   install.bat
   ```
   Este script instalará todas las dependencias de Node.js

3. Una vez completada la instalación, ejecuta:
   ```bash
   npm run dev
   ```

### Opción 2: Instalación Manual

#### Backend:

```bash
cd backend

# Crear entorno virtual
python -m venv venv

# Activar entorno virtual (Windows)
venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Iniciar servidor
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

#### Frontend:

```bash
cd frontend

# Instalar dependencias
npm install

# Iniciar servidor de desarrollo
npm run dev
```

## 🔑 Configuración de API Key

La API key ya está configurada en `backend/config.env`. Si necesitas cambiarla:

1. Edita el archivo `backend/config.env`
2. O crea un archivo `.env` en `backend/` con:
   ```
   OPENAI_API_KEY=tu-clave-aqui
   PROMPT_ID=pmpt_691e722d960081968e46c65f5c593d99071851aeba7d0701
   ```

## 🌐 Acceso a la Aplicación

Una vez que ambos servidores estén corriendo:

- **Frontend**: http://localhost:3000
- **Backend**: http://localhost:8000

## ✅ Verificación

Para verificar que todo funciona:

1. Abre http://localhost:8000 en tu navegador
2. Deberías ver:
   ```json
   {
     "message": "Rosetta Spectrum Analyzer API",
     "status": "running",
     "openai_configured": true
   }
   ```

3. Si `openai_configured` es `true`, la API key está correctamente configurada.

## 🐛 Solución de Problemas

### Error: "Python no encontrado"
- Instala Python 3.8+ desde https://www.python.org/downloads/
- Asegúrate de marcar "Add Python to PATH" durante la instalación

### Error: "Node.js no encontrado"
- Instala Node.js 16+ desde https://nodejs.org/

### Error: "OPENAI_API_KEY no configurada"
- Verifica que el archivo `backend/config.env` exista y tenga la API key
- O crea un archivo `.env` en `backend/` con la configuración

### El frontend no se conecta al backend
- Verifica que el backend esté corriendo en el puerto 8000
- Revisa la consola del navegador para ver errores de CORS

## 📝 Notas Importantes

- **Nunca subas** el archivo `config.env` o `.env` a un repositorio público
- El backend debe estar corriendo antes de usar el frontend
- El prompt ID ya está configurado y se usará automáticamente

## 🎯 Uso de la Aplicación

1. Abre http://localhost:3000
2. Haz clic en "Seleccionar archivo .tab"
3. Selecciona un archivo `.tab` de Rosetta
4. Espera a que se procese (puede tardar unos segundos)
5. Visualiza la gráfica del espectro
6. Lee la conclusión generada por el modelo de IA

¡Listo! Tu aplicación está configurada y lista para usar. 🚀

