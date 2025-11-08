from api_search.obis_api import obis_search
from api_search.worms_api import worms_search
from aws_search.obis_duckdb import search_obis_species_parallel

from agents.reasoning_agent import summarize_obis_data


if __name__ == "__main__":
    scientific_name = input("Ingrese nombre científico: ")
    
    print("\n🔎 Buscando datasets en OBIS...\n")
    datasets = obis_search(scientific_name)
    
    # print("\n🔎 Verificando taxon en WoRMS...\n")
    # taxon_info = worms_search(scientific_name)    

    print("\n🔎 Obteniendo ocurrencias desde el bucket s3 de OBIS...\n")
    
    # Acá se podría consultar por todo el dataset o sólo las ocurrencias de la especie seleccionada.
    # Pensar en agregar filtros: por país, por especie, por fecha, etc.


    # df = filter_species_from_datasets(datasets, scientific_name)
    

    df = search_obis_species_parallel(
        dataset_ids=datasets,  # tu lista de 47 IDs
        species_name=scientific_name,
        limit_per_dataset=200,
        sample_size=15,   # usa 15 datasets (ajustable)
        max_workers=8     # 8 consultas paralelas
    )

    print(df.head())
    # print("\n----- RESULTADO FINAL -----\n")
    # print("🧠 Pensando...\n")
    # result = summarize_obis_data(scientific_name, occurrences, taxon_info)
    # print(result)