# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec for Football Scanner AI
Produces: FootballScannerAI.exe (Windows)
Usage: pyinstaller FootballScannerAI.spec
"""
import sys
import os

block_cipher = None

ROOT = os.path.abspath(".")

a = Analysis(
    ["launcher.py"],
    pathex=[ROOT],
    binaries=[],
    datas=[
        ("frontend/templates", "frontend/templates"),
        ("frontend/static", "frontend/static"),
        ("config", "config"),
        (".env", "."),
        ("data", "data"),
    ],
    hiddenimports=[
        "uvicorn.logging",
        "uvicorn.loops",
        "uvicorn.loops.auto",
        "uvicorn.protocols",
        "uvicorn.protocols.http",
        "uvicorn.protocols.http.auto",
        "uvicorn.protocols.websockets",
        "uvicorn.protocols.websockets.auto",
        "uvicorn.lifespan",
        "uvicorn.lifespan.on",
        "fastapi",
        "fastapi.staticfiles",
        "fastapi.templating",
        "sqlalchemy.dialects.sqlite",
        "aiosqlite",
        "jinja2",
        "loguru",
        "backend.main",
        "backend.api.routes.dashboard",
        "backend.api.routes.matches",
        "backend.api.routes.rules",
        "backend.api.routes.alerts",
        "backend.api.routes.backtest",
        "backend.api.routes.config_routes",
        "backend.core.rules.rule_001",
        "backend.core.rules.rule_002",
        "backend.core.rules.rule_003",
        "backend.core.rules.rule_004",
        "backend.core.rules.rule_005",
        "backend.providers.mock_provider",
        "backend.providers.footballdata_provider",
        "backend.services.monitor_service",
        "backend.services.backtest_service",
        "config.settings",
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=["tkinter", "matplotlib", "numpy", "pandas"],
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
    name="FootballScannerAI",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,   # Keep console visible so user sees logs
    icon=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="FootballScannerAI",
)
