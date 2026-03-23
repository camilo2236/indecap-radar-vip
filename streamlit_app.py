import streamlit as st
import pandas as pd
import ast

# 1. Configuración de la Página
st.set_page_config(page_title="INDECAP Radar VIP", layout="wide", page_icon="🎯")

# 2. Función para limpiar el link del SECOP
def limpiar_url(link_str):
    try:
        # Si viene como "{'url': 'http...'}" lo convertimos a texto limpio
        if isinstance(link_str, str) and '{' in link_str:
            dict_link = ast.literal_eval(link_str)
            return dict_link.get('url', '')
        return link_str
    except:
        return link_str

# 3. Carga de Datos
@st.cache_data
def load_data():
    try:
        df = pd.read_excel("INTELIGENCIA_TOTAL_INDECAP.xlsx", sheet_name="HISTORIAL_COMPLETO")
        # Limpieza inmediata de datos
        df['Link'] = df['Link'].apply(limpiar_url)
        df['Presupuesto'] = pd.to_numeric(df['Presupuesto'], errors='coerce').fillna(0)
        return df
    except Exception as e:
        st.error(f"Error al cargar el Excel: {e}")
        return None

df_raw = load_data()

if df_raw is not None:
    st.title("🎯 Radar de Licitaciones INDECAP")
    st.markdown("---")

    # --- BARRA LATERAL (FILTROS) ---
    st.sidebar.header("🔍 Filtros Estratégicos")
    
    # Buscador por palabras (Salud, Educación, etc)
    search = st.sidebar.text_input("Buscar en el objeto:", "")
    
    # Filtro de Municipios
    lista_muni = ["Todos"] + sorted(df_raw['Municipio'].unique().tolist())
    muni_sel = st.sidebar.selectbox("Municipio:", lista_muni)
    
    # Filtro de Acciones
    lista_accion = ["Todas"] + sorted(df_raw['Accion_Sugerida'].unique().tolist())
    accion_sel = st.sidebar.selectbox("Acción Sugerida:", lista_accion)

    # APLICAR FILTROS
    df = df_raw.copy()
    if search:
        df = df[df['Objeto'].str.contains(search, case=False, na=False)]
    if muni_sel != "Todos":
        df = df[df['Municipio'] == muni_sel]
    if accion_sel != "Todas":
        df = df[df['Accion_Sugerida'] == accion_sel]

    # --- MÉTRICAS ---
    c1, c2, c3 = st.columns(3)
    c1.metric("Oportunidades", len(df))
    c2.metric("Bolsa Filtrada", f"${df['Presupuesto'].sum():,.0f}")
    c3.metric("Match Promedio", f"{df['Match_Score'].mean():.1f}/10")

    # --- TABLA PRO ---
    st.subheader("Listado de Oportunidades")
    
    st.dataframe(
        df,
        column_config={
            "Accion_Sugerida": st.column_config.TextColumn("Estado", width="medium"),
            "Match_Score": st.column_config.ProgressColumn("Match", min_value=0, max_value=10, format="%d"),
            "Entidad": st.column_config.TextColumn("Entidad Pública", width="medium"),
            "Presupuesto": st.column_config.NumberColumn("Presupuesto (COP)", format="$ %,.0f"),
            "Link": st.column_config.LinkColumn("Enlace SECOP", display_text="Abrir Contrato ↗️"),
            "Objeto": st.column_config.TextColumn("Detalle del Contrato", width="large")
        },
        hide_index=True,
        use_container_width=True
    )

    # Botón de descarga
    csv = df.to_csv(index=False).encode('utf-8')
    st.sidebar.download_button("📥 Descargar Reporte CSV", csv, "reporte_indecap.csv", "text/csv")

else:
    st.warning("⚠️ Sube el archivo 'INTELIGENCIA_TOTAL_INDECAP.xlsx' a tu repositorio para activar el radar.")