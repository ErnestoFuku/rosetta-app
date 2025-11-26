# 📋 Pasos de Instalación - Ejecutar en Terminal

## ⚠️ IMPORTANTE: Python debe estar instalado

Si Python no está instalado o no está en el PATH, descárgalo desde:
https://www.python.org/downloads/

**Durante la instalación, marca la opción: "Add Python to PATH"**

---

## 🚀 PASO 1: Instalar Backend

### Abre PowerShell o CMD y ejecuta:

```powershell
# Navegar al directorio backend
cd "C:\Users\ernes\Documents\Ingeniería química\Estancia académica\APPROSETTA\backend"

# Crear entorno virtual
python -m venv venv

# Activar entorno virtual (Windows)
venv\Scripts\activate

# Instalar dependencias
pip install --upgrade pip
pip install -r requirements.txt
```

### O simplemente ejecuta el script automático:

```powershell
cd "C:\Users\ernes\Documents\Ingeniería química\Estancia académica\APPROSETTA\backend"
.\install.bat
```

---

## 🚀 PASO 2: Iniciar Backend

```powershell
# Si no está activado el entorno virtual
cd "C:\Users\ernes\Documents\Ingeniería química\Estancia académica\APPROSETTA\backend"
venv\Scripts\activate

# Iniciar servidor
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

### O ejecuta el script de inicio:

```powershell
.\start.bat
```

**El backend estará disponible en: http://localhost:8000**

---

## 🚀 PASO 3: Instalar Frontend

### Abre una NUEVA terminal y ejecuta:

```powershell
# Navegar al directorio frontend
cd "C:\Users\ernes\Documents\Ingeniería química\Estancia académica\APPROSETTA\frontend"

# Instalar dependencias
npm install
```

### O ejecuta el script automático:

```powershell
.\install.bat
```

---

## 🚀 PASO 4: Iniciar Frontend

```powershell
# En la misma terminal del frontend
npm run dev
```

**El frontend estará disponible en: http://localhost:3000**

---

## ✅ Verificación

1. Abre tu navegador y ve a: **http://localhost:8000**
2. Deberías ver:
   ```json
   {
     "message": "Rosetta Spectrum Analyzer API",
     "status": "running",
     "openai_configured": true
   }
   ```

3. Si `openai_configured` es `true`, ¡todo está bien configurado!

---

## 🎯 Uso de la Aplicación

1. Abre **http://localhost:3000** en tu navegador
2. Haz clic en **"Seleccionar archivo .tab"**
3. Selecciona un archivo `.tab` de Rosetta
4. Espera a que se procese
5. Visualiza la gráfica del espectro
6. Lee la conclusión generada

---

## 🔧 Solución de Problemas

### Error: "Python no encontrado"
- Instala Python desde: https://www.python.org/downloads/
- **IMPORTANTE**: Marca "Add Python to PATH" durante la instalación
- Reinicia la terminal después de instalar

### Error: "npm no encontrado"
- Instala Node.js desde: https://nodejs.org/
- Reinicia la terminal después de instalar

### Error: "No se puede activar el entorno virtual"
- Asegúrate de estar en el directorio `backend`
- Verifica que el directorio `venv` exista
- Si no existe, ejecuta: `python -m venv venv`

### El frontend no se conecta al backend
- Verifica que el backend esté corriendo en el puerto 8000
- Abre http://localhost:8000 para verificar
- Revisa la consola del navegador (F12) para ver errores

---

## 📝 Notas

- **Mantén ambas terminales abiertas**: una para el backend y otra para el frontend
- La API key ya está configurada en `backend/config.env`
- El prompt ID ya está configurado
- Si cambias algo en el código del backend, se recargará automáticamente (gracias a `--reload`)

---

## 🎉 ¡Listo!

Una vez que ambos servidores estén corriendo, puedes usar la aplicación completa.

