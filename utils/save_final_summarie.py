import os

def append_global_summary_to_file(file_path: str, global_summary: str):
    """
    Agrega el resumen final (razonamiento global) al final del archivo de resultados.
    """
    if not global_summary:
        print("⚠️ No se proporcionó resumen global para agregar.")
        return

    if not os.path.exists(file_path):
        print(f"❌ El archivo {file_path} no existe.")
        return

    with open(file_path, "a", encoding="utf-8") as f:
        f.write("\n")
        f.write("🧠 Análisis global y razonamiento final\n")
        f.write("=" * 100 + "\n\n")
        f.write(global_summary.strip() + "\n")

    print(f"✅ Razonamiento final agregado al archivo existente: {file_path}")
