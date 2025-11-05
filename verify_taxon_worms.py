import requests
import time

def verify_taxon_worms(scientific_name):
    """
    Verifica la validez taxonómica de una especie en WoRMS (World Register of Marine Species).
    Devuelve un diccionario con estado, nombre válido, autoridad, y sinónimos si existen.
    """
    base_url = "https://www.marinespecies.org/rest"
    search_url = f"{base_url}/AphiaRecordsByName/{scientific_name}?like=false&marine_only=true"

    try:
        r = requests.get(search_url, timeout=10)

        if r.status_code == 204 or not r.text.strip():
            print(f" ⚠️  No se encontró información sobre la especie '{scientific_name}' en WoRMS.")
            return {"status": "not_found", "message": "Sin resultados en WoRMS"}
        
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        print(f"❌ Error al consultar WoRMS: {e}")
        return {"status": "error", "message": str(e)}

    # Toma el primer registro (el más relevante)
    record = data[0]

    aphia_id = record.get("AphiaID")
    valid_name = record.get("valid_name") or record.get("scientificname")
    authority = record.get("authority", "No especificada")
    status = record.get("status", "Desconocido")

    # Busca sinónimos si existen
    synonyms_url = f"{base_url}/AphiaSynonymsByAphiaID/{aphia_id}"
    time.sleep(0.3)
    try:
        rs = requests.get(synonyms_url, timeout=10)
        synonyms = [s["scientificname"] for s in rs.json()] if rs.status_code == 200 else []
    except Exception:
        synonyms = []

    result = {
        "status": "ok",
        "query": scientific_name,
        "aphia_id": aphia_id,
        "valid_name": valid_name,
        "authority": authority,
        "taxon_status": status,
        "rank": record.get("rank"),
        "kingdom": record.get("kingdom"),
        "phylum": record.get("phylum"),
        "class": record.get("class"),
        "order": record.get("order"),
        "family": record.get("family"),
        "genus": record.get("genus"),
        "is_marine": record.get("isMarine", True),
        "synonyms": synonyms,
    }

    print(f"✅ Verificación WoRMS completada para '{scientific_name}'.")
    return result
