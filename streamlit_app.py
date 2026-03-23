import streamlit as st
import pandas as pd

# 1. Configuración de la interfaz
st.set_page_config(page_title="RADAR ESTRATÉGICO 2026", layout="wide", page_icon="🚀")

st.markdown("""
    <style>
    .stDataFrame { border: 1px solid #1E3A8A; border-radius: 10px; }
    h1 { color: #1E3A8A; }
    </style>
    """, unsafe_allow_html=True)

st.title("🚀 Radar de Inteligencia Estratégica 2026")

# 2. Función de carga para las 4 redes
@st.cache_data
def load_radar_data(sheet_name):
    file_path = "INTELIGENCIA_ESTRATEGICA_INDECAP_2026.xlsx"
    try:
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        # Limpieza de moneda
        df['precio_base'] = pd.to_numeric(df['precio_base'], errors='coerce').fillna(0)
        return df
    except:
        return pd.DataFrame()

# 3. Menú de Navegación por Redes
menu = st.sidebar.radio(
    "Selecciona una Red de Pesca:",
    ["🔥 ACTIVOS (Licitar Ya)", "🟡 BORRADORES (Influir)", "♻️ RESCATE (Fallidos)", "📅 PREDICTIVO (Renovaciones)"]
)

# Mapeo de pestañas
sheet_map = {
    "🔥 ACTIVOS (Licitar Ya)": "ACTIVOS_LICITAR_YA",
    "🟡 BORRADORES (Influir)": "INFLUIR_BORRADORES",
    "♻️ RESCATE (Fallidos)": "RESCATE_FALLIDOS",
    "📅 PREDICTIVO (Renovaciones)": "PREDICCION_RENOVABLES"
}

df = load_radar_data(sheet_map[menu])

if not df.empty:
    # Métricas rápidas
    c1, c2, c3 = st.columns(3)
    c1.metric("Oportunidades en esta Red", len(df))
    c2.metric("Bolsa Total", f"${df['precio_base'].sum():,.0f}")
    c3.metric("Promedio x Contrato", f"${df['precio_base'].mean():,.0f}")

    # Buscador de texto
    search = st.text_input("🔍 Filtrar por entidad o palabra clave (ej: Salud, Educación):")
    if search:
        df = df[df.apply(lambda row: search.lower() in str(row).lower(), axis=1)]

    # Visualización Pro
    st.dataframe(
        df,
        column_config={
            "precio_base": st.column_config.NumberColumn("Presupuesto (COP)", format="$ %,.0f"),
            "urlproceso": st.column_config.LinkColumn("Enlace SECOP", display_text="Abrir ↗️"),
            "fecha_de_publicacion_del": "Fecha Publicación",
            "nombre_del_procedimiento": st.column_config.TextColumn("Objeto del Contrato", width="large")
        },
        hide_index=True,
        use_container_width=True
    )
else:
    st.info(f"La red '{menu}' está vacía por ahora. ¡Sigue pescando!")