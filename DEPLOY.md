# 🚀 Guía de Despliegue - Rosetta App

Esta guía te ayudará a desplegar la aplicación Rosetta de forma gratuita usando:
- **Vercel** (Frontend - React) - Gratis
- **Railway** (Backend - FastAPI) - Gratis con límites generosos

---

## 📋 Requisitos Previos

1. Cuenta en GitHub (gratis)
2. Cuenta en Vercel (gratis) - https://vercel.com
3. Cuenta en Railway (gratis) - https://railway.app
4. Tu API Key de OpenAI

---

## 🔧 Paso 1: Preparar el Repositorio

### 1.1 Subir el código a GitHub

```bash
# Inicializar git (si no lo has hecho)
git init
git add .
git commit -m "Initial commit - Rosetta App"

# Crear repositorio en GitHub y luego:
git remote add origin https://github.com/TU_USUARIO/TU_REPO.git
git branch -M main
git push -u origin main
```

**⚠️ IMPORTANTE**: Asegúrate de que el archivo `.gitignore` esté en la raíz para no subir archivos sensibles.

---

## 🚂 Paso 2: Desplegar Backend en Railway

### 2.1 Conectar Railway con GitHub

1. Ve a https://railway.app
2. Inicia sesión con GitHub
3. Click en "New Project"
4. Selecciona "Deploy from GitHub repo"
5. Elige tu repositorio

### 2.2 Configurar el Proyecto

Railway detectará automáticamente que es un proyecto Python. Si no, configura:

- **Root Directory**: `backend`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn app:app --host 0.0.0.0 --port $PORT`

O simplemente usa el `Procfile` que ya está en la raíz del proyecto.

### 2.3 Configurar Variables de Entorno

En Railway, ve a tu proyecto → Settings → Variables y agrega:

```
OPENAI_API_KEY=sk-tu-clave-aqui
PROMPT_ID=pmpt_691eb6347b388194bab33de01809fa1f0fb2b90b7c2f4bd5
```

**⚠️ IMPORTANTE**: 
- Reemplaza `sk-tu-clave-aqui` con tu API key real de OpenAI
- Railway automáticamente configurará `PORT`, no necesitas agregarlo

### 2.4 Obtener la URL del Backend

1. Ve a tu servicio en Railway
2. Click en "Settings" → "Domains" o "Networking"
3. Railway te dará una URL como: `https://tu-proyecto.railway.app`
4. **Copia esta URL** - la necesitarás para el frontend

### 2.5 Verificar que el Backend Funciona

Abre en tu navegador: `https://tu-proyecto.railway.app/docs`

Deberías ver la documentación de FastAPI.

---

## ⚡ Paso 3: Desplegar Frontend en Vercel

### 3.1 Conectar Vercel con GitHub

1. Ve a https://vercel.com
2. Inicia sesión con GitHub
3. Click en "Add New Project"
4. Importa tu repositorio de GitHub

### 3.2 Configurar el Proyecto

Vercel detectará automáticamente que es un proyecto Vite. Configura:

- **Framework Preset**: Vite
- **Root Directory**: `frontend`
- **Build Command**: `npm run build` (automático)
- **Output Directory**: `dist` (automático)
- **Install Command**: `npm install` (automático)

### 3.3 Configurar Variables de Entorno

En Vercel, ve a tu proyecto → Settings → Environment Variables y agrega:

```
VITE_API_URL=https://tu-proyecto.railway.app
```

**⚠️ IMPORTANTE**: 
- Reemplaza `https://tu-proyecto.railway.app` con la URL real de tu backend en Railway
- Agrega esta variable para todos los ambientes (Production, Preview, Development)

### 3.4 Desplegar

Click en "Deploy". Vercel construirá y desplegará tu aplicación automáticamente.

### 3.5 Obtener la URL del Frontend

Vercel te dará una URL como: `https://tu-proyecto.vercel.app`

---

## ✅ Paso 4: Verificar que Todo Funciona

1. Abre la URL de Vercel en tu navegador
2. Intenta subir un archivo `.tab`
3. Verifica que se procese correctamente
4. Revisa la consola del navegador (F12) si hay errores

---

## 🔄 Actualizaciones Futuras

Cada vez que hagas `git push` a GitHub:
- **Railway** se actualizará automáticamente
- **Vercel** se actualizará automáticamente

---

## 🐛 Solución de Problemas

### El frontend no se conecta al backend

1. Verifica que `VITE_API_URL` en Vercel sea la URL correcta de Railway
2. Verifica que el backend esté funcionando: `https://tu-backend.railway.app/docs`
3. Revisa la consola del navegador (F12) para ver errores
4. Asegúrate de que la variable de entorno esté configurada para "Production"

### Error de CORS

El backend ya está configurado para permitir CORS desde cualquier origen. Si tienes problemas:

1. Verifica que `allow_origins=["*"]` esté en `backend/app.py` (línea 24)
2. Reinicia el servicio en Railway

### El backend no inicia en Railway

1. Verifica que `Procfile` esté en la raíz del proyecto
2. Verifica que `requirements.txt` esté en `backend/`
3. Revisa los logs en Railway para ver el error específico
4. Asegúrate de que el comando en Procfile sea correcto

### Variables de entorno no funcionan

1. En Railway: Verifica que las variables estén en "Variables" (no en "Secrets")
2. En Vercel: Verifica que las variables estén en "Environment Variables"
3. Reinicia los servicios después de agregar variables
4. En Vercel, asegúrate de agregar la variable para "Production"

### El frontend muestra "Error al procesar el archivo"

1. Verifica que el backend esté funcionando en Railway
2. Verifica que `VITE_API_URL` esté correctamente configurada
3. Revisa los logs del backend en Railway para ver errores
4. Verifica que `OPENAI_API_KEY` esté correctamente configurada en Railway

---

## 💰 Límites Gratuitos

### Railway (Backend)
- $5 de crédito gratis al mes
- Suficiente para uso moderado
- Se renueva mensualmente
- Puedes ver el uso en el dashboard

### Vercel (Frontend)
- 100 GB de ancho de banda al mes
- Deployments ilimitados
- Más que suficiente para uso personal/académico
- Builds ilimitados

---

## 📝 Notas Importantes

1. **NUNCA** subas tu `.env` o `config.env` a GitHub (ya está en `.gitignore`)
2. Siempre usa variables de entorno en los servicios de despliegue
3. Railway puede tardar unos minutos en iniciar el backend la primera vez
4. Vercel suele ser más rápido en el despliegue (1-2 minutos)
5. Si cambias variables de entorno, puede que necesites hacer un nuevo deploy

---

## 🎉 ¡Listo!

Tu aplicación Rosetta ahora está en línea y accesible desde cualquier lugar.

Si necesitas ayuda, revisa los logs en Railway y Vercel para diagnosticar problemas.

---

## 📞 Checklist Final

Antes de considerar el despliegue completo, verifica:

- [ ] Backend desplegado en Railway y funcionando (`/docs` accesible)
- [ ] Frontend desplegado en Vercel
- [ ] Variable `VITE_API_URL` configurada en Vercel con la URL de Railway
- [ ] Variable `OPENAI_API_KEY` configurada en Railway
- [ ] Variable `PROMPT_ID` configurada en Railway
- [ ] Puedes subir un archivo `.tab` y procesarlo correctamente
- [ ] La imagen de fondo se muestra correctamente
- [ ] Los gráficos se muestran correctamente
- [ ] La conclusión de OpenAI se genera correctamente

