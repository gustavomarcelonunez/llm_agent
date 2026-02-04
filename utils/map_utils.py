import pydeck as pdk
import pandas as pd
import geopandas as gpd
import numpy as np
import streamlit as st


# ======================================
# 🔹 Cargar shapefile MEOW solo una vez
# ======================================
@st.cache_resource
def load_meow_polygons(shp_path="data/meow_ecos.shp"):
    gdf = gpd.read_file(shp_path)
    gdf = gdf.to_crs(epsg=4326)
    gdf = gdf[["ECOREGION", "geometry"]].copy()
    return gdf


# ======================================
# 🔹 Crear capa de polígonos MEOW
# ======================================
def build_meow_layer(meow_gdf, color_map):
    records = []

    for _, row in meow_gdf.iterrows():
        eco = row["ECOREGION"]
        color = color_map.get(eco, [150, 150, 150])
        geom = row["geometry"]

        # POLYGON simple
        if geom.geom_type == "Polygon":
            coords = list(geom.exterior.coords)
            records.append({
                "ECOREGION": eco,
                "polygon": coords,
                "color": color,
                "ECOREGION_display": "block",
                "lat_display": "none",
            })

        # MULTIPOLYGON → descomponer
        elif geom.geom_type == "MultiPolygon":
            for poly in geom.geoms:
                coords = list(poly.exterior.coords)
                records.append({
                    "ECOREGION": eco,
                    "polygon": coords,
                    "color": color,
                    "ECOREGION_display": "block",
                    "lat_display": "none",
                })

    return pdk.Layer(
        "PolygonLayer",
        data=records,
        get_polygon="polygon",
        get_fill_color="color",
        get_line_color="color",
        get_line_width=20,
        stroked=True,
        filled=True,
        opacity=0.15,
        pickable=True,
        auto_highlight=True,
        id="layer_polygons",
    )


# ======================================
# 🔹 Capa de puntos
# ======================================
def build_points_layer(df):
    return pdk.Layer(
        "ScatterplotLayer",
        data=df,
        pickable=True,
        opacity=0.7,
        stroked=True,
        filled=True,
        radius_scale=30,
        radius_min_pixels=3,
        radius_max_pixels=30,
        get_position='[lon, lat]',
        get_fill_color="color",
        get_radius=60,
        id="layer_points",
    )


# ======================================
# 🔹 Render del mapa final
# ======================================
def render_occurrence_map(df):
    df = df.copy()
    df = df.rename(columns={"decimalLatitude": "lat", "decimalLongitude": "lon"})
    df = df.dropna(subset=["lat", "lon"])

    if df.empty:
        st.info("No hay coordenadas disponibles para mapear.")
        return

    # Normalizar ecorregiones
    df["ecoregion"] = df["ecoregion"].fillna("Unknown")
    ecoregions = df["ecoregion"].unique()

    # Colores persistentes
    rng = np.random.default_rng(42)
    colors = rng.integers(0, 256, size=(len(ecoregions), 3))
    color_map = {eco: colors[i].tolist() for i, eco in enumerate(ecoregions)}
    df["color"] = df["ecoregion"].map(color_map)

    # Campos adicionales SOLO para tooltip híbrido
    df["lat_display"] = "block"
    df["ECOREGION_display"] = "none"  # los puntos NO muestran bloque de ecorregión

    # ====== Cargar shapefile ======
    meow = load_meow_polygons()

    # ====== Vista inicial ======
    view_state = pdk.ViewState(
        latitude=df["lat"].mean(),
        longitude=df["lon"].mean(),
        zoom=3,
        pitch=0,
    )

    # ====== Capas ======
    layers = []

    show_polygons = st.checkbox("Mostrar ecorregiones (MEOW)", value=False)

    if show_polygons:
        layers.append(build_meow_layer(meow, color_map))

    # Puntos SIEMPRE arriba
    layers.append(build_points_layer(df))

    # ======================================
    # 🔹 Tooltip único híbrido
    # ======================================
    tooltip = {
        "html": """
        <div style="min-width: 160px">

            <!-- Tooltip para ecorregiones -->
            <div style="display: {ECOREGION_display};">
                <b>Ecorregión:</b> {ECOREGION}
            </div>

            <!-- Tooltip para puntos -->
            <div style="display: {lat_display};">
                <b>Lat:</b> {lat} <br/>
                <b>Lon:</b> {lon} <br/>
                <b>Ecorregión:</b> {ecoregion} <br/>
                <b>Fecha:</b> {eventDate}
            </div>

        </div>
        """,
        "style": {"backgroundColor": "white", "color": "black"},
    }

    # Render final
    st.pydeck_chart(
        pdk.Deck(
            layers=layers,
            initial_view_state=view_state,
            tooltip=tooltip,
        )
    )
