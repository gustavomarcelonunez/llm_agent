import pandas as pd
import json
from textwrap import shorten
from openai import OpenAI

client = OpenAI()

# ==============================
# 🔹 Función principal
# ==============================

def summarize_with_llm(species_name: str, region_name: str, df_region: pd.DataFrame) -> str:
    """
    Genera un resumen interpretativo de los datos de una ecoregión usando un LLM.

    Parámetros
    ----------
    species_name : str
        Nombre científico de la especie (contexto biológico).
    region_name : str
        Nombre de la ecoregión (según MEOW u otro sistema).
    df_region : pd.DataFrame
        Subconjunto de datos de esa ecoregión.

    Retorna
    -------
    str
        Resumen textual generado por el modelo.
    """

    # ==============================
    # 🔹 Preprocesamiento
    # ==============================
    if len(df_region) == 0:
        return f"No hay registros para {species_name} en {region_name}."

    sample = df_region
    cols = ["eventDate", "decimalLatitude", "decimalLongitude", "basisOfRecord"]
    sample = sample[cols].fillna("Unknown")

    # Convertimos a JSON comprimido
    data_json = sample.to_json(orient="records", force_ascii=False)
    # data_json = shorten(data_json, width=5000, placeholder="...")  # corta por seguridad

    # ==============================
    # 🔹 Prompt
    # ==============================
    system_prompt = (
        "Eres un oceanógrafo especializado en distribución de especies marinas. "
        "Tu tarea es analizar registros de ocurrencias de una especie en una ecoregión, "
        "identificando patrones geográficos, temporales y de esfuerzo de muestreo. "
        "Sé conciso y preciso, usando un lenguaje técnico claro."
    )

    user_prompt = f"""
Analiza los siguientes datos de ocurrencias de **{species_name}** en la ecoregión **{region_name}**.

Registros (muestra): 
{data_json}

Por favor, entrega un resumen estructurado en idioma inglés con los siguientes puntos:
1. Rango geográfico (latitud y longitud aproximada).
2. Distribución temporal (años o períodos predominantes).
3. Tipo de registro más común (por ejemplo, 'HumanObservation', 'PreservedSpecimen', etc.).
5. Cualquier observación sobre calidad o completitud de datos (por ejemplo, registros sin coordenadas).
6. Una breve interpretación ecológica o biogeográfica (máx. 3 frases).
"""

    # ==============================
    # 🔹 Llamada al modelo
    # ==============================
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ]
        )
        summary = response.choices[0].message.content.strip()

    except Exception as e:
        summary = f"⚠️ Error en análisis de {region_name}: {e}"

    return summary
