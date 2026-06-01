# ============================================================================
# MR Letters Generator
#
# Copyright (c) 2026 ABA Centers of America
# All Rights Reserved.
#
# Proprietary and Confidential.
# For internal use only.
#
# Unauthorized copying, distribution, modification, or disclosure
# of this software is strictly prohibited.
# ============================================================================

import os
from datetime import datetime, timedelta, date
from concurrent.futures import ProcessPoolExecutor, as_completed

from rapidfuzz import process, fuzz

from core.extractor import extract_data_with_payer, extract_issue_date
from core.file_manager import save_file
from core.data_loader import load_assignments, build_lookup

# Configuration for old letter detection
OLD_FOLDER_NAME = "Year_Older_Letters"
OLD_DAYS_THRESHOLD = 365  # 1 YEAR

def find_best_match(patient, lookup_keys, threshold = 90):
    #Find best matching patient name

    if patient == "UNKNOWN":
        return None
    
    # Exact match first
    if patient in lookup_keys:
        print(f"Exact Match: {patient}")
        return patient
    
    # Fuzzy falback
    match = process.extractOne(
        patient,
        lookup_keys,
        scorer = fuzz.ratio
    )

    if match:
        name, score, _ = match
        print(f"Comparing: {patient} --> {name} ({score})")

        if score >= threshold:
            return name
        
    return None

# def find_best_match(patient, lookup_keys, threshold=90):
#     """Find best matching patient name in lookup dictionary using fuzzy matching."""
#     if patient == "UNKNOWN":
#         return None

#     match = process.extractOne(
#         patient,
#         lookup_keys,
#         scorer=fuzz.ratio
#     )

#     if match:
#         name, score, _ = match

#         print(f"Comparando: {patient} → {name} ({score})")

#         if score >= threshold:
#             return name

#     return None

def normalize_variants(patient):
    """
    Generate normalized variants for matching.
    Supports:
        FIRST LAST
        FIRST_LAST
        LAST_FIRST
    """

    if not patient or patient == "UNKNOWN":
        return []
    # Normalize spaces & underscores
    patient = patient.upper().strip()

    # Convert multiple spaces
    patient = " ".join(patient.split())

    variants =set()

    # Original version with spaces
    variants.add(patient)

    # Underscores version
    underscored = patient.replace(" ", "-")
    variants.add(underscored)

    # Divide using spaces or underscore
    if "_" in underscored:
        parts = underscored.split("_")
    else:
        parts = patient.split()

    # Invertir FIRST_LAST -> LAST_FIRST
    if len(parts) >= 2:
        first = parts[0]
        last = parts [-1]

        variants.add(f"{last}_{first}")
    return list(variants)

# def normalize_variants(patient):
#     """Generate name variants for fuzzy matching (e.g., FIRST_LAST and LAST_FIRST)."""
#     parts = patient.split("_")

#     if len(parts) == 2:
#         return [
#             patient,
#             f"{parts[1]}_{parts[0]}"
#         ]

#     return [patient]


def process_single(file, input_folder, lookup, output_folder, payer='default'):
    """
    Process a single PDF file with payer-specific extraction and old letter detection.
    
    Args:
        file: Filename of the PDF
        input_folder: Path to input folder
        lookup: Dictionary mapping patient names to collectors
        output_folder: Path to output folder
        payer: Payer identifier for format-specific extraction
    
    Returns:
        Dictionary with processing results
    """
    try:
        path = os.path.join(input_folder, file)

        # Extract patient and DOS using payer-specific config
        patient, dos = extract_data_with_payer(path, payer=payer)

        # Extract issue date for old letter detection
        issue_date = extract_issue_date(path, payer=payer)

        # Check if letter is older than threshold
        is_old = False
        if issue_date:
            cutoff = date.today() - timedelta(days=OLD_DAYS_THRESHOLD)
            is_old = issue_date < cutoff

        if is_old:
            # Route to old letters folder
            collector = OLD_FOLDER_NAME

            # Still try to find clean patient name from CSV for consistency
            variants = normalize_variants(patient)
            match = None
            clean_patient = patient

            for variant in variants:
                match = find_best_match(variant, lookup.keys())
                if match:
                    clean_patient = match
                    break

            save_file(path, clean_patient, dos, collector, output_folder)

            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            return {
                "archivo": file,
                "patient": patient,
                "dos": dos,
                "collector": collector,
                "payer": payer,
                "fecha": now,
                "issue_date": issue_date.strftime("%Y-%m-%d") if issue_date else None,
                "is_old": True,
            }

        # Normal processing for recent letters
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
            clean_patient = match  # Use clean name from CSV
        else:
            collector = "UNASSIGNED"
            clean_patient = final_patient  # Fallback to extracted OCR name

        save_file(path, clean_patient, dos, collector, output_folder)

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        return {
            "archivo": file,
            "patient": final_patient,
            "dos": dos,
            "collector": collector,
            "payer": payer,
            "fecha": now,
            "issue_date": issue_date.strftime("%Y-%m-%d") if issue_date else None,
            "is_old": False,
        }

    except Exception as e:
        print(f"Error processing {file} with payer {payer}: {e}")
        return {
            "archivo": file,
            "patient": "ERROR",
            "dos": "00-00-0000",
            "collector": "ERROR",
            "payer": payer,
            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "issue_date": None,
            "is_old": False,
            "error": str(e)
        }


def process_folder(input_folder, csv_path, output_folder, payer='default', log_callback=None):
    """
    Process all PDFs in a folder with payer-specific extraction and old letter detection.
    
    Args:
        input_folder: Path to folder containing PDFs
        csv_path: Path to CSV file with patient-collector assignments
        output_folder: Path to output folder for organized PDFs
        payer: Payer identifier for format-specific extraction
        log_callback: Optional callback function for logging progress
    
    Returns:
        List of processing results
    """
    print(f"\n{'='*70}")
    print(f"Processing folder: {input_folder}")
    print(f"Payer format: {payer}")
    print(f"Old letter threshold: {OLD_DAYS_THRESHOLD} days")
    print(f"{'='*70}\n")

    records = load_assignments(csv_path)
    lookup = build_lookup(records)

    files = [f for f in os.listdir(input_folder) if f.lower().endswith(".pdf")]

    if not files:
        raise ValueError(f"No PDF files found in {input_folder}")

    print(f"Found {len(files)} PDF files to process\n")

    results = []

    max_workers = min(4, os.cpu_count() or 1)

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(process_single, file, input_folder, lookup, output_folder, payer)
            for file in files
        ]

        for future in as_completed(futures):
            result = future.result()
            results.append(result)

            if log_callback:
                is_old_marker = "🕐 OLD" if result.get("is_old") else ""
                status = "✔" if result['collector'] != "ERROR" else "❌"
                log_callback(
                    f"{status} {result['archivo']} → {result['patient']} ({result['collector']}) {is_old_marker}"
                )

    return results