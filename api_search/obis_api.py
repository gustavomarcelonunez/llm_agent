import requests

def obis_search(taxonid):
    """
    Devuelve la lista de dataset_id que contienen registros del taxon.
    No requiere paginado para el endpoint /dataset.
    """

    url = "https://api.obis.org/v3/dataset"
    params = {"taxonid": taxonid}

    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()

    data = r.json()

    results = [item["id"] for item in data.get("results", [])]

    print(f"✅ Recuperados {len(results)} de {data.get('total', len(results))} datasets de OBIS.")

    return results
