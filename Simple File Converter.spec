# -*- mode: python ; coding: utf-8 -*-
from pathlib import Path
from PyInstaller.utils.hooks import collect_data_files

root = Path(SPECPATH).resolve()
source = root / 'src'
datas = collect_data_files('imageio_ffmpeg')
datas += [(str(source / 'sfc.ico'), '.')]
for path in source.iterdir():
    if path.is_file():
        datas.append((str(path), 'source'))
for name in ['README.md', 'THIRD_PARTY.txt']:
    datas.append((str(root / name), 'notices'))
datas.append((str(root / 'docs'), 'notices/docs'))
datas.append((str(root / 'licenses'), 'licenses'))

a = Analysis(
    [str(source / 'app.py')], pathex=[str(source)], binaries=[],
    datas=datas, hiddenimports=[], hookspath=[], hooksconfig={},
    runtime_hooks=[], excludes=[], noarchive=False, optimize=0,
)
# Qt must use Windows' unversioned ICU, not the incompatible DLL that some
# Python distributions place on the build machine's search path.
a.binaries = [entry for entry in a.binaries
              if Path(entry[0]).name.lower() not in {'icuuc.dll', 'icudt78.dll'}]
pyz = PYZ(a.pure)
exe = EXE(
    pyz, a.scripts, a.binaries, a.datas, [],
    name='Simple File Converter', icon=str(source / 'sfc.ico'),
    debug=False, bootloader_ignore_signals=False, strip=False, upx=False,
    console=False, disable_windowed_traceback=False,
)
