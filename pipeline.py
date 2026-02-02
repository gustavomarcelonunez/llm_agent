# pipeline.py
from api_search.obis_api import obis_search
from api_search.worms_api import worms_search
from aws_search.obis_duckdb import search_obis_species_parallel

from utils.meow_ecoregions import assign_meow_ecoregion
from utils.save_regional_summaries import save_regional_summaries
from utils.save_final_summarie import append_global_summary_to_file
from utils.get_optimal_workers import get_optimal_workers

from agents.regional_agent_runner import run_regional_agents
from agents.reasoning_agent import summarize_obis_data
from agents.summarizer_agent import summarize_with_llm


def run_pipeline(
    scientific_name: str,
    limit_per_dataset: int = 200,
    sample_size: int = 15,
    progress_cb=None,   # callback opcional para streamlit (mensajes)
) -> dict:
    """
    Ejecuta el pipeline completo y devuelve info estructurada.
    progress_cb: función opcional progress_cb(str) para reportar progreso.
    """
    def log(msg: str):
        if progress_cb:
            progress_cb(msg)

    # Establece la cantidad de hilos de ejecución
    max_workers = get_optimal_workers()

    log("Verificando taxón en WoRMS...")
    taxon_info = worms_search(scientific_name)
    if taxon_info.get("status") != "ok":
        return {
            "status": "error",
            "stage": "worms",
            "message": taxon_info.get("message", "Error desconocido en WoRMS."),
            "taxon_info": taxon_info
        }
 
    taxon_id = taxon_info["aphia_id"]

    log("Buscando datasets en OBIS...")
    datasets = obis_search(taxon_id)

    log("Obteniendo ocurrencias desde S3 (OBIS)...")
    df = search_obis_species_parallel(
        dataset_ids=datasets,
        aphia_id=taxon_id,
        limit_per_dataset=limit_per_dataset,
        sample_size=sample_size,
        max_workers=max_workers,
    )

    log("Asignando ecorregiones MEOW...")
    df_with_ecoregion = assign_meow_ecoregion(df)

    log("Generando resúmenes por ecorregión (LLM agents)...")
    resume = run_regional_agents(
        df_with_ecoregion,
        scientific_name,
        summarize_with_llm,
        max_workers=max_workers,
    )

    log("Guardando resumen regional en TXT...")
    txt_path = save_regional_summaries(resume, scientific_name, taxon_info)

    log("Generando resumen global...")

    with open(txt_path, "r", encoding="utf-8") as f:
        resumed_info = f.read()

    global_summary = summarize_obis_data(scientific_name, resumed_info)
    append_global_summary_to_file(txt_path, global_summary)

    return {
        "scientific_name": scientific_name,
        "taxon_info": taxon_info,
        "taxon_id": taxon_id,
        "datasets_count": len(datasets) if datasets is not None else 0,
        "occurrences_count": int(len(df)) if df is not None else 0,
        "txt_path": txt_path,
        "global_summary": global_summary,
        "df": df_with_ecoregion,
    }
