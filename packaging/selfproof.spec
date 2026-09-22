# PyInstaller spec for a single-file `selfproof` binary.
# Build (from the repo root):
#   pip install pyinstaller
#   pyinstaller packaging/selfproof.spec --distpath dist --workpath build/pyi
# Produces dist/selfproof (or dist/selfproof.exe on Windows). Each OS builds its
# own binary; PyInstaller does not cross-compile (see the release workflow).

import os

root = os.path.abspath(os.getcwd())
src = os.path.join(root, "src")
kernel = os.path.join(root, "src", "renker_core")

a = Analysis(
    [os.path.join(root, "packaging", "entry.py")],
    pathex=[src, kernel],
    binaries=[],
    datas=[
        (os.path.join(src, "selfproof", "gates", "data", "german_markers.json"),
         "selfproof/gates/data"),
    ],
    hiddenimports=["renker_core"],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="selfproof",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=True,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
