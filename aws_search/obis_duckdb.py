
import concurrent.futures
import logging
import random
import threading
import time

import duckdb
import pandas as pd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

thread_local = threading.local()


def get_con():
    if not hasattr(thread_local, "con"):
        con = duckdb.connect()

        try:
            con.execute("LOAD httpfs;")
            con.execute("SET enable_object_cache = true;")
            con.execute("SET disable_parquet_prefetching = true;")

            con.execute("SET threads = 2;")
        except Exception:
            con.close()
            logger.exception("Failed to initialize DuckDB/httpfs")
            raise

        thread_local.con = con

    return thread_local.con


def query_obis_dataset(dataset_id, aphia_id, limit_per_dataset):
    con = get_con()
    s3_path = (
        "s3://obis-open-data/occurrence/"
        f"{dataset_id}.parquet"
    )

    query = """
        SELECT
            interpreted.scientificName AS scientificName,
            interpreted.decimalLatitude AS decimalLatitude,
            interpreted.decimalLongitude AS decimalLongitude,
            interpreted.eventDate AS eventDate,
            interpreted.basisOfRecord AS basisOfRecord,
            _id AS occurrence_id
        FROM read_parquet(?, hive_partitioning = false)
        WHERE interpreted.aphiaid = ?
        LIMIT ?
    """

    start = time.perf_counter()

    try:
        df = con.execute(
            query,
            [s3_path, int(aphia_id), int(limit_per_dataset)],
        ).fetchdf()

        logger.info(
            "Dataset %s: %d rows in %.2f seconds",
            dataset_id,
            len(df),
            time.perf_counter() - start,
        )

        return df

    except Exception:
        logger.exception(
            "DuckDB query failed for dataset %s",
            dataset_id,
        )
        raise


def search_obis_species_parallel(
    dataset_ids,
    aphia_id,
    limit_per_dataset,
    sample_size,
    max_workers=3,
):
    if len(dataset_ids) > sample_size:
        dataset_ids = random.sample(dataset_ids, sample_size)

    results = []

    workers = max(1, min(int(max_workers), 3))

    with concurrent.futures.ThreadPoolExecutor(
        max_workers=workers
    ) as executor:
        futures = {
            executor.submit(
                query_obis_dataset,
                ds,
                aphia_id,
                limit_per_dataset,
            ): ds
            for ds in dataset_ids
        }

        for future in concurrent.futures.as_completed(futures):
            dataset_id = futures[future]

            # No ocultar fallos: registrar el dataset que falla.
            df = future.result()

            if not df.empty:
                results.append(df)
                logger.info(
                    "Dataset %s: %d occurrences found",
                    dataset_id,
                    len(df),
                )

    if not results:
        return pd.DataFrame()

    return pd.concat(results, ignore_index=True)
