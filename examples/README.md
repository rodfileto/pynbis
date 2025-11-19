
# PyNBIS Examples

This directory contains example scripts demonstrating various features of the PyNBIS library.

## Examples Overview

### 1. Basic Minutiae Extraction (`01_basic_minutiae_extraction.py`)
Learn how to extract fingerprint minutiae using both functional and object-oriented APIs.

**Key concepts:**
- Loading fingerprint images
- Extracting minutiae
- Accessing minutiae properties
- Counting minutiae by type

**Run:**
```bash
python 01_basic_minutiae_extraction.py
```

### 2. Fingerprint Matching (`02_fingerprint_matching.py`)
Demonstrates 1:1 fingerprint comparison and score interpretation.

**Key concepts:**
- Matching two fingerprints
- Understanding match scores
- Using thresholds for binary decisions
- Interpreting confidence levels

**Run:**
```bash
python 02_fingerprint_matching.py
```

### 3. Quality Assessment (`03_quality_assessment.py`)
Shows how to compute and interpret NFIQ quality scores.

**Key concepts:**
- Computing NFIQ scores
- Understanding quality levels (1-5)
- Quality-based filtering
- Combined quality and minutiae analysis

**Run:**
```bash
python 03_quality_assessment.py
```

### 4. One-to-Many Matching (`04_one_to_many_matching.py`)
Demonstrates 1:N identification by matching against a gallery.

**Key concepts:**
- Creating a fingerprint gallery
- Matching one probe against multiple gallery prints
- Ranking results by score
- Making identification decisions

**Run:**
```bash
python 04_one_to_many_matching.py
```

### 5. Batch Processing (`05_batch_processing.py`)
Shows how to process multiple fingerprints efficiently.

**Key concepts:**
- Batch minutiae extraction
- Batch quality assessment
- Statistical analysis
- Results export (JSON)

**Run:**
```bash
python 05_batch_processing.py
```

## Using with Real Data

To use these examples with real fingerprint data, replace the sample image generation:

```python
# Instead of:
image = np.random.randint(0, 256, (480, 640), dtype=np.uint8)

# Use:
from pynbis.utils import load_fingerprint
image = load_fingerprint('path/to/fingerprint.png')
```

## Sample Data

For testing purposes, you can download sample fingerprint images from:
- NIST Special Database 4: https://www.nist.gov/srd/nist-special-database-4
- NIST Special Database 14: https://www.nist.gov/itl/iad/image-group/nist-special-database-14

## Requirements

All examples require:
- NumPy
- PyNBIS (installed)

For loading images from files, install optional dependencies:
```bash
pip install pynbis[imaging]
```

## Notes

- Examples use randomly generated images for demonstration
- Real fingerprints will produce more realistic results
- Adjust PPI (pixels per inch) based on your scanner/device
- Match score thresholds depend on your security requirements
- Quality scores help filter poor-quality images before matching

## Further Reading

See the main README.md for:
- Detailed API documentation
- Installation instructions
- Advanced usage patterns
- Troubleshooting tips
