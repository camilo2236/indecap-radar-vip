import pandas as pd
import requests
import os

# --- CONFIGURACIÓN DE INVESTIGACIÓN ULTRA-PROFUNDA ---
CARPETA = r'C:\BUSQUEDA_SECOP'
archivo_historico = os.path.join(CARPETA, 'AUDITORIA_ULTRA_PROFUNDA_2025.xlsx')
URL_API_CONTRATOS = "https://www.datos.gov.co/resource/jbjy-vk9h.json"

# 1. Blindaje Geográfico y Entidades Supramunicipales
MUNICIPIOS = "('Medellín', 'Medellin', 'Envigado', 'Caldas', 'Itagüí', 'Itagui', 'La Estrella', 'Titiribí', 'Titiribi', 'Bello')"
ENTIDADES_EXTRA = "upper(nombre_entidad) LIKE '%UNIVERSIDAD DE ANTIOQUIA%' OR upper(nombre_entidad) LIKE '%AREA METROPOLITANA%' OR upper(nombre_entidad) LIKE '%METRO DE MEDELLIN%'"

# 2. Segmentos Expandidos: Añadimos 94 (Organizaciones) y 92 (Defensa/Seguridad)
SEGMENTOS = "('86', '80', '93', '81', '85', '94', '92')"

def auditoria_ultra_profunda_2025():
    columnas = "nombre_entidad,ciudad,objeto_del_contrato,valor_del_contrato,proveedor_adjudicado,fecha_de_firma,modalidad_de_contratacion,codigo_de_categoria_principal"
    
    # 3. El Vocabulario Secreto Expandido (La Jerga de las Entidades)
    palabras = ['CAPACITACION', 'EDUCACION', 'FORMACION', 'ENTRENAMIENTO', 'DIPLOMADO', 
                'ACTUALIZACION', 'SEMINARIO', 'TALLER', 'CURSO', 'INDUCCION', 
                'SENSIBILIZACION', 'FORTALECIMIENTO', 'CUALIFICACION', 'ACOMPAÑAMIENTO', 
                'TRANSFERENCIA', 'CERTIFICACION']
    
    # Construcción dinámica de la consulta OR para las palabras
    likes = " OR ".join([f"upper(objeto_del_contrato) LIKE '%{p}%'" for p in palabras])
    filtro_tematico = f"(substring(codigo_de_categoria_principal, 1, 2) IN {SEGMENTOS} OR {likes})"
    
    # 4. FILTRO ANTI-RUIDO
    filtro_ruido = "AND upper(objeto_del_contrato) NOT LIKE '%CONTRATISTA INDEPENDIENTE%' " \
                   "AND upper(objeto_del_contrato) NOT LIKE '%SERVICIOS PERSONALES%'"
    
    query = (
        f"(ciudad IN {MUNICIPIOS} OR {ENTIDADES_EXTRA}) "
        f"AND ({filtro_tematico}) "
        f"{filtro_ruido} "
        "AND fecha_de_firma BETWEEN '2025-01-01T00:00:00' AND '2025-12-31T23:59:59'"
    )
    
    params = {
        "$select": columnas, 
        "$where": query, 
        "$limit": 50000 
    }
    
    print("🌊 Lanzando RED ULTRA-PROFUNDA: Buscando AMVA, Metro, Personerías y nueva jerga...")
    try:
        # Aumentamos el timeout porque la consulta es muy pesada para el servidor del SECOP
        res = requests.get(URL_API_CONTRATOS, params=params, timeout=120)
        
        if res.status_code == 200:
            data = res.json()
            if not data:
                print("⚠️ No se encontraron datos con estos criterios.")
                return

            df = pd.DataFrame(data)
            df['valor_del_contrato'] = pd.to_numeric(df['valor_del_contrato'], errors='coerce').fillna(0)

            with pd.ExcelWriter(archivo_historico, engine='xlsxwriter') as writer:
                # Pestaña 1: Base limpia
                df.to_excel(writer, sheet_name='PANORAMA_TOTAL', index=False)
                
                # Pestaña 2: Auditoría de Ganadores Institucionales
                if 'proveedor_adjudicado' in df.columns:
                    df_validos = df[df['proveedor_adjudicado'].notna()]
                    top_ganadores = df_validos.groupby('proveedor_adjudicado')['valor_del_contrato'].agg(['count', 'sum']).sort_values(by='sum', ascending=False).reset_index()
                    top_ganadores.columns = ['Contratista', 'Nro Contratos', 'Bolsa Capturada ($)']
                    top_ganadores.to_excel(writer, sheet_name='COMPETIDORES_CORPORATIVOS', index=False)
            
            print(f"✅ ¡Extracción total completada! Archivo: {archivo_historico}")
            print(f"📊 Se aislaron {len(df)} contratos (Compara este número con los 2,268 de antes).")
            
        else:
            print(f"❌ Error API: {res.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    auditoria_ultra_profunda_2025()