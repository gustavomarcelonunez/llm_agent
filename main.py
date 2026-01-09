from api_search.obis_api import obis_search
from api_search.worms_api import worms_search
from aws_search.obis_duckdb import search_obis_species_parallel

from utils.meow_ecoregions import assign_meow_ecoregion
from utils.save_regional_summaries import save_regional_summaries
from utils.save_final_summarie import append_global_summary_to_file

from agents.regional_agent_runner import run_regional_agents
from agents.reasoning_agent import summarize_obis_data
from agents.summarizer_agent import summarize_with_llm

LIMIT_PER_DATASET=200
SAMPLE=10
MAXWORKERS = 8

if __name__ == "__main__":

    scientific_name = input("Ingrese nombre científico: ")

    print("\n🔎 Verificando taxon en WoRMS...\n")
    taxon_info = worms_search(scientific_name)

    taxon_id = taxon_info["aphia_id"]
    
    print("\n🔎 Buscando datasets en OBIS...\n")
    datasets = obis_search(taxon_id)
    
    print("\n🔎 Obteniendo ocurrencias desde el bucket s3 de OBIS...\n")
    
    df = search_obis_species_parallel(
        dataset_ids=datasets,
        aphia_id=taxon_id,
        limit_per_dataset=LIMIT_PER_DATASET,
        sample_size=SAMPLE,
        max_workers=MAXWORKERS
    )

    # Modifica el DF y agrega una ecoregión, según coordenadas
    df_with_ecoregion = assign_meow_ecoregion(df)

    # Genera un resumen para cada ecoregión
    resume = run_regional_agents(
        df_with_ecoregion,
        scientific_name,
        summarize_with_llm,
        max_workers=MAXWORKERS
    )
    
    txt_path = save_regional_summaries(
        resume,
        scientific_name,
        taxon_info)


    print("\n----- RESULTADO FINAL -----\n")
    print("🧠 Pensando...\n")


    result = summarize_obis_data(scientific_name, txt_path)
    append_global_summary_to_file(txt_path, result)

    print(result)