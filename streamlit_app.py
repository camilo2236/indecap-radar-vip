import streamlit as st
import pandas as pd
from datetime import date
import ast

# Configuración visual de la página
st.set_page_config(page_title="Inteligencia INDECAP", page_icon="🎯", layout="wide")

# --- FUNCIONES DE LIMPIEZA ---
def limpiar_url(valor):
    if pd.isna(valor): return ""
    if isinstance(valor, dict): return valor.get('url', '')
    if isinstance(valor, str) and '{' in valor:
        try: return ast.literal_eval(valor).get('url', '')
        except: return valor
    return valor

# --- ALERTA ESTRATÉGICA: LEY DE GARANTÍAS 2026 ---
fecha_limite = date(2025, 11, 25) 
dias_restantes = (fecha_limite - date.today()).days

with st.sidebar:
    st.title("🛡️ Centro de Comando")
    st.markdown("---")
    if dias_restantes > 0:
        st.error(f"## ⏳ {dias_restantes} DÍAS")
        st.warning("Para el inicio de la **Ley de Garantías**. ¡Urge radicar propuestas!")
    else:
        st.error("🚫 LEY DE GARANTÍAS ACTIVA. Solo licitaciones públicas permitidas.")

# --- CUERPO PRINCIPAL ---
st.title("🎯 Radar de Oportunidades INDECAP 2026")
st.markdown("Monitoreo en vivo. **Haz clic en el encabezado de cualquier columna para ordenar (Ej: Presupuesto o Fecha).**")

try:
    # 1. Cargar datos (Ruta relativa, lista para la nube o tu PC)
    df_vivo = pd.read_excel('RADAR_VIVO_INDECAP_2026.xlsx')
    
    # 2. Limpieza de URL y Fecha para que Streamlit pueda ordenarlas matemáticamente
    if 'urlproceso' in df_vivo.columns:
        df_vivo['urlproceso'] = df_vivo['urlproceso'].apply(limpiar_url)
    
    if 'fecha_de_publicacion_del' in df_vivo.columns:
        df_vivo['fecha_de_publicacion_del'] = pd.to_datetime(df_vivo['fecha_de_publicacion_del']).dt.date
    
    # Métricas rápidas
    col1, col2, col3 = st.columns(3)
    col1.metric("Procesos Vivos", len(df_vivo))
    col2.metric("Presupuesto en Juego", f"${df_vivo['precio_base'].sum():,.0f}".replace(",", "."))
    col3.metric("Municipios Activos", df_vivo['ciudad_entidad'].nunique())
    
    st.markdown("---")
    
    # 3. Seleccionar y renombrar las columnas que realmente importan para la vista
    df_mostrar = df_vivo[['entidad', 'ciudad_entidad', 'nombre_del_procedimiento', 'precio_base', 'fecha_de_publicacion_del', 'urlproceso']]
    
    # 4. Mostrar la tabla interactiva y ordenable
    st.dataframe(
        df_mostrar,
        column_config={
            "entidad": st.column_config.TextColumn("Entidad", width="medium"),
            "ciudad_entidad": st.column_config.TextColumn("Ciudad"),
            "nombre_del_procedimiento": st.column_config.TextColumn("Objeto del Contrato", width="large"),
            "precio_base": st.column_config.NumberColumn(
                "Presupuesto", 
                help="Haz clic para ordenar de mayor a menor",
                format="$ %d" # Formato de dinero nativo
            ),
            "fecha_de_publicacion_del": st.column_config.DateColumn(
                "Fecha de Publicación", 
                help="Haz clic para ver los más recientes",
                format="YYYY-MM-DD"
            ),
            "urlproceso": st.column_config.LinkColumn(
                "Enlace SECOP", 
                display_text="🔗 Abrir Proceso" # Oculta la URL fea y pone este texto limpio
            )
        },
        hide_index=True,
        use_container_width=True,
        height=600 # Altura cómoda para leer varios registros
    )

except FileNotFoundError:
    st.info("👋 Ejecuta primero el buscador `busqueda_secop_premium.py` para alimentar el radar.")