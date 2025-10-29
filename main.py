import ast

from agent import suggestion_agent, parsing_agent
from web_search import search_in


if __name__ == "__main__":
    thread = input("Escribí el tema que querés buscar: \n")
    suggestion = suggestion_agent(thread)
    print("----- SUGERENCIA DEL AGENTE -----")
    print(suggestion)

    option = input("Seleccione un número del 1 al 5 para obtener la URL: ")

    urls_dict = parsing_agent(suggestion)
    
    selected_url = ast.literal_eval(urls_dict)[option]
    resume = search_in(selected_url)
    print(resume)





    # resumen_wiki = buscar_wikipedia(tema)

    #prompt = f"Con la siguiente información de Wikipedia, haz un resumen breve:\n{resumen_wiki}"
    # resultado = agente(prompt)

    # print("----- RESULTADO DEL AGENTE -----")
    # print(resultado)

