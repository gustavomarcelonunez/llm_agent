import os

def append_global_summary_to_file(file_path: str, global_summary: str):
    """
    Agrega el resumen final (razonamiento global) al final del archivo de resultados.
    """
    if not global_summary:
        print("⚠️ No global summary was provided for addition.")
        return

    if not os.path.exists(file_path):
        print(f"❌ File {file_path} does not exist.")
        return

    with open(file_path, "a", encoding="utf-8") as f:
        f.write("\n")
        f.write("🧠 Global analysis and final reasoning\n")
        f.write("=" * 100 + "\n\n")
        f.write(global_summary.strip() + "\n")

    print(f"✅ Final reasoning added to the existing file: {file_path}")
