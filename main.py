from api_search.obis_api_search import obis_search
from verify_taxon_worms import verify_taxon_worms

from agents.reasoning_agent import summarize_obis_data


if __name__ == "__main__":
    specie_name = input("Tema de búsqueda: ")
    
    print("\n🔎 Buscando en OBIS...\n")
    occurrences = obis_search(specie_name)
    
    print("\n🔎 Verificando taxon en WoRMS...\n")
    taxon_info = verify_taxon_worms(specie_name)    

    
    print("\n----- RESULTADO FINAL -----\n")
    print("🧠 Pensando...\n")
    result = summarize_obis_data(specie_name, occurrences, taxon_info)
    print(result)