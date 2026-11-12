# -*- mode: python ; coding: utf-8 -*-
# Build:  .venv/bin/pyinstaller YaiisJournal.spec   (see installer/README.md)
# On Windows use installer/windows/build-setup.bat, on macOS installer/mac/build-mac.sh.

import sys

block_cipher = None

if sys.platform == "win32":
    ICON = "installer/icons/icon.ico"
elif sys.platform == "darwin":
    ICON = "installer/icons/icon.icns"
else:
    ICON = "installer/icons/icon-256.png"

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('game/assets', 'game/assets'),
        ('README.md', '.'),
    ],
    hiddenimports=['pygame', 'pygame.mixer', 'pygame.font', 'pygame.image', 'pygame.transform'],
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

if sys.platform == "win32":
    # Onefile: the IExpress setup hands out a single self-contained exe.
    exe = EXE(
        pyz,
        a.scripts,
        a.binaries,
        a.zipfiles,
        a.datas,
        [],
        name='YaiisJournal',
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
        icon=ICON,
    )
else:
    # Onedir: launches instantly (no self-extraction on every run).
    # The Linux tarball / macOS .app wrap the folder anyway.
    exe = EXE(
        pyz,
        a.scripts,
        [],
        exclude_binaries=True,
        name='YaiisJournal',
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=True,
        upx_exclude=[],
        console=False,
        disable_windowed_traceback=False,
        argv_emulation=False,
        target_arch=None,
        codesign_identity=None,
        entitlements_file=None,
        icon=ICON,
    )
    coll = COLLECT(
        exe,
        a.binaries,
        a.zipfiles,
        a.datas,
        strip=False,
        upx=True,
        upx_exclude=[],
        name='YaiisJournal',
    )
    if sys.platform == "darwin":
        # Wrap the folder into a proper double-clickable .app bundle.
        app = BUNDLE(
            coll,
            exe,
            name='YaiisJournal.app',
            icon=ICON,
            bundle_identifier='com.yaiisjournal.game',
            version='1.0.0',
            info_plist={
                'CFBundleDisplayName': "Yaai's Journal",
                'CFBundleName': "Yaai's Journal",
                'CFBundleShortVersionString': '1.0.0',
                'NSHighResolutionCapable': True,
            },
        )
