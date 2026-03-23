import pandas as pd
import requests
import os
import ast

# --- CONFIGURACIÓN ---
CARPETA_BASE = r'C:\BUSQUEDA_SECOP\anexos_proyectos'
EXCEL_PATH = r'C:\BUSQUEDA_SECOP\INTELIGENCIA_TOTAL_INDECAP.xlsx'

if not os.path.exists(CARPETA_BASE):
    os.makedirs(CARPETA_BASE)

def limpiar_url(link_str):
    try:
        # Extrae el link real eliminando el formato {'url': '...'}
        if isinstance(link_str, str) and '{' in link_str:
            # Usamos una forma segura de evaluar el texto como diccionario
            dict_link = ast.literal_eval(link_str)
            return dict_link.get('url', '')
        return link_str
    except:
        return str(link_str)

def descargar_anexos():
    print("📖 Leyendo base de datos...")
    df = pd.read_excel(EXCEL_PATH, sheet_name='OPORTUNIDADES_ABIERTAS')
    
    # AJUSTE CRÍTICO: Filtramos por Match_Score >= 8
    top_contratos = df[df['Match_Score'] >= 8].copy()
    top_contratos['Link_Limpio'] = top_contratos['Link'].apply(limpiar_url)

    total = len(top_contratos.head(10))
    print(f"🚀 Iniciando descarga de {total} carpetas de proyectos prioritarios...")

    for i, row in top_contratos.head(10).iterrows():
        # Limpiamos el nombre de la entidad para que sea un nombre de carpeta válido
        entidad_limpia = "".join(x for x in str(row['Entidad']) if x.isalnum() or x in "._- ").strip()
        nombre_carpeta = entidad_limpia[:50]
        
        ruta_contrato = os.path.join(CARPETA_BASE, nombre_carpeta)
        if not os.path.exists(ruta_contrato):
            os.makedirs(ruta_contrato)
            
        print(f"✅ Carpeta creada: {nombre_carpeta}")
        
        # Guardamos el link limpio en un archivo para que puedas darle click directo
        with open(os.path.join(ruta_contrato, "ACCESO_DIRECTO_SECOP.txt"), "w") as f:
            f.write(f"LINK AL CONTRATO:\n{row['Link_Limpio']}")

    print("\n✅ Proceso terminado. Revisa la carpeta 'anexos_proyectos' en tu PC.")

if __name__ == "__main__":
    descargar_anexos()