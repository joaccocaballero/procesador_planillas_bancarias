import streamlit as st
import pandas as pd
import datetime
import io

def procesar_planilla_brou(file_data, fecha_desde=None):
    """
    Procesa la planilla de movimientos del BROU.
    
    Args:
        file_data: Datos del archivo (puede ser .xls o .xlsx)
        fecha_desde: Fecha a partir de la cual filtrar (datetime)
                     Si es None, no se aplica filtro
    
    Returns:
        DataFrame procesado o None si hay error
    """
    try:
        # 1. Leer el archivo
        df_raw = pd.read_excel(file_data, header=None)
        
        # 2. Buscar dinámicamente la fila de cabezales
        try:
            header_row_idx = df_raw[df_raw[0] == 'Fecha'].index[0]
        except IndexError:
            st.error("Error: No se encontró la fila de cabezales (con la palabra 'Fecha' en la columna A).")
            return None

        # 3. Extraer datos desde esa fila en adelante
        df_raw.columns = df_raw.iloc[header_row_idx]
        df_data = df_raw.iloc[header_row_idx + 1:].copy()

        # 4. Inicializar DataFrame de salida
        df_out = pd.DataFrame()

        # --- Procesamiento de FECHA (Columna A) ---
        def format_fecha(val):
            if pd.isna(val): 
                return ""
            if isinstance(val, (pd.Timestamp, datetime.datetime)):
                return val.strftime('%d/%m/%Y')
            if isinstance(val, (float, int)):
                try:
                    base_date = datetime.datetime(1899, 12, 30)
                    delta = datetime.timedelta(days=float(val))
                    return (base_date + delta).strftime('%d/%m/%Y')
                except:
                    return str(val)
            return str(val)

        df_out['fecha'] = df_data['Fecha'].apply(format_fecha)

        # --- Procesamiento de DESCRIPCIÓN (Columna B) ---
        df_out['descripcion'] = df_data['Descripción'].astype(str)

        # --- Procesamiento de CRÉDITO (Columna H) y DÉBITO (Columna G) ---
        df_out['credito'] = pd.to_numeric(df_data['Crédito'], errors='coerce').fillna(0).astype(float)
        df_out['debito'] = pd.to_numeric(df_data['Débito'], errors='coerce').fillna(0).astype(float)

        # --- Procesamiento de COTIZACIÓN ---
        df_out['cotizacion'] = 0.0

        # 5. Filtrar por fecha si se especificó
        if fecha_desde:
            def parse_fecha(fecha_str):
                try:
                    return datetime.datetime.strptime(fecha_str, '%d/%m/%Y')
                except:
                    return None
            
            df_out['fecha_dt'] = df_out['fecha'].apply(parse_fecha)
            df_out = df_out[df_out['fecha_dt'] >= fecha_desde].copy()
            df_out = df_out.drop('fecha_dt', axis=1)

        # 6. Ordenar columnas
        columnas_ordenadas = ['fecha', 'descripcion', 'credito', 'debito', 'cotizacion']
        df_final = df_out[columnas_ordenadas]

        return df_final

    except Exception as e:
        st.error(f"Ocurrió un error: {e}")
        return None


def procesar_planilla_itau(file_data, fecha_desde=None):
    """
    Procesa la planilla de movimientos del Banco Itaú.
    
    Args:
        file_data: Datos del archivo (puede ser .xls, .xlsx o .csv)
        fecha_desde: Fecha a partir de la cual filtrar (datetime)
                     Si es None, no se aplica filtro
    
    Returns:
        DataFrame procesado o None si hay error
    """
    try:
        # 1. Leer el archivo
        df_raw = pd.read_excel(file_data, header=None)
        
        # 2. Buscar dinámicamente la fila de cabezales
        # En Itaú, buscamos la fila que contiene "Fecha" en la columna 1 (índice 1)
        header_row_idx = None
        for idx, row in df_raw.iterrows():
            if pd.notna(row[1]) and str(row[1]).strip().lower() == 'fecha':
                header_row_idx = idx
                break
        
        if header_row_idx is None:
            st.error("Error: No se encontró la fila de cabezales en el formato Itaú.")
            return None

        # 3. Extraer nombres de columnas (están en la columna 1, 2, 4, 5, etc.)
        # Estructura: columna 1=Fecha, 2=Concepto, 4=Débito, 5=Crédito
        header_row = df_raw.iloc[header_row_idx]
        
        # 4. Extraer datos desde la fila siguiente, excluyendo "SALDO ANTERIOR" y "SALDO FINAL"
        df_data = df_raw.iloc[header_row_idx + 1:].copy()
        
        # Inicializar DataFrame de salida
        df_out = pd.DataFrame()

        # --- Procesamiento de FECHA (Columna 1) ---
        def format_fecha(val):
            if pd.isna(val): 
                return ""
            if isinstance(val, (pd.Timestamp, datetime.datetime)):
                return val.strftime('%d/%m/%Y')
            if isinstance(val, (float, int)):
                try:
                    base_date = datetime.datetime(1899, 12, 30)
                    delta = datetime.timedelta(days=float(val))
                    return (base_date + delta).strftime('%d/%m/%Y')
                except:
                    return str(val)
            # Intentar parsear formato DD/MM/YYYY
            if isinstance(val, str):
                val = val.strip()
                for fmt in ['%d/%m/%Y', '%Y-%m-%d', '%d-%m-%Y']:
                    try:
                        dt = datetime.datetime.strptime(val, fmt)
                        return dt.strftime('%d/%m/%Y')
                    except:
                        continue
            return str(val)

        df_out['fecha'] = df_data[1].apply(format_fecha)

        # --- Procesamiento de DESCRIPCIÓN (Columna 2 = Concepto) ---
        df_out['descripcion'] = df_data[2].fillna('').astype(str)

        # --- Procesamiento de DÉBITO (Columna 4) y CRÉDITO (Columna 5) ---
        df_out['debito'] = pd.to_numeric(df_data[4], errors='coerce').fillna(0).astype(float)
        df_out['credito'] = pd.to_numeric(df_data[5], errors='coerce').fillna(0).astype(float)

        # --- Procesamiento de COTIZACIÓN ---
        df_out['cotizacion'] = 0.0

        # 5. Filtrar filas que no son movimientos (SALDO ANTERIOR, SALDO FINAL, filas vacías)
        # Eliminamos filas donde la descripción contiene "SALDO" o está vacía y no hay crédito ni débito
        df_out = df_out[
            ~(df_out['descripcion'].str.upper().str.contains('SALDO ANTERIOR|SALDO FINAL', na=False)) &
            ~((df_out['descripcion'] == '') & (df_out['credito'] == 0) & (df_out['debito'] == 0)) &
            (df_out['fecha'] != '')
        ].copy()

        # 6. Filtrar por fecha si se especificó
        if fecha_desde:
            def parse_fecha(fecha_str):
                try:
                    return datetime.datetime.strptime(fecha_str, '%d/%m/%Y')
                except:
                    return None
            
            df_out['fecha_dt'] = df_out['fecha'].apply(parse_fecha)
            df_out = df_out[df_out['fecha_dt'] >= fecha_desde].copy()
            df_out = df_out.drop('fecha_dt', axis=1)

        # 7. Ordenar columnas
        columnas_ordenadas = ['fecha', 'descripcion', 'credito', 'debito', 'cotizacion']
        df_final = df_out[columnas_ordenadas]

        return df_final

    except Exception as e:
        st.error(f"Ocurrió un error procesando Itaú: {e}")
        import traceback
        st.error(traceback.format_exc())
        return None


# ==================== INTERFAZ STREAMLIT ====================

st.set_page_config(
    page_title="Procesador de Planillas Bancarias - Finanzas Personales",
    page_icon="🏦",
    layout="centered"
)

st.title("🏦 Procesador de Planillas Bancarias")
st.markdown("##### Para importación en **Finanzas Personales** de ZetaSoftware")
st.markdown("---")

# Información del propósito
st.info("💡 **Propósito**: Convierte planillas de movimientos extraídas de BROU e Itaú al formato compatible con el software Finanzas Personales de ZetaSoftware.")

# Aviso de privacidad
st.success("🔒 **Privacidad garantizada**: Todos los archivos se procesan únicamente en memoria. No se guarda ningún dato en el servidor ni localmente. Tu información permanece 100% privada.")

# Selector de banco
col_banco1, col_banco2 = st.columns([1, 3])

with col_banco1:
    st.markdown("### Banco:")

with col_banco2:
    banco_seleccionado = st.selectbox(
        "Selecciona tu banco",
        ["BROU", "Itaú"],
        label_visibility="collapsed",
        help="Elige el banco del cual proviene tu archivo de movimientos"
    )

# Instrucciones dinámicas según el banco
with st.expander("ℹ️ Instrucciones de uso"):
    if banco_seleccionado == "BROU":
        st.markdown("""
        **BROU - Banco República**
        1. Descarga tu extracto de movimientos desde el sitio web del BROU (.xls o .xlsx)
        2. Sube el archivo aquí
        3. Opcionalmente, selecciona una fecha de inicio para filtrar los movimientos
        4. Haz clic en 'Procesar'
        5. Descarga el archivo procesado
        6. Importa el archivo en **Finanzas Personales de ZetaSoftware**
        """)
    else:
        st.markdown("""
        **Banco Itaú**
        1. Descarga tu extracto detallado desde el sitio web de Itaú (.xls, .xlsx o .csv)
        2. Sube el archivo aquí
        3. Opcionalmente, selecciona una fecha de inicio para filtrar los movimientos
        4. Haz clic en 'Procesar'
        5. Descarga el archivo procesado
        6. Importa el archivo en **Finanzas Personales de ZetaSoftware**
        
        *Nota: El procesador detecta automáticamente las columnas de fecha, descripción, crédito y débito*
        """)

st.markdown("---")

# Upload del archivo
tipos_archivo = ['xls', 'xlsx', 'csv'] if banco_seleccionado == "Itaú" else ['xls', 'xlsx']
uploaded_file = st.file_uploader(
    f"Selecciona el archivo de movimientos de {banco_seleccionado}", 
    type=tipos_archivo,
    help=f"Sube tu planilla de movimientos de {banco_seleccionado}"
)

# Filtro de fecha
col1, col2 = st.columns([1, 1])

with col1:
    usar_filtro = st.checkbox("Filtrar por fecha", value=False)

with col2:
    fecha_filtro = None
    if usar_filtro:
        fecha_filtro = st.date_input(
            "Desde la fecha:",
            value=datetime.date.today() - datetime.timedelta(days=30),
            help="Solo se incluirán movimientos desde esta fecha en adelante"
        )

st.markdown("---")

# Botón de procesamiento
if uploaded_file is not None:
    if st.button("🚀 Procesar Planilla", type="primary", use_container_width=True):
        with st.spinner("Procesando archivo..."):
            # Convertir fecha si está seleccionada
            fecha_desde = None
            if usar_filtro and fecha_filtro:
                fecha_desde = datetime.datetime.combine(fecha_filtro, datetime.time.min)
            
            # Procesar según el banco seleccionado
            if banco_seleccionado == "BROU":
                df_resultado = procesar_planilla_brou(uploaded_file, fecha_desde)
            else:  # Itaú
                df_resultado = procesar_planilla_itau(uploaded_file, fecha_desde)
            
            if df_resultado is not None and len(df_resultado) > 0:
                st.success(f"✅ ¡Procesamiento exitoso! {len(df_resultado)} registros procesados")
                
                # Vista previa
                st.subheader("Vista previa del resultado")
                st.dataframe(df_resultado.head(10), use_container_width=True)
                
                if len(df_resultado) > 10:
                    st.info(f"Mostrando 10 de {len(df_resultado)} registros")
                
                # Convertir a Excel en memoria
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df_resultado.to_excel(writer, index=False, sheet_name='Movimientos')
                excel_data = output.getvalue()
                
                # Botón de descarga
                st.download_button(
                    label="⬇️ Descargar archivo procesado",
                    data=excel_data,
                    file_name=f"Movimientos_{banco_seleccionado}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    type="primary",
                    use_container_width=True
                )
            elif df_resultado is not None:
                st.warning("⚠️ No se encontraron registros que cumplan con los criterios de filtrado")

# Footer
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        <strong>Procesador de Planillas Bancarias</strong><br>
        BROU & Itaú → Finanzas Personales de ZetaSoftware<br>
        <small>Convierte extractos bancarios al formato compatible</small>
    </div>
    """,
    unsafe_allow_html=True
)
