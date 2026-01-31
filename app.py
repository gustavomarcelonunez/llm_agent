import streamlit as st
from pipeline import run_pipeline
from utils.map_utils import render_occurrence_map

st.set_page_config(
    page_title="AquaMind",
    page_icon="🌊",  # Si querés usar un emoji
    layout="wide"
)

st.title("🌊 AquaMind - Exploración Inteligente de Biodiversidad Marina")

scientific_name = st.text_input("Nombre científico", placeholder="Ej: Odontesthes smitti")

# Parámetros opcionales (para no tocar código cada vez)
with st.expander("Parámetros"):
    limit_per_dataset = st.number_input("Límite por dataset", 1, 5000, 200,
                                            help="Máximo de registros que se obtendrán de cada dataset antes de procesarlos."
                                            )
    sample_size = st.number_input("Tamaño de muestra", 1, 1000, 15,
                                        help="Cantidad de datasets de OBIS aleatorios que se usarán para el análisis."
                                        )
    max_workers = st.number_input("Max workers", 1, 64, 16,
                                      help="Número de hilos/paralelización. A mayor número, más rápido, pero mayor consumo de CPU."
                                      )

run = st.button("Analizar")

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
            max_workers=int(max_workers),
            progress_cb=progress_cb,
        )

    st.success("Listo.")

    st.subheader("Resumen global")
    st.write(result["global_summary"])


    st.subheader("Mapa de ocurrencias")
    render_occurrence_map(result["df"])

    st.subheader("Descargar reporte completo (TXT)")
    with open(result["txt_path"], "rb") as f:
        st.download_button(
            label="Descargar TXT",
            data=f,
            file_name=f"{result['scientific_name'].replace(' ', '_')}_report.txt",
            mime="text/plain",
        )
    
    # st.subheader("Vista previa de datos crudos (DataFrame)")
    # st.write(result["df"].head())
