import duckdb
import pandas as pd
import concurrent.futures
import random
from typing import List

# ----------------------------------------------------------
# Función auxiliar: consulta un dataset individual en OBIS/S3
# ----------------------------------------------------------
def query_obis_dataset(dataset_id: str, species_name: str, limit_per_dataset: int = 200) -> pd.DataFrame:
    """Consulta un solo dataset parquet de OBIS en S3 y devuelve ocurrencias filtradas por especie."""
    s3_path = f"s3://obis-open-data/occurrence/{dataset_id}.parquet"
    try:
        con = duckdb.connect()
        con.execute("INSTALL httpfs;")
        con.execute("LOAD httpfs;")

        query = f"""
            SELECT
                interpreted.scientificName AS scientificName,
                interpreted.decimalLatitude AS decimalLatitude,
                interpreted.decimalLongitude AS decimalLongitude,
                interpreted.eventDate AS eventDate,
                interpreted.country AS country,
                interpreted.basisOfRecord AS basisOfRecord,
                _occurrence_id AS occurrence_id
            FROM read_parquet('{s3_path}')
            WHERE lower(interpreted.scientificName) LIKE lower('%{species_name}%')
            LIMIT {limit_per_dataset};
        """
        df = con.execute(query).fetchdf()
        con.close()

        if not df.empty:
            print(f"✅ {len(df)} registros encontrados en dataset {dataset_id}")
        else:
            print(f"— Sin registros para {dataset_id}")

        return df

    except Exception as e:
        print(f"⚠️ Error en dataset {dataset_id}: {e}")
        return pd.DataFrame()


# ----------------------------------------------------------
# Función principal: busca en varios datasets (paralelizada)
# ----------------------------------------------------------
def search_obis_species_parallel(dataset_ids: List[str], species_name: str, limit_per_dataset: int, sample_size: int, max_workers: int) -> pd.DataFrame:
    """
    Busca ocurrencias en múltiples datasets de OBIS en S3, en paralelo.
    1️⃣ Toma una muestra de los datasets (por defecto 20)
    2️⃣ Ejecuta consultas simultáneas a S3 (DuckDB + httpfs)
    3️⃣ Devuelve un DataFrame consolidado

    Args:
        dataset_ids (list[str]): lista de IDs de datasets OBIS
        species_name (str): nombre científico de la especie (ej. "Eubalaena australis")
        limit_per_dataset (int): límite por dataset
        sample_size (int): número máximo de datasets a consultar
        max_workers (int): número de hilos paralelos
    """

    # --- Sampling ---
    if len(dataset_ids) > sample_size:
        dataset_ids = random.sample(dataset_ids, sample_size)
        print(f"🎯 Usando una muestra de {sample_size} datasets para optimizar el tiempo.")

    results = []

    # --- Paralelismo controlado ---
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(query_obis_dataset, ds_id, species_name, limit_per_dataset): ds_id
            for ds_id in dataset_ids
        }
        for i, future in enumerate(concurrent.futures.as_completed(futures), 1):
            ds_id = futures[future]
            try:
                df = future.result()
                if not df.empty:
                    results.append(df)
            except Exception as e:
                print(f"⚠️ Error procesando dataset {ds_id}: {e}")

    # --- Consolidación final ---
    if not results:
        print("⚠️ No se encontraron ocurrencias en los datasets analizados.")
        return pd.DataFrame()

    df_final = pd.concat(results, ignore_index=True)
    print(f"✅ Total de ocurrencias recuperadas: {len(df_final)}")
    return df_final
