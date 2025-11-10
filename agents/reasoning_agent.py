from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def summarize_obis_data(species_name, resumed_info):
    """
    Usa el LLM para analizar los registros y generar un resumen interpretativo.
    Combina datos de OBIS (ocurrencias) y WoRMS (verificación taxonómica).
    """

    prompt = f"""
        Eres un oceanógrafo y taxónomo marino.
        Se te proporcionan dos fuentes de información sobre la especie {species_name}:

        Registros biogeográficos (OBIS + WoRMS):
        {resumed_info}

        Tu tarea:
        - Resume los patrones geográficos y ambientales más destacados (países, SST, SSS, profundidad).
        - Si es necesario, da información acerca de cada ecoregiṕn mencionada en el archivo.
        - Menciona toda información relevante acerca de su taxonomía.
        - Comenta si los registros son coherentes con la distribución esperada según WoRMS.
        - Indica si hay posibles errores o inconsistencias.
        - Redacta en español, con tono científico pero claro.
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
