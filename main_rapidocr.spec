# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_data_files
import os


# ------------------------------------------------------------
# RapidOCR data
# ------------------------------------------------------------
# Collect RapidOCR's configuration/data files, but only keep the
# English detection + recognition ONNX models used by C.R.E.N.
#
# Current OCR configuration:
#   Detection   : English mobile detector
#   Recognition : English PP-OCRv4 mobile
#   Angle CLS   : Disabled

all_rapidocr_datas = collect_data_files("rapidocr")

required_models = {
    "en_PP-OCRv3_det_mobile.onnx",
    "en_PP-OCRv4_rec_mobile.onnx",
}


rapidocr_datas = []

for source, destination in all_rapidocr_datas:

    # Keep everything that is NOT an ONNX model.
    # This preserves default_models.yaml and other required
    # RapidOCR configuration/data files.
    if not source.lower().endswith(".onnx"):
        rapidocr_datas.append((source, destination))
        continue

    # For ONNX models, only include the two actually used.
    if os.path.basename(source) in required_models:
        rapidocr_datas.append((source, destination))


# ------------------------------------------------------------
# Modules not needed by C.R.E.N.
# ------------------------------------------------------------
excludes = [

    # Old OCR / ML stacks
    "paddle",
    "paddleocr",
    "paddlepaddle",
    "easyocr",
    "torch",
    "torchvision",

    # Large scientific / visualization packages not used
    "matplotlib",
    "pandas",
    "pandas.tests",
    "scipy",
    "scipy.tests",

    # Interactive / notebook / documentation / testing
    "IPython",
    "jupyter",
    "notebook",
    "pytest",
    "unittest",
    "tkinter.test",
    "docutils",
    "sphinx",

    # Package/build tooling not required at runtime
    "setuptools",
    "pip",
    "wheel",

    # Development/test-only modules
    "numpy.tests",
    "numpy.f2py",
    "PIL.tests",
    "pydoc_data",
]


# ------------------------------------------------------------
# Native libraries that should NOT be UPX compressed
# ------------------------------------------------------------
upx_exclude = [

    "vcruntime140.dll",
    "vcruntime140_1.dll",

    "python3*.dll",

    "opencv_*.dll",

    "onnxruntime*.dll",
    "onnxruntime*.pyd",
]


# ------------------------------------------------------------
# Analysis
# ------------------------------------------------------------
a = Analysis(

    ["main.py"],

    pathex=[],

    binaries=[],

    datas=[
        ("alert.WAV", "."),
        ("CREN.ico", "."),
    ] + rapidocr_datas,

    hiddenimports=[],

    hookspath=[],

    hooksconfig={},

    runtime_hooks=[],

    excludes=excludes,

    noarchive=False,

    optimize=2,
)


# ------------------------------------------------------------
# Python archive
# ------------------------------------------------------------
pyz = PYZ(a.pure)


# ------------------------------------------------------------
# Executable
# ------------------------------------------------------------
# Produces CREN.exe with the C.R.E.N. application icon.
exe = EXE(

    pyz,

    a.scripts,

    [],

    exclude_binaries=True,

    name="CREN",

    icon="CREN.ico",

    debug=False,

    bootloader_ignore_signals=False,

    strip=False,

    upx=True,

    upx_exclude=upx_exclude,

    runtime_tmpdir=None,

    console=False,

    disable_windowed_traceback=False,

    argv_emulation=False,

    target_arch=None,

    codesign_identity=None,

    entitlements_file=None,
)


# ------------------------------------------------------------
# ONEDIR distribution
# ------------------------------------------------------------
# Final output:
#
# dist/
# └── CREN v2.0.1/
#     ├── CREN.exe
#     └── _internal/
#
coll = COLLECT(

    exe,

    a.binaries,

    a.datas,

    strip=False,

    upx=True,

    upx_exclude=upx_exclude,

    name="CREN v2.0.1",
)