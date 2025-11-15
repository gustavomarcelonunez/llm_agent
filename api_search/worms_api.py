import requests
import time

def worms_search(scientific_name):
    """
    Consulta WoRMS por un nombre científico.
    Devuelve información taxonómica clave:
    - AphiaID
    - Estado taxonómico (accepted / unaccepted / synonym)
    - Nombre válido (si aplica)
    - Nivel taxonómico
    - Información ambiental (isMarine, isBrackish, etc.)
    """

    base_url = "https://www.marinespecies.org/rest"
    search_url = f"{base_url}/AphiaRecordsByName/{scientific_name}?like=false&marine_only=false"

    try:
        r = requests.get(search_url, timeout=10)

        if r.status_code == 204 or not r.text.strip():
            return {
                "status": "not_found",
                "query": scientific_name,
                "message": f"No se encontró la especie '{scientific_name}' en WoRMS."
            }

        r.raise_for_status()
        data = r.json()

    except Exception as e:
        return {"status": "error", "message": str(e)}

    # Primer registro (más relevante)
    record = data[0]

    aphia_id = record.get("AphiaID")
    status = record.get("status", "unknown")  # accepted, unaccepted, synonym, etc.
    valid_name = record.get("valid_name") or record.get("scientificname")
    valid_aphia = record.get("valid_AphiaID") or aphia_id

    # ----------------------------------------
    # Obtener también el registro válido
    # ----------------------------------------
    valid_record = None
    if valid_aphia != aphia_id:
        try:
            val_url = f"{base_url}/AphiaRecordByAphiaID/{valid_aphia}"
            time.sleep(0.2)
            rv = requests.get(val_url, timeout=10)
            if rv.status_code == 200:
                valid_record = rv.json()
        except:
            valid_record = None

    result = {
        "status": "ok",
        "query": scientific_name,
        "aphia_id": aphia_id,
        "input_status": status,                # accepted / unaccepted / synonym / misapplied
        "input_scientific_name": record.get("scientificname"),
        "is_valid": (status == "accepted"),    # <--- muy útil
        "valid_name": valid_name,
        "valid_aphia_id": valid_aphia,
        "authority": record.get("authority"),
        "rank": record.get("rank"),
        "environment": {
            "is_marine": record.get("isMarine"),
            "is_brackish": record.get("isBrackish"),
            "is_freshwater": record.get("isFreshwater"),
            "is_terrestrial": record.get("isTerrestrial"),
        },
        "taxonomy": {
            "kingdom": record.get("kingdom"),
            "phylum": record.get("phylum"),
            "class": record.get("class"),
            "order": record.get("order"),
            "family": record.get("family"),
            "genus": record.get("genus"),
        }
    }

    # Agregar información del taxon válido, si es distinto
    if valid_record:
        result["valid_taxon"] = {
            "scientific_name": valid_record.get("scientificname"),
            "authority": valid_record.get("authority"),
            "rank": valid_record.get("rank"),
            "status": valid_record.get("status")
        }

    return result
