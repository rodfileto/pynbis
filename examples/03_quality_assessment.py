
#!/usr/bin/env python3
"""
Example 3: Fingerprint Quality Assessment (NFIQ)

This example demonstrates how to compute and interpret
NFIQ (NIST Fingerprint Image Quality) scores.
"""

import numpy as np
from pathlib import Path
from pynbis import compute_quality, Fingerprint

try:
    from imageio.v2 import imread
    HAS_IMAGEIO = True
except ImportError:
    HAS_IMAGEIO = False

def interpret_nfiq(quality_value):
    """Interpret NFIQ score and return detailed information."""
    descriptions = {
        1: ("Excellent", "High confidence for matching", "Green"),
        2: ("Very Good", "Good confidence for matching", "Green"),
        3: ("Good", "Acceptable for matching", "Yellow"),
        4: ("Fair", "Marginal for matching", "Orange"),
        5: ("Poor", "Not recommended for matching", "Red"),
    }
    
    if quality_value in descriptions:
        return descriptions[quality_value]
    else:
        return ("Unknown", "Invalid quality score", "Gray")

def load_sample_image():
    """Load a real fingerprint image if available, else generate random."""
    fingerprints_dir = Path(__file__).parent.parent / "data" / "fingerprints"
    
    if HAS_IMAGEIO and fingerprints_dir.exists():
        image_files = list(fingerprints_dir.glob("*.jpg")) + list(fingerprints_dir.glob("*.png"))
        if len(image_files) >= 1:
            try:
                image = imread(image_files[0]).astype(np.uint8)
                if image.ndim == 3:
                    image = image[:, :, 0]
                print(f"Loaded real fingerprint: {image_files[0].name}\n")
                return image, True
            except Exception:
                pass
    
    print("Using random image (no real fingerprint found)\n")
    return np.random.randint(0, 256, (480, 640), dtype=np.uint8), False

def main():
    print("PyNBIS Example 3: Quality Assessment (NFIQ)")
    print("=" * 50)
    
    # Load real fingerprint or generate random
    base_image, is_real = load_sample_image()
    
    # Create variations for comparison
    if is_real:
        # Use real image with different crops/regions
        h, w = base_image.shape
        images = {
            "Full image": base_image,
            "Top half": base_image[:h//2, :],
            "Bottom half": base_image[h//2:, :],
        }
    else:
        # Generate sample fingerprint images with different characteristics
        images = {
            "Sample 1": np.random.randint(0, 256, (480, 640), dtype=np.uint8),
            "Sample 2": np.random.randint(50, 200, (480, 640), dtype=np.uint8),
            "Sample 3": np.random.randint(100, 150, (480, 640), dtype=np.uint8),
        }
    
    # Method 1: Functional API
    print("\n1. Using Functional API:")
    print("-" * 50)
    
    for name, image in images.items():
        quality = compute_quality(image, ppi=500)
        desc, meaning, color = interpret_nfiq(quality.quality)
        
        print(f"\n{name}:")
        print(f"  NFIQ Score: {quality.quality}/5")
        print(f"  Rating: {desc}")
        print(f"  Meaning: {meaning}")
        print(f"  Confidence: {quality.confidence:.4f}")
        print(f"  Return Code: {quality.return_code}")
    
    # Method 2: Object-Oriented API
    print("\n2. Using Object-Oriented API:")
    print("-" * 50)
    
    fingerprints = []
    for name, image in images.items():
        fp = Fingerprint(image, ppi=500)
        fp.compute_quality()
        fingerprints.append((name, fp))
    
    # Sort by quality (best first)
    fingerprints.sort(key=lambda x: x[1].quality.quality)
    
    print("\nFingerprints ranked by quality (best to worst):")
    for rank, (name, fp) in enumerate(fingerprints, 1):
        quality = fp.quality
        desc, _, _ = interpret_nfiq(quality.quality)
        print(f"  {rank}. {name}: {quality.quality}/5 ({desc})")
    
    # Quality-based filtering
    print("\n3. Quality-Based Filtering:")
    print("-" * 50)
    
    min_quality = 3  # Accept quality 1-3 (reject 4-5)
    
    print(f"Filtering with minimum quality threshold: {min_quality}")
    
    for name, fp in fingerprints:
        if fp.quality.quality <= min_quality:
            status = "✓ ACCEPTED"
        else:
            status = "✗ REJECTED"
        print(f"  {name}: Quality {fp.quality.quality}/5 -> {status}")
    
    # Combined quality and minutiae analysis
    print("\n4. Combined Quality and Minutiae Analysis:")
    print("-" * 50)
    
    for name, image in list(images.items())[:1]:  # Just first sample
        fp = Fingerprint(image, ppi=500)
        
        # Get quality
        quality = fp.compute_quality()
        
        # Extract minutiae
        minutiae = fp.extract_minutiae()
        
        # Analyze
        print(f"\n{name} - Detailed Analysis:")
        print(f"  Quality: {quality.quality}/5 ({interpret_nfiq(quality.quality)[0]})")
        print(f"  Confidence: {quality.confidence:.4f}")
        print(f"  Minutiae count: {len(minutiae)}")
        
        # Overall assessment
        if quality.quality <= 2 and len(minutiae) >= 30:
            assessment = "Excellent for matching"
        elif quality.quality <= 3 and len(minutiae) >= 20:
            assessment = "Good for matching"
        elif quality.quality <= 4 and len(minutiae) >= 15:
            assessment = "Acceptable for matching"
        else:
            assessment = "Poor for matching"
        
        print(f"  Overall: {assessment}")


if __name__ == "__main__":
    main()
