# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['src\\main.py'],
    pathex=[],
    binaries=[],
    datas=[('E:\\Environment\\Anaconda\\Anaconda3\\envs\\gpu6\\lib\\site-packages\\customtkinter', 'customtkinter/')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['numpy', 'PIL', 'Pillow', 'scipy', 'pandas', 'matplotlib', 'psutil', 'setuptools', 'pkg_resources', 'xml', 'unittest', 'email', 'http', 'sqlite3', 'ssl', 'multiprocessing'],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='TwoYaTimer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
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
