import duckdb
import pandas as pd
import threading
import concurrent.futures
import random


import time


thread_local = threading.local()


def get_con():
    if not hasattr(thread_local, "con"):
        con = duckdb.connect()
        con.execute("INSTALL httpfs;")
        con.execute("LOAD httpfs;")
        con.execute("SET enable_object_cache = true;")
        con.execute("SET threads=8;")
        thread_local.con = con
    return thread_local.con



# ----------------------------------------------------------
# Función auxiliar: consulta un dataset individual en OBIS/S3
# Esta se ejecuta en procesos separados.
# ----------------------------------------------------------
def query_obis_dataset(dataset_id, aphia_id, limit_per_dataset):
    con = get_con()

    s3_path = f"s3://obis-open-data/occurrence/{dataset_id}.parquet"
    query = f"""
        SELECT
            interpreted.scientificName,
            interpreted.decimalLatitude,
            interpreted.decimalLongitude,
            interpreted.eventDate,
            interpreted.basisOfRecord,
            _occurrence_id
        FROM read_parquet('{s3_path}', hive_partitioning = false)
        WHERE interpreted.aphiaid = {aphia_id}
        LIMIT {limit_per_dataset}
    """

    start = time.perf_counter()

    df = con.execute(query).fetchdf()

    elapsed = time.perf_counter() - start
    print(f"Tiempo de ejecución: {elapsed:.3f} segundos")

    return df

# ----------------------------------------------------------
# Función principal: busca en varios datasets (paralelizada)
# ----------------------------------------------------------
def search_obis_species_parallel(dataset_ids, aphia_id, limit_per_dataset, sample_size, max_workers):
    if len(dataset_ids) > sample_size:
        dataset_ids = random.sample(dataset_ids, sample_size)
        print(f"🎯 Usando una muestra de {sample_size} datasets para optimizar el tiempo.")

    results = []

    # --- Paralelismo controlado ---
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(query_obis_dataset, ds, aphia_id, limit_per_dataset): ds
                    for ds in dataset_ids}

            for future in concurrent.futures.as_completed(futures):
                dataset_id = futures[future]
                df = future.result()
                if not df.empty:
                    print(f"✅ {len(df)} registros encontrados en dataset: https://obis.org/dataset/{dataset_id}")
                    results.append(df)
                else:
                    print(f"— Sin registros para dataset: {dataset_id}")
    
    # --- Consolidación final ---
    if not results:
        print("⚠️ No se encontraron ocurrencias en los datasets analizados.")
        return pd.DataFrame()

    df_final = pd.concat(results, ignore_index=True)
    print(f"✅ Total de ocurrencias recuperadas: {len(df_final)}")
    
    return df_final
