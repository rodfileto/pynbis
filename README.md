# PyNBIS - Python Bindings for NBIS

[![Python Version](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-Public%20Domain-green.svg)](LICENSE)

**PyNBIS** is a comprehensive Python package providing Python bindings for **NBIS** (NIST Biometric Image Software), the industry-standard fingerprint processing library developed by the National Institute of Standards and Technology (NIST).

## Features

### Core Functionality
- **Minutiae Extraction** - Extract fingerprint minutiae using the MINDTCT algorithm
- **1:1 Fingerprint Matching** - Compare two fingerprints using the Bozorth3 matcher
- **1:N Identification** - Match one fingerprint against multiple gallery prints
- **Quality Assessment** - Compute NFIQ (NIST Fingerprint Image Quality) scores
- **Image Processing** - Binary fingerprint image generation and enhancement

### Package Highlights
- 🐍 **Pythonic API** - Clean, intuitive interface with both functional and OOP styles
- 🎯 **Type Hints** - Full type annotations for Python 3.10+
- 📦 **Easy Installation** - Simple pip installation with pre-compiled wheels (coming soon)
- 🔧 **Flexible** - Works with NumPy arrays for easy integration
- 📚 **Well Documented** - Comprehensive documentation and examples
- ⚡ **Fast** - Native C implementation for high performance

## Installation

### From PyPI (Recommended)
```bash
pip install pynbis
```

### From Source
```bash
git clone https://github.com/yourusername/pynbis.git
cd pynbis
pip install .
```

### Requirements
- Python 3.10 or higher
- NumPy 1.20.0 or higher
- C compiler (GCC, Clang, or MSVC)

### Optional Dependencies
For image loading and visualization:
```bash
pip install pynbis[imaging]
```

For development:
```bash
pip install pynbis[dev]
```

## Quick Start

### Basic Usage

```python
import numpy as np
from pynbis import extract_minutiae, match_fingerprints, compute_quality

# Load fingerprint images (as NumPy arrays)
probe = np.load('probe_fingerprint.npy')
gallery = np.load('gallery_fingerprint.npy')

# Extract minutiae
minutiae, binarized = extract_minutiae(probe)
print(f"Found {len(minutiae)} minutiae")

# Match two fingerprints
result = match_fingerprints(probe, gallery)
print(f"Match score: {result.score}")

# Compute quality
quality = compute_quality(probe)
print(quality)  # Quality: 2/5 (Very Good), Confidence: 0.847
```

### Object-Oriented Interface

```python
from pynbis import Fingerprint

# Create fingerprint objects
probe = Fingerprint(probe_image, ppi=500)
gallery = Fingerprint(gallery_image, ppi=500)

# Extract minutiae
probe.extract_minutiae()
print(f"Probe has {len(probe.minutiae)} minutiae")

# Compute quality
quality = probe.compute_quality()
print(f"Quality: {quality.quality}/5")

# Match fingerprints
result = probe.match(gallery, threshold=40)
print(f"Match: {result.matched}, Score: {result.score}")

# Access binarized image
binary_img = probe.binarized_image
```

## API Reference

### Functional API

#### `extract_minutiae(image, ppi=500)`
Extract minutiae from a fingerprint image.

**Parameters:**
- `image` (np.ndarray): Grayscale fingerprint image (uint8)
- `ppi` (int): Pixels per inch (default: 500)

**Returns:**
- `List[Minutia]`: List of detected minutiae
- `np.ndarray`: Binarized fingerprint image

**Example:**
```python
minutiae, binary = extract_minutiae(fingerprint_image)
for m in minutiae:
    print(f"Position: ({m.x}, {m.y}), Type: {m.minutia_type}, Quality: {m.quality}")
```

#### `match_fingerprints(probe, gallery, threshold=None, ppi=500)`
Match two fingerprint images.

**Parameters:**
- `probe` (np.ndarray): Probe fingerprint image
- `gallery` (np.ndarray): Gallery fingerprint image
- `threshold` (int, optional): Score threshold for binary decision
- `ppi` (int): Pixels per inch (default: 500)

**Returns:**
- `MatchResult`: Match result with score and metadata

**Example:**
```python
result = match_fingerprints(probe, gallery, threshold=40)
if result.matched:
    print(f"Fingerprints match with score {result.score}")
else:
    print(f"No match (score: {result.score})")
```

#### `compute_quality(image, ppi=500)`
Compute NFIQ quality score.

**Parameters:**
- `image` (np.ndarray): Grayscale fingerprint image
- `ppi` (int): Pixels per inch (default: 500)

**Returns:**
- `QualityResult`: Quality assessment result

**Example:**
```python
quality = compute_quality(fingerprint_image)
print(f"NFIQ Score: {quality.quality} (1=best, 5=worst)")
print(f"Confidence: {quality.confidence:.3f}")
```

#### `match_minutiae(probe_minutiae, gallery_minutiae)`
Match pre-extracted minutiae sets.

**Parameters:**
- `probe_minutiae` (List[Minutia]): Probe minutiae
- `gallery_minutiae` (List[Minutia]): Gallery minutiae

**Returns:**
- `MatchResult`: Match result with score

**Example:**
```python
probe_min, _ = extract_minutiae(probe_image)
gallery_min, _ = extract_minutiae(gallery_image)
result = match_minutiae(probe_min, gallery_min)
print(f"Match score: {result.score}")
```

### Object-Oriented API

#### `Fingerprint(image, ppi=500)`
Fingerprint object for processing.

**Methods:**
- `extract_minutiae()`: Extract minutiae from the image
- `compute_quality()`: Compute NFIQ quality score
- `match(other, threshold=None)`: Match against another fingerprint

**Properties:**
- `image`: Original fingerprint image
- `minutiae`: Extracted minutiae (after calling extract_minutiae)
- `quality`: Quality result (after calling compute_quality)
- `binarized_image`: Binarized image (after calling extract_minutiae)

**Example:**
```python
fp = Fingerprint(image, ppi=500)
fp.extract_minutiae()
fp.compute_quality()
print(fp)  # Fingerprint(640x480, 42 minutiae, quality=2)
```

### Data Classes

#### `Minutia`
Represents a fingerprint minutia point.

**Attributes:**
- `x` (int): X-coordinate
- `y` (int): Y-coordinate
- `direction` (int): Direction/angle
- `minutia_type` (MinutiaType): Type (RIDGE_ENDING or BIFURCATION)
- `quality` (float): Quality score (0.0-1.0)

#### `MatchResult`
Result of fingerprint matching.

**Attributes:**
- `score` (int): Match score (higher = better match)
- `probe_minutiae` (int): Number of probe minutiae
- `gallery_minutiae` (int): Number of gallery minutiae
- `matched` (bool): Whether prints match (if threshold specified)

#### `QualityResult`
Result of quality assessment.

**Attributes:**
- `quality` (int): NFIQ score (1-5, where 1 is best)
- `confidence` (float): Confidence value
- `return_code` (int): Return code from computation

### Utility Functions

```python
from pynbis.utils import (
    load_fingerprint,
    save_fingerprint,
    normalize_image,
    resize_fingerprint,
    visualize_minutiae,
    get_roi
)

# Load image from file
image = load_fingerprint('fingerprint.png')

# Normalize image
normalized = normalize_image(image, target_mean=127, target_std=64)

# Resize to target PPI
resized = resize_fingerprint(image, target_ppi=500, source_ppi=300)

# Visualize minutiae
minutiae, _ = extract_minutiae(image)
vis_image = visualize_minutiae(image, minutiae)
save_fingerprint(vis_image, 'minutiae_visualization.png')

# Get region of interest
x_min, y_min, x_max, y_max = get_roi(image)
roi = image[y_min:y_max, x_min:x_max]
```

## Advanced Examples

### 1:N Identification (Match one against many)

```python
from pynbis import Fingerprint

# Load probe
probe = Fingerprint(probe_image)
probe.extract_minutiae()

# Load gallery
gallery = [
    Fingerprint(gallery_img_1),
    Fingerprint(gallery_img_2),
    Fingerprint(gallery_img_3),
]

# Extract minutiae from gallery
for fp in gallery:
    fp.extract_minutiae()

# Match probe against all gallery prints
results = []
for i, gal_fp in enumerate(gallery):
    result = probe.match(gal_fp)
    results.append((i, result.score))

# Sort by score (descending)
results.sort(key=lambda x: x[1], reverse=True)

# Print top matches
print("Top matches:")
for idx, score in results[:5]:
    print(f"  Gallery #{idx}: Score {score}")
```

### Batch Processing

```python
from pathlib import Path
from pynbis import Fingerprint
import numpy as np

def process_directory(input_dir, output_dir):
    """Process all fingerprints in a directory."""
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    results = []
    
    for img_file in input_path.glob('*.png'):
        # Load and process
        fp = Fingerprint(load_fingerprint(img_file))
        fp.extract_minutiae()
        fp.compute_quality()
        
        # Save results
        result = {
            'filename': img_file.name,
            'minutiae_count': len(fp.minutiae),
            'quality': fp.quality.quality,
        }
        results.append(result)
        
        # Save binarized image
        output_file = output_path / f"{img_file.stem}_binary.png"
        save_fingerprint(fp.binarized_image, output_file)
    
    return results
```

### Quality-Based Filtering

```python
from pynbis import Fingerprint

def filter_by_quality(images, min_quality=3):
    """Filter fingerprints by minimum quality threshold."""
    good_images = []
    
    for img in images:
        fp = Fingerprint(img)
        quality = fp.compute_quality()
        
        if quality.quality <= min_quality:  # Lower is better
            good_images.append(img)
            print(f"✓ Quality {quality.quality}/5 - Accepted")
        else:
            print(f"✗ Quality {quality.quality}/5 - Rejected")
    
    return good_images
```

## Understanding Match Scores

Match scores from Bozorth3 typically range from 0 to several hundred:
- **0-20**: No match / very poor match
- **20-40**: Possible match, low confidence
- **40-100**: Good match, medium to high confidence
- **100+**: Excellent match, very high confidence

The exact threshold depends on your security requirements:
- **High security**: Use threshold of 80-100+
- **Medium security**: Use threshold of 40-60
- **Low security / verification**: Use threshold of 20-30

Always test on your specific dataset to determine optimal thresholds.

## Performance Considerations

- **Image Size**: Larger images take longer to process. Standard size is around 500x500 pixels.
- **PPI**: Higher PPI provides better accuracy but slower processing.
- **Minutiae Count**: More minutiae = more accurate matching but slower.
- **Pre-extraction**: For 1:N matching, pre-extract and cache minutiae.

## Troubleshooting

### ImportError: DLL load failed
- **Windows**: Ensure Visual C++ Redistributable is installed
- **Linux**: Install required system libraries: `sudo apt-get install build-essential`
- **macOS**: Install Xcode Command Line Tools: `xcode-select --install`

### Poor matching results
- Ensure images are at 500 PPI
- Check image quality with `compute_quality()`
- Verify images are grayscale and uint8
- Try normalizing images with `normalize_image()`

### Compilation errors
- Ensure you have a C compiler installed
- Update setuptools: `pip install --upgrade setuptools`
- On Windows, install Microsoft C++ Build Tools

## License and Disclaimer

This package wraps the **NBIS (NIST Biometric Image Software)** library, which is in the **public domain**.

### NIST Disclaimer

This software and/or related materials was developed at the National Institute of Standards and Technology (NIST) by employees of the Federal Government in the course of their official duties. Pursuant to title 17 Section 105 of the United States Code, this software is not subject to copyright protection and is in the public domain.

This software and/or related materials are provided "AS-IS" without warranty of any kind including NO WARRANTY OF PERFORMANCE, MERCHANTABILITY, NO WARRANTY OF NON-INFRINGEMENT OF ANY 3RD PARTY INTELLECTUAL PROPERTY or FITNESS FOR A PARTICULAR PURPOSE or for any purpose whatsoever. In no event shall NIST be liable for any damages and/or costs, including but not limited to incidental or consequential damages of any kind, including economic damage or injury to property and lost profits, regardless of whether NIST shall be advised, have reason to know, or in fact shall know of the possibility.

By using this software, you agree to bear all risk relating to quality, use and performance of the software and/or related materials. You agree to hold the Government harmless from any claim arising from your use of the software.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## References

- [NBIS Official Site](https://www.nist.gov/services-resources/software/nist-biometric-image-software-nbis)
- [NIST Fingerprint Research](https://www.nist.gov/programs-projects/fingerprint-research)
- [Bozorth3 Matcher](https://www.nist.gov/itl/iad/image-group/minutiae-interoperability-exchange-minex-iii)

## Support

For issues, questions, or contributions:
- GitHub Issues: https://github.com/yourusername/pynbis/issues
- Documentation: https://github.com/yourusername/pynbis#readme

## Acknowledgments

This package is a Python wrapper for NBIS, developed by NIST. All credit for the core fingerprint algorithms goes to the NIST development team and contributors to the NBIS project.
