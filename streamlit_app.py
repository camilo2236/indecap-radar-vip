import streamlit as st
import pandas as pd
from datetime import date
import ast

# Configuración visual de la página
st.set_page_config(page_title="Inteligencia INDECAP", page_icon="🎯", layout="wide")

# --- FUNCIONES DE LIMPIEZA ---
def limpiar_url(valor):
    if pd.isna(valor): return "https://www.colombiacompra.gov.co/secop-ii"
    if isinstance(valor, dict): return valor.get('url', 'https://www.colombiacompra.gov.co/secop-ii')
    if isinstance(valor, str) and '{' in valor:
        try: return ast.literal_eval(valor).get('url', 'https://www.colombiacompra.gov.co/secop-ii')
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
st.markdown("Monitoreo en vivo. **Haz clic en el encabezado de cualquier columna para ordenar.**")

try:
    # 1. Cargar datos
    df_vivo = pd.read_excel('RADAR_VIVO_INDECAP_2026.xlsx')
    
    # 2. LIMPIEZA DE DATOS
    if 'urlproceso' in df_vivo.columns:
        df_vivo['urlproceso'] = df_vivo['urlproceso'].apply(limpiar_url)
    
    if 'fecha_de_publicacion_del' in df_vivo.columns:
        df_vivo['fecha_de_publicacion_del'] = pd.to_datetime(df_vivo['fecha_de_publicacion_del'], errors='coerce').dt.strftime('%Y-%m-%d')
        
    if 'precio_base' in df_vivo.columns:
        # Aseguramos formato de 64 bits para que aguante cifras de miles de millones sin romperse
        df_vivo['precio_base'] = pd.to_numeric(df_vivo['precio_base'], errors='coerce').fillna(0).astype('int64')
        max_presupuesto = int(df_vivo['precio_base'].max()) if not df_vivo.empty else 1000000
    else:
        max_presupuesto = 1000000
    
    # Métricas rápidas
    col1, col2, col3 = st.columns(3)
    col1.metric("Procesos Vivos", len(df_vivo))
    col2.metric("Presupuesto en Juego", f"${df_vivo['precio_base'].sum():,.0f}".replace(",", "."))
    col3.metric("Municipios Activos", df_vivo['ciudad_entidad'].nunique())
    
    st.markdown("---")
    
    # 3. Preparar columnas
    df_mostrar = df_vivo[['entidad', 'ciudad_entidad', 'nombre_del_procedimiento', 'precio_base', 'fecha_de_publicacion_del', 'urlproceso']].copy()
    
    # Renombramos la columna del precio para que se vea elegante en la tabla
    df_mostrar.rename(columns={'precio_base': 'Presupuesto (COP)'}, inplace=True)
    
    # --- LA MAGIA: ESTILO VISUAL DE PANDAS ---
    # Esto dibuja la barra azul y además fuerza el formato de puntos (Ej: $ 7.000.000)
    df_estilizado = df_mostrar.style.format({
        "Presupuesto (COP)": lambda x: f"$ {x:,.0f}".replace(",", ".")
    }).bar(
        subset=["Presupuesto (COP)"], 
        color="rgba(0, 104, 201, 0.4)", # Un azul corporativo semitransparente
        vmin=0, 
        vmax=max_presupuesto
    )
    
    # 4. RENDERIZAR LA TABLA
    st.dataframe(
        df_estilizado,
        column_config={
            "entidad": st.column_config.TextColumn("Entidad", width="medium"),
            "ciudad_entidad": st.column_config.TextColumn("Ciudad"),
            "nombre_del_procedimiento": st.column_config.TextColumn("Objeto del Contrato", width="large"),
            "fecha_de_publicacion_del": st.column_config.TextColumn("Fecha de Pub.", help="Haz clic para ordenar"),
            "urlproceso": st.column_config.LinkColumn("Enlace SECOP", display_text="🔗 Abrir Proceso")
        },
        hide_index=True,
        use_container_width=True,
        height=600 
    )

except FileNotFoundError:
    st.info("👋 Ejecuta primero el buscador `busqueda_secop_premium.py` para alimentar el radar.")