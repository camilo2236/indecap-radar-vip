import requests

url = "https://www.datos.gov.co/resource/p6dx-8zbt.json?$limit=1"
try:
    res = requests.get(url)
    if res.status_code == 200:
        columnas_reales = res.json()[0].keys()
        print("\n✅ COLUMNAS DETECTADAS EN LA API:")
        print(list(columnas_reales))
    else:
        print(f"❌ Error al conectar: {res.status_code}")
except Exception as e:
    print(f"❌ Error: {e}")