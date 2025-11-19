
# Changelog

All notable changes to PyNBIS will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-11-18

### Added
- Initial release of PyNBIS
- Python bindings for NBIS (NIST Biometric Image Software)
- Minutiae extraction using MINDTCT algorithm
- Fingerprint matching using Bozorth3 matcher
- Quality assessment using NFIQ algorithm
- Both functional and object-oriented APIs
- Type hints for Python 3.10+
- Comprehensive documentation and examples
- Utility functions for image loading and processing
- Support for NumPy arrays
- Example scripts demonstrating key features
- Batch processing capabilities

### Features
- Extract fingerprint minutiae from images
- Perform 1:1 fingerprint matching
- Support for 1:N identification
- Compute NFIQ quality scores
- Generate binarized fingerprint images
- Match pre-extracted minutiae
- Visualization utilities
- Image preprocessing functions

### Supported Platforms
- Linux (tested on Ubuntu 20.04+)
- macOS (tested on macOS 12+)
- Windows (with MSVC)

### Python Support
- Python 3.10
- Python 3.11
- Python 3.12

### Dependencies
- NumPy >= 1.20.0
- Optional: Pillow, scipy, opencv-python for image utilities

### Documentation
- Comprehensive README with API reference
- Example scripts covering all major features
- NIST disclaimer and public domain notice
- Installation and troubleshooting guides

## [Unreleased]

### Planned
- Pre-compiled wheels for major platforms
- Additional image format support
- Performance optimizations
- More comprehensive test suite
- Advanced matching options
- Support for ANSI/NIST-ITL format export
