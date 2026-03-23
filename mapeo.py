import requests

print("\n🚀 --- COLUMNAS DEL DATASET DE CONTRATOS (Para Auditoría 2025) ---")
res_contratos = requests.get("https://www.datos.gov.co/resource/jbjy-vk9h.json?$limit=1")
if res_contratos.status_code == 200:
    columnas_contratos = list(res_contratos.json()[0].keys())
    print(columnas_contratos)
else:
    print("Error conectando a Contratos")

print("\n🚀 --- COLUMNAS DEL DATASET DE PROCESOS (Para Radar 2026) ---")
res_procesos = requests.get("https://www.datos.gov.co/resource/p6dx-8zbt.json?$limit=1")
if res_procesos.status_code == 200:
    columnas_procesos = list(res_procesos.json()[0].keys())
    print(columnas_procesos)
else:
    print("Error conectando a Procesos")
print("\n")