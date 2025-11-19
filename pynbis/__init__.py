
"""
PyNBIS - Python bindings for NBIS (NIST Biometric Image Software)

A comprehensive Python package for fingerprint processing, including:
- Minutiae extraction
- Fingerprint matching (1:1 and 1:N)
- Quality assessment (NFIQ)
- Image processing utilities

NIST Public Domain Notice:
This software includes the NBIS library developed by the National Institute
of Standards and Technology (NIST). NBIS is in the public domain.
"""

__version__ = "1.0.0"
__author__ = "NBIS Python Bindings Project"
__license__ = "Public Domain"

from .core import (
    extract_minutiae,
    match_fingerprints,
    compute_quality,
    match_minutiae,
    Fingerprint,
    MinutiaType,
    Minutia,
    MatchResult,
    QualityResult,
)

__all__ = [
    "extract_minutiae",
    "match_fingerprints",
    "compute_quality",
    "match_minutiae",
    "Fingerprint",
    "MinutiaType",
    "Minutia",
    "MatchResult",
    "QualityResult",
]
