import concurrent.futures
import pandas as pd
from typing import Dict, Any

# ==============================
# 🔹 Función principal
# ==============================

def run_regional_agents(df: pd.DataFrame, scientific_name: str, summarize_fn, max_workers: int = 8) -> Dict[str, Any]:
    """
    Ejecuta agentes regionales en paralelo.
    
    Parámetros
    ----------
    df : pd.DataFrame
        DataFrame con columnas: scientificName, ecoregion, country, eventDate, etc.
    scientific_name : str
        Nombre científico de la especie analizada (para contexto en los prompts).
    summarize_fn : callable
        Función que recibe (scientific_name, region_name, df_region) y devuelve un resumen (str o dict).
    max_workers : int
        Número máximo de hilos a usar en paralelo.
    
    Retorna
    -------
    Dict[str, Any]
        Diccionario con claves = ecoregiones, valores = resumen del agente.
    """
    if "ecoregion" not in df.columns:
        raise ValueError("El DataFrame debe contener una columna 'ecoregion'.")

    grouped = dict(tuple(df.groupby("ecoregion")))
    print(f"🌊 {len(grouped)} ecoregiones detectadas para análisis paralelo.")

    results = {}

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_region = {
            executor.submit(summarize_fn, scientific_name, region, subdf): region
            for region, subdf in grouped.items()
        }

        for future in concurrent.futures.as_completed(future_to_region):
            region = future_to_region[future]
            try:
                summary = future.result()
                results[region] = summary
                print(f"✅ Resumen completado: {region}")
            except Exception as e:
                print(f"⚠️ Error procesando región {region}: {e}")
                results[region] = None

    return results