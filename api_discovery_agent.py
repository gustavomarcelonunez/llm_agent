# api_discovery_agent.py
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def discover_api(url):
    """
    Agente que analiza un dominio web y determina si el sitio tiene una API pública disponible.
    Si la tiene, devuelve la URL base y el tipo (REST, GraphQL, SPARQL, etc.).
    Si no, sugiere usar scraping.
    """
    prompt = f"""
    Analiza información online sobre el sitio {url}.
    Tu tarea es determinar si el sitio ofrece una API pública (REST, GraphQL, SPARQL, etc.).
    Si la tiene, devuelve un JSON con el formato:
    {{
      "tiene_api": true,
      "url_api": "https://ejemplo.org/api/...",
      "tipo": "REST",
      "descripcion": "qué tipo de datos ofrece"
    }}
    Si no tiene una API pública, devuelve:
    {{
      "tiene_api": false,
      "descripcion": "No se encontró documentación de API pública. Se puede usar scraping básico."
    }}
    Devuelve solo el JSON, sin texto adicional.
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Eres un agente experto en detección de APIs web. Devuelves solo JSON estructurado válido."},
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content.strip()
