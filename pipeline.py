
import time

from api_search.obis_api import obis_search
from api_search.worms_api import worms_search
from aws_search.obis_duckdb import search_obis_species_parallel

from utils.meow_ecoregions import assign_meow_ecoregion
from utils.save_regional_summaries import save_regional_summaries
from utils.save_final_summarie import append_global_summary_to_file

from agents.regional_agent_runner import run_regional_agents
from agents.reasoning_agent import summarize_obis_data
from agents.summarizer_agent import summarize_with_llm


PIPELINE_STAGES = [
    "Checking taxon in WoRMS...",
    "Searching for datasets in OBIS...",
    "Retrieving occurrences from S3 (OBIS)...",
    "Assigning MEOW ecoregions...",
    "Generating summaries by ecoregion (LLM agents)...",
    "Saving regional summary to TXT...",
    "Generating a global summary...",
]


def run_pipeline(
    scientific_name: str,
    limit_per_dataset: int = 200,
    sample_size: int = 15,
    progress_cb=None,
) -> dict:
    """
    Ejecuta el pipeline completo y devuelve información estructurada.

    progress_cb recibe eventos con:
    - stage: nombre de la etapa
    - status: running, complete o error
    - duration: duración en segundos, cuando corresponde
    """

    def emit_progress(stage, status, duration=None):
        if progress_cb:
            event = {
                "stage": stage,
                "status": status,
            }

            if duration is not None:
                event["duration"] = round(duration, 2)

            progress_cb(event)

    def run_stage(stage, function):
        emit_progress(stage, "running")
        start_time = time.perf_counter()

        try:
            result = function()
        except Exception:
            duration = time.perf_counter() - start_time
            emit_progress(stage, "error", duration)
            raise

        duration = time.perf_counter() - start_time
        emit_progress(stage, "complete", duration)

        return result

    # Conservamos la configuración actual de concurrencia.
    max_workers = 3

    # 1. Validación del taxón en WoRMS.
    worms_stage = PIPELINE_STAGES[0]
    taxon_info = run_stage(
        worms_stage,
        lambda: worms_search(scientific_name),
    )

    if taxon_info.get("status") != "ok":
        # WoRMS respondió, pero no pudo validar el taxón.
        emit_progress(worms_stage, "error")

        return {
            "status": "error",
            "stage": "worms",
            "message": taxon_info.get(
                "message",
                "Error desconocido en WoRMS.",
            ),
            "taxon_info": taxon_info,
        }

    taxon_id = taxon_info["aphia_id"]

    # 2. Búsqueda de datasets en OBIS.
    datasets = run_stage(
        PIPELINE_STAGES[1],
        lambda: obis_search(taxon_id),
    )

    # 3. Recuperación de ocurrencias desde S3.
    df = run_stage(
        PIPELINE_STAGES[2],
        lambda: search_obis_species_parallel(
            dataset_ids=datasets,
            aphia_id=taxon_id,
            limit_per_dataset=limit_per_dataset,
            sample_size=sample_size,
            max_workers=max_workers,
        ),
    )

    # 4. Asignación de ecorregiones MEOW.
    df_with_ecoregion = run_stage(
        PIPELINE_STAGES[3],
        lambda: assign_meow_ecoregion(df),
    )

    # 5. Generación de resúmenes regionales.
    resume = run_stage(
        PIPELINE_STAGES[4],
        lambda: run_regional_agents(
            df_with_ecoregion,
            scientific_name,
            summarize_with_llm,
            max_workers=max_workers,
        ),
    )

    # 6. Guardado del resumen regional.
    txt_path = run_stage(
        PIPELINE_STAGES[5],
        lambda: save_regional_summaries(
            resume,
            scientific_name,
            taxon_info,
        ),
    )

    # 7. Generación y guardado del resumen global.
    def generate_global_summary():
        with open(txt_path, "r", encoding="utf-8") as file:
            resumed_info = file.read()

        global_summary = summarize_obis_data(
            scientific_name,
            resumed_info,
        )

        append_global_summary_to_file(
            txt_path,
            global_summary,
        )

        return global_summary

    global_summary = run_stage(
        PIPELINE_STAGES[6],
        generate_global_summary,
    )

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
