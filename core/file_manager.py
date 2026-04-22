import os
import shutil

from utils.helpers import sanitize_filename


def save_file(source_path, patient, date_of_service, collector, output_dir):
    """Copy *source_path* into ``<output_dir>/<collector>/`` with a sanitised filename.

    The new filename follows the pattern ``<patient>_<dos>_<original_basename>``.
    The collector sub-folder is created automatically if it does not exist.

    Parameters
    ----------
    source_path : str
        Path of the file to copy.
    patient : str
        Patient name (used in the destination filename).
    date_of_service : str
        Date of Service string (used in the destination filename).
    collector : str
        Name of the collector; determines the sub-folder.
    output_dir : str
        Base output directory.

    Returns
    -------
    str  – success message
    str  – error message if an exception occurs
    """
    try:
        collector_dir = os.path.join(output_dir, sanitize_filename(collector))
        os.makedirs(collector_dir, exist_ok=True)

        original_ext = os.path.splitext(source_path)[1]
        new_filename = sanitize_filename(f"{patient}_{date_of_service}") + original_ext
        destination = os.path.join(collector_dir, new_filename)

        shutil.copy2(source_path, destination)
        return f"File saved successfully: {destination}"

    except Exception as exc:
        return f"Error saving file: {os.path.basename(source_path)} – {exc}"
