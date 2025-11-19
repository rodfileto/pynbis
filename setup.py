
"""
Setup script for PyNBIS - Python bindings for NBIS fingerprint library.
"""

import os
import sys
import glob
from pathlib import Path
from setuptools import setup, Extension
import numpy as np

# Get the directory containing this setup.py
here = Path(__file__).parent.absolute()
nbis_src = here / "nbis_src"

# Collect all NBIS source files we need to compile
def get_nbis_sources():
    """Get all required NBIS C source files."""
    sources = []
    
    # Core algorithm directories (these are required)
    core_dirs = [
        nbis_src / "bozorth3" / "src" / "lib" / "bozorth3",
        nbis_src / "mindtct" / "src" / "lib" / "mindtct",
        nbis_src / "nfiq" / "src" / "lib" / "nfiq",
    ]
    
    # Get all .c files from core directories
    # Exclude files that are not needed or have complex dependencies
    excluded_files = ['to_type9.c', 'update.c']  # ANSI/NIST format related
    
    for src_dir in core_dirs:
        if src_dir.exists():
            c_files = list(src_dir.glob("*.c"))
            for f in c_files:
                if f.name not in excluded_files:
                    sources.append(str(f))
    
    # Common library sources (selective - only what we need)
    # These directories contain utility functions used by the core algorithms
    common_subdirs = [
        "util",     # Utility functions
        "mlp",      # Multi-layer perceptron (for NFIQ)
        "ihead",    # Image header utilities
        "image",    # Image manipulation
    ]
    
    for subdir in common_subdirs:
        src_dir = nbis_src / "commonnbis" / "src" / "lib" / subdir
        if src_dir.exists():
            c_files = list(src_dir.glob("*.c"))
            # Exclude problematic files that have extra dependencies
            excluded = ['nistcom.c', 'readihdr.c']
            for f in c_files:
                if f.name not in excluded:
                    sources.append(str(f))
    
    # Math libraries (needed by NFIQ)
    math_dirs = [
        nbis_src / "commonnbis" / "src" / "lib" / "cblas",
        nbis_src / "commonnbis" / "src" / "lib" / "f2c",
    ]
    
    for src_dir in math_dirs:
        if src_dir.exists():
            c_files = list(src_dir.glob("*.c"))
            sources.extend([str(f) for f in c_files])
    
    return sources

def get_nbis_includes():
    """Get all required NBIS include directories."""
    includes = [
        str(nbis_src / "bozorth3" / "include"),
        str(nbis_src / "mindtct" / "include"),
        str(nbis_src / "nfiq" / "include"),
        str(nbis_src / "commonnbis" / "include"),
        str(nbis_src / "an2k" / "include"),
        str(nbis_src / "pcasys" / "include"),
        str(nbis_src / "imgtools" / "include"),
        str(nbis_src / "commonnbis" / "include" / "mlp"),
    ]
    return includes

# Define compiler flags
extra_compile_args = []
extra_link_args = []

if sys.platform == 'darwin':  # macOS
    extra_compile_args.extend(['-Wno-deprecated-declarations', '-Wno-unused-result'])
elif sys.platform == 'linux':
    extra_compile_args.extend(['-Wno-deprecated-declarations', '-Wno-unused-result'])
elif sys.platform == 'win32':
    extra_compile_args.extend(['/D_CRT_SECURE_NO_WARNINGS'])

# Get NBIS sources and includes
nbis_sources = get_nbis_sources()
nbis_includes = get_nbis_includes()

print(f"Found {len(nbis_sources)} NBIS source files")
print(f"Include directories: {nbis_includes}")

# Define the extension module
ext_module = Extension(
    'pynbis._nbis_ext',
    sources=[
        'pynbis/_nbis_ext.c',
    ] + nbis_sources,
    include_dirs=[
        np.get_include(),
    ] + nbis_includes,
    extra_compile_args=extra_compile_args,
    extra_link_args=extra_link_args,
    define_macros=[
        ('NPY_NO_DEPRECATED_API', 'NPY_1_7_API_VERSION'),
    ],
    language='c',
)

# Read long description from README
long_description = ""
readme_path = here / "README.md"
if readme_path.exists():
    with open(readme_path, 'r', encoding='utf-8') as f:
        long_description = f.read()

# Setup configuration
setup(
    ext_modules=[ext_module],
    long_description=long_description,
    long_description_content_type='text/markdown',
)
