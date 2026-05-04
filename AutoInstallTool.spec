# -*- mode: python ; coding: utf-8 -*-
import os
import customtkinter

# Lấy đường dẫn của thư viện customtkinter để đóng gói assets của nó
ctk_path = os.path.dirname(customtkinter.__file__)

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('gui/assets', 'gui/assets'),
        (ctk_path, 'customtkinter'), # QUAN TRỌNG: Bao gồm dữ liệu giao diện của customtkinter
    ],
    hiddenimports=[
        'gui', 'gui.tabs', 'gui.tabs.install_tab', 'gui.tabs.edit_tab', 'gui.tabs.info_tab', 
        'gui.overlays', 'gui.overlays.edit_overlay', 'gui.components', 'gui.components.app_card',
        'gui.sidebar', 'gui.header', 'gui.styles',
        'core', 'core.admin_check', 'core.config_manager', 'core.process_runner', 'core.asset_manager',
        'PIL', 'PIL.Image', 'customtkinter'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
    name='AutoInstallToolBYPhamSu',
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
    icon='gui/assets/icons/title-logo.png', # Nếu có file .ico sẽ tốt hơn
    uac_admin=True, # Tự động yêu cầu quyền Admin khi chạy file .exe
)

