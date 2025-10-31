# api_search.py
import requests
import time

def search_obis(keyword):
    """
    Busca registros biológicos en OBIS (Ocean Biogeographic Information System)
    según una palabra clave, usando su API pública.
    """
    base_url = "https://api.obis.org/v3/occurrence"
    max_records=500
    size = 100  # cantidad por página
    offset = 0
    results = []
    
    while len(results) < max_records:
        params = {"scientificname": keyword, "size": size, "offset": offset}
        r = requests.get(base_url, params=params, timeout=10)
        if r.status_code != 200:
            print(f"Error en la solicitud (HTTP {r.status_code})")
            break

        data = r.json()
        page_results = data.get("results", [])
        if not page_results:
            break

        results.extend(page_results)
        offset += size
        time.sleep(0.3)  # evita abusar de la API

        if len(page_results) < size:
            break  # última página

    print(f"✅ Recuperados {len(results)} registros de OBIS.")
    return results