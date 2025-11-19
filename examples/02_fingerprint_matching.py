
#!/usr/bin/env python3
"""
Example 2: Fingerprint Matching (1:1 Comparison)

This example demonstrates how to match two fingerprint images
and interpret the matching scores.
"""

import numpy as np
from pynbis import match_fingerprints, Fingerprint

def interpret_score(score):
    """Interpret a match score and return a description."""
    if score >= 100:
        return "Excellent match (very high confidence)"
    elif score >= 60:
        return "Good match (high confidence)"
    elif score >= 40:
        return "Moderate match (medium confidence)"
    elif score >= 20:
        return "Weak match (low confidence)"
    else:
        return "No match (very low confidence)"

def main():
    print("PyNBIS Example 2: Fingerprint Matching")
    print("=" * 50)
    
    # Generate sample fingerprint images (replace with real data)
    probe_image = np.random.randint(0, 256, (480, 640), dtype=np.uint8)
    gallery_image = np.random.randint(0, 256, (480, 640), dtype=np.uint8)
    
    # Method 1: Functional API
    print("\n1. Using Functional API:")
    print("-" * 50)
    
    # Match without threshold (get score only)
    result = match_fingerprints(probe_image, gallery_image)
    print(f"Match score: {result.score}")
    print(f"Interpretation: {interpret_score(result.score)}")
    
    # Match with threshold (binary decision)
    result_with_threshold = match_fingerprints(
        probe_image, 
        gallery_image, 
        threshold=40
    )
    print(f"\nWith threshold=40:")
    print(f"  Score: {result_with_threshold.score}")
    print(f"  Matched: {result_with_threshold.matched}")
    
    # Method 2: Object-Oriented API
    print("\n2. Using Object-Oriented API:")
    print("-" * 50)
    
    probe = Fingerprint(probe_image, ppi=500)
    gallery = Fingerprint(gallery_image, ppi=500)
    
    # Extract minutiae first
    probe.extract_minutiae()
    gallery.extract_minutiae()
    
    print(f"Probe minutiae: {len(probe.minutiae)}")
    print(f"Gallery minutiae: {len(gallery.minutiae)}")
    
    # Match fingerprints
    result = probe.match(gallery, threshold=40)
    
    print(f"\nMatch result:")
    print(f"  Score: {result.score}")
    print(f"  Matched: {result.matched}")
    print(f"  Interpretation: {interpret_score(result.score)}")
    
    # Test multiple thresholds
    print("\n3. Testing Multiple Thresholds:")
    print("-" * 50)
    
    thresholds = [20, 40, 60, 80, 100]
    for threshold in thresholds:
        result = probe.match(gallery, threshold=threshold)
        match_str = "✓ MATCH" if result.matched else "✗ NO MATCH"
        print(f"Threshold {threshold:3d}: Score {result.score:3d} -> {match_str}")


if __name__ == "__main__":
    main()
