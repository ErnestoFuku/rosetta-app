# 🚀 Cómo Ejecutar la Aplicación

## ✅ Backend ya está corriendo

El backend está activo en: **http://localhost:8000**

---

## 🎯 Para iniciar el Frontend:

### Método más fácil:

1. **Abre una NUEVA terminal** (PowerShell o CMD)
   - Cierra esta terminal si es necesario
   - Abre una nueva desde el menú Inicio

2. **Navega al directorio del proyecto:**
   ```powershell
   cd "C:\Users\ernes\Documents\Ingeniería química\Estancia académica\APPROSETTA"
   ```

3. **Ejecuta el script automático:**
   ```powershell
   .\INICIAR_APLICACION.bat
   ```

Este script:
- ✅ Verifica que Node.js esté instalado
- ✅ Instala las dependencias automáticamente
- ✅ Inicia el servidor de desarrollo

---

### Método manual:

Si prefieres hacerlo paso a paso:

1. **Abre una nueva terminal**

2. **Navega al frontend:**
   ```powershell
   cd "C:\Users\ernes\Documents\Ingeniería química\Estancia académica\APPROSETTA\frontend"
   ```

3. **Instala dependencias (solo la primera vez):**
   ```powershell
   npm install
   ```

4. **Inicia el servidor:**
   ```powershell
   npm run dev
   ```

---

## ⚠️ Si Node.js no se reconoce:

1. **Verifica la instalación:**
   - Abre una nueva terminal
   - Ejecuta: `node --version`
   - Si no funciona, Node.js no está en el PATH

2. **Solución:**
   - Reinstala Node.js desde https://nodejs.org/
   - **IMPORTANTE**: Marca "Add to PATH" durante la instalación
   - Reinicia tu terminal después de instalar

---

## 🌐 URLs de la Aplicación:

- **Backend API**: http://localhost:8000
- **Frontend**: http://localhost:3000

---

## ✅ Verificación:

1. **Backend**: Abre http://localhost:8000
   - Deberías ver: `{"message": "Rosetta Spectrum Analyzer API", "status": "running"}`

2. **Frontend**: Abre http://localhost:3000
   - Deberías ver la interfaz de la aplicación con el botón "Seleccionar archivo .tab"

---

## 🎉 ¡Listo para usar!

Una vez que ambos servidores estén corriendo:

1. Abre http://localhost:3000 en tu navegador
2. Haz clic en "Seleccionar archivo .tab"
3. Sube un archivo `.tab` de Rosetta
4. Visualiza la gráfica del espectro
5. Lee la conclusión generada por el modelo de IA

---

## 📝 Notas:

- **Mantén ambas terminales abiertas**: una para el backend y otra para el frontend
- El backend ya está corriendo, solo necesitas iniciar el frontend
- Si cierras alguna terminal, el servidor correspondiente se detendrá

