import geopandas as gpd
import pandas as pd
from shapely.geometry import Point


def assign_meow_ecoregion(df: pd.DataFrame) -> pd.DataFrame:
    print("🌍 Asignando ecoregión MEOW...")

    meow_path = "data/meow_ecos.shp"


    meow = gpd.read_file(meow_path)
    meow = meow.to_crs(epsg=4326)

    # Filtrar solo registros con coordenadas válidas
    df_geo = df.dropna(subset=["decimalLatitude", "decimalLongitude"]).copy()
    df_geo["geometry"] = [
        Point(xy) for xy in zip(df_geo["decimalLongitude"], df_geo["decimalLatitude"])
    ]
    gdf = gpd.GeoDataFrame(df_geo, geometry="geometry", crs="EPSG:4326")

    # Hacer spatial join
    joined = gpd.sjoin(gdf, meow[["geometry", "ECOREGION"]], how="left")

    # Crear columna combinada jerárquica
    joined["ecoregion"] = (
        joined["ECOREGION"].fillna("Unknown")
    )

    # Para los sin coordenadas
    df_no_coords = df[df["decimalLatitude"].isna() | df["decimalLongitude"].isna()].copy()
    df_no_coords["ecoregion"] = "Unknown / No coordinates"

    # Combinar ambos
    df_final = pd.concat([joined.drop(columns="geometry"), df_no_coords], ignore_index=True)
    print(f"✅ Asignadas {df_final['ecoregion'].nunique()}.")

    return df_final
