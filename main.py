from api_search.obis_api import obis_search
from api_search.worms_api import worms_search
from aws_search.obis_duckdb import search_obis_species_parallel
from meow_ecoregions import assign_meow_ecoregion
from agents.regional_agent_runner import run_regional_agents
from utils.save_regional_summaries import save_regional_summaries


from agents.reasoning_agent import summarize_obis_data
from agents.summarizer_agent import summarize_with_llm


if __name__ == "__main__":

    scientific_name = input("Ingrese nombre científico: ")
    
    print("\n🔎 Buscando datasets en OBIS...\n")
    datasets = obis_search(scientific_name)
    
    print("\n🔎 Obteniendo ocurrencias desde el bucket s3 de OBIS...\n")
    
    df = search_obis_species_parallel(
        dataset_ids=datasets,
        species_name=scientific_name,
        limit_per_dataset=200,
        sample_size=20,   # usa 20 datasets (ajustable)
        max_workers=8     # 10 consultas paralelas
    )

    # Modifica el DF y agrega una ecoregión, según coordenadas
    df_with_ecoregion = assign_meow_ecoregion(df)

    # Genera un resumen para cada ecoregión
    resume = run_regional_agents(df_with_ecoregion, scientific_name, summarize_with_llm)
   
    print("\n🔎 Verificando taxon en WoRMS...\n")
    taxon_info = worms_search(scientific_name) 

    txt_path = save_regional_summaries(resume, scientific_name, taxon_info)


    print("\n----- RESULTADO FINAL -----\n")
    print("🧠 Pensando...\n")
    result = summarize_obis_data(scientific_name, txt_path)
    print(result)