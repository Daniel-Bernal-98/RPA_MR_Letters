import os
import pandas as pd

REQUIRED_COLUMNS = ["patient_name", "collector"]


def normalizar_texto(texto):
    return str(texto).strip().upper().replace(" ", "_")


def load_assignments(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    ext = os.path.splitext(file_path)[1].lower()

    # Lectura robusta del archivo
    if ext == ".csv":
        df = pd.read_csv(
            file_path,
            encoding="utf-8-sig",   # elimina BOM
            sep=None,               # autodetecta separador (, ; etc)
            engine="python"
        )
    elif ext in (".xlsx", ".xls"):
        df = pd.read_excel(file_path)
    else:
        raise ValueError("Unsupported file format")

    # Limpiar filas inválidas
    df = df.dropna(subset=REQUIRED_COLUMNS)

    # Normalizar contenido
    df["patient_name"] = df["patient_name"].apply(normalizar_texto)
    df["collector"] = df["collector"].apply(normalizar_texto)

    return df.to_dict(orient="records")


def build_lookup(records):
    lookup = {}

    for r in records:
        key = r["patient_name"]
        lookup[key] = r["collector"]

    return lookup