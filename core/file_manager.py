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
import shutil
from utils.helpers import sanitize_filename


def save_file(source_path, patient, dos, collector, output_dir):
    """
    Save file to: output_dir / collector / patient_dos.pdf
    
    If file already exists, appends a counter to make it unique:
    - patient_dos.pdf
    - patient_dos_2.pdf
    - patient_dos_3.pdf
    etc.
    """

    try:
        # If no collector -> UNASSIGNED
        collector = collector if collector else "UNASSIGNED"

        collector_dir = os.path.join(output_dir, sanitize_filename(collector))
        os.makedirs(collector_dir, exist_ok=True)

        # Base Filename: patient_dos.pdf
        base_filename = f"{patient}_{dos}.pdf"
        base_filename = sanitize_filename(base_filename)

        destination = os.path.join(collector_dir, base_filename)

        #Check if file exists, if so append counter
        if os.path.exists(destination):
            counter = 2
            name_parts = base_filename.rsplit('.', 1)  # Split filename and extension
            base_name = name_parts[0]
            extension = name_parts[1] if len(name_parts) > 1 else ''

            # Keep increasing the counter until we find a unique filename
            while os.path.exists(destination):
                new_filename = f"{base_name}_{counter}.{extension}"
                destination = os.path.join(collector_dir, new_filename)
                counter += 1

        # Copy file
        shutil.copy2(source_path, destination)

        return f"OK → {destination}"

    except Exception as exc:
        return f"ERROR → {os.path.basename(source_path)} → {exc}"