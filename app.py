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
        # Validar y formatear fecha, retornando None si no es válida
        def format_fecha(val):
            if pd.isna(val): 
                return None
            if isinstance(val, (pd.Timestamp, datetime.datetime)):
                return val.strftime('%d/%m/%Y')
            if isinstance(val, (float, int)):
                try:
                    base_date = datetime.datetime(1899, 12, 30)
                    delta = datetime.timedelta(days=float(val))
                    return (base_date + delta).strftime('%d/%m/%Y')
                except:
                    return None
            # Si es string, intentar parsear
            if isinstance(val, str):
                val_stripped = val.strip()
                for fmt in ['%d/%m/%Y', '%Y-%m-%d', '%d-%m-%Y']:
                    try:
                        dt = datetime.datetime.strptime(val_stripped, fmt)
                        return dt.strftime('%d/%m/%Y')
                    except:
                        continue
            return None

        df_out['fecha'] = df_data['Fecha'].apply(format_fecha)

        # --- Procesamiento de DESCRIPCIÓN (Columna B) ---
        df_out['descripcion'] = df_data['Descripción'].astype(str)

        # --- Procesamiento de CRÉDITO (Columna H) y DÉBITO (Columna G) ---
        df_out['credito'] = pd.to_numeric(df_data['Crédito'], errors='coerce').fillna(0).astype(float)
        df_out['debito'] = pd.to_numeric(df_data['Débito'], errors='coerce').fillna(0).astype(float)

        # --- Procesamiento de COTIZACIÓN ---
        df_out['cotizacion'] = 0.0

        # 5. Eliminar filas sin fecha válida (skipea filas que no tienen fecha)
        df_out = df_out[df_out['fecha'].notna()].copy()

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
        # Validar y formatear fecha, retornando None si no es válida
        def format_fecha(val):
            if pd.isna(val): 
                return None
            if isinstance(val, (pd.Timestamp, datetime.datetime)):
                return val.strftime('%d/%m/%Y')
            if isinstance(val, (float, int)):
                try:
                    base_date = datetime.datetime(1899, 12, 30)
                    delta = datetime.timedelta(days=float(val))
                    return (base_date + delta).strftime('%d/%m/%Y')
                except:
                    return None
            # Intentar parsear formato DD/MM/YYYY
            if isinstance(val, str):
                val = val.strip()
                for fmt in ['%d/%m/%Y', '%Y-%m-%d', '%d-%m-%Y']:
                    try:
                        dt = datetime.datetime.strptime(val, fmt)
                        return dt.strftime('%d/%m/%Y')
                    except:
                        continue
            return None

        df_out['fecha'] = df_data[1].apply(format_fecha)

        # --- Procesamiento de DESCRIPCIÓN (Columna 2 = Concepto) ---
        df_out['descripcion'] = df_data[2].fillna('').astype(str)

        # --- Procesamiento de DÉBITO (Columna 4) y CRÉDITO (Columna 5) ---
        df_out['debito'] = pd.to_numeric(df_data[4], errors='coerce').fillna(0).astype(float)
        df_out['credito'] = pd.to_numeric(df_data[5], errors='coerce').fillna(0).astype(float)

        # --- Procesamiento de COTIZACIÓN ---
        df_out['cotizacion'] = 0.0

        # 5. Filtrar filas que no son movimientos (SALDO ANTERIOR, SALDO FINAL, filas vacías)
        # Eliminamos filas sin fecha válida, con "SALDO" o vacías sin movimientos
        df_out = df_out[
            (df_out['fecha'].notna()) &  # Debe tener fecha válida
            ~(df_out['descripcion'].str.upper().str.contains('SALDO ANTERIOR|SALDO FINAL', na=False)) &
            ~((df_out['descripcion'] == '') & (df_out['credito'] == 0) & (df_out['debito'] == 0))
        ].copy()

        # 6. Filtrar por fecha si se especificó
        if fecha_desde:
            def parse_fecha(fecha_str):
                try:
                    return datetime.datetime.strptime(fecha_str, '%d/%m/%Y')
                except:
                    return None
            
            df_out['fecha_dt'] = df_out['fecha'].apply(parse_fecha)
            # Excluir filas con fecha anterior a fecha_desde (solo mantener >= fecha_desde)
            df_out = df_out[df_out['fecha_dt'].notna() & (df_out['fecha_dt'] >= fecha_desde)].copy()
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
    layout="wide",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': None
    }
)

st.title("🏦 Procesador de Planillas Bancarias")
st.markdown("##### Para importación en **Finanzas Personales** de ZetaSoftware")
st.markdown("---")

# Información del propósito
st.info("💡 **Propósito**: Convierte planillas de movimientos extraídas de BROU e Itaú al formato compatible con el software Finanzas Personales de ZetaSoftware.")

st.markdown("---")

# Layout horizontal: Formulario a la izquierda, Resultados a la derecha
col_form, col_result = st.columns([1, 1.5])

with col_form:
    st.markdown("### 📝 Configuración")
    
    # Selector de banco
    banco_seleccionado = st.selectbox(
        "Banco",
        ["BROU", "Itaú"],
        help="Elige el banco del cual proviene tu archivo de movimientos"
    )
    
    # Upload del archivo
    tipos_archivo = ['xls', 'xlsx', 'csv'] if banco_seleccionado == "Itaú" else ['xls', 'xlsx']
    uploaded_file = st.file_uploader(
        f"Archivo de {banco_seleccionado}", 
        type=tipos_archivo,
        help=f"Sube tu planilla de movimientos de {banco_seleccionado}"
    )
    
    # Filtro de fecha
    usar_filtro = st.checkbox("Filtrar por fecha", value=False)
    
    fecha_filtro = None
    if usar_filtro:
        fecha_filtro = st.date_input(
            "Desde la fecha:",
            value=datetime.date.today(),
            help="Solo se incluirán movimientos desde esta fecha en adelante",
            format="DD/MM/YYYY"
        )
    
    st.markdown("")
    
    # Botón de procesamiento
    procesar_clicked = False
    if uploaded_file is not None:
        procesar_clicked = st.button("🚀 Procesar Planilla", type="primary", use_container_width=True)

with col_result:
    if uploaded_file is not None and procesar_clicked:
        st.markdown("### 📊 Resultado")
        
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
                st.success(f"✅ {len(df_resultado)} registros procesados")
                
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
                
                # Vista previa
                st.markdown("**Vista previa:**")
                st.dataframe(df_resultado.head(10), use_container_width=True, height=350)
                if len(df_resultado) > 10:
                    st.caption(f"Mostrando 10 de {len(df_resultado)} registros")
            elif df_resultado is not None:
                st.warning("⚠️ No se encontraron registros que cumplan con los criterios de filtrado")
