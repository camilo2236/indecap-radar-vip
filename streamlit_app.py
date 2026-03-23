import streamlit as st
import pandas as pd

# Configuración de la página
st.set_page_config(page_title="INDECAP Intelligence Hub", layout="wide", page_icon="🎯")

# Estilo personalizado (Touch de diseño)
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

st.title("🎯 INDECAP: Centro de Inteligencia de Licitaciones")
st.sidebar.header("Filtros Estratégicos")

# --- CARGA DE DATOS ---
@st.cache_data
def load_data():
    # Intenta leer el archivo local
    file_path = "INTELIGENCIA_TOTAL_INDECAP.xlsx"
    try:
        return pd.read_excel(file_path, sheet_name="HISTORIAL_COMPLETO")
    except:
        return None

df = load_data()

if df is not None:
    # Métricas Globales
    c1, c2, c3 = st.columns(3)
    total_bolsa = df['Presupuesto'].sum()
    c1.metric("Bolsa Total Detectada", f"${total_bolsa:,.0f}")
    c2.metric("Oportunidades Abiertas", len(df[df['Accion_Sugerida'].str.contains('LICITAR')]))
    c3.metric("Para Re-licitar", len(df[df['Accion_Sugerida'].str.contains('RE-LICITACIÓN')]))

    # Pestañas de Navegación
    tab1, tab2, tab3 = st.tabs(["🔥 ATAQUE INMEDIATO", "💎 CORE (140M - 800M)", "📞 SEGUNDA OPORTUNIDAD"])

    with tab1:
        st.subheader("Licitaciones listas para enviar propuesta")
        abiertas = df[df['Accion_Sugerida'].str.contains('LICITAR')].sort_values('Presupuesto', ascending=False)
        st.dataframe(abiertas, use_container_width=True)

    with tab2:
        st.subheader("Contratos en el rango ideal de INDECAP")
        # Filtro corregido a 140M para atrapar las gemas de 149M
        core = df[(df['Presupuesto'] >= 140000000) & (df['Presupuesto'] <= 800000000)]
        st.dataframe(core.sort_values('Match_Score', ascending=False), use_container_width=True)

    with tab3:
        st.subheader("Procesos Desiertos o Cancelados (Llamar ya)")
        relicitar = df[df['Accion_Sugerida'].str.contains('RE-LICITACIÓN')]
        st.write("Estas entidades ya fallaron en su contratación. Es el momento de ofrecer servicios directos.")
        st.table(relicitar[['Entidad', 'Municipio', 'Presupuesto', 'Link']].head(10))

else:
    st.error("No se encontró el archivo de datos. Asegúrate de subir 'INTELIGENCIA_TOTAL_INDECAP.xlsx' a GitHub.")