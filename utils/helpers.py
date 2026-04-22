import re


def sanitize_filename(name):
    """Return a Windows-safe version of *name* suitable for use in a file or folder path.

    Replaces or removes characters that are forbidden in Windows filenames
    (``< > : " / \\ | ? *`` and control characters 0x00-0x1F).
    Spaces are replaced with underscores.
    Leading/trailing dots and spaces are stripped.
    The result is capped at 200 characters so that full paths stay well below
    the Windows MAX_PATH limit.
    """
    # Replace forbidden characters with underscore
    name = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", str(name))
    # Replace spaces with underscores for cleaner filenames
    name = name.replace(" ", "_")
    # Strip leading/trailing dots, underscores, and spaces
    name = name.strip("._- ")
    # Collapse consecutive underscores
    name = re.sub(r"_+", "_", name)
    # Ensure the name is not empty after sanitisation
    if not name:
        name = "unnamed"
    # Limit length to keep paths short
    return name[:200]
