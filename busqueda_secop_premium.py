import pandas as pd
import requests
import os
from datetime import datetime, timedelta

# --- CONFIGURACIÓN DEL RADAR EN VIVO 2026 ---
CARPETA = r'C:\BUSQUEDA_SECOP'
archivo_radar = os.path.join(CARPETA, 'RADAR_VIVO_INDECAP_2026.xlsx')
URL_API_PROCESOS = "https://www.datos.gov.co/resource/p6dx-8zbt.json"

# La malla ultra-profunda que descubrimos
MUNICIPIOS = "('Medellín', 'Medellin', 'Envigado', 'Caldas', 'Itagüí', 'Itagui', 'La Estrella', 'Titiribí', 'Titiribi', 'Bello')"
ENTIDADES_EXTRA = "upper(entidad) LIKE '%UNIVERSIDAD DE ANTIOQUIA%' OR upper(entidad) LIKE '%AREA METROPOLITANA%' OR upper(entidad) LIKE '%METRO DE MEDELLIN%'"
SEGMENTOS = "('86', '80', '93', '81', '85', '94', '92')"
PALABRAS = ['CAPACITACION', 'EDUCACION', 'FORMACION', 'ENTRENAMIENTO', 'DIPLOMADO', 
            'ACTUALIZACION', 'SEMINARIO', 'TALLER', 'CURSO', 'INDUCCION', 
            'SENSIBILIZACION', 'FORTALECIMIENTO', 'CUALIFICACION', 'ACOMPAÑAMIENTO', 
            'TRANSFERENCIA', 'CERTIFICACION']

def ejecutar_radar_vivo():
    columnas = "entidad,nombre_del_procedimiento,precio_base,fase,estado_del_procedimiento,fecha_de_publicacion_del,urlproceso,ciudad_entidad,codigo_principal_de_categoria"
    
    # Construir la búsqueda de palabras
    likes = " OR ".join([f"upper(nombre_del_procedimiento) LIKE '%{p}%'" for p in PALABRAS])
    filtro_tematico = f"(substring(codigo_principal_de_categoria, 1, 2) IN {SEGMENTOS} OR {likes})"
    
    # Filtro Anti-Ruido (Sin profesores individuales)
    filtro_ruido = "AND upper(nombre_del_procedimiento) NOT LIKE '%CONTRATISTA INDEPENDIENTE%' " \
                   "AND upper(nombre_del_procedimiento) NOT LIKE '%SERVICIOS PERSONALES%'"
    
    # Solo procesos VIVOS (Publicados o en presentación de ofertas) de los últimos 60 días
    hace_60_dias = (datetime.now() - timedelta(days=60)).strftime("%Y-%m-%dT00:00:00")
    filtro_vivo = f"AND fecha_de_publicacion_del >= '{hace_60_dias}' AND estado_del_procedimiento IN ('Publicado', 'Presentación de oferta', 'Borrador', 'Convocada')"

    query = (
        f"(ciudad_entidad IN {MUNICIPIOS} OR {ENTIDADES_EXTRA}) "
        f"AND ({filtro_tematico}) "
        f"{filtro_ruido} "
        f"{filtro_vivo}"
    )
    
    params = {"$select": columnas, "$where": query, "$limit": 2000}
    
    print("📡 Escaneando oportunidades VIVAS para INDECAP en el Anillo de Oro...")
    res = requests.get(URL_API_PROCESOS, params=params)
    
    if res.status_code == 200:
        data = res.json()
        if not data:
            print("⚠️ No hay procesos nuevos hoy con estos criterios.")
            return

        df = pd.DataFrame(data)
        df['precio_base'] = pd.to_numeric(df['precio_base'], errors='coerce').fillna(0)
        
        # Ordenar por los más recientes y más jugosos
        df = df.sort_values(by=['fecha_de_publicacion_del', 'precio_base'], ascending=[False, False])
        
        df.to_excel(archivo_radar, index=False)
        print(f"🎯 ¡Cacería exitosa! {len(df)} oportunidades vivas guardadas en: {archivo_radar}")
    else:
        print(f"❌ Error API: {res.text}")

if __name__ == "__main__":
    ejecutar_radar_vivo()