# 🚀 Inicio Rápido - Rosetta App

## ✅ Backend ya está corriendo

El backend está activo en: **http://localhost:8000**

---

## 🎯 Para iniciar el Frontend:

### Opción 1: Script Automático (Recomendado)

1. Abre una **nueva terminal** (PowerShell o CMD)
2. Navega al directorio frontend:
   ```powershell
   cd "C:\Users\ernes\Documents\Ingeniería química\Estancia académica\APPROSETTA\frontend"
   ```
3. Ejecuta el script:
   ```powershell
   .\start-frontend.bat
   ```

### Opción 2: Comandos Manuales

1. Abre una **nueva terminal**
2. Navega al directorio frontend:
   ```powershell
   cd "C:\Users\ernes\Documents\Ingeniería química\Estancia académica\APPROSETTA\frontend"
   ```
3. Instala dependencias (solo la primera vez):
   ```powershell
   npm install
   ```
4. Inicia el servidor:
   ```powershell
   npm run dev
   ```

---

## ⚠️ Si Node.js no se reconoce:

1. **Cierra esta terminal completamente**
2. **Abre una nueva terminal** (PowerShell o CMD)
3. Verifica que Node.js funcione:
   ```powershell
   node --version
   npm --version
   ```
4. Si aún no funciona, verifica que Node.js esté instalado y en el PATH:
   - Ve a: Panel de Control > Sistema > Configuración avanzada del sistema > Variables de entorno
   - Verifica que la ruta de Node.js esté en la variable PATH

---

## 🌐 URLs de la Aplicación:

- **Backend API**: http://localhost:8000
- **Frontend**: http://localhost:3000 (después de iniciar)

---

## ✅ Verificación:

1. **Backend**: Abre http://localhost:8000 en tu navegador
   - Deberías ver un JSON con `"status": "running"`

2. **Frontend**: Abre http://localhost:3000 en tu navegador
   - Deberías ver la interfaz de la aplicación

---

## 🎉 ¡Listo!

Una vez que ambos servidores estén corriendo, puedes:
1. Abrir http://localhost:3000
2. Hacer clic en "Seleccionar archivo .tab"
3. Subir un archivo .tab de Rosetta
4. Ver la gráfica y la conclusión

