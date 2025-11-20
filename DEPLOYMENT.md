# Procesador de Planillas Bancarias

Aplicación web para convertir extractos bancarios de BROU e Itaú al formato compatible con **Finanzas Personales de ZetaSoftware**.

## 🚀 Deployment en Streamlit Community Cloud

### Opción 1: Streamlit Community Cloud (Recomendada - GRATIS)

1. **Crear repositorio en GitHub**:

   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/TU_USUARIO/procesador-planillas-bancarias.git
   git push -u origin main
   ```

2. **Deployar en Streamlit**:
   - Ve a [share.streamlit.io](https://share.streamlit.io)
   - Inicia sesión con GitHub
   - Click en "New app"
   - Selecciona tu repositorio
   - Main file: `app.py`
   - Click "Deploy"
   - ¡Listo! Tu app estará en: `https://tu-usuario-procesador-planillas.streamlit.app`

**Ventajas**:

- ✅ Completamente gratis
- ✅ Deploy automático con cada push
- ✅ HTTPS incluido
- ✅ No requiere configuración de servidor

---

### Opción 2: Railway (GRATIS con límites)

1. **Crear cuenta en Railway**:

   - Ve a [railway.app](https://railway.app)
   - Inicia sesión con GitHub

2. **Crear `Procfile`** (ya incluido en este proyecto)

3. **Deploy**:
   - Click "New Project"
   - Selecciona "Deploy from GitHub repo"
   - Selecciona tu repositorio
   - Railway detectará automáticamente Streamlit
   - ¡Deploy automático!

**Ventajas**:

- ✅ $5 USD de crédito gratis mensual
- ✅ Auto-deploy con GitHub
- ✅ Más recursos que Streamlit Cloud

---

### Opción 3: Render (GRATIS)

1. **Crear cuenta en Render**:

   - Ve a [render.com](https://render.com)
   - Inicia sesión con GitHub

2. **Deploy**:
   - Click "New +" → "Web Service"
   - Conecta tu repositorio
   - Runtime: Python 3
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `streamlit run app.py --server.port $PORT --server.address 0.0.0.0`
   - ¡Deploy!

**Ventajas**:

- ✅ Completamente gratis (plan Free)
- ✅ Auto-deploy desde GitHub
- ✅ SSL automático

---

## 📦 Archivos necesarios para deployment

Todos los archivos ya están incluidos:

- ✅ `app.py` - Aplicación principal
- ✅ `requirements.txt` - Dependencias
- ✅ `.gitignore` - Archivos a ignorar
- ✅ `Procfile` - Configuración para Railway
- ✅ `.streamlit/config.toml` - Configuración de Streamlit

---

## 🎯 Recomendación

**Usar Streamlit Community Cloud** porque:

1. Es gratis sin límites
2. Específicamente diseñado para apps Streamlit
3. Deploy en 2 minutos
4. URL personalizada automática
5. No requiere configuración adicional

---

## 📝 Pasos rápidos (Streamlit Cloud)

```bash
# 1. Crear repositorio en GitHub (desde la web de GitHub)
#    Nombre sugerido: procesador-planillas-bancarias

# 2. En tu terminal:
cd /Users/joaquincaballero/Desarrollo/finanzas
git init
git add .
git commit -m "Procesador de planillas BROU e Itaú para Finanzas Personales"
git branch -M main
git remote add origin https://github.com/TU_USUARIO/procesador-planillas-bancarias.git
git push -u origin main

# 3. Ve a share.streamlit.io y deploya en 1 click
```

---

## 🌐 Después del deployment

Tu aplicación estará disponible 24/7 en una URL pública que podrás compartir con quien quieras.

**URL ejemplo**: `https://joaquin-procesador-planillas.streamlit.app`
