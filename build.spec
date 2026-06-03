# PyInstaller spec for Automatic Letter Reader for workload Assignations
# Usage: pyinstaller build.spec

from pathlib import Path

block_cipher = None


def collect_assets():
    """
    Bundle everything under ./assets into the application.
    """
    datas = []
    assets_root = Path("assets")

    if not assets_root.exists():
        return datas

    for p in assets_root.rglob("*"):
        if p.is_file():
            rel_parent = p.parent.relative_to(assets_root)
            dest = str(Path("assets") / rel_parent)
            datas.append((str(p), dest))

    return datas


a = Analysis(
    ["main.py"],
    pathex=["."],
    binaries=[],
    datas=collect_assets(),
    hiddenimports=[
        # Core
        "pandas",
        "openpyxl",
        "docx",
        "PIL",

        # GUI
        "tkinter",
        "tkinter.filedialog",
        "tkinter.messagebox",
        "tkinter.ttk",
        "tkinter.scrolledtext",

        # PDF Processing
        "pdf2image",

        # OCR
        "cv2",
        "numpy",
        "pytesseract",

        # Matching
        "rapidfuzz",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
    icon="assets/icon.ico",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
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
