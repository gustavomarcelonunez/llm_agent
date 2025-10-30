# api_search.py
import requests

def search_obis(keyword):
    """
    Busca registros biológicos en OBIS (Ocean Biogeographic Information System)
    según una palabra clave, usando su API pública.
    """
    base_url = "https://api.obis.org/v3/occurrence"
    params = {"scientificname": keyword, "size": 5}  # 5 primeros resultados

    r = requests.get(base_url, params=params)
    if r.status_code != 200:
        return f"⚠️ No se pudo acceder a OBIS (status {r.status_code})"

    data = r.json()

    if not data.get("results"):
        return f"No se encontraron registros para '{keyword}'."

    print(f"\n🔍 Resultados encontrados en OBIS para '{keyword}':\n")
    for i, result in enumerate(data["results"], start=1):
        especie = result.get("scientificName", "Sin nombre")
        lat = result.get("decimalLatitude", "?")
        lon = result.get("decimalLongitude", "?")
        fecha = result.get("eventDate", "Desconocida")
        print(f"{i}. {especie} — 📍({lat}, {lon}) — 🗓 {fecha}")

    return "✅ Consulta finalizada."
