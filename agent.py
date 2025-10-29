from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")


client = OpenAI(api_key=api_key)

def suggestion_agent(tema):
    prompt1 = f"Con el siguiente tema {tema}, sugiere al usuario una lista de cinco sitios web para buscar información sobre eso. Debes asegurarte que las páginas existan, y que se puedan acceder y que contengan la información solicitada."
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Eres un asistente que sugiere sitios web para buscar información relacionada al tema. Solo devuelve una lista de URLs"},
            {"role": "user", "content": prompt1}
        ]
    )
    return response.choices[0].message.content

def parsing_agent(sugerencia):
    prompt1 = f"Convierte la siguiente cadena {sugerencia}, en un dict para python."
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": ("Recibirás un texto que representa una estructura de datos en formato string. "
                                           "Tu tarea es convertir ese string a un diccionario de Python con sintaxis correcta. "
                                           "Usa comillas simples para las claves y los valores string. Las claves son siempre strings numéricas o de texto. "
                                           "Los valores pueden ser strings, números o listas. Entrega solo el diccionario en formato Python sin explicaciones ni texto adicional. "
                                           "Formatea el resultado para que pueda ser usado directamente por ast.literal_eval() en Python.")},
            {"role": "user", "content": prompt1}
        ]
    )
    return response.choices[0].message.content

def agente(prompt):
    # Llamada al modelo de OpenAI
    response = client.chat.completions.create(model="gpt-4o-mini",  # o "gpt-4o" si tenés acceso
    messages=[
        {"role": "system", "content": "Eres un asistente que puede buscar en Wikipedia."}, #este es un rol, determina el comportamiento del modelo
        {"role": "user", "content": prompt}
    ])
    return response.choices[0].message.content
