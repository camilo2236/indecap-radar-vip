import pandas as pd
import requests
import os
from datetime import datetime, timedelta

# --- 1. CONFIGURACIÓN ---
CARPETA = r'C:\BUSQUEDA_SECOP'
nombre_archivo = os.path.join(CARPETA, 'INTELIGENCIA_ESTRATEGICA_INDECAP_2026.xlsx')
URL_API = "https://www.datos.gov.co/resource/p6dx-8zbt.json"

def obtener_datos(query_where, limit=1000):
    # USAMOS LOS NOMBRES REALES DETECTADOS EN TU TERMINAL
    columnas = "entidad,nombre_del_procedimiento,precio_base,fase,estado_del_procedimiento,fecha_de_publicacion_del,urlproceso,ciudad_entidad,descripci_n_del_procedimiento"
    params = {
        "$select": columnas,
        "$where": query_where,
        "$order": "precio_base DESC",
        "$limit": limit
    }
    try:
        res = requests.get(URL_API, params=params, timeout=60)
        if res.status_code == 200:
            return res.json()
        else:
            print(f"⚠️ Error {res.status_code}: {res.text}")
            return []
    except Exception as e:
        print(f"❌ Error: {e}")
        return []

try:
    print("\n" + "="*50)
    print("🚀 LANZANDO RADAR ESTRATÉGICO INDECAP 2026")
    print("="*50)
    
    # Filtro de tiempo: Últimos 60 días para carne fresca
    hace_60_dias = (datetime.now() - timedelta(days=60)).strftime('%Y-%m-%dT%H:%M:%S')
    # Inicio de año para rescates
    inicio_2026 = "2026-01-01T00:00:00"

    # RED 1: ACTIVOS (Para licitar ya - Lo más caliente)
    print("🎣 Red 1: Buscando contratos abiertos en Antioquia...")
    q_activos = (
        "departamento_entidad = 'Antioquia' "
        f"AND fecha_de_publicacion_del > '{hace_60_dias}' "
        "AND estado_del_procedimiento IN ('Publicado', 'Presentación de ofertas')"
    )
    df_activos = pd.DataFrame(obtener_datos(q_activos))

    # RED 2: INFLUENCIA (Borradores para meter observaciones)
    print("🎣 Red 2: Buscando borradores (Presentación de observaciones)...")
    q_borradores = (
        "departamento_entidad = 'Antioquia' "
        f"AND fecha_de_publicacion_del > '{hace_60_dias}' "
        "AND estado_del_procedimiento = 'Presentación de observaciones'"
    )
    df_borradores = pd.DataFrame(obtener_datos(q_borradores))

    # RED 3: RESCATE (Desiertos o Cancelados en 2026)
    print("🎣 Red 3: Buscando procesos fallidos para contacto comercial...")
    q_rescate = (
        "departamento_entidad = 'Antioquia' "
        f"AND fecha_de_publicacion_del > '{inicio_2026}' "
        "AND estado_del_procedimiento IN ('Desierto', 'Cancelado')"
    )
    df_rescate = pd.DataFrame(obtener_datos(q_rescate))

    # RED 4: PREDICTIVO (Renovaciones: Contratos de 2025 de Salud/Educación)
    print("🎣 Red 4: Analizando renovaciones probables de 2025...")
    q_predictivo = (
        "departamento_entidad = 'Antioquia' "
        "AND fecha_de_publicacion_del BETWEEN '2025-01-01T00:00:00' AND '2025-12-31T23:59:59' "
        "AND (nombre_del_procedimiento LIKE '%Salud%' OR nombre_del_procedimiento LIKE '%Capacitación%')"
    )
    df_predictivo = pd.DataFrame(obtener_datos(q_predictivo))

    # GUARDAR RESULTADOS
    if all(df.empty for df in [df_activos, df_borradores, df_rescate, df_predictivo]):
        print("❌ No se encontró información con los filtros actuales.")
    else:
        with pd.ExcelWriter(nombre_archivo, engine='xlsxwriter') as writer:
            if not df_activos.empty: df_activos.to_excel(writer, sheet_name='ACTIVOS_LICITAR_YA', index=False)
            if not df_borradores.empty: df_borradores.to_excel(writer, sheet_name='INFLUIR_BORRADORES', index=False)
            if not df_rescate.empty: df_rescate.to_excel(writer, sheet_name='RESCATE_FALLIDOS', index=False)
            if not df_predictivo.empty: df_predictivo.to_excel(writer, sheet_name='PREDICCION_RENOVABLES', index=False)
        
        print(f"\n✅ ¡Misión Cumplida! Archivo generado en: {nombre_archivo}")
        print(f"   - Activos: {len(df_activos)} | Fallidos: {len(df_rescate)}")

except Exception as e:
    print(f"❌ Error crítico: {e}")