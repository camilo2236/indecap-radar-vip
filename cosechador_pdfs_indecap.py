import pandas as pd
import os
import ast
import time
from playwright.sync_api import sync_playwright

# --- CONFIGURACIÓN ---
CARPETA_BASE = r'C:\BUSQUEDA_SECOP\anexos_proyectos'
# ESTA CARPETA GUARDARÁ TU SESIÓN (Tu "identidad" ante el SECOP)
CARPETA_PERFIL = r'C:\BUSQUEDA_SECOP\perfil_secop' 
EXCEL_PATH = r'C:\BUSQUEDA_SECOP\INTELIGENCIA_TOTAL_INDECAP.xlsx'

def limpiar_url(link_str):
    try:
        if isinstance(link_str, str) and '{' in link_str:
            return ast.literal_eval(link_str).get('url', '')
        return link_str
    except: return str(link_str)

def cosecha_pro_persistencia():
    df = pd.read_excel(EXCEL_PATH, sheet_name='OPORTUNIDADES_ABIERTAS')
    top_contratos = df[df['Match_Score'] >= 8].head(10).copy()
    
    if not os.path.exists(CARPETA_PERFIL): os.makedirs(CARPETA_PERFIL)

    with sync_playwright() as p:
        print("🌐 Iniciando navegador con memoria de sesión...")
        
        # USAMOS launch_persistent_context para que guarde el CAPTCHA resuelto
        context = p.chromium.launch_persistent_context(
            user_data_dir=CARPETA_PERFIL,
            headless=False, # Necesitamos verlo para resolver el CAPTCHA
            slow_mo=500     # Movimientos más humanos
        )
        
        page = context.new_page()

        # 1. Entramos a la página de inicio para que nos pida el CAPTCHA
        print("\n🔒 ESPERANDO CAPTCHA...")
        page.goto("https://community.secop.gov.co/Public/Tendering/OpportunityDetail/Index")
        
        print("👉 Si ves el 'No soy un robot', resuélvelo AHORA en la ventana del navegador.")
        input("Una vez veas la página principal del SECOP, presiona ENTER aquí para continuar...")

        # 2. Iniciamos el ciclo de descargas
        for i, row in top_contratos.iterrows():
            url = limpiar_url(row['Link'])
            entidad = "".join(x for x in str(row['Entidad']) if x.isalnum() or x in " " )[:40].strip()
            ruta_destino = os.path.join(CARPETA_BASE, entidad)
            if not os.path.exists(ruta_destino): os.makedirs(ruta_destino)
            
            print(f"\n🚀 Procesando: {entidad}")
            
            try:
                # Al tener la sesión guardada, este link debería abrir DIRECTO
                page.goto(url, wait_until="domcontentloaded", timeout=60000)
                time.sleep(3)
                
                # Intentamos la descarga
                botones = page.locator("a[id*='download'], .cl-download-icon, a:has-text('Descargar')").all()
                
                if not botones:
                    print(f"   ⚠️ No vi documentos. Tomando foto de control.")
                    page.screenshot(path=os.path.join(ruta_destino, "revisar_estado.png"))
                    continue

                for idx, boton in enumerate(botones[:3]):
                    try:
                        with page.expect_download(timeout=10000) as download_info:
                            boton.click(force=True)
                        download = download_info.value
                        nombre = f"Pliego_{idx}_{download.suggested_filename}"
                        download.save_as(os.path.join(ruta_destino, nombre))
                        print(f"   ✅ Descargado: {nombre}")
                    except: continue
                        
            except Exception as e:
                print(f"   ❌ Error: {str(e)[:40]}...")
        
        context.close()

if __name__ == "__main__":
    cosecha_pro_persistencia()