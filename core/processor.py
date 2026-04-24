import os
from datetime import datetime
from concurrent.futures import ProcessPoolExecutor, as_completed

from rapidfuzz import process, fuzz

from core.extractor import extract_data
from core.file_manager import save_file
from core.data_loader import load_assignments, build_lookup


def find_best_match(patient, lookup_keys, threshold=65):
    if patient == "UNKNOWN":
        return None

    match = process.extractOne(
        patient,
        lookup_keys,
        scorer=fuzz.ratio
    )

    if match:
        name, score, _ = match

        print(f"Comparando: {patient} → {name} ({score})")

        if score >= threshold:
            return name

    return None


def normalize_variants(patient):
    parts = patient.split("_")

    if len(parts) == 2:
        return [
            patient,
            f"{parts[1]}_{parts[0]}"
        ]

    return [patient]


def process_single(file, input_folder, lookup, output_folder):
    try:
        path = os.path.join(input_folder, file)

        patient, dos = extract_data(path)

        # Probar variantes de nombre
        variants = normalize_variants(patient)

        match = None
        final_patient = patient

        for variant in variants:
            match = find_best_match(variant, lookup.keys())
            if match:
                final_patient = variant
                break

        if match:
            collector = lookup[match]
            clean_patient = match  # usar nombre limpio del CSV
        else:
            collector = "UNASSIGNED"
            clean_patient = final_patient  # fallback al OCR

        save_file(path, clean_patient, dos, collector, output_folder)

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        return {
            "archivo": file,
            "patient": final_patient,
            "dos": dos,
            "collector": collector,
            "fecha": now
        }

    except Exception as e:
        return {
            "archivo": file,
            "patient": "ERROR",
            "dos": "00-00-0000",
            "collector": "ERROR",
            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "error": str(e)
        }


def process_folder(input_folder, csv_path, output_folder, log_callback=None):
    records = load_assignments(csv_path)
    lookup = build_lookup(records)

    files = [f for f in os.listdir(input_folder) if f.lower().endswith(".pdf")]

    results = []

    max_workers = min(4, os.cpu_count() or 1)

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(process_single, file, input_folder, lookup, output_folder)
            for file in files
        ]

        for future in as_completed(futures):
            result = future.result()
            results.append(result)

            if log_callback:
                log_callback(f"Procesado: {result['archivo']} → {result['collector']}")

    return results