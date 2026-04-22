# PyInstaller spec for MR Letters Generator
# Usage: pyinstaller build.spec
# Output: dist/MR_Letters_Generator/

import sys
import os
from pathlib import Path

block_cipher = None

# ---------------------------------------------------------------------------
# Collect all files inside assets/poppler so they are bundled with the app
# ---------------------------------------------------------------------------
def collect_assets():
    """Return a list of (src, dest_in_bundle) tuples for assets."""
    datas = []
    assets_root = Path("assets")
    if assets_root.exists():
        for path in assets_root.rglob("*"):
            if path.is_file():
                rel = str(path.parent)
                datas.append((str(path), rel))
    return datas


a = Analysis(
    ["main.py"],
    pathex=["."],
    binaries=[],
    datas=collect_assets(),
    hiddenimports=[
        "pandas",
        "openpyxl",
        "docx",
        "PIL",
        "tkinter",
        "tkinter.filedialog",
        "tkinter.messagebox",
        "tkinter.ttk",
        "tkinter.scrolledtext",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclude heavy ML libraries from the UI-only build to keep it smaller.
        # Remove these lines if the OCR pipeline is needed in the distributed build.
        "torch",
        "torchvision",
        "easyocr",
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="MR_Letters_Generator",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # No console window – GUI application
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="MR_Letters_Generator",
)
