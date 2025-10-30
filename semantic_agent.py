from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=api_key)

import json

def semantic_query(thread):
    prompt = f"""
    El usuario busca información sobre {thread}.
    Sugiere al menos tres portales REALES y ACTIVOS donde puede consultar información sobre ese tema.
    Verifica que cada portal tenga una URL accesible (https:// preferentemente).
    Los sitios deben tener información, NO deben devolver status code 404 ni page not found.
    Si no estás seguro de la validez de una URL, reemplázala por otra.

    DEVUELVE **solo** un JSON válido (usa comillas dobles, sin texto adicional), con este formato exacto:
    [
      {{"nombre": "Portal", "url": "URL", "descripcion": "qué tipo de datos ofrece"}}
    ]
    Solo devuelve el JSON, sin texto adicional.
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Eres un asistente experto en datos oceanográficos. Devuelves solo JSON estructurado válido."},
            {"role": "user", "content": prompt}
        ]
    )

    content = response.choices[0].message.content.strip()

    try:
        return json.loads(content)
    except json.JSONDecodeError:
        print("⚠️  Error al parsear JSON, devolviendo texto sin procesar.")
        return content
