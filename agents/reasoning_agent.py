from openai import OpenAI
import os
import streamlit as st
from dotenv import load_dotenv


# Cargar la API key desde el entorno
client = OpenAI(
    api_key=st.secrets["OPENAI_API_KEY"],
)

# Descomentar para uso local
# api_key = (
#     st.secrets.get("OPENAI_API_KEY", None)
#     or os.getenv("OPENAI_API_KEY")
# )

# load_dotenv()
# client = OpenAI(api_key)

def summarize_obis_data(species_name, resumed_info):
    """
    Usa el LLM para analizar los registros y generar un resumen interpretativo.
    Combina datos de OBIS (ocurrencias) y WoRMS (verificación taxonómica).
    """

    prompt = f"""
        Eres un oceanógrafo y taxónomo marino.
        Se te proporcionan un archivo de texto con información sobre la especie {species_name}:

        Registros biogeográficos (OBIS + WoRMS):
        {resumed_info}

        Tu tarea:
        - Resume los patrones geográficos y ambientales más destacados.
        - Si es necesario, da información acerca de cada ecoregión mencionada en el archivo.
        - Menciona toda información relevante acerca de su taxonomía.
        - Indica si hay posibles errores o inconsistencias.
        - Redacta siempre en inglés, con tono científico pero claro.
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "Eres un oceanógrafo experto en análisis biogeográficos marinos y validación taxonómica. "
                    "Comenta siempre en inglés, con precisión científica y estilo analítico."
                ),
            },
            {"role": "user", "content": prompt},
        ],
    )

    return response.choices[0].message.content
