import duckdb
import pandas as pd
import concurrent.futures
import random
from typing import List


GLOBAL_DUCKDB = duckdb.connect()
GLOBAL_DUCKDB.execute("INSTALL httpfs;")

# ----------------------------------------------------------
# Función auxiliar: consulta un dataset individual en OBIS/S3
# Esta se ejecuta en procesos separados.
# ----------------------------------------------------------
def query_obis_dataset(dataset_id: str, aphia_id: str, limit_per_dataset: int) -> pd.DataFrame:
    """Consulta un solo dataset parquet de OBIS en S3 y devuelve ocurrencias filtradas por especie."""
    s3_path = f"s3://obis-open-data/occurrence/{dataset_id}.parquet"
    try:
        con = duckdb.connect()
        con.execute("LOAD httpfs;")

        query = f"""
            SELECT
                interpreted.scientificName AS scientificName,
                interpreted.decimalLatitude AS decimalLatitude,
                interpreted.decimalLongitude AS decimalLongitude,
                interpreted.eventDate AS eventDate,
                interpreted.basisOfRecord AS basisOfRecord,
                _occurrence_id AS occurrence_id
            FROM read_parquet('{s3_path}')
            WHERE interpreted.aphiaid = CAST({aphia_id} AS BIGINT)
            LIMIT {limit_per_dataset};
        """
        df = con.execute(query).fetchdf()
        con.close()

        if not df.empty:
            print(f"✅ {len(df)} registros encontrados en dataset:  https://obis.org/dataset/{dataset_id}")
        else:
            print(f"— Sin registros para {dataset_id}")

        return df

    except Exception as e:
        print(f"⚠️ Error en dataset {dataset_id}: {e}")
        return pd.DataFrame()


# ----------------------------------------------------------
# Función principal: busca en varios datasets (paralelizada)
# ----------------------------------------------------------
def search_obis_species_parallel(dataset_ids: List[str], aphia_id: int, limit_per_dataset: int, sample_size: int, max_workers: int) -> pd.DataFrame:
    """
    Busca ocurrencias en múltiples datasets OBIS usando paralelismo.
    
    Args:
        dataset_ids (list[str]): lista de IDs de datasets OBIS
        aphia_id (int): identificar único de la especie
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
    with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(query_obis_dataset, ds_id, aphia_id, limit_per_dataset): ds_id
            for ds_id in dataset_ids
        }
        for future in concurrent.futures.as_completed(futures):
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
