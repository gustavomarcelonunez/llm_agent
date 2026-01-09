import streamlit as st
from pipeline import run_pipeline

st.title("LLM Agent - Biodiversidad Marina")

scientific_name = st.text_input("Nombre científico", placeholder="Ej: Odontesthes smitti")

# Parámetros opcionales (para no tocar código cada vez)
with st.expander("Parámetros"):
    limit_per_dataset = st.number_input("Límite por dataset", 1, 5000, 200)
    sample_size = st.number_input("Sample size", 1, 1000, 10)
    max_workers = st.number_input("Max workers", 1, 64, 8)

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

    st.subheader("Descargar reporte completo (TXT)")
    with open(result["txt_path"], "rb") as f:
        st.download_button(
            label="Descargar TXT",
            data=f,
            file_name=f"{result['scientific_name'].replace(' ', '_')}_report.txt",
            mime="text/plain",
        )
