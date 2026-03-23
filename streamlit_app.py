import streamlit as st
import pandas as pd

# Configuración PRO de la página
st.set_page_config(page_title="Radar VIP INDECAP", layout="wide", page_icon="🎯")

# Inyección de CSS para mejorar la legibilidad
st.markdown("""
    <style>
    .stDataFrame { border: 1px solid #e6e9ef; border-radius: 10px; }
    [data-testid="stMetricValue"] { font-size: 28px; color: #1E3A8A; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎯 INDECAP: Inteligencia de Licitaciones")

# --- CARGA DE DATOS ---
@st.cache_data
def load_data():
    try:
        df = pd.read_excel("INTELIGENCIA_TOTAL_INDECAP.xlsx", sheet_name="HISTORIAL_COMPLETO")
        # Aseguramos que el presupuesto sea numérico
        df['Presupuesto'] = pd.to_numeric(df['Presupuesto'], errors='coerce').fillna(0)
        return df
    except:
        return None

df_raw = load_data()

if df_raw is not None:
    # --- BARRA LATERAL (FILTROS FUNCIONALES) ---
    st.sidebar.header("🛠️ Panel de Control")
    
    # Filtro de Búsqueda de Texto
    search_query = st.sidebar.text_input("🔍 Buscar en Objeto (ej: Salud)", "")
    
    # Filtro de Municipio
    municipios = ["Todos"] + sorted(df_raw['Municipio'].unique().tolist())
    muni_sel = st.sidebar.selectbox("📍 Municipio", municipios)
    
    # Filtro de Acción Sugerida
    acciones = ["Todas"] + sorted(df_raw['Accion_Sugerida'].unique().tolist())
    accion_sel = st.sidebar.selectbox("⚡ Estado de Acción", acciones)
    
    # Filtro de Rango de Precio
    min_p = float(df_raw['Presupuesto'].min())
    max_p = float(df_raw['Presupuesto'].max())
    rango_precio = st.sidebar.slider("💰 Rango de Presupuesto (COP)", min_p, max_p, (min_p, max_p))

    # APLICAR FILTROS
    df = df_raw.copy()
    if search_query:
        df = df[df['Objeto'].str.contains(search_query, case=False, na=False)]
    if muni_sel != "Todos":
        df = df[df['Municipio'] == muni_sel]
    if accion_sel != "Todas":
        df = df[df['Accion_Sugerida'] == accion_sel]
    df = df[(df['Presupuesto'] >= rango_precio[0]) & (df['Presupuesto'] <= rango_precio[1])]

    # --- MÉTRICAS ---
    m1, m2, m3 = st.columns(3)
    m1.metric("Resultados Filtrados", len(df))
    m2.metric("Bolsa en Vista", f"${df['Presupuesto'].sum():,.0f}")
    m3.metric("Match Promedio", f"{df['Match_Score'].mean():.1f}/10")

    # --- TABLA ESTRUCTURADA ---
    # Usamos column_config para que los valores se vean como moneda y los links funcionen
    st.dataframe(
        df,
        column_config={
            "Presupuesto": st.column_config.NumberColumn(
                "Presupuesto (COP)",
                format="$ %,.0f",
            ),
            "Link": st.column_config.LinkColumn("Enlace SECOP"),
            "Match_Score": st.column_config.ProgressColumn(
                "Match",
                help="Calificación de relevancia para INDECAP",
                format="%f",
                min_value=0,
                max_value=10,
            ),
            "Objeto": st.column_config.TextColumn("Descripción del Contrato", width="large"),
        },
        hide_index=True,
        use_container_width=True
    )

    # Botón para descargar lo que filtraste
    st.sidebar.download_button(
        label="📥 Descargar Vista Actual (Excel)",
        data=df.to_csv(index=False).encode('utf-8'),
        file_name='filtro_indecap.csv',
        mime='text/csv',
    )

else:
    st.error("No se detectó el archivo 'INTELIGENCIA_TOTAL_INDECAP.xlsx'. Ejecuta tu script de Python local primero.")