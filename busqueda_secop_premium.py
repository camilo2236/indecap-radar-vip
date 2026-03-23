import pandas as pd
import requests
import os

# --- 1. CONFIGURACIÓN MAESTRA ---
CARPETA = r'C:\BUSQUEDA_SECOP'
nombre_archivo = os.path.join(CARPETA, 'INTELIGENCIA_TOTAL_INDECAP.xlsx')
URL_API = "https://www.datos.gov.co/resource/p6dx-8zbt.json"
ZONAS_ESTRATEGICAS = ['Medellín', 'Amagá', 'Angelópolis', 'La Pintada', 'Itagüí', 'Envigado', 'Sabaneta', 'Bello', 'Rionegro', 'Copacabana']

# --- 2. FUNCIONES DE INTELIGENCIA DE ESTADOS ---

def clasificar_oportunidad(estado):
    """Identifica el potencial de acción según el estado del SECOP."""
    estado = str(estado).lower()
    if any(e in estado for e in ['publicado', 'presentación de ofertas']):
        return "🟢 LICITAR YA (Abierto)"
    if any(e in estado for e in ['observaciones', 'comentarios']):
        return "🟡 INFLUIR (En borrador)"
    if any(e in estado for e in ['desierto', 'cancelado']):
        return "🔥 RE-LICITACIÓN PROBABLE (Llamar ya)"
    if any(e in estado for e in ['adjudicado', 'celebrado', 'en selección']):
        return "⚪ CERRADO (Seguimiento)"
    return "🔵 OTROS"

def limpiar_objeto_pro(row):
    nombre = str(row.get('nombre_del_procedimiento', '')).strip()
    desc = str(row.get('descripci_n_del_procedimiento', '')).strip()
    if (len(nombre) < 35 or "SAS" in nombre.upper()) and len(desc) > 20:
        return desc[:450]
    return nombre

def obtener_datos(query_where, limit):
    columnas = "entidad,nombre_del_procedimiento,descripci_n_del_procedimiento,precio_base,estado_del_procedimiento,fecha_de_recepcion_de,urlproceso,ciudad_entidad"
    params = {"$select": columnas, "$where": query_where, "$order": "precio_base DESC", "$limit": limit}
    res = requests.get(URL_API, params=params, timeout=60)
    return res.json()

# --- 3. EJECUCIÓN DEL MOTOR ---

try:
    print("\n" + "="*60)
    print("📡 INICIANDO SISTEMA DE INTELIGENCIA DE MERCADO - INDECAP")
    print("="*60)
    
    # TRIPLE RED: Ajustamos los rangos para capturar los contratos de 320M, 110M, etc.
    print("🎣 Red 1: 50M - 150M (Agilidad)")
    r1 = obtener_datos("departamento_entidad = 'Antioquia' AND precio_base >= 50000000 AND precio_base < 150000000", 600)
    
    print("🎣 Red 2: 150M - 900M (Core / Ejecución Directa)")
    r2 = obtener_datos("departamento_entidad = 'Antioquia' AND precio_base >= 150000000 AND precio_base <= 900000000", 1200)
    
    print("🎣 Red 3: > 900M (Macro Alianzas)")
    r3 = obtener_datos("departamento_entidad = 'Antioquia' AND precio_base > 900000000", 600)

    df_raw = pd.DataFrame(r1 + r2 + r3).drop_duplicates(subset=['urlproceso'])
    
    if not df_raw.empty:
        # Renombramiento y Limpieza
        df_raw['Entidad'] = df_raw['entidad']
        df_raw['Municipio'] = df_raw['ciudad_entidad'].fillna('Antioquia')
        df_raw['Presupuesto'] = pd.to_numeric(df_raw['precio_base'], errors='coerce').fillna(0)
        df_raw['Link'] = df_raw['urlproceso']
        
        # Inteligencia de Estados y Negocio
        df_raw['Objeto'] = df_raw.apply(limpiar_objeto_pro, axis=1)
        df_raw['Accion_Sugerida'] = df_raw['estado_del_procedimiento'].apply(clasificar_oportunidad)
        df_raw['Match_Score'] = df_raw.apply(lambda r: 8 if any(z.lower() in str(r['Municipio']).lower() for z in ZONAS_ESTRATEGICAS) else 5, axis=1)
        
        # Organización Final
        columnas = ['Accion_Sugerida', 'Match_Score', 'Entidad', 'Municipio', 'Objeto', 'Presupuesto', 'Link']
        df_final = df_raw[columnas].sort_values(['Accion_Sugerida', 'Presupuesto'], ascending=[True, False])

        # Guardado por Estrategia
        with pd.ExcelWriter(nombre_archivo, engine='xlsxwriter') as writer:
            # Pestaña de Oro: Los que están para licitar YA
            df_final[df_final['Accion_Sugerida'].str.contains('LICITAR')].to_excel(writer, sheet_name='OPORTUNIDADES_ABIERTAS', index=False)
            
            # Pestaña de Plomo: Los cancelados/desiertos que podrían repetirse
            df_final[df_final['Accion_Sugerida'].str.contains('RE-LICITACIÓN')].to_excel(writer, sheet_name='SEGUNDA_OPORTUNIDAD', index=False)
            
            # Pestaña Core: Rango 150M - 600M
            df_final[(df_final['Presupuesto'] >= 150000000) & (df_final['Presupuesto'] <= 600000000)].to_excel(writer, sheet_name='EJECUCION_DIRECTA_CORE', index=False)
            
            df_final.to_excel(writer, sheet_name='HISTORIAL_COMPLETO', index=False)

        print("\n" + "📊 RESUMEN DE ESTADOS DE MERCADO")
        print("-" * 60)
        print(df_final['Accion_Sugerida'].value_counts().to_string())
        print("-" * 60)
        print(f"✅ Sistema actualizado. Archivo listo en:\n{nombre_archivo}\n")
    else:
        print("⚠ No se capturaron datos. Revisa la conexión.")

except Exception as e:
    print(f"❌ Error crítico: {e}")