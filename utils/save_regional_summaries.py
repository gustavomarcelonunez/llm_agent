import os
import json

def save_regional_summaries(
        results: dict,
        species_name: str,
        worms_info: str = None,
        output_dir: str = "outputs") -> str:
    """
    Guarda los resúmenes regionales y la información de WoRMS en un archivo .txt.

    Parámetros
    ----------
    results : dict
        Diccionario {ecoregión: resumen generado}.
    species_name : str
        Nombre de la especie (para nombrar el archivo).
    worms_info : str, opcional
        Texto con la información de WoRMS (taxonomía, sinónimos, status, etc).
    output_dir : str, opcional
        Carpeta donde guardar los resultados (por defecto 'outputs').

    Retorna
    -------
    str
        Ruta completa del archivo guardado.
    """
    os.makedirs(output_dir, exist_ok=True)
    safe_name = species_name.replace(" ", "_").lower()
    output_path = os.path.join(output_dir, f"{safe_name}_summarie.txt")

    with open(output_path, "w", encoding="utf-8") as f:
        # Encabezado
        f.write(f"📄 Integrated report for {species_name}\n")
        f.write("=" * 90 + "\n\n")

        # Sección WoRMS (si está disponible)
        if worms_info:
            f.write("🔬 Taxonomic information (WoRMS)\n")
            f.write("-" * 90 + "\n")
            f.write(json.dumps(worms_info, ensure_ascii=False, indent=2) + "\n\n")

        # Sección de resúmenes regionales
        f.write("🌎 Regional summaries (OBIS)\n")
        f.write("=" * 90 + "\n\n")

        for region, summary in results.items():
            f.write(f"🗺️ {region}\n")
            f.write("-" * 90 + "\n")
            f.write(summary.strip() + "\n\n")

    print(f"✅ Combined file saved in: {output_path}")
    return output_path
