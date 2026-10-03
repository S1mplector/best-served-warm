# PyInstaller spec shared by Linux, macOS, and Windows runners.
from pathlib import Path
import sys

root = Path(SPECPATH)
a = Analysis(
    [str(root / "run.py")],
    pathex=[str(root / "src")],
    binaries=[],
    datas=[(str(root / "assets"), "assets")],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, [], exclude_binaries=True, name="BestServedWarm", console=False)
coll = COLLECT(exe, a.binaries, a.datas, strip=False, upx=False, name="BestServedWarm")
if sys.platform == "darwin":
    app = BUNDLE(coll, name="BestServedWarm.app", bundle_identifier="io.github.s1mplector.bestservedwarm")
