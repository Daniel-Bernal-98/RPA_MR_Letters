import os
import shutil
from utils.helpers import sanitize_filename


def save_file(source_path, patient, dos, collector, output_dir):
    """
    Guarda el archivo en:
    output_dir / collector / patient_dos.pdf
    """

    try:
        # Si no hay collector → UNASSIGNED
        collector = collector if collector else "UNASSIGNED"

        collector_dir = os.path.join(output_dir, sanitize_filename(collector))
        os.makedirs(collector_dir, exist_ok=True)

        # Nombre final: Apellido_Nombre_DOS.pdf
        new_filename = f"{patient}_{dos}.pdf"
        new_filename = sanitize_filename(new_filename)

        destination = os.path.join(collector_dir, new_filename)

        # Copiar archivo
        shutil.copy2(source_path, destination)

        return f"OK → {destination}"

    except Exception as exc:
        return f"ERROR → {os.path.basename(source_path)} → {exc}"