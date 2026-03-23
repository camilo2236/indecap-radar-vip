import pandas as pd
import requests
import os
import ast
from datetime import datetime, timedelta

# --- 1. CONFIGURACIÓN ---
CARPETA = r'C:\BUSQUEDA_SECOP'
nombre_archivo = os.path.join(CARPETA, 'INTELIGENCIA_ESTRATEGICA_INDECAP_2026.xlsx')
URL_API = "https://www.datos.gov.co/resource/p6dx-8zbt.json"

# Filtro de ciudades estratégicas
CIUDADES_INDECAP = "('Medellín', 'Envigado', 'Itagüí', 'Sabaneta', 'Bello', 'La Estrella', 'Caldas', 'Amagá', 'Rionegro', 'Marinilla', 'La Ceja', 'El Retiro', 'Copacabana')"

def limpiar_url(valor):
    if isinstance(valor, dict): return valor.get('url', '')
    if isinstance(valor, str) and '{' in valor:
        try: return ast.literal_eval(valor).get('url', '')
        except: return valor
    return valor

def obtener_datos(filtro_base, limit=1000):
    columnas = "entidad,nombre_del_procedimiento,precio_base,fase,estado_del_procedimiento,fecha_de_publicacion_del,urlproceso,ciudad_entidad"
    
    # Combinamos el filtro de estado/fecha con el filtro de ciudades
    query_where = f"ciudad_entidad IN {CIUDADES_INDECAP} AND {filtro_base}"
    
    params = {
        "$select": columnas,
        "$where": query_where,
        "$order": "precio_base DESC",
        "$limit": limit
    }
    try:
        res = requests.get(URL_API, params=params, timeout=60)
        if res.status_code == 200:
            data = res.json()
            for item in data:
                if 'urlproceso' in item: item['urlproceso'] = limpiar_url(item['urlproceso'])
            return data
        else:
            print(f"⚠️ Error {res.status_code} en API")
            return []
    except Exception as e:
        print(f"❌ Error: {e}")
        return []

try:
    print("\n" + "="*50)
    print("🚀 LANZANDO RADAR ESTRATÉGICO INDECAP 2026 (FILTRADO)")
    print("="*50)
    
    hace_60_dias = (datetime.now() - timedelta(days=60)).strftime('%Y-%m-%dT%H:%M:%S')
    inicio_2026 = "2026-01-01T00:00:00"

    # Red 1: ACTIVOS
    print(f"🎣 Red 1: Buscando activos en {CIUDADES_INDECAP[:50]}...")
    f_activos = f"fecha_de_publicacion_del > '{hace_60_dias}' AND estado_del_procedimiento IN ('Publicado', 'Presentación de ofertas')"
    df_activos = pd.DataFrame(obtener_datos(f_activos))

    # Red 2: BORRADORES
    print("🎣 Red 2: Buscando borradores...")
    f_borradores = f"fecha_de_publicacion_del > '{hace_60_dias}' AND estado_del_procedimiento = 'Presentación de observaciones'"
    df_borradores = pd.DataFrame(obtener_datos(f_borradores))

    # Red 3: RESCATE
    print("🎣 Red 3: Buscando procesos fallidos 2026...")
    f_rescate = f"fecha_de_publicacion_del > '{inicio_2026}' AND estado_del_procedimiento IN ('Desierto', 'Cancelado')"
    df_rescate = pd.DataFrame(obtener_datos(f_rescate))

    # Red 4: PREDICTIVO (Renovaciones de Salud/Educación 2025)
    print("🎣 Red 4: Analizando renovaciones probables...")
    f_pre = "fecha_de_publicacion_del BETWEEN '2025-01-01T00:00:00' AND '2025-12-31T23:59:59' AND (nombre_del_procedimiento LIKE '%Salud%' OR nombre_del_procedimiento LIKE '%Capacitación%')"
    df_predictivo = pd.DataFrame(obtener_datos(f_pre))

    # Guardado en Excel
    with pd.ExcelWriter(nombre_archivo, engine='xlsxwriter') as writer:
        if not df_activos.empty: df_activos.to_excel(writer, sheet_name='ACTIVOS_LICITAR_YA', index=False)
        if not df_borradores.empty: df_borradores.to_excel(writer, sheet_name='INFLUIR_BORRADORES', index=False)
        if not df_rescate.empty: df_rescate.to_excel(writer, sheet_name='RESCATE_FALLIDOS', index=False)
        if not df_predictivo.empty: df_predictivo.to_excel(writer, sheet_name='PREDICCION_RENOVABLES', index=False)
    
    print(f"\n✅ ¡Misión Cumplida! Archivo generado en: {nombre_archivo}")
    print(f"   Filtrado para {len(CIUDADES_INDECAP.split(','))} ciudades estratégicas.")

except PermissionError:
    print(f"\n❌ ERROR: Cierra el archivo Excel '{nombre_archivo}' primero.")
except Exception as e:
    print(f"❌ Error crítico: {e}")