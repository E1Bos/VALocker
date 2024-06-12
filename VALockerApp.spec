# VALockerApp.spec
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['VALockerApp.py'],
    pathex=['.'],  # Ensure the current directory is in the path
    binaries=[],
    datas=[
        ('images/icons/*', 'images/icons'),  # Include icons
        ('src/*', 'src')  # Include src directory
    ],
    hiddenimports=[
        'customtkinter',
        'requests',
        'pillow',
        'pynput',
        'dxcam',
        'ruamel.yaml'
    ],
    hookspath=[],
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
    a.binaries,
    a.zipfiles,
    a.datas,
    name='VALocker',
    icon='images/icons/valocker.ico',
    debug=False,
    strip=False,
    upx=True,
    runtime_tmpdir=None,
    console=False )
