from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def summarize_obis_data(species_name, obis_data, worms_data):
    """
    Usa el LLM para analizar los registros y generar un resumen interpretativo.
    Combina datos de OBIS (ocurrencias) y WoRMS (verificación taxonómica).
    """
    # Preparamos una muestra resumida
    sample = []
    for r in obis_data:  # limita a 50 para no pasar demasiado texto
        sample.append({
            "country": r.get("country", "Desconocido"),
            "lat": r.get("decimalLatitude", "?"),
            "lon": r.get("decimalLongitude", "?"),
            "date": r.get("eventDate", "N/A"),
            "sst": r.get("sst"),
            "sss": r.get("sss"),
            "bathymetry": r.get("bathymetry"),
        })

    # Integramos información taxonómica de WoRMS
    worms_summary = (
        f"Nombre válido según WoRMS: {worms_data.get('valid_name', 'Desconocido')} "
        f"({worms_data.get('authority', 'sin autoridad')}). "
        f"Estado taxonómico: {worms_data.get('taxon_status', 'Desconocido')}. "
        f"Familia: {worms_data.get('family', 'N/A')}, "
        f"Género: {worms_data.get('genus', 'N/A')}. "
    )

    synonyms = worms_data.get("synonyms", [])
    if synonyms:
        worms_summary += f"Sinónimos registrados: {', '.join(synonyms[:5])}."

    prompt = f"""
        Eres un oceanógrafo y taxónomo marino.
        Se te proporcionan dos fuentes de información sobre la especie {species_name}:

        Información taxonómica (WoRMS):
        {worms_summary}

        Registros biogeográficos (OBIS):
        {sample}

        Tu tarea:
        - Resume los patrones geográficos y ambientales más destacados (países, SST, SSS, profundidad).
        - Menciona toda información relevante acerca de su taxonomía.
        - Comenta si los registros son coherentes con la distribución esperada según WoRMS.
        - Indica si hay posibles errores o inconsistencias.
        - Redacta en español, en no más de 20 líneas, con tono científico pero claro.
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "Eres un oceanógrafo experto en análisis biogeográficos marinos y validación taxonómica. "
                    "Comenta con precisión científica y estilo analítico."
                ),
            },
            {"role": "user", "content": prompt},
        ],
    )

    return response.choices[0].message.content
