from api_search import search_obis
from reasoning_agent import summarize_obis_data

def mostrar_resultados(lista):

    print("----- SUGERENCIA DEL AGENTE -----")

    print("\n🌊 Portales sugeridos:\n")
    for i, item in enumerate(lista, start=1):
        print(f" {i}. {item['nombre']}")
        print(f"    🌐 URL: {item['url']}")
        print(f"    📘 Descripción: {item['descripcion']}\n")


if __name__ == "__main__":
    topic = input("Tema de búsqueda: ")

    occurrences = search_obis(topic)
    # opcion = int(input("👉 Elegí el número del portal: ")) - 1
    

    # print(f"\n🔎 Analizando el portal {nombre} para descubrir si tiene API...")
    # resultado = search_in(url)

    print("\n----- RESULTADO FINAL -----\n")
    result = summarize_obis_data(occurrences, topic)
    print(result)