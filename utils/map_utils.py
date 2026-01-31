import pydeck as pdk
import pandas as pd
import numpy as np
import streamlit as st

def render_occurrence_map(df):
    """Renderiza un mapa interactivo de ocurrencias con pydeck."""
    # Copia para no modificar el DF original
    df = df.copy()

    # --- Preprocesamiento ---
    df = df.rename(columns={
        "decimalLatitude": "lat",
        "decimalLongitude": "lon",
    })




    # Filtrar coordenadas válidas
    df = df.dropna(subset=["lat", "lon"])

    if df.empty:
        st.info("No hay coordenadas disponibles para mapear.")
        return

    # --- Asignación de colores por ecoregión ---
    df["ecoregion"] = df["ecoregion"].fillna("unknown")
    ecoregions = df["ecoregion"].unique()

    rng = np.random.default_rng(42)
    colors = rng.integers(0, 256, size=(len(ecoregions), 3))
    color_map = {eco: colors[i].tolist() for i, eco in enumerate(ecoregions)}

    df["color"] = df["ecoregion"].map(color_map)

    # --- Capa de puntos ---
    layer = pdk.Layer(
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
    )

    # --- Tooltip ---
    tooltip = {
        "html": """
            <b>Lat:</b> {lat} <br/>
            <b>Lon:</b> {lon} <br/>
            <b>Ecoregión:</b> {ecoregion} <br/>
            <b>Fecha:</b> {eventDate}
        """,
        "style": {"backgroundColor": "white", "color": "black"}
    }

    # --- Vista inicial ---
    view_state = pdk.ViewState(
        latitude=df["lat"].mean(),
        longitude=df["lon"].mean(),
        zoom=3,
        pitch=0,
    )

    deck = pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        tooltip=tooltip,
    )

    st.pydeck_chart(deck)
