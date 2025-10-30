import json

from semantic_agent import semantic_query
from api_discovery_agent import discover_api
from web_validation import url_funciona
from web_search import search_in

def mostrar_resultados(lista):

    print("----- SUGERENCIA DEL AGENTE -----")

    print("\n🌊 Portales sugeridos:\n")
    for i, item in enumerate(lista, start=1):
        print(f" {i}. {item['nombre']}")
        print(f"    🌐 URL: {item['url']}")
        print(f"    📘 Descripción: {item['descripcion']}\n")


if __name__ == "__main__":
    topic = input("Tema de búsqueda: ")
    semantic_results = semantic_query(topic)
    mostrar_resultados(semantic_results)

    opcion = int(input("👉 Elegí el número del portal: ")) - 1
    portal = semantic_results[opcion]

   

    nombre, url = portal["nombre"], portal["url"]


    print("Analizando sitio web...")

    if url_funciona(portal["url"]):

        print(f"\n🔎 Analizando el portal {nombre} para descubrir si tiene API...")
        api_info = discover_api(url)
        print(api_info)
    
        try:
            api_info = json.loads(api_info)
        except:
            print("⚠️ No se pudo interpretar la respuesta del agente. Se usará scraping.")
            resultado = search_in(url)
        else:
            if api_info.get("tiene_api"):
                print(f"🌐 API detectada ({api_info['tipo']}): {api_info['url_api']}")
                # Ejemplo: si reconoce OBIS
        #        if "obis" in api_info["url_api"].lower():
        #            resultado = search_obis(topic)
        #        else:
        #            resultado = f"El portal tiene API, pero no hay conector implementado aún. {api_info}"
            else:
                print("⚠️ No se detectó API pública. Usando scraping...")
                resultado = search_in(url)

        print("\n----- RESULTADO FINAL -----\n")
        print(resultado)

    else:
        print(f"❌ El sitio {url} no está disponible. Elegí otro portal.")
        exit()


