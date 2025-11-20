# Procesador de Planillas Bancarias

🏦 Aplicación web para convertir extractos bancarios de **BROU** e **Itaú** al formato compatible con **Finanzas Personales de ZetaSoftware**.

## ✨ Características

- ✅ Procesamiento automático de extractos de BROU
- ✅ Procesamiento automático de extractos de Itaú
- ✅ Filtrado opcional por fecha
- ✅ Vista previa de resultados
- ✅ Descarga inmediata en formato Excel
- ✅ Interfaz web intuitiva
- ✅ 100% privado (procesamiento en memoria, sin almacenamiento)

## 🛠️ Tecnologías

- Python 3.13
- Streamlit
- Pandas
- OpenPyXL
- XLRD

## 📋 Formato de salida

El archivo procesado contiene:

- `fecha`: Fecha del movimiento (DD/MM/YYYY)
- `descripcion`: Descripción del movimiento
- `credito`: Monto de crédito
- `debito`: Monto de débito
- `cotizacion`: Cotización (siempre 0)

## 👨‍💻 Desarrollo local

```bash
# Clonar repositorio
git clone https://github.com/TU_USUARIO/procesador-planillas-bancarias.git
cd procesador-planillas-bancarias

# Crear entorno virtual
python -m venv env
source env/bin/activate  # En Windows: env\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar aplicación
streamlit run app.py
```

## 📄 Licencia

Proyecto creado para uso con Finanzas Personales de ZetaSoftware.

---

Desarrollado con ❤️ para facilitar la gestión financiera personal
