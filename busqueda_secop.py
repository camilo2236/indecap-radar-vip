import pandas as pd
import requests
import os

# --- CONFIGURACIÓN ---
CARPETA = r'C:\BUSQUEDA_SECOP'
nombre_archivo = os.path.join(CARPETA, 'INTELIGENCIA_INDECAP_20260319.xlsx')
URL_API = "https://www.datos.gov.co/resource/p6dx-8zbt.json"

# Columnas exactas para evitar errores 400
columnas = (
    "entidad,nombre_del_procedimiento,descripci_n_del_procedimiento,"
    "precio_base,estado_del_procedimiento,modalidad_de_contratacion,"
    "fecha_de_publicacion,fecha_de_recepcion_de,urlproceso,ciudad_entidad"
)

params = {
    "$select": columnas,
    "$where": "departamento_entidad = 'Antioquia' AND precio_base > 100000000",
    "$order": "precio_base DESC",
    "$limit": 1000 # Bajamos a 1000 para que sea más rápido
}

def limpiar_objeto(row):
    nombre = str(row.get('nombre_del_procedimiento', '')).strip()
    desc = str(row.get('descripci_n_del_procedimiento', '')).strip()
    es_codigo = any(c.isdigit() for c in nombre) and ('-' in nombre or len(nombre) < 20)
    if (es_codigo or "CMA" in nombre) and len(desc) > 15:
        return desc[:250]
    return nombre

try:
    print("Conectando con SECOP II (Buscando contratos > 100M)...")
    # Añadimos timeout de 60 segundos por si el servidor está lento
    response = requests.get(URL_API, params=params, timeout=60)
    response.raise_for_status()
    data = response.json()

    if data:
        df = pd.DataFrame(data)
        df['Objeto'] = df.apply(limpiar_objeto, axis=1)
        df['Presupuesto'] = pd.to_numeric(df['precio_base'], errors='coerce').fillna(0)
        
        df = df.rename(columns={
            'entidad': 'Entidad', 'estado_del_procedimiento': 'Estado',
            'fecha_de_recepcion_de': 'Fecha_Cierre', 'urlproceso': 'Link',
            'ciudad_entidad': 'Municipio'
        })

        columnas_finales = ['Entidad', 'Municipio', 'Objeto', 'Presupuesto', 'Estado', 'Fecha_Cierre', 'Link']
        df_final = df[columnas_finales]

        # Segmentación
        estados_abiertos = ['Publicado', 'Presentación de ofertas', 'En selección']
        df_abiertas = df_final[df_final['Estado'].str.contains('|'.join(estados_abiertos), case=False, na=False)]
        df_cancelados = df_final[df_final['Estado'].str.contains('Cancelado|Desierto', case=False, na=False)]

        # Guardado Multi-pestaña
        with pd.ExcelWriter(nombre_archivo, engine='xlsxwriter') as writer:
            df_abiertas.to_excel(writer, sheet_name='OPORTUNIDADES_ABIERTAS', index=False)
            df_final.to_excel(writer, sheet_name='HISTORICO_TOTAL_VIP', index=False)
            df_cancelados.to_excel(writer, sheet_name='PROCESOS_CANCELADOS', index=False)

        print(f"--- EXCEL GENERADO CON ÉXITO ---")
        print(f"Abiertos: {len(df_abiertas)} | Total: {len(df_final)}")
    else:
        print("No se encontraron resultados.")

except Exception as e:
    print(f"Error: {e}")