import streamlit as st
import pandas as pd

# Configuración Estética
st.set_page_config(page_title="Radar INDECAP VIP", layout="wide")

st.markdown("""
    <style>
    .reportview-container { background: #f0f2f6; }
    .card {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        border-left: 10px solid #1f77b4;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    .price { color: #2ecc71; font-size: 24px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# Cargar Datos
df = pd.read_excel(r'C:\BUSQUEDA_SECOP\INTELIGENCIA_INDECAP_20260319.xlsx', sheet_name='ATACAR_YA')

st.title("🎯 Radar de Oportunidades Estratégicas")

# Filtro Rápido
sector = st.selectbox("Selecciona Sector Crítico", df['Categoria'].unique())
top_n = st.slider("Ver Top N Contratos", 5, 50, 10)

df_view = df[df['Categoria'] == sector].head(top_n)

# Visualización en Tarjetas (Innovación)
for i, row in df_view.iterrows():
    with st.container():
        st.markdown(f"""
            <div class="card">
                <h3>{row['Entidad']}</h3>
                <p><b>📍 Ubicación:</b> {row['Municipio']} | <b>⭐ Match:</b> {row['Match_Score']}/10</p>
                <p class="price">${row['Presupuesto']:,.0f} COP</p>
                <p><b>📝 Objeto:</b> {row['Objeto'][:300]}...</p>
                <a href="{row['Link']}" target="_blank">🔗 Abrir en SECOP II</a>
            </div>
        """, unsafe_allow_html=True)