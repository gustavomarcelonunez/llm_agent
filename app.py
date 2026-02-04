import streamlit as st
import pandas as pd
from pipeline import run_pipeline
from utils.map_utils import render_occurrence_map

st.set_page_config(
    page_title="AquaMind",
    page_icon="🌊",
)

# ---------------------------------------------------------
# HEADER
# ---------------------------------------------------------
st.markdown("""
<style>
.header-container {
    display: flex;
    align-items: center;
    gap: 20px;
    padding: 10px 0px 30px 0px;
}
.header-logo {
    font-size: 60px;
}
.header-title {
    font-size: 42px;
    font-weight: 700;
    margin-bottom: -5px;
}
.header-subtitle {
    font-size: 20px;
    color: #BBBBBB;
}
</style>

<div class="header-container">
    <div class="header-logo">🌊</div>
    <div>
        <div class="header-title">AquaMind</div>
        <div class="header-subtitle">Exploración Inteligente de Biodiversidad Marina</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# INPUTS
# ---------------------------------------------------------
scientific_name = st.text_input("Nombre científico", placeholder="Ej: Odontesthes smitti")

with st.expander("Parámetros"):
    limit_per_dataset = st.number_input("Límite por dataset", 1, 5000, 200,
                                        help="Cantidad máxima de ocurrencias que se obtendrán de cada dataset antes de procesarlos. Rango: 1-5000"
                                        )
    sample_size = st.number_input("Tamaño de muestra", 1, 1000, 15,
                                  help="Cantidad de datasets de OBIS aleatorios que se usarán para el análisis. Rango: 1-1000"
                                  )

run = st.button("Analizar")

with st.sidebar:
    st.info("""
    ### Acerca de esta aplicación
    
    Esta app permite buscar taxones en WoRMS y OBIS, procesar registros biológicos,
    asignar ecorregiones y generar informes automáticos. Se basa en el uso de agentes IA, los cuales están 
    programados para razonar sobre la información obtenida sobre una especie en particular.
    """)


# ---------------------------------------------------------
# EJECUCIÓN DEL PIPELINE (solo cuando se presiona Analizar)
# ---------------------------------------------------------
if run:
    if not scientific_name.strip():
        st.error("Ingresá un nombre científico.")
        st.stop()

    log_box = st.empty()

    def progress_cb(msg: str):
        log_box.info(msg)

    with st.spinner("Ejecutando análisis (puede tardar algunos minutos)..."):
        result = run_pipeline(
            scientific_name=scientific_name.strip(),
            limit_per_dataset=int(limit_per_dataset),
            sample_size=int(sample_size),
            progress_cb=progress_cb,
        )

    # Si hubo error al buscar el taxón
    if result.get("status") == "error":
        st.error(f"❌ {result['message']}")
        st.stop()

    # Guardamos resultados
    st.session_state["analysis_result"] = result

# ---------------------------------------------------------
# MOSTRAR RESULTADOS SI EXISTEN EN SESSION_STATE
# ---------------------------------------------------------
if "analysis_result" in st.session_state:
    result = st.session_state["analysis_result"]

    st.success("Análisis completado")

    st.subheader("Resumen global")
    st.write(result["global_summary"])

    st.subheader("Mapa de ocurrencias")

    df_map = result["df"].copy()

    # ================================
    #      FILTROS INTERACTIVOS
    # ================================

    eco_counts = df_map["ecoregion"].value_counts().to_dict()   # {eco: count}

    options = ["Todas ({})".format(len(df_map))] + [
        f"{eco} ({eco_counts[eco]})" for eco in sorted(eco_counts.keys())
    ]

    selected = st.selectbox("Filtrar por ecorregión", options)

    # --- Filtro por ecoregión ---
    # Extraer el nombre real de la ecoregión (sin el número)
    if selected.startswith("Todas"):
        selected_ecoregion = None
    else:
        selected_ecoregion = selected.rsplit(" (", 1)[0]   # "North Patagonian Gulf"

    # Aplicar filtro
    if selected_ecoregion:
        df_map = df_map[df_map["ecoregion"] == selected_ecoregion]

    # ================================
    #      RENDER DEL MAPA
    # ================================

    render_occurrence_map(df_map)



    st.subheader("Descargar reporte completo (TXT)")
    with open(result["txt_path"], "rb") as f:
        st.download_button(
            label="📥 Descargar resumen completo",
            data=f,
            file_name=f"{result['scientific_name'].replace(' ', '_')}_report.txt",
            mime="text/plain",
        )
