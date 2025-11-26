# Analizador de Espectros Rosetta

Aplicación web completa para analizar archivos `.tab` de la misión Rosetta, generar gráficas de espectros de masas y obtener conclusiones científicas mediante un modelo fine-tuneado de OpenAI.

## 🏗️ Arquitectura

- **Frontend**: React + Vite
- **Backend**: Python + FastAPI
- **IA**: OpenAI GPT-4 fine-tuneado

## 📋 Requisitos Previos

- Python 3.8+
- Node.js 16+
- npm o yarn
- API Key de OpenAI
- Modelo fine-tuneado de OpenAI (opcional, pero recomendado)

## 🚀 Instalación

### 1. Backend

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

pip install -r requirements.txt
```

### 2. Configurar Variables de Entorno

Crea un archivo `.env` en el directorio `backend/`:

```env
OPENAI_API_KEY=sk-tu-clave-aqui
FT_MODEL_NAME=ft:gpt-4o-mini:astroquimico-2025
```

**⚠️ IMPORTANTE**: Reemplaza `sk-tu-clave-aqui` con tu API key real de OpenAI y `ft:gpt-4o-mini:astroquimico-2025` con el nombre de tu modelo fine-tuneado.

### 3. Frontend

```bash
cd frontend
npm install
```

### 4. Configurar URL del Backend (Opcional)

Si el backend no está en `http://localhost:8000`, crea un archivo `.env` en `frontend/`:

```env
VITE_API_URL=http://localhost:8000
```

## ▶️ Ejecución

### Iniciar Backend

```bash
cd backend
# Asegúrate de tener el entorno virtual activado
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

El backend estará disponible en `http://localhost:8000`

### Iniciar Frontend

```bash
cd frontend
npm run dev
```

El frontend estará disponible en `http://localhost:3000`

## 📖 Uso

1. Abre `http://localhost:3000` en tu navegador
2. Haz clic en "Seleccionar archivo .tab"
3. Selecciona un archivo `.tab` de Rosetta
4. Espera a que se procese el archivo
5. Visualiza la gráfica del espectro y lee la conclusión generada

## 🔧 Estructura del Proyecto

```
APPROSETTA/
├── backend/
│   ├── app.py                 # API FastAPI principal
│   ├── rosetta_pipeline.py    # Procesamiento de archivos .tab
│   ├── requirements.txt       # Dependencias Python
│   └── .env                   # Variables de entorno (crear manualmente)
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   └── UploadForm.jsx # Componente principal
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
└── README.md
```

## 🐛 Solución de Problemas

### Error: "OPENAI_API_KEY no configurada"
- Asegúrate de haber creado el archivo `.env` en `backend/`
- Verifica que la variable `OPENAI_API_KEY` esté correctamente escrita

### Error: "El archivo debe ser .tab"
- Solo se aceptan archivos con extensión `.tab`

### Error de CORS
- El backend ya está configurado para permitir CORS desde cualquier origen
- En producción, modifica `allow_origins` en `backend/app.py`

### El frontend no se conecta al backend
- Verifica que el backend esté corriendo en el puerto 8000
- Revisa la variable `VITE_API_URL` en `frontend/.env`

## 📝 Notas

- El procesamiento de archivos `.tab` está adaptado del código original de Google Colab
- El modelo fine-tuneado debe estar entrenado con espectros de Rosetta para mejores resultados
- Los espectros se resumen en 100 bins antes de enviarse al modelo de OpenAI

## 🔒 Seguridad

- **NUNCA** subas el archivo `.env` a un repositorio público
- El archivo `.env` ya está en `.gitignore`
- En producción, usa variables de entorno del sistema o un gestor de secretos

## 🌐 Despliegue en Línea

Para desplegar la aplicación en línea de forma gratuita, consulta el archivo [DEPLOY.md](./DEPLOY.md) que contiene instrucciones detalladas para usar:
- **Vercel** (Frontend)
- **Railway** (Backend)

## 📄 Licencia

Este proyecto es para uso académico y de investigación.

