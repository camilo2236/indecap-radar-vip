import streamlit as st
import pandas as pd

# 1. Configuración de página
st.set_page_config(page_title="INTELIGENCIA INDECAP 2026", layout="wide", page_icon="📈")

# Estilo personalizado
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: #ffffff; padding: 20px; border-radius: 10px; border: 1px solid #e0e0e0; }
    h1 { color: #1E3A8A; font-family: 'Arial'; }
    </style>
    """, unsafe_allow_html=True)

st.title("🛡️ Inteligencia Estratégica INDECAP 2026")
st.write("Análisis de oportunidades en el Anillo de Oro de Antioquia.")

# 2. Función para cargar datos
@st.cache_data
def load_radar_data(sheet_name):
    try:
        # Cargamos el archivo generado por el pescador
        df = pd.read_excel("INTELIGENCIA_ESTRATEGICA_INDECAP_2026.xlsx", sheet_name=sheet_name)
        # Asegurar que el precio sea numérico
        df['precio_base'] = pd.to_numeric(df['precio_base'], errors='coerce').fillna(0)
        return df
    except Exception as e:
        return pd.DataFrame()

# 3. Sidebar: Selección de Red y Filtros
st.sidebar.image("https://via.placeholder.com/150x50?text=INDECAP", use_container_width=True) # Puedes poner tu logo aquí
st.sidebar.header("Control de Radar")

opcion_red = st.sidebar.radio(
    "Selecciona una categoría:",
    ["🔥 ACTIVOS (Licitar Ya)", "🟡 BORRADORES (Influir)", "♻️ RESCATE (Fallidos)", "📅 PREDICTIVO (Renovaciones)"]
)

# Mapeo de pestañas del Excel
mapping = {
    "🔥 ACTIVOS (Licitar Ya)": "ACTIVOS_LICITAR_YA",
    "🟡 BORRADORES (Influir)": "INFLUIR_BORRADORES",
    "♻️ RESCATE (Fallidos)": "RESCATE_FALLIDOS",
    "📅 PREDICTIVO (Renovaciones)": "PREDICCION_RENOVABLES"
}

# Cargar la data según la opción
df_raw = load_radar_data(mapping[opcion_red])

if not df_raw.empty:
    # --- FILTRO POR MUNICIPIO ---
    municipios_disponibles = sorted(df_raw['ciudad_entidad'].unique().tolist())
    municipios_seleccionados = st.sidebar.multiselect(
        "📍 Filtrar por Municipio:",
        options=municipios_disponibles,
        default=municipios_disponibles
    )

    # Aplicar filtros
    df = df_raw[df_raw['ciudad_entidad'].isin(municipios_seleccionados)]

    # 4. Métricas en Pantalla
    m1, m2, m3 = st.columns(3)
    m1.metric("Oportunidades", len(df))
    m2.metric("Bolsa Total", f"${df['precio_base'].sum():,.0f}")
    m3.metric("Ticket Promedio", f"${df['precio_base'].mean():,.0f}" if len(df)>0 else "$0")

    # 5. Buscador de Texto
    search = st.text_input("🔍 Buscar palabra clave (ej: Salud, Capacitación, EPM):")
    if search:
        df = df[df.apply(lambda row: search.lower() in str(row).lower(), axis=1)]

    # 6. Tabla de Resultados con Links de SECOP
    st.dataframe(
        df,
        column_config={
            "urlproceso": st.column_config.LinkColumn("Link SECOP", display_text="Abrir ↗️"),
            "precio_base": st.column_config.NumberColumn("Presupuesto (COP)", format="$ %,.0f"),
            "nombre_del_procedimiento": st.column_config.TextColumn("Objeto del Contrato", width="large"),
            "entidad": "Institución",
            "ciudad_entidad": "Municipio",
            "fecha_de_publicacion_del": "Publicado el"
        },
        hide_index=True,
        use_container_width=True
    )
    
    # Botón para descargar lo que estás viendo en pantalla
    st.sidebar.download_button(
        label="📥 Descargar Vista Actual (CSV)",
        data=df.to_csv(index=False).encode('utf-8'),
        file_name=f"radar_indecap_{opcion_red}.csv",
        mime='text/csv',
    )
else:
    st.warning(f"No hay datos en la categoría {opcion_red}. ¡Asegúrate de correr el script de búsqueda!")