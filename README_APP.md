# Aplicación Web - Procesador de Planillas BROU

## 🚀 Instalación

1. Asegúrate de tener el entorno virtual activado:

```bash
source env/bin/activate
```

2. Instala las dependencias:

```bash
pip install streamlit
```

## ▶️ Cómo ejecutar la aplicación

Desde la terminal, en la carpeta del proyecto, ejecuta:

```bash
streamlit run app.py
```

La aplicación se abrirá automáticamente en tu navegador en `http://localhost:8501`

## 📋 Cómo usar

1. **Sube tu archivo**: Haz clic en "Browse files" y selecciona tu archivo .xls o .xlsx de movimientos del BROU

2. **Filtrar por fecha (opcional)**:

   - Marca la casilla "Filtrar por fecha"
   - Selecciona la fecha desde la cual quieres ver movimientos

3. **Procesar**: Haz clic en el botón "🚀 Procesar Planilla"

4. **Descargar**: Revisa la vista previa y descarga el archivo procesado con el botón "⬇️ Descargar archivo procesado"

## ✨ Características

- ✅ Interfaz web simple e intuitiva
- ✅ Carga de archivos .xls y .xlsx
- ✅ Filtrado opcional por fecha
- ✅ Vista previa de resultados
- ✅ Descarga automática con timestamp
- ✅ Sin necesidad de editar código

## 🛑 Detener la aplicación

Presiona `Ctrl + C` en la terminal donde está corriendo Streamlit.
