
#!/usr/bin/env python3
"""
Example 1: Basic Minutiae Extraction

This example demonstrates how to extract minutiae from a fingerprint image
using both the functional and object-oriented interfaces.
"""

import numpy as np
from pynbis import extract_minutiae, Fingerprint

def main():
    # Generate a sample fingerprint image (replace with real data)
    # In practice, you would load this from a file using:
    # from pynbis.utils import load_fingerprint
    # image = load_fingerprint('fingerprint.png')
    
    print("PyNBIS Example 1: Basic Minutiae Extraction")
    print("=" * 50)
    
    # Create a sample image (normally you'd load a real fingerprint)
    image = np.random.randint(0, 256, (480, 640), dtype=np.uint8)
    
    # Method 1: Functional API
    print("\n1. Using Functional API:")
    print("-" * 50)
    
    minutiae, binarized = extract_minutiae(image, ppi=500)
    
    print(f"Extracted {len(minutiae)} minutiae")
    print(f"Binarized image shape: {binarized.shape}")
    
    # Print first few minutiae
    print("\nFirst 5 minutiae:")
    for i, m in enumerate(minutiae[:5]):
        print(f"  {i+1}. Position: ({m.x:3d}, {m.y:3d}), "
              f"Direction: {m.direction:3d}, "
              f"Type: {m.minutia_type.name}, "
              f"Quality: {m.quality:.3f}")
    
    # Method 2: Object-Oriented API
    print("\n2. Using Object-Oriented API:")
    print("-" * 50)
    
    fp = Fingerprint(image, ppi=500)
    fp.extract_minutiae()
    
    print(f"Fingerprint object: {fp}")
    print(f"Total minutiae: {len(fp.minutiae)}")
    print(f"Binarized image available: {fp.binarized_image is not None}")
    
    # Count minutiae by type
    endings = sum(1 for m in fp.minutiae if m.minutia_type.name == 'RIDGE_ENDING')
    bifurcations = sum(1 for m in fp.minutiae if m.minutia_type.name == 'BIFURCATION')
    
    print(f"\nMinutiae breakdown:")
    print(f"  Ridge endings: {endings}")
    print(f"  Bifurcations: {bifurcations}")
    
    # Find high-quality minutiae
    high_quality = [m for m in fp.minutiae if m.quality > 0.9]
    print(f"  High quality (>0.9): {len(high_quality)}")


if __name__ == "__main__":
    main()
