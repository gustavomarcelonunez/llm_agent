
import time
import duckdb

dataset_id = "4c9552cc-9ba5-4d41-be19-3e397f8bacf1"
aphia_id = 220222

path = (
    "s3://obis-open-data/occurrence/"
    f"{dataset_id}.parquet"
)

con = duckdb.connect()
con.execute("LOAD httpfs;")
con.execute("SET disable_parquet_prefetching = true;")

def measure(label, query, params):
    print(f"\n{label}")
    start = time.perf_counter()

    try:
        result = con.execute(query, params).fetchall()
        print(f"Resultado: {result[:5]}")
        print(f"Tiempo: {time.perf_counter() - start:.2f} segundos")
    except Exception as e:
        print(f"Error: {e}")

measure(
    "1. Conteo sin filtro",
    "SELECT COUNT(*) FROM read_parquet(?)",
    [path],
)

measure(
    "2. Conteo con filtro AphiaID",
    """
    SELECT COUNT(*)
    FROM read_parquet(?)
    WHERE interpreted.aphiaid = ?
    """,
    [path, aphia_id],
)

measure(
    "3. Recuperación completa de ocurrencias",
    """
    SELECT
        interpreted.scientificName,
        interpreted.decimalLatitude,
        interpreted.decimalLongitude,
        interpreted.eventDate,
        interpreted.basisOfRecord,
        _id AS occurrence_id
    FROM read_parquet(?)
    WHERE interpreted.aphiaid = ?
    LIMIT 200
    """,
    [path, aphia_id],
)

con.close()
