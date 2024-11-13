# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['app3.py'],
    pathex=[],
    binaries=[],
    datas=[('electric_locks.json', '.'), ('box_locks.json', '.'), ('translations.json', '.'), ('simple.png', '.'), ('kunci.png', '.'), ('kunci menkongqi.png', '.'), ('UB.png', '.')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['unittest', 'email', 'html', 'http', 'tkinter.dnd', 'tkinter.colorchooser'],
    noarchive=True,
    optimize=2,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='app3',
    debug=False,
    bootloader_ignore_signals=False,
    strip=True,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
