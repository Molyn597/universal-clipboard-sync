# -*- mode: python ; coding: utf-8 -*-
# Build: pyinstaller --noconfirm universal_clipboard.spec
import os
import sys

sys.path.insert(0, SPECPATH)
from version import APP_NAME, __version__  # noqa: E402

IS_MAC = sys.platform == "darwin"
MAC_ICON = os.path.join("build", "icon.icns")  # generated from assets/icon.png in CI

a = Analysis(
    ["main.py"],
    pathex=[SPECPATH],
    datas=[("static", "static"), ("assets", "assets")],
    excludes=["tkinter"],
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name=APP_NAME,
    console=False,
    icon=os.path.join("assets", "icon.ico") if not IS_MAC else (MAC_ICON if os.path.exists(MAC_ICON) else None),
)

coll = COLLECT(exe, a.binaries, a.datas, name=APP_NAME)

if IS_MAC:
    app = BUNDLE(
        coll,
        name=f"{APP_NAME}.app",
        icon=MAC_ICON if os.path.exists(MAC_ICON) else None,
        bundle_identifier="com.molyn597.universalclipboard",
        version=__version__,
        info_plist={
            "CFBundleShortVersionString": __version__,
            "CFBundleVersion": __version__,
            "LSMinimumSystemVersion": "12.0",
            "NSHighResolutionCapable": True,
            "NSDownloadsFolderUsageDescription": "Universal Clipboard ukládá soubory přijaté z jiných zařízení do složky Stažené.",
        },
    )
