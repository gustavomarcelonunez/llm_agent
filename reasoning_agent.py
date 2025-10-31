from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def summarize_obis_data(results, species_name):
    """
    Usa el LLM para analizar los registros y generar un resumen interpretativo.
    """
    # Preparamos una muestra resumida
    sample = []
    for r in results[:50]:  # limita a 50 para no pasar demasiado texto
        sample.append({
            "country": r.get("country", "Desconocido"),
            "lat": r.get("decimalLatitude", "?"),
            "lon": r.get("decimalLongitude", "?"),
            "date": r.get("eventDate", "N/A"),
            "sst": r.get("sst"),
            "sss": r.get("sss"),
            "bathymetry": r.get("bathymetry"),
        })

    prompt = f"""
        Analiza los siguientes registros de OBIS sobre {species_name}.
        Describe los patrones geográficos y ambientales más notables:
        - países o regiones con más observaciones
        - condiciones oceanográficas típicas (SST, salinidad, profundidad)
        - si se observan tendencias temporales

        Datos (muestra de {len(sample)} registros):
        {sample}

        Devuelve un resumen analítico de no más de 10 líneas, en español.
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Eres un oceanógrafo experto en análisis de datos biogeográficos."},
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content
