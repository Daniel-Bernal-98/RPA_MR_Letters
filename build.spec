# PyInstaller spec for MR Letters Generator
# Usage: pyinstaller build.spec
# Output: dist/MR_Letters_Generator/

from pathlib import Path

block_cipher = None


def collect_assets():
    """
    Bundle everything under ./assets into the app under an 'assets/' folder.

    Returns a list of (src, dest_relative_to_app) tuples.
    """
    datas = []
    assets_root = Path("assets")
    if not assets_root.exists():
        return datas

    for p in assets_root.rglob("*"):
        if p.is_file():
            # destination folder inside the bundle:
            # e.g. assets/poppler/Library/bin
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
        # Remove these lines if OCR / EasyOCR is needed in the distributed build.
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
    console=False,
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