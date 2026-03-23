import streamlit as st
import pandas as pd

st.set_page_config(page_title="RADAR INDECAP 2026", layout="wide", page_icon="🚀")

# Estilo para mejorar la lectura
st.markdown("""
    <style>
    .stMetric { background-color: #f0f2f6; padding: 15px; border-radius: 10px; }
    h1 { color: #1E3A8A; }
    </style>
    """, unsafe_allow_html=True)

st.title("🚀 Radar de Inteligencia Estratégica 2026")

@st.cache_data
def load_data(sheet_name):
    try:
        df = pd.read_excel("INTELIGENCIA_ESTRATEGICA_INDECAP_2026.xlsx", sheet_name=sheet_name)
        df['precio_base'] = pd.to_numeric(df['precio_base'], errors='coerce').fillna(0)
        return df
    except:
        return pd.DataFrame()

menu = st.sidebar.radio(
    "Selecciona una Red de Oportunidades:",
    ["🔥 ACTIVOS (Licitar Ya)", "🟡 BORRADORES (Influir)", "♻️ RESCATE (Fallidos)", "📅 PREDICTIVO (Renovaciones)"]
)

mapping = {
    "🔥 ACTIVOS (Licitar Ya)": "ACTIVOS_LICITAR_YA",
    "🟡 BORRADORES (Influir)": "INFLUIR_BORRADORES",
    "♻️ RESCATE (Fallidos)": "RESCATE_FALLIDOS",
    "📅 PREDICTIVO (Renovaciones)": "PREDICCION_RENOVABLES"
}

df = load_data(mapping[menu])

if not df.empty:
    col1, col2 = st.columns([1, 1])
    col1.metric("Contratos Encontrados", len(df))
    col2.metric("Bolsa Total Disponible", f"${df['precio_base'].sum():,.0f}")

    search = st.text_input("🔍 Buscar por entidad o palabra clave:")
    if search:
        df = df[df.apply(lambda row: search.lower() in str(row).lower(), axis=1)]

    # TABLA CON LINKS CLICKEABLES
    st.dataframe(
        df,
        column_config={
            "urlproceso": st.column_config.LinkColumn("Enlace SECOP", display_text="Abrir ↗️"),
            "precio_base": st.column_config.NumberColumn("Presupuesto", format="$ %,.0f"),
            "nombre_del_procedimiento": st.column_config.TextColumn("Objeto", width="large")
        },
        hide_index=True,
        use_container_width=True
    )
else:
    st.info("Sin datos en esta categoría. Ejecuta el Pescador para actualizar.")